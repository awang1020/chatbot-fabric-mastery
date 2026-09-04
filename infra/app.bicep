// Resource-group-scoped deployment for Ask Fabric Mastery on Container Apps.
// Adds a Log Analytics workspace, a Container Apps Environment, the Container App
// (scale-to-zero, system-assigned managed identity) and grants it
// "Cognitive Services OpenAI User" on the existing Azure OpenAI account.
targetScope = 'resourceGroup'

@description('Existing Azure OpenAI account name in this resource group.')
param openAiName string

@description('Full container image (tag included).')
param containerImage string = 'mcr.microsoft.com/k8se/quickstart:latest'

@description('Container App name. Kept as-is across product renames: changing it recreates the app and re-issues the managed TLS certificate for the custom domain.')
param appName string = 'ask-fabric-mastery'

@description('Location. Defaults to the resource group location.')
param location string = resourceGroup().location

@description('Min replicas (0 = scale-to-zero).')
@minValue(0)
@maxValue(10)
param minReplicas int = 0

@description('Max replicas.')
@minValue(1)
@maxValue(10)
param maxReplicas int = 2

@description('Container chat deployment name (overrides image default if set).')
param chatDeployment string = 'gpt-4o-mini'

@description('Container chat model id.')
param chatModel string = 'gpt-4o-mini'

@description('Container embedding deployment name.')
param embeddingDeployment string = 'text-embedding-3-small'

@description('Container embedding model id.')
param embeddingModel string = 'text-embedding-3-small'

@description('Default UI language (en or fr).')
@allowed([ 'en', 'fr' ])
param defaultLanguage string = 'fr'

@description('Daily LAW ingestion cap (GB). Keeps the bill predictable.')
param logDailyQuotaGb int = 1

@description('Shared access code that visitors must enter to unlock unlimited questions. Publish it in the latest newsletter edition so readers can try the app.')
@secure()
param appPassword string = ''

@description('Free demo questions allowed before the newsletter access code is required.')
@minValue(0)
@maxValue(20)
param freeQuestions int = 2

@description('Max questions a single browser session can ask per window.')
@minValue(1)
@maxValue(500)
param rateLimitMaxQuestions int = 20

@description('Sliding window size, in seconds, for the per-session rate limit.')
@minValue(60)
@maxValue(86400)
param rateLimitWindowSeconds int = 900

@description('Tags applied to every resource created here.')
param tags object = {
  project: 'chatbot-fabric-mastery'
  managedBy: 'bicep'
}

resource openai 'Microsoft.CognitiveServices/accounts@2024-10-01' existing = {
  name: openAiName
}

resource law 'Microsoft.OperationalInsights/workspaces@2023-09-01' = {
  name: 'law-${appName}'
  location: location
  tags: tags
  properties: {
    sku: { name: 'PerGB2018' }
    retentionInDays: 30
    workspaceCapping: { dailyQuotaGb: logDailyQuotaGb }
  }
}

resource env 'Microsoft.App/managedEnvironments@2024-03-01' = {
  name: 'cae-${appName}'
  location: location
  tags: tags
  properties: {
    appLogsConfiguration: {
      destination: 'log-analytics'
      logAnalyticsConfiguration: {
        customerId: law.properties.customerId
        sharedKey: law.listKeys().primarySharedKey
      }
    }
    zoneRedundant: false
  }
}

resource app 'Microsoft.App/containerApps@2024-03-01' = {
  name: appName
  location: location
  tags: tags
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    managedEnvironmentId: env.id
    configuration: {
      activeRevisionsMode: 'Single'
      secrets: [
        {
          name: 'app-password'
          value: appPassword
        }
      ]
      ingress: {
        external: true
        targetPort: 8501
        transport: 'auto'
        allowInsecure: false
        stickySessions: {
          affinity: 'sticky'
        }
        traffic: [
          {
            latestRevision: true
            weight: 100
          }
        ]
      }
    }
    template: {
      containers: [
        {
          name: 'streamlit'
          image: containerImage
          resources: {
            cpu: json('0.5')
            memory: '1Gi'
          }
          env: [
            { name: 'AZURE_OPENAI_ENDPOINT', value: openai.properties.endpoint }
            { name: 'AZURE_OPENAI_API_VERSION', value: '2024-10-21' }
            { name: 'AZURE_OPENAI_CHAT_DEPLOYMENT', value: chatDeployment }
            { name: 'AZURE_OPENAI_CHAT_MODEL', value: chatModel }
            { name: 'AZURE_OPENAI_EMBEDDING_DEPLOYMENT', value: embeddingDeployment }
            { name: 'AZURE_OPENAI_EMBEDDING_MODEL', value: embeddingModel }
            { name: 'DATA_DIR', value: '/app/data/newsletters' }
            { name: 'STORAGE_DIR', value: '/app/storage/chroma' }
            { name: 'COLLECTION_NAME', value: 'fabric_mastery' }
            { name: 'DEFAULT_LANGUAGE', value: defaultLanguage }
            // Retrieval & generation tuning (TOP_K, SIMILARITY_CUTOFF, TEMPERATURE, MAX_TOKENS)
            // live in src/config.py — not in infra — so a code change ships without a Bicep redeploy.
            { name: 'APP_PASSWORD', secretRef: 'app-password' }
            { name: 'FREE_QUESTIONS', value: string(freeQuestions) }
            { name: 'RATE_LIMIT_MAX_QUESTIONS', value: string(rateLimitMaxQuestions) }
            { name: 'RATE_LIMIT_WINDOW_SECONDS', value: string(rateLimitWindowSeconds) }
          ]
          probes: [
            {
              type: 'Liveness'
              httpGet: {
                path: '/_stcore/health'
                port: 8501
              }
              initialDelaySeconds: 20
              periodSeconds: 30
              timeoutSeconds: 5
            }
            {
              type: 'Readiness'
              httpGet: {
                path: '/_stcore/health'
                port: 8501
              }
              initialDelaySeconds: 10
              periodSeconds: 15
              timeoutSeconds: 5
            }
          ]
        }
      ]
      scale: {
        minReplicas: minReplicas
        maxReplicas: maxReplicas
        rules: [
          {
            name: 'http-rule'
            http: {
              metadata: {
                concurrentRequests: '50'
              }
            }
          }
        ]
      }
    }
  }
}

// Cognitive Services OpenAI User
var openAiUserRoleId = '5e0bd9bd-7b93-4f28-af87-19fc36ad61bd'

resource roleAssign 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  scope: openai
  name: guid(openai.id, app.id, openAiUserRoleId)
  properties: {
    principalId: app.identity.principalId
    principalType: 'ServicePrincipal'
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', openAiUserRoleId)
  }
}

output appName string = app.name
output fqdn string = app.properties.configuration.ingress.fqdn
output appUrl string = 'https://${app.properties.configuration.ingress.fqdn}'
output logAnalyticsName string = law.name
output containerEnvironmentName string = env.name
