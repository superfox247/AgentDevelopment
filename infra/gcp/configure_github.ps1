[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$Repo,

    [Parameter(Mandatory = $true)]
    [string]$ProjectId,

    [string]$Region = 'us-central1',
    [string]$ArtifactHost = 'us-docker.pkg.dev',
    [string]$ArtifactRepo = 'antigravity',
    [string]$ImageName = 'dashboard-api',
    [string]$Pipeline = 'dashboard-api',
    [string]$StagingService = 'dashboard-api-staging',
    [string]$ProductionService = 'dashboard-api-production',
    [string]$WifProvider = '',
    [string]$ServiceAccount = ''
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
if (Get-Variable PSNativeCommandUseErrorActionPreference -ErrorAction SilentlyContinue) {
    $PSNativeCommandUseErrorActionPreference = $false
}

$ghCmd = $null
if (Get-Command gh.exe -ErrorAction SilentlyContinue) {
    $ghCmd = 'gh.exe'
} elseif (Get-Command gh -ErrorAction SilentlyContinue) {
    $ghCmd = 'gh'
} else {
    throw 'GitHub CLI (gh) is required.'
}

function Invoke-Gh {
    param([Parameter(Mandatory = $true)][string[]]$Args)

    & $ghCmd @Args
    if ($LASTEXITCODE -ne 0) {
        throw "gh command failed: gh $($Args -join ' ')"
    }
}

Write-Host "Setting GitHub variables for $Repo..."

Invoke-Gh -Args @('variable', 'set', 'GCP_PROJECT_ID', '--body', $ProjectId, '--repo', $Repo)
Invoke-Gh -Args @('variable', 'set', 'GCP_REGION', '--body', $Region, '--repo', $Repo)
Invoke-Gh -Args @('variable', 'set', 'ARTIFACT_REGISTRY_HOSTNAME', '--body', $ArtifactHost, '--repo', $Repo)
Invoke-Gh -Args @('variable', 'set', 'ARTIFACT_REGISTRY_REPOSITORY', '--body', $ArtifactRepo, '--repo', $Repo)
Invoke-Gh -Args @('variable', 'set', 'CLOUD_RUN_IMAGE_NAME', '--body', $ImageName, '--repo', $Repo)
Invoke-Gh -Args @('variable', 'set', 'CLOUD_DEPLOY_PIPELINE', '--body', $Pipeline, '--repo', $Repo)
Invoke-Gh -Args @('variable', 'set', 'CLOUD_RUN_SERVICE_STAGING', '--body', $StagingService, '--repo', $Repo)
Invoke-Gh -Args @('variable', 'set', 'CLOUD_RUN_SERVICE_PRODUCTION', '--body', $ProductionService, '--repo', $Repo)

if (-not [string]::IsNullOrWhiteSpace($WifProvider)) {
    Write-Host 'Setting secret GCP_WORKLOAD_IDENTITY_PROVIDER...'
    Invoke-Gh -Args @('secret', 'set', 'GCP_WORKLOAD_IDENTITY_PROVIDER', '--body', $WifProvider, '--repo', $Repo)
}

if (-not [string]::IsNullOrWhiteSpace($ServiceAccount)) {
    Write-Host 'Setting secret GCP_SERVICE_ACCOUNT...'
    Invoke-Gh -Args @('secret', 'set', 'GCP_SERVICE_ACCOUNT', '--body', $ServiceAccount, '--repo', $Repo)
}

Write-Host 'GitHub configuration complete.'
