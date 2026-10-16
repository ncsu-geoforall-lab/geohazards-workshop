"""Build the workshop data release (instructor only).

Creates grassdata/humbug_creek (EPSG:26910) with the study area vectors and the
saved `focal` region, clips each lidar epoch to the focal region in its native
grid under grassdata/raw, and writes humbug_creek.tar.gz for the GitHub Release.

The 2013 USFS rasters need an OpenTopography login, so download them once
(bare earth and highest hit, GeoTIFF) and pass the files with --dtm2013 and
--dsm2013. Participants get them from the release.

Usage (inside the devcontainer):
    uv run python scripts/prepare_data.py \
        --dtm2013 /path/to/output_be.tif --dsm2013 /path/to/output_hh.tif
"""

import argparse
import json
import subprocess
import sys
import tarfile
import urllib.parse
import urllib.request
from pathlib import Path

from osgeo import gdal

REPO = Path(__file__).resolve().parent.parent
B22_TILE = (
    "/vsicurl/https://prd-tnm.s3.amazonaws.com/StagedProducts/Elevation/1m/Projects/"
    "CA_NorthernCA_B22/TIFF/USGS_1M_10_x52y463_CA_NorthernCA_B22.tif"
)
MTBS_PERIMETERS_2022 = (
    "https://apps.fs.usda.gov/arcx/rest/services/EDW/EDW_MTBS_01/MapServer/79/query"
)
MCKINNEY_FIRE_ID = "CA4183012289520220729"
EPSG = "26910"
BUFFER_M = 100

sys.path.append(
    subprocess.check_output(["grass", "--config", "python_path"], text=True).strip()
)
import grass.script as gs  # noqa: E402
from grass.tools import Tools  # noqa: E402

gdal.UseExceptions()


def fetch_perimeter(dest):
    """Download the MTBS McKinney Fire perimeter as GeoJSON."""
    query = urllib.parse.urlencode(
        {
            "where": f"fire_id='{MCKINNEY_FIRE_ID}'",
            "outFields": "fire_id,fire_name,ig_date,acres,asmnt_type",
            "outSR": "4326",
            "f": "geojson",
        }
    )
    with urllib.request.urlopen(f"{MTBS_PERIMETERS_2022}?{query}", timeout=60) as r:
        data = json.load(r)
    if not data.get("features"):
        raise RuntimeError("MTBS returned no perimeter for the McKinney Fire")
    dest.write_text(json.dumps(data))


def clip(src, dest, bounds):
    """Clip a raster to bounds (w, s, e, n) in its own grid, no resampling."""
    w, s, e, n = bounds
    gdal.Translate(
        str(dest),
        src,
        projWin=[w - BUFFER_M, n + BUFFER_M, e + BUFFER_M, s - BUFFER_M],
        creationOptions=["COMPRESS=DEFLATE", "PREDICTOR=3", "TILED=YES"],
    )
    print(f"Wrote {dest}")


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--dtm2013", type=Path, help="USFS 2013 bare-earth DEM from OpenTopography"
    )
    parser.add_argument(
        "--dsm2013",
        type=Path,
        help="USFS 2013 highest-hit DSM from OpenTopography, for canopy height",
    )
    parser.add_argument("--out", type=Path, default=REPO / "grassdata")
    args = parser.parse_args()

    project = args.out / "humbug_creek"
    raw = args.out / "raw"
    if project.exists():
        sys.exit(f"{project} exists. Remove it to rebuild.")
    raw.mkdir(parents=True, exist_ok=True)

    perimeter = raw / "mckinney_perimeter.geojson"
    fetch_perimeter(perimeter)

    gs.create_project(project, epsg=EPSG)
    with gs.setup.init(project) as session:
        tools = Tools(session=session)
        tools.v_import(input=str(REPO / "data/aoi/HumbugCreek.geojson"), output="huc12")
        tools.v_import(input=str(REPO / "data/aoi/focal.geojson"), output="focal_aoi")
        tools.v_import(input=str(perimeter), output="mckinney_perimeter")
        tools.g_region(vector="focal_aoi", res=1, flags="a")
        tools.g_region(save="focal")
        tools.g_region(flags="s")  # also make it the project default
        region = tools.g_region(flags="g", format="json")
        bounds = (region["west"], region["south"], region["east"], region["north"])

    clip(B22_TILE, raw / "usgs_2022_dtm.tif", bounds)
    if args.dtm2013:
        clip(str(args.dtm2013), raw / "usfs_2013_dtm.tif", bounds)
    else:
        print("WARNING: no --dtm2013 given, the release will be missing the 2013 epoch")
    if args.dsm2013:
        clip(str(args.dsm2013), raw / "usfs_2013_dsm.tif", bounds)

    tarball = REPO / "humbug_creek.tar.gz"
    with tarfile.open(tarball, "w:gz") as tar:
        tar.add(project, arcname="humbug_creek")
        tar.add(raw, arcname="raw")
    print(f"Wrote {tarball}")


if __name__ == "__main__":
    main()
