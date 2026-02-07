[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$ProjectId,

    [Parameter(Mandatory = $true)]
    [string]$Repo,

    [string]$PoolId = 'github-pool',
    [string]$ProviderId = 'github-provider',
    [string]$ServiceAccountId = 'github-actions-cicd'
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

Invoke-Gcloud -Args @('config', 'set', 'project', $ProjectId)

$projectNumber = (& $gcloudCmd projects describe $ProjectId --format='value(projectNumber)').Trim()
if (-not $projectNumber) {
    throw "Failed to resolve project number for project: $ProjectId"
}

$serviceAccountEmail = "$ServiceAccountId@$ProjectId.iam.gserviceaccount.com"

Invoke-Gcloud -Args @('services', 'enable', 'iam.googleapis.com', 'iamcredentials.googleapis.com', 'sts.googleapis.com')

$prevErrAction = $ErrorActionPreference
$ErrorActionPreference = 'Continue'
& $gcloudCmd iam workload-identity-pools describe $PoolId --location global *> $null
$poolExitCode = $LASTEXITCODE
$ErrorActionPreference = $prevErrAction

if ($poolExitCode -ne 0) {
    Invoke-Gcloud -Args @(
        'iam', 'workload-identity-pools', 'create', $PoolId,
        '--location=global',
        '--display-name=GitHub Actions Pool'
    )
} else {
    Write-Host "Workload identity pool exists: $PoolId"
}

$prevErrAction = $ErrorActionPreference
$ErrorActionPreference = 'Continue'
& $gcloudCmd iam workload-identity-pools providers describe $ProviderId --workload-identity-pool=$PoolId --location=global *> $null
$providerExitCode = $LASTEXITCODE
$ErrorActionPreference = $prevErrAction

if ($providerExitCode -ne 0) {
    Invoke-Gcloud -Args @(
        'iam', 'workload-identity-pools', 'providers', 'create-oidc', $ProviderId,
        '--location=global',
        "--workload-identity-pool=$PoolId",
        '--display-name=GitHub Provider',
        '--issuer-uri=https://token.actions.githubusercontent.com',
        '--attribute-mapping=google.subject=assertion.sub,attribute.actor=assertion.actor,attribute.repository=assertion.repository,attribute.ref=assertion.ref',
        "--attribute-condition=assertion.repository=='$Repo'"
    )
} else {
    Write-Host "Workload identity provider exists: $ProviderId"
}

$prevErrAction = $ErrorActionPreference
$ErrorActionPreference = 'Continue'
& $gcloudCmd iam service-accounts describe $serviceAccountEmail *> $null
$saExitCode = $LASTEXITCODE
$ErrorActionPreference = $prevErrAction

if ($saExitCode -ne 0) {
    Invoke-Gcloud -Args @(
        'iam', 'service-accounts', 'create', $ServiceAccountId,
        '--display-name=GitHub Actions CI/CD'
    )
} else {
    Write-Host "Service account exists: $serviceAccountEmail"
}

$roles = @(
    'roles/cloudbuild.builds.editor',
    'roles/artifactregistry.writer',
    'roles/run.admin',
    'roles/clouddeploy.releaser',
    'roles/clouddeploy.jobRunner',
    'roles/iam.serviceAccountUser'
)

foreach ($role in $roles) {
    Invoke-Gcloud -Args @(
        'projects', 'add-iam-policy-binding', $ProjectId,
        "--member=serviceAccount:$serviceAccountEmail",
        "--role=$role"
    )
}

$principalSet = "principalSet://iam.googleapis.com/projects/$projectNumber/locations/global/workloadIdentityPools/$PoolId/attribute.repository/$Repo"
Invoke-Gcloud -Args @(
    'iam', 'service-accounts', 'add-iam-policy-binding', $serviceAccountEmail,
    '--role=roles/iam.workloadIdentityUser',
    "--member=$principalSet"
)

$providerValue = "projects/$projectNumber/locations/global/workloadIdentityPools/$PoolId/providers/$ProviderId"

Write-Host ''
Write-Host 'WIF setup complete.'
Write-Host ''
Write-Host 'Add these GitHub repository secrets:'
Write-Host "- GCP_WORKLOAD_IDENTITY_PROVIDER=$providerValue"
Write-Host "- GCP_SERVICE_ACCOUNT=$serviceAccountEmail"
