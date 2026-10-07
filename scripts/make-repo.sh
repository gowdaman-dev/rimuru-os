#!/usr/bin/env bash
# scripts/make-repo.sh
# Builds local [rimuru] repository database

set -euo pipefail

REPO_DIR="/var/tmp/rimuru-repo"
mkdir -p "$REPO_DIR"

echo "==> Updating [rimuru] repository in $REPO_DIR..."

if ls "$REPO_DIR"/*.pkg.tar.zst >/dev/null 2>&1; then
    repo-add "$REPO_DIR/rimuru.db.tar.zst" "$REPO_DIR"/*.pkg.tar.zst
    echo "==> [rimuru] repository index updated successfully."
else
    echo "==> Creating empty [rimuru] database index..."
    repo-add "$REPO_DIR/rimuru.db.tar.zst"
fi
