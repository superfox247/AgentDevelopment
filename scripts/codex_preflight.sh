#!/usr/bin/env bash
set -euo pipefail

warn() { echo "⚠️  $1"; }
pass() { echo "✅ $1"; }
fail() { echo "❌ $1"; }

require_docker=0
require_playwright=0

for arg in "$@"; do
  case "$arg" in
    --require-docker) require_docker=1 ;;
    --require-playwright) require_playwright=1 ;;
    *)
      fail "Unknown argument: $arg"
      echo "Usage: $0 [--require-docker] [--require-playwright]"
      exit 2
      ;;
  esac
done

check_cmd() {
  local cmd="$1"
  local label="$2"
  if command -v "$cmd" >/dev/null 2>&1; then
    pass "$label"
  else
    fail "$label (missing command: $cmd)"
    return 1
  fi
}

status=0

echo "== Codex preflight checks =="
check_cmd uv "uv installed" || status=1
check_cmd pnpm "pnpm installed" || status=1
check_cmd node "node installed" || status=1

if command -v docker >/dev/null 2>&1; then
  if docker info >/dev/null 2>&1; then
    pass "Docker daemon reachable"
  else
    warn "Docker CLI found but daemon unreachable"
    (( require_docker == 1 )) && status=1
  fi
else
  warn "Docker CLI not available (Docker-dependent workflows unavailable)"
  (( require_docker == 1 )) && status=1
fi

if [ -d "frontend/node_modules" ]; then
  pass "frontend dependencies present"
else
  warn "frontend/node_modules missing (run: make install)"
  status=1
fi

if [ -d "$HOME/.cache/ms-playwright" ]; then
  pass "Playwright browser cache present"
else
  warn "Playwright browsers not installed (run: cd frontend && pnpm exec playwright install --with-deps chromium)"
  (( require_playwright == 1 )) && status=1
fi

if [ $status -ne 0 ]; then
  fail "Preflight checks found blocking issues"
  exit 1
fi

pass "Preflight checks passed"
