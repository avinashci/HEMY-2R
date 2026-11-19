# CAD

STEP files for HEMY 2R v2.2. Units: mm. Coordinates as described in the [design overview](../docs/01-design-overview.md#coordinate-system-and-naming).

| Folder | Contents |
|---|---|
| `parts/` | Every part to machine, plus `stock_hemy_parts/` (polvinc's unchanged parts) and bay envelopes used for clearance checks only. See [mechanical parts](../docs/02-mechanical-parts.md). |
| `assemblies/` | `HEMY2R v2.2 - assembly.step`: the whole mount with base, LA-40B placeholder, counterweight, dovetail (both jaw options; hide one), board and accessories, in named groups. |
| `reference/` | Not machined: Angeleyes LA-40B interface drawing and a measured placeholder of its top plate. |
| `logo/` | Laser-marking artwork for the side plates and the lid sticker print file. |
| `tools/` | The Python scripts (CadQuery / OCP) that produced each edit; reusable ones at the top, one-off edits in `history/`. |

## Regenerating parts

The parts were made by editing polvinc's STEP files one change at a time with Python scripts. The STEP files here are the source of truth; the scripts in [`tools/`](tools/) record every change, and a few can be re-run with your own measurements (notably the dovetail bay). See [`tools/README.md`](tools/README.md).

## Vendor models

The HBK17 reducer and NEMA17 motor models in the assembly come from the sellers. Their source files are not redistributed here; download them from the seller listings if you need them separately.
