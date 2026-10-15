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
- Focal area: the bbox in Tim Bailey's OpenTopography link
  (-122.7530, 41.7727, -122.7173, 41.7922), about 3 x 2 km, all inside B22
  tile x52y463. It's the candidate workshop region. The full HUC12 is the
  optional extension.

## Elevation epochs

Collection dates come from the 3DEP WESM index and the OpenTopography catalog,
checked 2026-10-13.

| Epoch | Dataset | Collected | Horizontal CRS | Vertical datum | Covers focal area |
| --- | --- | --- | --- | --- | --- |
| 2010 | CA_OR_KLAMATHRIVER_2010 (legacy) | 2010-02-27 to 2010-03-15 | EPSG:2870, NAD83(HARN) CA zone 1, ftUS | NAVD88 ftUS, GEOID09 | to check |
| 2013 | USFS Humbug Creek Lidar, CA 2013 (OpenTopography `CA13_Humbug`) | 2013-09-04 to 2013-09-07 | EPSG:26910, NAD83 UTM 10N | NAVD88 (geoid to confirm) | yes |
| 2018 | CA_Klamath_Topography_2018 | 2018-06-01 to 2018-06-14 | EPSG:6339, NAD83(2011) UTM 10N | NAVD88, GEOID12B | no, north strip only |
| 2022 | CA_NorthernCA_6_B22 | 2022-09-14 to 2022-10-28 | EPSG:6339, NAD83(2011) UTM 10N | NAVD88, GEOID18 | yes |

The 2022 collection came 6 to 12 weeks after the storm and before the winter
rains, so it records the immediate rain-on-fire response.

The epochs use different NAD83 realizations and different geoid models. That
difference is part of the lesson on co-registration. Do not hide it in
preprocessing.

## Still to confirm

- The 2013 USFS product: point cloud only, or a delivered DTM, and its geoid
  model.
- Whether the 2010 legacy collection covers the focal area. It's the only
  candidate for a pre-fire vs pre-fire noise baseline there. If it doesn't,
  use stable unburned ground across the control line instead.
- Burn severity source for the McKinney Fire (MTBS or RAVG) and its license.

## References

- Curtis, J.A., Johnson, G.S., Cahill, J.D., Genzoli, L., Dahm, C.N.,
  Schenk, L.N., Oberholzer, J.R., 2025. 2022 McKinney rain-on-wildfire event,
  dissolved oxygen sags, and a fish kill on the Klamath River, California.
  Scientific Reports 15, 24668. <https://doi.org/10.1038/s41598-025-08179-9>
