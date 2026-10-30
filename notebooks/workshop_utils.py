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
    If any map in `required` is missing there, the checkpoint mapsets of all
    earlier blocks are added to the search path so the block can still run.
    """
    if not (PROJECT / "PERMANENT").exists():
        raise FileNotFoundError(
            f"No workshop data in {PROJECT}. Run `bash scripts/fetch_data.sh`."
        )
    mapset = os.environ.get("WORKSHOP_MAPSET", "workshop")
    if (PROJECT / mapset).exists():
        # Start in the mapset directly. Switching to it with g.mapset fails while
        # the previous notebook's kernel still holds a session there.
        session = gj.init(PROJECT / mapset)
        tools = Tools()
    else:
        session = gj.init(PROJECT / "PERMANENT")
        tools = Tools()
        tools.g_mapset(flags="c", mapset=mapset)

    def in_mapset(name):
        # g.list prints nothing for an empty match, and Tools then returns None.
        # Compare with None explicitly: truth-testing a ToolResult parses JSON.
        result = tools.g_list(type="raster", pattern=name, mapset=mapset)
        return result is not None and bool(result.text.strip())

    missing = [m for m in required if not in_mapset(m)]
    if missing:
        checkpoints = [
            f"checkpoint_{n:02d}"
            for n in range(int(block) - 1, 0, -1)
            if (PROJECT / f"checkpoint_{n:02d}").exists()
        ]
        if not checkpoints:
            raise RuntimeError(
                f"Missing {missing} and no checkpoint mapsets to fall back on."
            )
        tools.g_mapsets(operation="add", mapset=",".join(checkpoints))
        print(f"Missing {', '.join(missing)}; using {', '.join(checkpoints)}")

    tools.g_region(region="focal@PERMANENT")
    print(f"Block {block} ready in mapset {mapset}")
    return tools, session


def stable_stats(tools, dod, mask):
    """Median, NMAD, and cell count of a DoD on the cells of a mask.

    NMAD is 1.4826 times the median absolute deviation from the median, a
    standard deviation estimate that is not pulled by outliers.
    """
    values = "tmp_stable_values"
    deviation = "tmp_stable_deviation"
    tools.r_mapcalc(expression=f"{values} = if(!isnull({mask}), {dod}, null())")
    median = _percentile(tools, values, 50)
    tools.r_mapcalc(expression=f"{deviation} = abs({values} - {median})")
    nmad = 1.4826 * _percentile(tools, deviation, 50)
    n = tools.r_univar(map=values, format="json")["n"]
    tools.g_remove(type="raster", name=f"{values},{deviation}", flags="f")
    return {"median": median, "nmad": nmad, "n": n}


def _percentile(tools, name, percentile):
    text = tools.r_quantile(input=name, percentiles=percentile).text
    return float(text.strip().split(":")[-1])
