#!/usr/bin/env bash
# Script to build and upload source package to Launchpad PPA
set -euo pipefail

PACKAGE_DIR="${1:-.}"
PPA_TARGET="${2:-ppa:myuser/myrepo}"
GPG_KEY_ID="${3:-}"

cd "$PACKAGE_DIR"

echo "=== 1. Building source-only package for Launchpad PPA ==="
if [ -n "$GPG_KEY_ID" ]; then
    debuild -S -sa -k"$GPG_KEY_ID"
else
    debuild -S -sa
fi

CHANGES_FILE=$(ls -t ../*_source.changes | head -n 1)
echo "=== 2. Generated Changes File: $CHANGES_FILE ==="

echo "=== 3. Uploading to $PPA_TARGET via dput ==="
# Requires user confirmation in interactive mode
dput "$PPA_TARGET" "$CHANGES_FILE"

echo "=== Upload complete. Monitor build at https://launchpad.net/~$PPA_TARGET ==="
