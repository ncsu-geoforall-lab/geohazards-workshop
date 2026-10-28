"""Build the workshop data release (instructor only).

Creates grassdata/humbug_creek (EPSG:26910) with the study area vectors and the
saved `focal` region, clips each lidar epoch to the focal region in its native
grid under grassdata/raw, and writes humbug_creek.tar.gz for the GitHub Release.

The 2013 USFS rasters need an OpenTopography login, so download them once
(bare earth and highest hit, GeoTIFF) and pass the files with --dtm2013 and
--dsm2013. Participants get them from the release.

Burn severity comes from Sentinel-2 through the t.stac addon, so install it
first: pip install pystac pystac_client tqdm, then g.extension extension=t.stac.

Usage (inside the devcontainer):
    uv run python scripts/prepare_data.py \
        --dtm2013 /path/to/output_be.tif --dsm2013 /path/to/output_hh.tif
"""

import argparse
import io
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

# Sentinel-2 L2A scenes for burn severity, from Element84 Earth Search. Earth
# Search has already removed the processing baseline 04.00 offset from these
# pixels (earthsearch:boa_offset_applied), so reflectance is DN * 1e-4.
EARTH_SEARCH = "https://earth-search.aws.element84.com/v1"
S2_PRE = "S2B_10TEM_20220721_0_L2A"
S2_POST = "S2B_10TEM_20220909_0_L2A"
# dNBR (x1000) thresholds published by MTBS for this fire (Landsat, extended
# assessment). They are an approximation for this Sentinel-2 initial assessment.
MTBS_THRESHOLDS = {"greenness": -150, "low": 35, "moderate": 300, "high": 530}
SEVERITY_CLASSES = (
    "1:Unburned to low\n2:Low\n3:Moderate\n4:High\n5:Increased greenness\n"
)
SEVERITY_COLORS = "1 0:100:0\n2 127:255:212\n3 255:255:0\n4 255:0:0\n5 127:255:0\n"

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


def add_burn_severity(tools):
    """Compute 10 m dNBR and MTBS-threshold severity classes in PERMANENT.

    Needs the t.stac addon (g.extension extension=t.stac) and pystac_client.
    """
    th = MTBS_THRESHOLDS
    tools.g_region(region="focal", res=10, flags="a")
    tools.t_stac_item(
        url=EARTH_SEARCH,
        collection_id="sentinel-2-l2a",
        ids=f"{S2_PRE},{S2_POST}",
        asset_keys="nir,swir22",
        method="bilinear",
        resolution="value",
        resolution_value=10,
        extent="region",
        flags="d",
    )
    bands = []
    for label, item in (("pre", S2_PRE), ("post", S2_POST)):
        nir = f"sentinel-2-l2a.{item}.nir"
        swir = f"sentinel-2-l2a.{item}.swir22"
        bands += [nir, swir]
        n, s = f'(double("{nir}") * 0.0001)', f'(double("{swir}") * 0.0001)'
        tools.r_mapcalc(
            expression=(
                f"tmp_nbr_{label} = if(({n} + {s}) < 0.02, null(), "
                f"({n} - {s}) / ({n} + {s}))"
            )
        )
    tools.v_to_rast(input="mckinney_perimeter", output="tmp_burned", use="val", value=1)
    tools.r_mapcalc(expression="tmp_dnbr = 1000 * (tmp_nbr_pre - tmp_nbr_post)")
    tools.r_mapcalc(
        expression="tmp_unburned = if(isnull(tmp_burned), tmp_dnbr, null())"
    )
    offset = float(
        tools.r_quantile(input="tmp_unburned", percentiles=50).text.split(":")[-1]
    )
    tools.r_mapcalc(expression=f"dnbr = tmp_dnbr - {offset}")
    tools.r_mapcalc(
        expression=(
            f"burn_severity = if(dnbr < {th['greenness']}, 5, if(dnbr < {th['low']}, 1, "
            f"if(dnbr < {th['moderate']}, 2, if(dnbr < {th['high']}, 3, 4))))"
        )
    )
    tools.r_category(
        map="burn_severity", separator=":", rules=io.StringIO(SEVERITY_CLASSES)
    )
    tools.r_colors(map="burn_severity", rules=io.StringIO(SEVERITY_COLORS))
    tools.r_colors(map="dnbr", color="differences")
    source = f"Sentinel-2 L2A {S2_PRE} and {S2_POST}, Element84 Earth Search"
    tools.r_support(
        map="dnbr",
        title="dNBR x1000 (pre minus post), McKinney Fire",
        units="dNBR x1000",
        source1=source,
        history=f"Offset {offset:.1f} removed (median dNBR outside the MTBS perimeter)",
    )
    tools.r_support(
        map="burn_severity",
        title="Burn severity, McKinney Fire",
        source1=source,
        source2=f"MTBS {MCKINNEY_FIRE_ID} dNBR thresholds {th}",
    )
    tools.g_remove(
        type="raster",
        name=",".join(
            bands
            + ["tmp_nbr_pre", "tmp_nbr_post", "tmp_burned", "tmp_dnbr", "tmp_unburned"]
        ),
        flags="f",
    )
    tools.g_region(region="focal")
    print(f"Burn severity added (dNBR offset {offset:.1f})")


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
    parser.add_argument(
        "--perimeter",
        type=Path,
        help="Local copy of the MTBS perimeter GeoJSON, used instead of the MTBS service",
    )
    parser.add_argument("--out", type=Path, default=REPO / "grassdata")
    args = parser.parse_args()

    project = args.out / "humbug_creek"
    raw = args.out / "raw"
    if project.exists():
        sys.exit(f"{project} exists. Remove it to rebuild.")
    raw.mkdir(parents=True, exist_ok=True)

    perimeter = raw / "mckinney_perimeter.geojson"
    if args.perimeter:
        perimeter.write_text(args.perimeter.read_text())
    else:
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
        add_burn_severity(tools)

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
