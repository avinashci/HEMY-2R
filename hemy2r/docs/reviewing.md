# How to review this project

[← Back to README](../../README.md)

Thank you for taking a look. HEMY 2R was designed by a software developer who is new to mechanical and electronics design, with AI assistance. **Please question every decision**: a wrong assumption is far cheaper to catch here than after a CNC and PCB order.

## What would help most

| If you know… | Please look at | Start with |
|---|---|---|
| **Electronics / PCB** | The single-board schematic and the protection fixes | [Electronics](04-electronics.md), [design review E1–E11](design-review.md#electrical), `pcb/single-board/` |
| **Mechanical / CNC** | The L-plate, base flange, dovetail bay, tolerances and drawing notes | [Mechanical parts](02-mechanical-parts.md), [manufacturing](06-manufacturing.md), the STEP assembly |
| **Telescope mounts** | Loads, balance, cable routing, usability at night | [Design overview](01-design-overview.md), [assembly](05-assembly.md) |

## Files you'll need

| What | Where | Open with |
|---|---|---|
| Full assembly | `hemy2r/cad/assemblies/HEMY2R v2.2 - assembly.step` (55 MB) | FreeCAD, Fusion, Onshape, eDrawings |
| Individual parts | `hemy2r/cad/parts/*.step` | same |
| Board project | `hemy2r/pcb/single-board/*.epro` | EasyEDA Pro (free), File → Open |
| Schematic | `hemy2r/pcb/single-board/*.pdf` | any PDF viewer |
| BOM / netlist | `hemy2r/pcb/single-board/` | spreadsheet / text editor |
| v2.3 concept assembly | [Releases](../../../../releases) | (too large for git) |

Each review round is tagged as a release (`review-1`, `review-2`, …) so everyone talks about the same files.

## How to give feedback

- **One issue per topic.** Use the "Design review item" template. Reference an ID from the [design review](design-review.md) (E1–E11, M1–M10) if it fits, or start a new one.
- **Small fixes** (typos, a wrong value in the docs): a pull request is welcome.
- **Design changes:** open an issue first so we can agree on the approach; then a pull request against the `hemy2r` branch (mechanical/docs) or `single-board` (electronics).
- Screenshots, marked-up PDFs and rough sketches are all fine.

## Electronics questions

The open questions for the single-board experiment:

1. **Stack-up:** polvinc's board is 4-layer. Keep 4 layers for the merged board, or is 2 enough with the extra space?
2. **Placement:** board under the lid (v2.2), or flipped components-up under a window (v2.3 concept)?
3. **Connectors:** JST PH/XH for signals, but what for the 10 A input and ACC path: Molex Micro-Fit, XT30, or screw terminals?
4. **Protection:** ideal diode + TVS + fuses on the board, or on a small separate power board at the input?
5. **Thermal:** two TMC5160s at ≤ 0.9 A in a sealed aluminium box with no heatsinks: OK?
6. **DRV103 status flag:** wire it to a spare Teensy pin with a pull-up, or leave it open?
7. **Isolator:** ISO7721 vs ADuM1201 for a 9600–38400 baud UART, powered from the module side through a 26–28 AWG core; anything to watch?
8. **Anything else** that looks like a beginner's mistake.

## Mechanical questions

1. Are the drawing notes in [manufacturing](06-manufacturing.md#notes-for-the-drawings) the right ones for a hobby-grade CNC service?
2. L-plate: is an inside fillet worth it, and is "flatness 0.02, perpendicularity 0.05" realistic and sufficient?
3. Base flange: 1.5 mm floor and 1.9 mm wall in the load path: acceptable?
4. Dovetail jaws: bronze, brass, or stainless?
