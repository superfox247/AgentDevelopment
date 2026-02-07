# GCP Automation Scripts

These scripts bootstrap Google Cloud resources and GitHub OIDC auth for CI/CD.

## Scripts

- `bootstrap.sh` / `bootstrap.ps1`
  - Enables required APIs.
  - Ensures Artifact Registry repository exists.
  - Applies Cloud Deploy pipeline + targets.
  - Prints required GitHub repository variables.

- `setup_wif.sh` / `setup_wif.ps1`
  - Creates/updates Workload Identity Pool + OIDC provider for GitHub.
  - Creates/updates CI/CD service account.
  - Grants baseline roles for build, deploy, and release workflows.
  - Prints required GitHub repository secrets.

- `configure_github.sh` / `configure_github.ps1`
  - Sets required GitHub repository variables for workflows.
  - Optionally sets OIDC service-account secrets (`GCP_WORKLOAD_IDENTITY_PROVIDER`, `GCP_SERVICE_ACCOUNT`).

## Usage

Linux/macOS:

```bash
bash infra/gcp/bootstrap.sh --project <PROJECT_ID>
bash infra/gcp/setup_wif.sh --project <PROJECT_ID> --repo <OWNER/REPO>
```

Windows PowerShell:

```powershell
.\infra\gcp\bootstrap.ps1 -ProjectId <PROJECT_ID>
.\infra\gcp\setup_wif.ps1 -ProjectId <PROJECT_ID> -Repo <OWNER/REPO>
.\infra\gcp\configure_github.ps1 -Repo <OWNER/REPO> -ProjectId <PROJECT_ID>
```

Or via project command wrappers:

```bash
make gcp-bootstrap PROJECT=<PROJECT_ID>
make gcp-setup-wif PROJECT=<PROJECT_ID> REPO=<OWNER/REPO>
make gcp-configure-github PROJECT=<PROJECT_ID> REPO=<OWNER/REPO>
```

```powershell
.\make.ps1 gcp-bootstrap -Project <PROJECT_ID>
.\make.ps1 gcp-setup-wif -Project <PROJECT_ID> -Repo <OWNER/REPO>
.\make.ps1 gcp-configure-github -Project <PROJECT_ID> -Repo <OWNER/REPO>
```
