# Geohazard Change Detection for Emergency Management with GRASS

FOSS4G NA 2026 workshop, Sacramento. 2026-11-02, 13:00-16:00, Room Bondi.

Repeat lidar shows how wildfire and the storms that follow it reshape a
watershed. A raw DEM of Difference (DoD) mixes that change with measurement
error, co-registration offsets, and vegetation effects. In this workshop we
build an uncertainty-aware change detection workflow in GRASS with the
[`r.dem`](https://grass.osgeo.org/grass-stable/manuals/addons/r.dem.html)
toolset and run it on Humbug Creek, California, which burned in the 2022
McKinney Fire and was hit four days later by a storm that dropped about 4 in
of rain on the burn scar.

The workshop is fully hands-on. Everything runs in a browser through GitHub
Codespaces, or locally in the same container.

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/ncsu-geoforall-lab/geohazards-workshop)

## Learning objectives

By the end of the workshop you will be able to:

1. Compute a DoD between two lidar epochs and explain where it misleads.
2. Find and correct horizontal and vertical datum and co-registration
   offsets using stable terrain.
3. Estimate a level of detection (LoD) and apply a spatially variable
   threshold instead of a single value.
4. Organize multi-date elevation data with the GRASS temporal framework.
5. Turn significant change into volumes and hazard maps by burn severity and
   subwatershed.

## Schedule

| Time | Block | Notebook |
| --- | --- | --- |
| 13:00 | Welcome and environment check | [00_setup_check](notebooks/00_setup_check.ipynb) |
| 13:15 | The McKinney rain-on-fire event, lidar products, and sources of error | slides |
| 13:35 | Data, datums, and the temporal framework | [01_data_and_time](notebooks/01_data_and_time.ipynb) |
| 14:10 | Co-registration and bias | [02_coregister_and_bias](notebooks/02_coregister_and_bias.ipynb) |
| 14:45 | Break | |
| 14:55 | Level of detection and significant change | [03_lod_and_change](notebooks/03_lod_and_change.ipynb) |
| 15:30 | Products for emergency management | [04_hazard_products](notebooks/04_hazard_products.ipynb) |
| 15:50 | Wrap-up and adapting the workflow to your area | [slides](slides/wrapup.qmd) |

Each notebook starts by loading a checkpoint, so you can rejoin at any block.
If you fall behind, open the next notebook and run all cells. It picks up the
maps it needs from the checkpoints of the earlier blocks, and you do not need
to finish or close the notebook you were in.

## Getting started

See [SETUP.md](SETUP.md). The short version is to click the Codespaces badge
above and wait for the setup to finish, then open
`notebooks/00_setup_check.ipynb` and run all cells.

## Prerequisites

Some GIS experience and basic Python. Prior GRASS experience helps but is not
required.

## Data

Lidar from the USFS (2013) and USGS 3DEP (2018, 2022). Sources, collection
dates, and datums are in [data/README.md](data/README.md).

## Acknowledgments

Tim Bailey suggested the Humbug Creek site and provided the data sources and
background on the event.

## License

Code is GPL-3.0. Workshop text is CC BY 4.0. Data keep their original terms,
listed in [data/README.md](data/README.md).
