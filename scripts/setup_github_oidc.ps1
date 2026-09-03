#requires -Version 7.0
<#
.SYNOPSIS
    Bootstrap GitHub Actions OIDC trust for the Ask Fabric Mastery repo.

.DESCRIPTION
    Creates an Entra ID app registration + service principal, federated credentials
    bound to your GitHub repo, and the RBAC role assignments the workflow needs
    (read Azure OpenAI for embeddings; update the Container App image).
    Prints the exact GitHub secrets and variables to set at the end.

.EXAMPLE
    pwsh ./scripts/setup_github_oidc.ps1 `
        -GithubOwner antoinewang `
        -GithubRepo  chatbot-fabric-mastery `
        -OpenAiName  oai-fabmastery-rdeaxiqrltzqo

.NOTES
    The federated credential subject embeds the repository name. After renaming
    the GitHub repo, re-run this script BEFORE the next workflow run: GitHub
    redirects the repo URL but mints OIDC tokens with the NEW name, so the old
    credential no longer matches and azure/login fails.
    Azure resource names (resource group, Container App, app registration) are
    deliberately left unchanged by a rename - they are physical resources.
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory)] [string]$GithubOwner,
    [Parameter(Mandatory)] [string]$GithubRepo,
    [Parameter(Mandatory)] [string]$OpenAiName,
    [string]$SubscriptionId,
    [string]$ResourceGroupName = 'rg-ask-fabric-mastery',
    [string]$AppRegistrationName = 'gha-ask-fabric-mastery',
    [string]$ContainerAppName = 'ask-fabric-mastery'
)

$ErrorActionPreference = 'Stop'
$PSNativeCommandUseErrorActionPreference = $true

# Built-in role IDs
$OpenAiUserRoleId  = '5e0bd9bd-7b93-4f28-af87-19fc36ad61bd'  # Cognitive Services OpenAI User
$ContributorRoleId = 'b24988ac-6180-42a0-ab88-20f7382dd24c'  # Contributor

# ---------------------------------------------------------------------------
function Initialize-AzLogin {
    $acct = az account show 2>$null | ConvertFrom-Json
    if (-not $acct) {
        Write-Host 'Not logged in — launching az login' -ForegroundColor Yellow
        az login --only-show-errors | Out-Null
        $acct = az account show | ConvertFrom-Json
    }
    return $acct
}

function Invoke-AzWithFallback {
    param([scriptblock]$Block, [string]$Description)
    & $Block 2>$null 1>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "  $Description — skipped (idempotent)" -ForegroundColor DarkYellow
    } else {
        Write-Host "  $Description" -ForegroundColor Green
    }
}

# ---------------------------------------------------------------------------
$account = Initialize-AzLogin
if (-not $SubscriptionId) { $SubscriptionId = $account.id }
az account set --subscription $SubscriptionId | Out-Null
$tenantId = (az account show --query tenantId -o tsv)

Write-Host ''
Write-Host '=== Setup parameters ===' -ForegroundColor Cyan
Write-Host "Subscription:      $($account.name) [$SubscriptionId]"
Write-Host "Tenant:            $tenantId"
Write-Host "GitHub repo:       $GithubOwner/$GithubRepo"
Write-Host "App registration:  $AppRegistrationName"
Write-Host "Resource group:    $ResourceGroupName"
Write-Host "OpenAI account:    $OpenAiName"
Write-Host "Container App:     $ContainerAppName"
Write-Host ''

# 1. App registration + SP (idempotent)
Write-Host '=== 1. App registration + Service Principal ===' -ForegroundColor Cyan
$existing = az ad app list --display-name $AppRegistrationName --query "[0]" -o json | ConvertFrom-Json
if ($existing) {
    Write-Host "  Reusing app registration '$AppRegistrationName' ($($existing.appId))" -ForegroundColor Yellow
    $appId       = $existing.appId
    $appObjectId = $existing.id
} else {
    Write-Host "  Creating app registration '$AppRegistrationName'..."
    $created     = az ad app create --display-name $AppRegistrationName | ConvertFrom-Json
    $appId       = $created.appId
    $appObjectId = $created.id
}

$sp = az ad sp list --filter "appId eq '$appId'" --query "[0]" -o json | ConvertFrom-Json
if (-not $sp) {
    Write-Host '  Creating service principal...'
    az ad sp create --id $appId --only-show-errors | Out-Null
    $sp = az ad sp list --filter "appId eq '$appId'" --query "[0]" -o json | ConvertFrom-Json
}
$spObjectId = $sp.id

# 2. Federated credentials
Write-Host ''
Write-Host '=== 2. Federated credentials ===' -ForegroundColor Cyan
$existingCreds = az ad app federated-credential list --id $appObjectId -o json | ConvertFrom-Json
$existingNames = @($existingCreds | ForEach-Object { $_.name })

$creds = @(
    @{
        # Name carries the repo so a rename adds a NEW credential instead of
        # silently skipping: the subject is what GitHub matches on, and a
        # renamed repo mints tokens under its new name.
        name = "gha-${GithubRepo}-main"
        subject = "repo:${GithubOwner}/${GithubRepo}:ref:refs/heads/main"
    }
    # NOTE: pull_request federated credential intentionally omitted.
    # On a public repo it lets any PR (incl. from forks) impersonate the SP.
    # If you ever need PR validation, scope it via GitHub "Environments"
    # with required reviewers and use subject "environment:<name>".
)

foreach ($c in $creds) {
    if ($existingNames -contains $c.name) {
        Write-Host "  Federated credential '$($c.name)' already exists." -ForegroundColor DarkYellow
        continue
    }
    $body = @{
        name      = $c.name
        issuer    = 'https://token.actions.githubusercontent.com'
        subject   = $c.subject
        audiences = @('api://AzureADTokenExchange')
    } | ConvertTo-Json -Compress

    $tmp = New-TemporaryFile
    Set-Content -Path $tmp -Value $body -Encoding utf8
    az ad app federated-credential create --id $appObjectId --parameters "@$($tmp.FullName)" --only-show-errors | Out-Null
    Remove-Item $tmp
    Write-Host "  Created federated credential '$($c.name)'" -ForegroundColor Green
}

# 3. RBAC
Write-Host ''
Write-Host '=== 3. RBAC role assignments ===' -ForegroundColor Cyan
$rgScope     = "/subscriptions/$SubscriptionId/resourceGroups/$ResourceGroupName"
$openaiScope = "$rgScope/providers/Microsoft.CognitiveServices/accounts/$OpenAiName"

Invoke-AzWithFallback -Description "Contributor on $ResourceGroupName" -Block {
    az role assignment create `
        --assignee-object-id $spObjectId `
        --assignee-principal-type ServicePrincipal `
        --role $ContributorRoleId `
        --scope $rgScope `
        --only-show-errors
}

Invoke-AzWithFallback -Description "Cognitive Services OpenAI User on $OpenAiName" -Block {
    az role assignment create `
        --assignee-object-id $spObjectId `
        --assignee-principal-type ServicePrincipal `
        --role $OpenAiUserRoleId `
        --scope $openaiScope `
        --only-show-errors
}

# 4. Print GitHub secrets/variables to copy-paste
$endpoint = "https://$OpenAiName.openai.azure.com/"

Write-Host ''
Write-Host '==============================================================' -ForegroundColor Cyan
Write-Host '  Add these in GitHub: Settings → Secrets and variables → Actions' -ForegroundColor Cyan
Write-Host '==============================================================' -ForegroundColor Cyan
Write-Host ''
Write-Host '## Repository secrets:' -ForegroundColor Yellow
Write-Host ('  AZURE_CLIENT_ID       = {0}' -f $appId)
Write-Host ('  AZURE_TENANT_ID       = {0}' -f $tenantId)
Write-Host ('  AZURE_SUBSCRIPTION_ID = {0}' -f $SubscriptionId)
Write-Host ''
Write-Host '## Repository variables:' -ForegroundColor Yellow
Write-Host ('  AZURE_RESOURCE_GROUP              = {0}' -f $ResourceGroupName)
Write-Host ('  AZURE_CONTAINERAPP_NAME           = {0}' -f $ContainerAppName)
Write-Host ('  AZURE_OPENAI_ENDPOINT             = {0}' -f $endpoint)
Write-Host  '  AZURE_OPENAI_CHAT_DEPLOYMENT      = gpt-4o-mini'
Write-Host  '  AZURE_OPENAI_CHAT_MODEL           = gpt-4o-mini'
Write-Host  '  AZURE_OPENAI_EMBEDDING_DEPLOYMENT = text-embedding-3-small'
Write-Host  '  AZURE_OPENAI_EMBEDDING_MODEL      = text-embedding-3-small'
Write-Host ''
Write-Host 'Tip: use the gh CLI to set them in one go:' -ForegroundColor DarkGray
Write-Host ('  gh secret set AZURE_CLIENT_ID --body "{0}"' -f $appId) -ForegroundColor DarkGray
Write-Host ('  gh secret set AZURE_TENANT_ID --body "{0}"' -f $tenantId) -ForegroundColor DarkGray
Write-Host ('  gh secret set AZURE_SUBSCRIPTION_ID --body "{0}"' -f $SubscriptionId) -ForegroundColor DarkGray
Write-Host ('  gh variable set AZURE_RESOURCE_GROUP --body "{0}"' -f $ResourceGroupName) -ForegroundColor DarkGray
Write-Host ('  gh variable set AZURE_CONTAINERAPP_NAME --body "{0}"' -f $ContainerAppName) -ForegroundColor DarkGray
Write-Host ('  gh variable set AZURE_OPENAI_ENDPOINT --body "{0}"' -f $endpoint) -ForegroundColor DarkGray
