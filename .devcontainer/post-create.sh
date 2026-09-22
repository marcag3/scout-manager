#!/usr/bin/env bash
set -euo pipefail

DEV_DIR="/workspace/development"
BENCH_DIR="${DEV_DIR}/frappe-bench"
SITE="development.localhost"

if [ ! -w "${DEV_DIR}" ]; then
	sudo chown -R frappe:frappe "${DEV_DIR}"
fi

mkdir -p "${DEV_DIR}/.vscode"
cp /workspace/.devcontainer/vscode/launch.json "${DEV_DIR}/.vscode/launch.json"
cp /workspace/.devcontainer/vscode/tasks.json "${DEV_DIR}/.vscode/tasks.json"

cd "${DEV_DIR}"

if [ ! -d "${BENCH_DIR}" ]; then
	echo "==> Initializing Frappe bench (first run may take several minutes)..."
	python3 /workspace/.devcontainer/installer.py \
		-j /workspace/.devcontainer/apps.json \
		-t version-16 \
		-p 3.14 \
		-n v24
fi

cd "${BENCH_DIR}"

if [ ! -e "apps/scout_manager" ]; then
	echo "==> Linking scout_manager from /workspace"
	bench get-app --soft-link scout_manager /workspace
fi

if ! bench --site "${SITE}" list-apps 2>/dev/null | grep -q "scout_manager"; then
	echo "==> Installing scout_manager on ${SITE}"
	bench --site "${SITE}" install-app scout_manager
fi

if command -v uv >/dev/null 2>&1; then
	uv tool install pre-commit >/dev/null 2>&1 || true
fi

echo
echo "==> Dev environment ready"
echo "    Site:  ${SITE}"
echo "    Login: Administrator / admin"
echo "    Start: cd /workspace/development/frappe-bench && bench start"
echo "    URL:   http://localhost:8000"
