"""Make the figures for the context slides.

Run after notebooks 01 to 04 have run in the workshop mapset, from the repo
root inside the devcontainer:

    uv run python slides/make_figures.py
"""

import io
import subprocess
import sys
from datetime import date
from pathlib import Path

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from PIL import Image

sys.path.append(
    subprocess.check_output(["grass", "--config", "python_path"], text=True).strip()
)
import grass.jupyter as gj  # noqa: E402
from grass.tools import Tools  # noqa: E402

REPO = Path(__file__).resolve().parent.parent
OUT = REPO / "slides" / "figures"
OUT.mkdir(exist_ok=True)

# GRASS brand ink and the validated event palette (lidar, fire and storm, Sentinel-2).
INK = "#021905"
MUTED = "#4e4d4c"
GRID = "#d8d8d8"
LIDAR, FIRE, SENTINEL = "#2f6db5", "#c2402f", "#14907f"
LOWERING = "#c2402f"

plt.rcParams.update(
    {
        "font.family": ["Fira Sans", "DejaVu Sans"],
        "font.size": 13,
        "axes.edgecolor": GRID,
        "axes.labelcolor": INK,
        "xtick.color": MUTED,
        "ytick.color": MUTED,
        "text.color": INK,
    }
)

session = gj.init(REPO / "grassdata" / "humbug_creek" / "workshop")
tools = Tools()
tools.g_region(region="focal@PERMANENT")


def save_map(name, build, width=1100, region=None, jpeg=True):
    """Render a map. Shaded rasters go to JPEG to keep the repo small."""
    figure = gj.Map(width=width, saved_region=region) if region else gj.Map(width=width)
    build(figure)
    png = OUT / f"{name}.png"
    figure.save(str(png))
    if jpeg:
        Image.open(png).convert("RGB").save(OUT / f"{name}.jpg", quality=85)
        png.unlink()
    print(f"Wrote {name}.{'jpg' if jpeg else 'png'}")


# Location: the HUC12, the focal region, and the fire perimeter.
tools.g_region(vector="huc12@PERMANENT", res=30, flags="a")
tools.g_region(save="huc12_view", overwrite=True)
tools.g_region(region="focal@PERMANENT")
save_map(
    "location",
    lambda m: (
        m.d_vect(map="huc12@PERMANENT", fill_color="240:240:241", color="none"),
        m.d_vect(
            map="mckinney_perimeter@PERMANENT",
            fill_color="246:206:200",
            color="194:64:47",
            width=2,
        ),
        m.d_vect(map="huc12@PERMANENT", fill_color="none", color="0:57:63", width=3),
        m.d_vect(
            map="focal_aoi@PERMANENT", fill_color="none", color="8:139:54", width=4
        ),
    ),
    width=800,
    region="huc12_view",
    jpeg=False,
)

save_map(
    "focal",
    lambda m: (
        m.d_rast(map="dtm_2022_relief"),
        m.d_rast(map="channels"),
        m.d_vect(
            map="mckinney_perimeter@PERMANENT",
            fill_color="none",
            color="194:64:47",
            width=3,
        ),
    ),
)

save_map(
    "severity",
    lambda m: (
        m.d_shade(shade="dtm_2022_relief", color="burn_severity@PERMANENT"),
        m.d_vect(
            map="mckinney_perimeter@PERMANENT",
            fill_color="none",
            color="black",
            width=2,
        ),
        m.d_legend(
            raster="burn_severity@PERMANENT",
            title="Burn severity",
            at=(5, 38, 2, 5),
            fontsize=14,
            flags="b",
        ),
    ),
)

# Nearest-cell error from notebook 01, on a symmetric scale.
tools.r_colors(
    map="nearest_error",
    rules=io.StringIO(
        "-1000 64:0:75\n-0.5 64:0:75\n0 247:247:247\n0.5 0:68:27\n1000 0:68:27\n"
    ),
)
save_map(
    "nearest_error",
    lambda m: (
        m.d_shade(shade="dtm_2022_relief", color="nearest_error"),
        m.d_legend(
            raster="nearest_error",
            title="Nearest-cell error (m)",
            range=(-0.5, 0.5),
            at=(5, 40, 2, 5),
            fontsize=14,
            flags="b",
        ),
    ),
)

# Debiased DoD with the r.dem.dod palette copied from dod_nk.
tools.r_colors(map="dod_debiased", raster="dod_nk")
save_map(
    "dod",
    lambda m: (
        m.d_shade(shade="dtm_2022_relief", color="dod_debiased"),
        m.d_vect(
            map="mckinney_perimeter@PERMANENT",
            fill_color="none",
            color="black",
            width=2,
        ),
        m.d_legend(
            raster="dod_debiased",
            title="DoD (m)",
            range=(-1, 1),
            at=(5, 40, 2, 5),
            fontsize=14,
            flags="b",
        ),
    ),
)

save_map(
    "change_class",
    lambda m: (
        m.d_shade(shade="dtm_2022_relief", color="change_class"),
        m.d_vect(
            map="mckinney_perimeter@PERMANENT",
            fill_color="none",
            color="black",
            width=2,
        ),
        m.d_legend(
            raster="change_class",
            title="Change class",
            at=(48, 95, 2, 5),
            fontsize=13,
            flags="b",
        ),
    ),
)

# Timeline: 2013 and summer to fall 2022, as two panels on their own scales.
fig, (left, right) = plt.subplots(
    1, 2, figsize=(12, 3.4), gridspec_kw={"width_ratios": [1, 4]}, sharey=True
)
rows = {"Lidar": 2, "Fire and storm": 1, "Sentinel-2": 0}


def span(ax, row, start, end, color, label):
    ax.plot([start, end], [row, row], color=color, linewidth=8, solid_capstyle="butt")
    ax.annotate(
        label,
        (start, row),
        xytext=(0, 12),
        textcoords="offset points",
        color=INK,
        fontsize=12,
    )


def point(ax, row, day, color, label, dy=12):
    ax.plot(
        [day],
        [row],
        marker="o",
        markersize=10,
        color=color,
        markeredgecolor="white",
        markeredgewidth=2,
    )
    ax.annotate(
        label,
        (day, row),
        xytext=(-4, dy),
        textcoords="offset points",
        color=INK,
        fontsize=12,
    )


span(left, rows["Lidar"], date(2013, 9, 4), date(2013, 9, 8), LIDAR, "USFS lidar")
left.set_xlim(date(2013, 8, 20), date(2013, 9, 25))
point(right, rows["Sentinel-2"], date(2022, 7, 21), SENTINEL, "Pre-fire scene")
point(right, rows["Fire and storm"], date(2022, 7, 29), FIRE, "Ignition", dy=-22)
point(right, rows["Fire and storm"], date(2022, 8, 2), FIRE, "Storm, >100 mm in 3 h")
point(right, rows["Sentinel-2"], date(2022, 9, 9), SENTINEL, "Post-fire scene")
span(
    right,
    rows["Lidar"],
    date(2022, 9, 14),
    date(2022, 10, 29),
    LIDAR,
    "USGS 3DEP lidar",
)
right.set_xlim(date(2022, 7, 10), date(2022, 11, 10))

for ax in (left, right):
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.grid(axis="x", color=GRID, linewidth=0.8)
    ax.set_ylim(-0.6, 2.8)
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
left.set_yticks(list(rows.values()), list(rows.keys()))
left.tick_params(axis="y", length=0)
right.tick_params(axis="y", length=0)
fig.tight_layout()
fig.savefig(OUT / "timeline.png", dpi=150, transparent=True)
plt.close(fig)
print("Wrote timeline.png")

# Net change per hectare by burn severity, from the significant DoD.
area = {
    z["zone"]: (z["zone_label"], z["n"])
    for z in tools.r_univar(
        map="dod_debiased", zones="burn_severity@PERMANENT", format="json"
    )
}
net = {
    z["zone"]: z["sum"]
    for z in tools.r_univar(
        map="sig_slope", zones="burn_severity@PERMANENT", format="json"
    )
}
classes = [1, 2, 3, 4]
labels = [area[c][0] for c in classes]
values = [net[c] / (area[c][1] / 10_000) for c in classes]

fig, ax = plt.subplots(figsize=(8, 4.2))
bars = ax.bar(labels, values, color=LOWERING, width=0.6, edgecolor="white", linewidth=2)
for bar, value in zip(bars, values):
    ax.annotate(
        f"{value:,.0f}",
        (bar.get_x() + bar.get_width() / 2, value),
        xytext=(0, -16),
        textcoords="offset points",
        ha="center",
        color=INK,
    )
ax.axhline(0, color=MUTED, linewidth=1)
ax.set_ylabel("Net change (m³ per ha)")
ax.set_ylim(min(values) * 1.18, 0)
ax.grid(axis="y", color=GRID, linewidth=0.8)
ax.set_axisbelow(True)
for side in ("top", "right"):
    ax.spines[side].set_visible(False)
fig.tight_layout()
fig.savefig(OUT / "severity_bars.png", dpi=150, transparent=True)
plt.close(fig)
print("Wrote severity_bars.png", [round(v) for v in values])
