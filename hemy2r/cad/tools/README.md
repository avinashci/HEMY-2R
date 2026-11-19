# CAD tools

Python scripts (CadQuery / OCP) used to make HEMY 2R's parts. Install with `pip install cadquery-ocp`.

**How the parts were made:** the HEMY 2R parts started as polvinc's STEP files and were changed step by step, one script per change. The STEP files in [`../parts/`](../parts/) are the result and the source of truth. The scripts are a record of every change and a starting point if you want to make a similar one.

## Reusable scripts

These take their files as arguments and can be run again.

| Script | What it does | Run |
|---|---|---|
| `v22_dovetail_bay.py` | Makes the dovetail with its closed bay, the bay cover and the red USB-module insert from polvinc's dovetail. **Re-run this with measured parts:** the jack, LED and CH340E module sizes are parameters at the top. | `python3 v22_dovetail_bay.py <in-dovetail.step> <out-dovetail.step> <out-cover.step> <out-insert.step> [<out-envelopes.step>]` |
| `v22_dovetail_bay_asm.py` | Puts the outputs of the script above into the full assembly, keeping part names and colours. | `python3 v22_dovetail_bay_asm.py <assembly> <dovetail> <cover> <insert> <envelopes> <out>` |
| `v22_swap_part_asm.py` | Replaces one part in the assembly with an updated STEP (same coordinates), keeping names, colours and layers. | `python3 v22_swap_part_asm.py <assembly> <part.step> <out.step> go ["Part name"]` |
| `v22_move_part_asm.py` | Moves one part inside the assembly. With no name, lists the part names. | `python3 v22_move_part_asm.py <assembly> <out.step> "<part name>" dx dy dz` |
| `v22_remove_parts_asm.py` | Removes parts from the assembly by name prefix. | `python3 v22_remove_parts_asm.py <in.step> <out.step> "<prefix>" ...` |
| `render/render_load_step.py`, `render/render_views.py` | Quick VTK renders of the assembly (the docs use Onshape views instead): the first tessellates the STEP with its part names into `asm.pkl`, the second draws views at the home pose. Needs `vtk`. | `python3 render/render_load_step.py <assembly.step> asm.pkl` then `python3 render/render_views.py hero sideB_ports` |
| `render/make_render_step.py` | Writes a render-ready copy of the assembly for Onshape or other renderers: home pose (dovetail turned 180°), brass jaws and clearance envelopes removed, appearance colours set. | `python3 render/make_render_step.py <assembly.step> <out.step>` |
| `make_logo.py` | Writes the side plate B laser-marking SVG and the lid sticker SVG (needs matplotlib and the Liberation Sans font). | `python3 make_logo.py` |

## History (`history/`)

The one-off edits, in the order they were made (October–November 2026). They're kept as a record. **They won't run as-is:** most point at the old `restyle/v2.1` and `restyle/v2.2` folders and at intermediate files that no longer exist.

| Part | Scripts, in order |
|---|---|
| L-plate | `move_ra.py` (RA seat −6 mm) → `v22_parts.py` (board turned, corner cubes) → `v22_cw.py` (counterweight-ready) → `v22_lplate_csk.py` (clamp-hole countersinks) |
| Far wall | `farwall_relief.py`, `farwall_notch.py` (v2.1 panels) → `v22_cw.py` (counterweight lug and foot) |
| Base flange and plate | `v22_base_build_flange.py` → `v22_base_build_flange80.py` (80 × 80) → `v22_base_plate.py` (flat bottom, corner M5, base plate) → `v22_base_recess.py` (LA-40B recess) → `v22_flange_single_jack.py` (one input jack) → `v22_flange_one_bay.py` (jack and LED in one bay). Helpers and checks: `v22_base_lib.py`, `v22_base_ra.py`, `v22_base_regroup.py`, `v22_base_plate_checks.py` |
| Lid | `v22_gps.py` → `v22_gps2.py` → `v22_gps_remove.py` → `v22_gps_restore.py` (GPS pocket, final) ; `v22_lid_handle.py` (handle holes) ; `v22_swap_lid_asm.py` (superseded by `v22_swap_part_asm.py`) |
| Side plate A | `v22_usbc_window.py` → `v22_sideA_usbc.py` (USB-C window, rev 3, final) |
| Home marks | `v22_marks.py` → `v22_marks2.py` → `v22_marks3.py` → `v22_marks_fix.py` → `v22_marks_both.py` → `v22_unmark_sideB.py` → `v22_unmark_sideB_dec.py` (final: marks on side A only) ; `v22_merge_faces.py` (cleans seams after the edits) |

The v2.3 window-lid concept's scripts are in [`../../concepts/v2.3-window-lid/tools/`](../../concepts/v2.3-window-lid/tools/).
