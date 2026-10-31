# Workshop data

Large rasters are not committed. `scripts/fetch_data.sh` downloads the prepared
GRASS project from the repository's GitHub Release. This folder holds the area
of interest, the source lists, and the provenance record.

## Study area

Humbug Creek, HUC12 180102060801, Siskiyou County, California (95.7 km2). The
creek burned at high severity in the 2022 McKinney Fire (ignition 2022-07-29).
On 2022-08-02 a monsoonal storm cell dropped roughly 4 in of rain on the burn
scar. A fire control line follows the creek, so unburned terrain sits next to
burned channels.

- `aoi/HumbugCreek.geojson`: HUC12 boundary from the Watershed Boundary
  Dataset, EPSG:4269.
- `aoi/focal.geojson`: the workshop region, the bbox in Tim Bailey's
  OpenTopography link (-122.7530, 41.7727, -122.7173, 41.7922). About
  3.0 x 2.2 km at 1 m, all inside B22 tile x52y463. The full HUC12 is the
  optional extension.
- Fire perimeter: MTBS McKinney Fire, `CA4183012289520220729` (Extended
  assessment, post-fire scene 2023-08-15), fetched from the USFS EDW MTBS
  map service by `scripts/prepare_data.py`.

## Elevation epochs

Collection dates come from the 3DEP WESM index and the OpenTopography catalog,
checked 2026-10-13 and 2026-10-15.

| Epoch | Dataset | Collected | Horizontal CRS | Vertical datum | Covers focal area |
| --- | --- | --- | --- | --- | --- |
| 2010 | CA_OR_KLAMATHRIVER_2010 (legacy) | 2010-02-27 to 2010-03-15 | EPSG:2870, NAD83(HARN) CA zone 1, ftUS | NAVD88 ftUS, GEOID09 | no |
| 2013 | USFS Humbug Creek Lidar, CA 2013 (OpenTopography `CA13_Humbug`) | 2013-09-04 to 2013-09-07 | EPSG:26910, NAD83 UTM 10N | NAVD88, GEOID12A | yes |
| 2018 | CA_Klamath_Topography_2018 | 2018-06-01 to 2018-06-14 | EPSG:6339, NAD83(2011) UTM 10N | NAVD88, GEOID12B | no, north strip only |
| 2022 | CA_NorthernCA_6_B22 | 2022-09-14 to 2022-10-28 | EPSG:6339, NAD83(2011) UTM 10N | NAVD88, GEOID18 | yes |

The 2022 collection came 6 to 12 weeks after the storm and before the winter
rains, so it records the immediate rain-on-fire response.

The epochs use different NAD83 realizations and different geoid models. That
difference is part of the lesson on co-registration. Do not hide it in
preprocessing.

- Both the 2013 file and the USGS 1 m tiles declare EPSG:26910 in their
  headers, so the realization is only in the collection metadata. The GRASS
  project uses EPSG:26910 and nothing is reprojected on import.
- Treating the 2013 data as NAD83(1986) and transforming to NAD83(2011)
  moves a point at the site by 0.20 m east and 0.55 m north with the NADCON5
  grids, and by 0 m when PROJ cannot reach them. Reprojecting would make the
  result depend on network access.
- GEOID18 minus GEOID12B undulation across the focal region is -0.021 to
  -0.027 m, so 2022 heights read 2 to 3 cm higher for the same ellipsoid
  height. GEOID12B stands in for GEOID12A here. NGS documents GEOID12B as
  identical to GEOID12A except in Puerto Rico
  ([GEOID12B technical details](https://geodesy.noaa.gov/research/technical-details/USGG2012-GEOID12B-technical-information.pdf)).

## Getting the 2013 DTM

OpenTopography distributes the 2013 USFS DTM (raster ID
`OTSDEM.122022.26910.2`, <https://doi.org/10.5069/G9FJ2F12>) only after you
sign in, and it is not in the public bulk buckets. Download it once for the
focal region and pass it to `scripts/prepare_data.py --dtm2013`. Participants
get the clipped copy from the release.

The download box in EPSG:26910 is the focal region plus the 100 m clip
buffer: xmin 520423, ymin 4624467, xmax 523597, ymax 4626838. Choose
GeoTIFF output with the bare-earth and highest-hit layers, then pass
`output_be.tif` as `--dtm2013` and `output_hh.tif` as `--dsm2013`. Highest hit
minus bare earth gives pre-fire canopy height for block 02. Cite the dataset
as listed under References.

The delivered 2013 grid starts at 520422.29, 4626838.83, so its cells sit
0.29 m east and 0.17 m south of the whole-meter grid the 2022 data and the
focal region use. `r.import` keeps that grid because the CRS already matches.
Notebook 01 resamples the 2013 DTM onto the region with *r.resamp.interp*
(bilinear). Reading the native grid on the region instead takes the nearest
cell, which shifts the surface by that offset and changes the DoD by up to
2 m on steep slopes.

## Noise baseline

- The 2010 legacy collection does not cover the focal region, so the noise
  baseline comes from stable unburned ground across the control line. About
  15 percent of the focal region is unburned.

## Burn severity

`dnbr` and `burn_severity` in PERMANENT (10 m) come from two Sentinel-2 L2A
scenes on Element84 Earth Search, imported with *t.stac.item* by
`scripts/prepare_data.py`:

- Pre-fire: `S2B_10TEM_20220721_0_L2A`, eight days before ignition.
- Post-fire: `S2B_10TEM_20220909_0_L2A`, after the 2022-08-02 storm and five
  days before the 2022 lidar collection began.

B12 is natively 20 m, so NBR has an effective resolution of 20 m resampled to
10 m. NBR is (B08 - B12) / (B08 + B12) on reflectance, and `dnbr` is
1000 x (NBR pre - NBR post) minus its median outside the fire perimeter (2.4).

Reflectance is DN x 1e-4. The Earth Search items list a `raster:bands` offset
of -0.1 and set `earthsearch:boa_offset_applied: true`, and the pixels already
have the processing baseline 04.00 offset removed. Applying -0.1 again pushes
20% of pre-fire cells to near-zero reflectance and moves the unburned median
dNBR to -25; without it the unburned median is +2.

The classes use the dNBR thresholds MTBS published for this fire
(`CA4183012289520220729`): increased greenness below -150, unburned to low
below 35, low below 300, moderate below 530, high from 530. MTBS derived them
from a Landsat extended assessment (post-fire scene 2023-08-15), so they
approximate classes for this Sentinel-2 initial assessment.

The build falls back to a local perimeter (`--perimeter`) when the USFS MTBS
service is unavailable.

Contains modified Copernicus Sentinel data 2022.

## References

- U.S. Forest Service Region 5 Remote Sensing Lab Information Management
  Staff. (2022). USFS Humbug Creek Lidar, CA 2013. Collected by Digital
  Mapping Inc. Distributed by OpenTopography.
  <https://doi.org/10.5069/G9FJ2F12>. Accessed 2026-10-15
- Curtis, J.A., Johnson, G.S., Cahill, J.D., Genzoli, L., Dahm, C.N.,
  Schenk, L.N., Oberholzer, J.R., 2025. 2022 McKinney rain-on-wildfire event,
  dissolved oxygen sags, and a fish kill on the Klamath River, California.
  Scientific Reports 15, 24668. <https://doi.org/10.1038/s41598-025-08179-9>
