#!/usr/bin/env bash
# Build one checkpoint mapset per workshop block and repack the data release
# (instructor only). Run after scripts/prepare_data.py, inside the devcontainer.
#
# Each notebook runs with WORKSHOP_MAPSET=checkpoint_NN, so its outputs land in
# that mapset and it reads earlier blocks from the earlier checkpoints. A
# participant who falls behind starts the next notebook in their own mapset and
# workshop_utils.start() picks up the checkpoints. Each checkpoint keeps only
# the rasters later blocks read, which keeps the release small. Block 04 feeds
# no later block, so it has no checkpoint.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PROJECT="$ROOT/grassdata/humbug_creek"
if [ ! -d "$PROJECT/PERMANENT" ]; then
    echo "No project at $PROJECT. Run scripts/prepare_data.py first." >&2
    exit 1
fi

declare -A KEEP=(
    [01]="dtm_2013,dtm_2022,dtm_2022_relief,dod_naive,burned,slope_2013"
    [02]="stable,stream_distance,dod_debiased"
    [03]="sig_slope"
)

cd "$ROOT/notebooks"
for block in 01 02 03; do
    notebook="$(ls "${block}"_*.ipynb)"
    mapset="checkpoint_${block}"
    echo "Building ${mapset} from ${notebook}"
    WORKSHOP_MAPSET="$mapset" uv run --with nbconvert jupyter nbconvert \
        --to notebook --execute --ExecutePreprocessor.timeout=1800 \
        --output "/tmp/${mapset}.ipynb" "$notebook"
    grass "$PROJECT/$mapset" --exec g.remove -f type=raster,vector \
        pattern="*" exclude="${KEEP[$block]}" > /dev/null
done

cd "$ROOT"
tar -czf humbug_creek.tar.gz -C grassdata \
    --exclude=".gislock" --exclude="humbug_creek/workshop" \
    humbug_creek raw
echo "Wrote $ROOT/humbug_creek.tar.gz"
