[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$ProjectId,

    [string]$Region = 'us-central1',
    [string]$ArtifactLocation = 'us',
    [string]$ArtifactRepository = 'antigravity',
    [string]$PipelineName = 'dashboard-api',
    [string]$StagingService = 'dashboard-api-staging',
    [string]$ProductionService = 'dashboard-api-production',
    [switch]$SkipPipeline
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
if (Get-Variable PSNativeCommandUseErrorActionPreference -ErrorAction SilentlyContinue) {
    $PSNativeCommandUseErrorActionPreference = $false
}

$gcloudCmd = $null
if (Get-Command gcloud.cmd -ErrorAction SilentlyContinue) {
    $gcloudCmd = 'gcloud.cmd'
} elseif (Get-Command gcloud -ErrorAction SilentlyContinue) {
    $gcloudCmd = 'gcloud'
} else {
    throw 'gcloud CLI is required. Install Google Cloud SDK first.'
}

function Invoke-Gcloud {
    param([Parameter(Mandatory = $true)][string[]]$Args)

    & $gcloudCmd @Args
    if ($LASTEXITCODE -ne 0) {
        throw "gcloud command failed: gcloud $($Args -join ' ')"
    }
}

Write-Host "Using project: $ProjectId"
Write-Host "Using region: $Region"

Invoke-Gcloud -Args @('config', 'set', 'project', $ProjectId)

$apis = @(
    'cloudbuild.googleapis.com',
    'artifactregistry.googleapis.com',
    'run.googleapis.com',
    'clouddeploy.googleapis.com',
    'iamcredentials.googleapis.com'
)

Write-Host 'Enabling required APIs...'
Invoke-Gcloud -Args (@('services', 'enable') + $apis)

Write-Host 'Ensuring Artifact Registry repository exists...'
$prevErrAction = $ErrorActionPreference
$ErrorActionPreference = 'Continue'
& $gcloudCmd artifacts repositories describe $ArtifactRepository --location $ArtifactLocation *> $null
$describeExitCode = $LASTEXITCODE
$ErrorActionPreference = $prevErrAction

if ($describeExitCode -ne 0) {
    Invoke-Gcloud -Args @(
        'artifacts', 'repositories', 'create', $ArtifactRepository,
        '--repository-format=docker',
        '--location', $ArtifactLocation,
        '--description', 'Antigravity container images'
    )
} else {
    Write-Host "Artifact repo exists: $ArtifactRepository"
}

if (-not $SkipPipeline) {
    Write-Host 'Applying Cloud Deploy pipeline + targets...'

    $repoRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
    $templatePath = Join-Path $repoRoot 'clouddeploy/pipeline.yaml'

    if (-not (Test-Path $templatePath)) {
        throw "Missing template file: $templatePath"
    }

    $rendered = Get-Content -Path $templatePath -Raw
    $rendered = $rendered.Replace('__PIPELINE_NAME__', $PipelineName)
    $rendered = $rendered.Replace('__PROJECT_ID__', $ProjectId)
    $rendered = $rendered.Replace('__REGION__', $Region)

    $tmpFile = Join-Path $env:TEMP ("pipeline-{0}.yaml" -f [Guid]::NewGuid().ToString('N'))
    Set-Content -Path $tmpFile -Value $rendered -NoNewline

    try {
        Invoke-Gcloud -Args @('deploy', 'apply', '--file', $tmpFile, '--region', $Region)
    }
    finally {
        Remove-Item -Path $tmpFile -ErrorAction SilentlyContinue
    }
}

Write-Host ''
Write-Host 'Bootstrap complete.'
Write-Host ''
Write-Host 'Set these GitHub repo variables:'
Write-Host "- GCP_PROJECT_ID=$ProjectId"
Write-Host "- GCP_REGION=$Region"
Write-Host "- ARTIFACT_REGISTRY_HOSTNAME=$ArtifactLocation-docker.pkg.dev"
Write-Host "- ARTIFACT_REGISTRY_REPOSITORY=$ArtifactRepository"
Write-Host "- CLOUD_DEPLOY_PIPELINE=$PipelineName"
Write-Host "- CLOUD_RUN_SERVICE_STAGING=$StagingService"
Write-Host "- CLOUD_RUN_SERVICE_PRODUCTION=$ProductionService"
Write-Host ''
Write-Host 'Next steps:'
Write-Host '1) Run infra/gcp/setup_wif.ps1 to configure GitHub OIDC auth.'
Write-Host '2) Trigger workflow: CD Cloud Deploy.'
