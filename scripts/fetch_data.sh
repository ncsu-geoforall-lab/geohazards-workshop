#!/usr/bin/env bash
# Download the prepared Humbug Creek GRASS project from the GitHub Release
# and unpack it to ./grassdata. Safe to rerun.
set -euo pipefail

REPO="ncsu-geoforall-lab/geohazards-workshop"
TAG="${DATA_TAG:-data-v0.2}"
ASSET="humbug_creek.tar.gz"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DEST="$ROOT/grassdata"

if [ -d "$DEST/humbug_creek/PERMANENT" ]; then
    echo "Workshop data already present in $DEST/humbug_creek"
    exit 0
fi

mkdir -p "$DEST"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

URL="https://github.com/$REPO/releases/download/$TAG/$ASSET"
echo "Downloading $URL"
if ! curl -fL --retry 3 -o "$TMP/$ASSET" "$URL"; then
    echo "Workshop data release $TAG is not available yet." >&2
    echo "The environment still works. Rerun 'bash scripts/fetch_data.sh' later." >&2
    exit 0
fi

tar -xzf "$TMP/$ASSET" -C "$DEST"
echo "Workshop data ready in $DEST/humbug_creek"
