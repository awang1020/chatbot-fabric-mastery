// Subscription-scope deployment for Ask Fabric Mastery.
// Creates the resource group + the Azure OpenAI account & deployments.
targetScope = 'subscription'

@description('Azure region (must support the requested model SKUs).')
param location string = 'eastus2'

@description('Resource group name.')
param resourceGroupName string = 'rg-ask-fabric-mastery'

@description('Cognitive Services (Azure OpenAI) account name. Must be globally unique.')
param openAiName string = 'oai-fabmastery-${uniqueString(subscription().id, resourceGroupName)}'

@description('Chat deployment name (used by the app).')
param chatDeployment string = 'gpt-4o-mini'

@description('Underlying chat model.')
param chatModel string = 'gpt-4o-mini'

@description('Chat model version.')
param chatModelVersion string = '2024-07-18'

@description('Chat deployment SKU name.')
param chatSkuName string = 'GlobalStandard'

@description('Chat deployment capacity (×1000 TPM).')
param chatCapacity int = 50

@description('Embedding deployment name (used by the app).')
param embeddingDeployment string = 'text-embedding-3-small'

@description('Underlying embedding model.')
param embeddingModel string = 'text-embedding-3-small'

@description('Embedding model version.')
param embeddingModelVersion string = '1'

@description('Embedding deployment SKU name.')
param embeddingSkuName string = 'GlobalStandard'

@description('Embedding deployment capacity (×1000 TPM).')
param embeddingCapacity int = 50

@description('Tags applied to all resources.')
param tags object = {
  project: 'chatbot-fabric-mastery'
  managedBy: 'bicep'
}

resource rg 'Microsoft.Resources/resourceGroups@2024-03-01' = {
  name: resourceGroupName
  location: location
  tags: tags
}

module openai 'openai.bicep' = {
  scope: rg
  name: 'openai-deploy'
  params: {
    name: openAiName
    location: location
    chatDeployment: chatDeployment
    chatModel: chatModel
    chatModelVersion: chatModelVersion
    chatSkuName: chatSkuName
    chatCapacity: chatCapacity
    embeddingDeployment: embeddingDeployment
    embeddingModel: embeddingModel
    embeddingModelVersion: embeddingModelVersion
    embeddingSkuName: embeddingSkuName
    embeddingCapacity: embeddingCapacity
    tags: tags
  }
}

output resourceGroupName string = rg.name
output openAiName string = openai.outputs.name
output openAiEndpoint string = openai.outputs.endpoint
output chatDeployment string = chatDeployment
output chatModel string = chatModel
output embeddingDeployment string = embeddingDeployment
output embeddingModel string = embeddingModel
output location string = location
