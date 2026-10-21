#!/usr/bin/env bash
# Download the prepared Humbug Creek GRASS project from the GitHub Release
# and unpack it to ./grassdata. Safe to rerun.
set -euo pipefail

REPO="ncsu-geoforall-lab/geohazards-workshop"
TAG="${DATA_TAG:-data-v0.1}"
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

download() {
    # With a token (Codespaces, CI, or `export GH_TOKEN=$(gh auth token)`), use
    # the API so the download also works while the repository is private.
    local token="${GH_TOKEN:-${GITHUB_TOKEN:-}}"
    if [ -n "$token" ]; then
        local api="https://api.github.com/repos/$REPO/releases/tags/$TAG"
        local asset_url
        asset_url="$(curl -fsSL -H "Authorization: Bearer $token" "$api" |
            python3 -c 'import json, sys; print(next(a["url"] for a in json.load(sys.stdin)["assets"] if a["name"] == sys.argv[1]))' "$ASSET")" ||
            return 1
        echo "Downloading $ASSET from release $TAG"
        curl -fL --retry 3 -H "Authorization: Bearer $token" \
            -H "Accept: application/octet-stream" -o "$TMP/$ASSET" "$asset_url"
    else
        local url="https://github.com/$REPO/releases/download/$TAG/$ASSET"
        echo "Downloading $url"
        curl -fL --retry 3 -o "$TMP/$ASSET" "$url"
    fi
}

if ! download; then
    echo "Could not download workshop data release $TAG." >&2
    echo "If the repository is private, set GH_TOKEN and rerun 'bash scripts/fetch_data.sh'." >&2
    exit 0
fi

tar -xzf "$TMP/$ASSET" -C "$DEST"
echo "Workshop data ready in $DEST/humbug_creek"
