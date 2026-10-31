#!/usr/bin/env bash
# Download the prepared Humbug Creek GRASS project from the GitHub Release
# and unpack it to ./grassdata. Safe to rerun. An older release is replaced,
# and your own mapsets are kept.
set -euo pipefail

REPO="ncsu-geoforall-lab/geohazards-workshop"
TAG="${DATA_TAG:-data-v0.2}"
ASSET="humbug_creek.tar.gz"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DEST="$ROOT/grassdata"
PROJECT="$DEST/humbug_creek"
STAMP="$PROJECT/.data_tag"

if [ -f "$STAMP" ] && [ "$(cat "$STAMP")" = "$TAG" ]; then
    echo "Workshop data $TAG already present in $PROJECT"
    exit 0
fi
# data-v0.2 was released before the stamp file. Its checkpoints mark it.
if [ ! -f "$STAMP" ] && [ "$TAG" = "data-v0.2" ] && [ -d "$PROJECT/checkpoint_03" ]; then
    echo "$TAG" >"$STAMP"
    echo "Workshop data $TAG already present in $PROJECT"
    exit 0
fi
if [ -d "$PROJECT/PERMANENT" ]; then
    echo "Replacing older workshop data in $PROJECT with $TAG"
fi

mkdir -p "$DEST"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

URL="https://github.com/$REPO/releases/download/$TAG/$ASSET"
echo "Downloading $URL"
if ! curl -fL --retry 3 -o "$TMP/$ASSET" "$URL"; then
    echo "Could not download workshop data release $TAG." >&2
    echo "Check the network and rerun 'bash scripts/fetch_data.sh'." >&2
    exit 1
fi

tar -xzf "$TMP/$ASSET" -C "$DEST"
echo "$TAG" >"$STAMP"
echo "Workshop data $TAG ready in $PROJECT"
