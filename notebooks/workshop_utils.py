"""Shared setup for the workshop notebooks."""

import os
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
GRASSDATA = REPO / "grassdata"
PROJECT = GRASSDATA / "humbug_creek"
RAW = GRASSDATA / "raw"

# Make the GRASS Python packages importable from this kernel.
sys.path.append(
    subprocess.check_output(["grass", "--config", "python_path"], text=True).strip()
)

import grass.jupyter as gj  # noqa: E402
from grass.tools import Tools  # noqa: E402


def start(block, required=()):
    """Start a GRASS session for a workshop block.

    Work happens in the mapset named by WORKSHOP_MAPSET (default "workshop").
    If any map in `required` is missing there, the checkpoint mapset from the
    previous block is added to the search path so the block can still run.
    """
    if not (PROJECT / "PERMANENT").exists():
        raise FileNotFoundError(
            f"No workshop data in {PROJECT}. Run `bash scripts/fetch_data.sh`."
        )
    mapset = os.environ.get("WORKSHOP_MAPSET", "workshop")
    session = gj.init(PROJECT / "PERMANENT")
    tools = Tools()
    tools.g_mapset(flags="c", mapset=mapset)

    missing = [
        m
        for m in required
        if not tools.g_list(type="raster", pattern=m, mapset=mapset).text
    ]
    if missing:
        checkpoint = f"checkpoint_{int(block) - 1:02d}"
        if not (PROJECT / checkpoint).exists():
            raise RuntimeError(
                f"Missing {missing} and no {checkpoint} mapset to fall back on."
            )
        tools.g_mapsets(operation="add", mapset=checkpoint)
        print(f"Using {checkpoint} for: {', '.join(missing)}")

    tools.g_region(region="focal@PERMANENT")
    print(f"Block {block} ready in mapset {mapset}")
    return tools, session
