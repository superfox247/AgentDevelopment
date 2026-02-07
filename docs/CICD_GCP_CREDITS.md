# CI/CD with Google Cloud Credits

This guide wires the repository to a practical two-lane CI/CD model:

- Fast CI in GitHub Actions for pull requests.
- Heavy tests and deployment in Google Cloud, where eligible Cloud credits can offset cost.

## Pipeline Layout

1. `.github/workflows/ci.yml`
- Runs on `pull_request` and `push` to `main`.
- Required checks: backend quality/tests + frontend lint/type/unit/E2E (dev server).
- Docker-stack E2E runs on `push` and optional manual dispatch.

2. `.github/workflows/gcp-heavy-tests.yml`
- Nightly/manual heavy lane in Cloud Build.
- Runs backend fast tests, frontend tests, and optional model-backed evals.

3. `.github/workflows/cd-cloud-run.yml`
- Build image in Cloud Build.
- Manual fallback deploy directly to Cloud Run.
- Useful for emergency rollback or bypassing Cloud Deploy.

4. `.github/workflows/cd-cloud-deploy.yml`
- Automatic progressive delivery workflow on `main` using Cloud Deploy.
- Creates release to staging and can create production rollout (approval-gated).

## Files Added for GCP

- `cloudbuild/heavy-tests.yaml`
- `cloudbuild/release-dashboard.yaml`
- `clouddeploy/pipeline.yaml`
- `clouddeploy/skaffold.yaml`
- `clouddeploy/service-staging.yaml`
- `clouddeploy/service-production.yaml`
- `dashboard_api/Dockerfile`
- `infra/gcp/bootstrap.sh`
- `infra/gcp/setup_wif.sh`

## One-Time GitHub Setup

### Repository Variables

Add these repo variables:

- `GCP_PROJECT_ID`
- `GCP_REGION` (example: `us-central1`)
- `ARTIFACT_REGISTRY_HOSTNAME` (optional, default: `us-docker.pkg.dev`)
- `ARTIFACT_REGISTRY_REPOSITORY` (optional, default: `antigravity`)
- `CLOUD_RUN_IMAGE_NAME` (optional, default: `dashboard-api`)
- `CLOUD_DEPLOY_PIPELINE` (optional, default: `dashboard-api`)
- `CLOUD_RUN_SERVICE_STAGING`
- `CLOUD_RUN_SERVICE_PRODUCTION`

### Repository Secrets

Add these repo secrets:

- `GCP_WORKLOAD_IDENTITY_PROVIDER`
- `GCP_SERVICE_ACCOUNT`
- `GEMINI_API_KEY` (optional; used by local/docker integration checks)

## Google Cloud Prerequisites

1. Enable APIs:
- Cloud Build API
- Artifact Registry API
- Cloud Run Admin API
- Cloud Deploy API
- IAM Credentials API

2. Run bootstrap script (recommended):
```bash
bash infra/gcp/bootstrap.sh --project <PROJECT_ID>
```
Windows PowerShell:
```powershell
.\infra\gcp\bootstrap.ps1 -ProjectId <PROJECT_ID>
```

3. Create Artifact Registry repo manually (alternative):
```bash
gcloud artifacts repositories create antigravity \
  --repository-format=docker \
  --location=us \
  --description="Antigravity images"
```

4. Create Cloud Run services (or let first deploy create them):
- Staging service name = `CLOUD_RUN_SERVICE_STAGING`
- Production service name = `CLOUD_RUN_SERVICE_PRODUCTION`

5. Configure GitHub OIDC -> Workload Identity Federation:
```bash
bash infra/gcp/setup_wif.sh --project <PROJECT_ID> --repo <OWNER/REPO>
```
Windows PowerShell:
```powershell
.\infra\gcp\setup_wif.ps1 -ProjectId <PROJECT_ID> -Repo <OWNER/REPO>
```

Make wrappers:
```bash
make gcp-bootstrap PROJECT=<PROJECT_ID>
make gcp-setup-wif PROJECT=<PROJECT_ID> REPO=<OWNER/REPO>
make gcp-configure-github PROJECT=<PROJECT_ID> REPO=<OWNER/REPO> WIF_PROVIDER=<provider> SERVICE_ACCOUNT_EMAIL=<email>
```

- Provider maps this repo to a workload identity pool.
- Service account has minimum roles:
  - `roles/cloudbuild.builds.editor`
  - `roles/artifactregistry.writer`
  - `roles/run.admin`
  - `roles/clouddeploy.releaser`
  - `roles/clouddeploy.jobRunner`
  - `roles/iam.serviceAccountUser`

6. Configure GitHub repository variables/secrets automatically (optional):
```bash
bash infra/gcp/configure_github.sh \
  --repo <OWNER/REPO> \
  --project <PROJECT_ID> \
  --wif-provider <provider-from-setup_wif-output> \
  --service-account <service-account-email-from-setup_wif-output>
```

## Credit-Aware Operation

Use billing reports to verify credits are applied to Cloud Build/Cloud Run SKUs:

1. Billing -> Credits: confirm active credits and expiry.
2. Cost table: add `Credit name`, `Credit ID`, and `SKU` columns.
3. Keep heavy tests in `gcp-heavy-tests.yml` so expensive runs are intentional.

## Runbooks

### Run fast CI manually
- Actions -> `CI` -> `Run workflow`
- Set `run_docker_e2e=true` when you want Docker-stack E2E.

### Run heavy credit-backed tests
- Actions -> `GCP Heavy Tests` -> `Run workflow`
- Optionally set `run_evals=true` if model credentials are configured in Cloud Build.

### Deploy staging or production
- Actions -> `CD Cloud Run` -> `Run workflow`
- `target=staging` or `target=production`.
- This is a manual fallback path.

### Progressive delivery via Cloud Deploy
- Actions -> `CD Cloud Deploy` -> `Run workflow`
- Also runs automatically on pushes to `main`.
- `promote_to_production=false` creates/rolls out to staging only.
- `promote_to_production=true` creates production rollout; Cloud Deploy approval is still required for final promotion.

## Notes

- `dashboard_api/server.py` has Docker-dependent routes. In Cloud Run, health endpoint still works, but Docker-management routes are not expected to function unless Docker is reachable.
- Use GitHub `production` environment protection plus Cloud Deploy target approval for a two-layer release gate.
