#!/usr/bin/env bash
# Vibe3D — fetch Blender 2.83 LTS source (shallow) into source/
# Usage: bash scripts/fetch-blender.sh [--force]
set -euo pipefail

TAG="v2.83.20"
REPO="https://github.com/blender/blender.git"
DEST="source"

if [ -d "$DEST/.git" ]; then
  if [ "${1:-}" = "--force" ]; then
    echo "Removing existing $DEST ..."
    rm -rf "$DEST"
  else
    echo "$DEST already cloned. Pass --force to re-clone."
    git -C "$DEST" log -1 --format='%H %d %s'
    exit 0
  fi
fi

echo "Cloning Blender $TAG (shallow) into $DEST/ ..."
git clone --depth 1 --branch "$TAG" "$REPO" "$DEST"
git -C "$DEST" log -1 --format='Blender %H %d %s'
echo "Done. Source lives in $DEST/ (untouched upstream; patch from vibe/ and docs/)."
