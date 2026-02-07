#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Bootstrap core GCP resources for CI/CD.

Usage:
  infra/gcp/bootstrap.sh --project PROJECT_ID [options]

Options:
  --project PROJECT_ID                 GCP project id (required)
  --region REGION                      Cloud Deploy/Run region (default: us-central1)
  --artifact-location LOCATION         Artifact Registry location (default: us)
  --artifact-repo NAME                 Artifact Registry repo (default: antigravity)
  --pipeline NAME                      Cloud Deploy pipeline name (default: dashboard-api)
  --staging-service NAME               Cloud Run staging service (default: dashboard-api-staging)
  --production-service NAME            Cloud Run production service (default: dashboard-api-production)
  --skip-pipeline                      Skip Cloud Deploy apply
  -h, --help                           Show help

Examples:
  infra/gcp/bootstrap.sh --project my-proj
  infra/gcp/bootstrap.sh --project my-proj --region us-east1 --artifact-location us
EOF
}

PROJECT_ID=""
REGION="us-central1"
ARTIFACT_LOCATION="us"
ARTIFACT_REPOSITORY="antigravity"
PIPELINE_NAME="dashboard-api"
STAGING_SERVICE="dashboard-api-staging"
PRODUCTION_SERVICE="dashboard-api-production"
SKIP_PIPELINE="false"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --project)
      PROJECT_ID="$2"
      shift 2
      ;;
    --region)
      REGION="$2"
      shift 2
      ;;
    --artifact-location)
      ARTIFACT_LOCATION="$2"
      shift 2
      ;;
    --artifact-repo)
      ARTIFACT_REPOSITORY="$2"
      shift 2
      ;;
    --pipeline)
      PIPELINE_NAME="$2"
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
    --skip-pipeline)
      SKIP_PIPELINE="true"
      shift
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

if [[ -z "$PROJECT_ID" ]]; then
  echo "--project is required"
  usage
  exit 1
fi

if ! command -v gcloud >/dev/null 2>&1; then
  echo "gcloud CLI is required. Install Google Cloud SDK first."
  exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

echo "Using project: ${PROJECT_ID}"
echo "Using region: ${REGION}"

gcloud config set project "${PROJECT_ID}" >/dev/null

API_LIST=(
  cloudbuild.googleapis.com
  artifactregistry.googleapis.com
  run.googleapis.com
  clouddeploy.googleapis.com
  iamcredentials.googleapis.com
)

echo "Enabling required APIs..."
gcloud services enable "${API_LIST[@]}"

echo "Ensuring Artifact Registry repository exists..."
if gcloud artifacts repositories describe "${ARTIFACT_REPOSITORY}" --location "${ARTIFACT_LOCATION}" >/dev/null 2>&1; then
  echo "Artifact repo exists: ${ARTIFACT_REPOSITORY}"
else
  gcloud artifacts repositories create "${ARTIFACT_REPOSITORY}" \
    --repository-format=docker \
    --location "${ARTIFACT_LOCATION}" \
    --description "Antigravity container images"
fi

if [[ "$SKIP_PIPELINE" == "false" ]]; then
  echo "Applying Cloud Deploy pipeline + targets..."
  tmp_dir="$(mktemp -d)"
  trap 'rm -rf "${tmp_dir}"' EXIT

  sed "s|__PIPELINE_NAME__|${PIPELINE_NAME}|g; s|__PROJECT_ID__|${PROJECT_ID}|g; s|__REGION__|${REGION}|g" \
    "${REPO_ROOT}/clouddeploy/pipeline.yaml" > "${tmp_dir}/pipeline.yaml"

  gcloud deploy apply \
    --file "${tmp_dir}/pipeline.yaml" \
    --region "${REGION}"
fi

cat <<EOF

Bootstrap complete.

Set these GitHub repo variables:
- GCP_PROJECT_ID=${PROJECT_ID}
- GCP_REGION=${REGION}
- ARTIFACT_REGISTRY_HOSTNAME=${ARTIFACT_LOCATION}-docker.pkg.dev
- ARTIFACT_REGISTRY_REPOSITORY=${ARTIFACT_REPOSITORY}
- CLOUD_DEPLOY_PIPELINE=${PIPELINE_NAME}
- CLOUD_RUN_SERVICE_STAGING=${STAGING_SERVICE}
- CLOUD_RUN_SERVICE_PRODUCTION=${PRODUCTION_SERVICE}

Next steps:
1) Run infra/gcp/setup_wif.sh to configure GitHub OIDC auth.
2) Trigger workflow: CD Cloud Deploy.
EOF
