#!/usr/bin/env bash
set -euo pipefail

warn() { echo "⚠️  $1"; }
pass() { echo "✅ $1"; }
fail() { echo "❌ $1"; }

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
    status=1
  fi
else
  warn "Docker CLI not available (Docker-dependent workflows unavailable)"
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
fi

if [ $status -ne 0 ]; then
  fail "Preflight checks found blocking issues"
  exit 1
fi

pass "Preflight checks passed"
