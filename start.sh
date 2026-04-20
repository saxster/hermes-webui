#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Maintenance-mode notice (2026-04-20). A leaner Vite/React dashboard now
# ships with hermes-agent and is launched via `hermes web`. This project
# continues to receive bug fixes and security updates; new feature work
# lands on the bundled dashboard. Set HERMES_WEBUI_SILENCE_DEPRECATION=1
# to suppress this banner.
if [[ -z "${HERMES_WEBUI_SILENCE_DEPRECATION:-}" ]]; then
  printf '\n\033[33m[hermes-webui]\033[0m maintenance mode — see README.md.\n'
  printf '              For the bundled dashboard: %s\n' 'hermes web'
  printf '              Silence this: export HERMES_WEBUI_SILENCE_DEPRECATION=1\n\n'
fi

if [[ -f "${REPO_ROOT}/.env" ]]; then
  set -a
  # shellcheck source=/dev/null
  source "${REPO_ROOT}/.env"
  set +a
fi

PYTHON="${HERMES_WEBUI_PYTHON:-}"
if [[ -z "${PYTHON}" ]]; then
  if command -v python3 >/dev/null 2>&1; then
    PYTHON="$(command -v python3)"
  elif command -v python >/dev/null 2>&1; then
    PYTHON="$(command -v python)"
  else
    echo "[XX] Python 3 is required to run bootstrap.py" >&2
    exit 1
  fi
fi

exec "${PYTHON}" "${REPO_ROOT}/bootstrap.py" --no-browser "$@"
