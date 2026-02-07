#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Configure GitHub repository variables and secrets for CI/CD workflows.

Usage:
  infra/gcp/configure_github.sh --repo OWNER/REPO [options]

Options:
  --repo OWNER/REPO                    GitHub repository (required)
  --project PROJECT_ID                 GCP project id (required)
  --region REGION                      GCP region (default: us-central1)
  --artifact-host HOST                 Artifact host (default: us-docker.pkg.dev)
  --artifact-repo NAME                 Artifact repo (default: antigravity)
  --image-name NAME                    Cloud Run image name (default: dashboard-api)
  --pipeline NAME                      Cloud Deploy pipeline (default: dashboard-api)
  --staging-service NAME               Cloud Run staging service (default: dashboard-api-staging)
  --production-service NAME            Cloud Run production service (default: dashboard-api-production)
  --wif-provider VALUE                 Value for GCP_WORKLOAD_IDENTITY_PROVIDER secret
  --service-account EMAIL              Value for GCP_SERVICE_ACCOUNT secret
  -h, --help                           Show help

Notes:
- Requires GitHub CLI (gh) authenticated with repo admin access.
- If --wif-provider and --service-account are omitted, only variables are set.
EOF
}

REPO=""
PROJECT_ID=""
REGION="us-central1"
ARTIFACT_HOST="us-docker.pkg.dev"
ARTIFACT_REPO="antigravity"
IMAGE_NAME="dashboard-api"
PIPELINE="dashboard-api"
STAGING_SERVICE="dashboard-api-staging"
PRODUCTION_SERVICE="dashboard-api-production"
WIF_PROVIDER=""
SERVICE_ACCOUNT=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --repo)
      REPO="$2"
      shift 2
      ;;
    --project)
      PROJECT_ID="$2"
      shift 2
      ;;
    --region)
      REGION="$2"
      shift 2
      ;;
    --artifact-host)
      ARTIFACT_HOST="$2"
      shift 2
      ;;
    --artifact-repo)
      ARTIFACT_REPO="$2"
      shift 2
      ;;
    --image-name)
      IMAGE_NAME="$2"
      shift 2
      ;;
    --pipeline)
      PIPELINE="$2"
      shift 2
      ;;
    --staging-service)
      STAGING_SERVICE="$2"
      shift 2
      ;;
    --production-service)
      PRODUCTION_SERVICE="$2"
      shift 2
      ;;
    --wif-provider)
      WIF_PROVIDER="$2"
      shift 2
      ;;
    --service-account)
      SERVICE_ACCOUNT="$2"
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

if [[ -z "$REPO" || -z "$PROJECT_ID" ]]; then
  echo "--repo and --project are required"
  usage
  exit 1
fi

if ! command -v gh >/dev/null 2>&1; then
  echo "GitHub CLI (gh) is required."
  exit 1
fi

echo "Setting GitHub variables for ${REPO}..."

gh variable set GCP_PROJECT_ID --body "$PROJECT_ID" --repo "$REPO"
gh variable set GCP_REGION --body "$REGION" --repo "$REPO"
gh variable set ARTIFACT_REGISTRY_HOSTNAME --body "$ARTIFACT_HOST" --repo "$REPO"
gh variable set ARTIFACT_REGISTRY_REPOSITORY --body "$ARTIFACT_REPO" --repo "$REPO"
gh variable set CLOUD_RUN_IMAGE_NAME --body "$IMAGE_NAME" --repo "$REPO"
gh variable set CLOUD_DEPLOY_PIPELINE --body "$PIPELINE" --repo "$REPO"
gh variable set CLOUD_RUN_SERVICE_STAGING --body "$STAGING_SERVICE" --repo "$REPO"
gh variable set CLOUD_RUN_SERVICE_PRODUCTION --body "$PRODUCTION_SERVICE" --repo "$REPO"

if [[ -n "$WIF_PROVIDER" ]]; then
  echo "Setting secret GCP_WORKLOAD_IDENTITY_PROVIDER..."
  gh secret set GCP_WORKLOAD_IDENTITY_PROVIDER --body "$WIF_PROVIDER" --repo "$REPO"
fi

if [[ -n "$SERVICE_ACCOUNT" ]]; then
  echo "Setting secret GCP_SERVICE_ACCOUNT..."
  gh secret set GCP_SERVICE_ACCOUNT --body "$SERVICE_ACCOUNT" --repo "$REPO"
fi

echo "GitHub configuration complete."
