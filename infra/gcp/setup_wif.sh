#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Create/Update GitHub OIDC Workload Identity Federation for this repo.

Usage:
  infra/gcp/setup_wif.sh --project PROJECT_ID --repo OWNER/REPO [options]

Options:
  --project PROJECT_ID                 GCP project id (required)
  --repo OWNER/REPO                    GitHub repository (required)
  --pool POOL_ID                       Workload identity pool id (default: github-pool)
  --provider PROVIDER_ID               Provider id (default: github-provider)
  --service-account SERVICE_ACCOUNT_ID Service account id (default: github-actions-cicd)
  -h, --help                           Show help

Outputs:
  - GCP_WORKLOAD_IDENTITY_PROVIDER value for GitHub secret
  - GCP_SERVICE_ACCOUNT value for GitHub secret
EOF
}

PROJECT_ID=""
REPO=""
POOL_ID="github-pool"
PROVIDER_ID="github-provider"
SERVICE_ACCOUNT_ID="github-actions-cicd"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --project)
      PROJECT_ID="$2"
      shift 2
      ;;
    --repo)
      REPO="$2"
      shift 2
      ;;
    --pool)
      POOL_ID="$2"
      shift 2
      ;;
    --provider)
      PROVIDER_ID="$2"
      shift 2
      ;;
    --service-account)
      SERVICE_ACCOUNT_ID="$2"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown option: $1"
      usage
      exit 1
      ;;
  esac
done

if [[ -z "$PROJECT_ID" || -z "$REPO" ]]; then
  echo "--project and --repo are required"
  usage
  exit 1
fi

if ! command -v gcloud >/dev/null 2>&1; then
  echo "gcloud CLI is required. Install Google Cloud SDK first."
  exit 1
fi

gcloud config set project "${PROJECT_ID}" >/dev/null
PROJECT_NUMBER="$(gcloud projects describe "${PROJECT_ID}" --format='value(projectNumber)')"
SA_EMAIL="${SERVICE_ACCOUNT_ID}@${PROJECT_ID}.iam.gserviceaccount.com"

# Ensure IAM APIs are enabled.
gcloud services enable iam.googleapis.com iamcredentials.googleapis.com sts.googleapis.com >/dev/null

if gcloud iam workload-identity-pools describe "${POOL_ID}" --location=global >/dev/null 2>&1; then
  echo "Workload identity pool exists: ${POOL_ID}"
else
  gcloud iam workload-identity-pools create "${POOL_ID}" \
    --location=global \
    --display-name="GitHub Actions Pool"
fi

if gcloud iam workload-identity-pools providers describe "${PROVIDER_ID}" \
  --workload-identity-pool="${POOL_ID}" --location=global >/dev/null 2>&1; then
  echo "Workload identity provider exists: ${PROVIDER_ID}"
else
  gcloud iam workload-identity-pools providers create-oidc "${PROVIDER_ID}" \
    --location=global \
    --workload-identity-pool="${POOL_ID}" \
    --display-name="GitHub Provider" \
    --issuer-uri="https://token.actions.githubusercontent.com" \
    --attribute-mapping="google.subject=assertion.sub,attribute.actor=assertion.actor,attribute.repository=assertion.repository,attribute.ref=assertion.ref" \
    --attribute-condition="assertion.repository=='${REPO}'"
fi

if gcloud iam service-accounts describe "${SA_EMAIL}" >/dev/null 2>&1; then
  echo "Service account exists: ${SA_EMAIL}"
else
  gcloud iam service-accounts create "${SERVICE_ACCOUNT_ID}" \
    --display-name="GitHub Actions CI/CD"
fi

# Project roles for CI/CD workflow.
ROLES=(
  roles/cloudbuild.builds.editor
  roles/artifactregistry.writer
  roles/run.admin
  roles/clouddeploy.releaser
  roles/clouddeploy.jobRunner
  roles/iam.serviceAccountUser
)

for role in "${ROLES[@]}"; do
  gcloud projects add-iam-policy-binding "${PROJECT_ID}" \
    --member="serviceAccount:${SA_EMAIL}" \
    --role="${role}" >/dev/null
done

# Allow GitHub OIDC principal to impersonate service account.
gcloud iam service-accounts add-iam-policy-binding "${SA_EMAIL}" \
  --role="roles/iam.workloadIdentityUser" \
  --member="principalSet://iam.googleapis.com/projects/${PROJECT_NUMBER}/locations/global/workloadIdentityPools/${POOL_ID}/attribute.repository/${REPO}" >/dev/null

WIF_PROVIDER="projects/${PROJECT_NUMBER}/locations/global/workloadIdentityPools/${POOL_ID}/providers/${PROVIDER_ID}"

cat <<EOF

WIF setup complete.

Add these GitHub repository secrets:
- GCP_WORKLOAD_IDENTITY_PROVIDER=${WIF_PROVIDER}
- GCP_SERVICE_ACCOUNT=${SA_EMAIL}
EOF
