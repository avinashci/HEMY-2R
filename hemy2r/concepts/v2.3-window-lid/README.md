# HEMY 2R v2.3 concept: window lid with polvinc's boards (rev 3, 2026-11-16)

Concept only, not part of the build. The v2.2 design is in [`../../cad/`](../../cad/). The full concept assembly (95 MB) is attached to the GitHub Releases instead of git.

**Decision (2026-11-16):** v2.3 keeps the **window lid** but uses **polvinc's proven main board and brake board, unmodified**. The brake board moves from stacked on the main board to beside it. The custom single-board idea is parked (see the end of this file).

## What changes from v2.2
- **Lid:** same flat 6 mm plate, cube silhouette kept.
  - **Deep-red polycarbonate window:** 3 mm pane in a 33 × 39 × 3 mm rebate (X 6…39, Y −46…−7, R4), with a 3 mm ledge (opening 27 × 33). It shows the Teensy and the RA driver.
  - The window stays clear of the MX1 standoff (3 mm web) and of the corner screw (3 mm).
  - Old handle, switch, SMA and spacer holes filled.
- **Handle:** moved to X −30 (M5 countersunk from below). Rough CG estimate without the counterweight: X ≈ −23, so it carries more level than X −11.
- **Switch:** TechEss 16 mm at (37, 28). Clearances: frame 5.6 mm, DEC side 3.1 mm, far wall 2.0 mm.
- **Wi-Fi SMA antenna:** removed. The antenna goes inside, under the window.
- **Main board (polvinc Redux v2.6.5M, unchanged files):** flipped **components-up**.
  - PCB at Z 99.5–101.1; parts up to Z 117.35, which is 1.65 mm under the lid (**from polvinc's model: measure the real drivers and Teensy stack**).
  - Underside (B1, pins) down to Z 95.2, about 3 mm above the RA drive.
  - CN1 and DC1 not fitted.
  - **3 supports** (the same pattern as v2.2):
    - 2 × M3 FF ~18 mm standoffs at polvinc's 3.2 mm holes, box (−21, −3) and (25, −3)
    - 1 × M2.5 FF ~14 mm standoff from the lid down onto the **MicroMod screw post MX1** at (0.5, −29). It replaces the MicroMod screw and clamps the card. Check the thread on the real part; MicroMod normally uses M2.5.
  - Board edge to side plate A: 0.5 mm.
- **Brake board (polvinc Brake Driver 1.1, unchanged files):**
  - Beside the main board, side A half: X −50…−27, Y −54.5…−37. That's 1.0 mm to the DEC-end corner cube, 2.0 mm to side plate A, ~4 mm to the main board, under the solid lid and outside the window.
  - **Components down, back face on 2.5 mm VHB foam tape** on the lid. No screw, because its edge notch lands on the corner cube.
  - **P1 not fitted** (no stacking): solder a standard **2×2, 2.0 mm through-hole pin header** into P1's four Ø0.85 holes, and use a short **4-wire 2.0 mm female–female jumper** to the main board's BRAKE header (VIN, GND, 3.3 V, M1_ENA). **Mark pin 1 on both ends.**
  - P3 (brake leads) unchanged.
- **Side plate A:** USB-C window moved to the flipped CN2 at **X 22, Z 102.5**, fully inside the recess. The old window and tab are filled; this is a rough fill, to be redone properly if adopted.

## Files
- `HEMY2R v2.3 concept - window lid.step`: the full assembly (from v2.2 asm17). Swapped parts are renamed "… v2.3 CONCEPT"; the brake board, window and foam are in the ELECTRONICS group.
- `parts/`: lid, side plate A and window STEP files.
- `docs/`:
  - `v23_lid_old_vs_new.jpg`: old vs new, from side A, side B, top, and a section at Y −28
  - `open_top.jpg`: lid off, from the top
  - `new_*.jpg`: the other views
- `tools/`: `v23_window_lid_concept.py`, `v23_make_asm.py` (need the v2.2 parts exported as p*.brep from asm17 and the brake board 3D STEP), `eda_refill_and_drc_mainboard.js`.

## Open
- **Measure the real parts** (calipers): TMC5160 SilentStepStick height with heatsink and headers, and the MicroMod card stack. The lid gap is 1.65 mm on paper.
- Window retention (VHB or small clips), gasket, inside fogging. Unfitted LED1/LED2 and any LEDs on the Teensy or driver modules show through the red window.
- USB-C alignment through the stack (lid screws → standoffs → board): consider making the side A window 1 mm larger.
- A human electronics review is wanted before any **custom** board. None is needed for this concept: both boards are polvinc's.

## Parked: custom single board (EasyEDA project "HEMY 2R board")
On 2026-11-16 the main board outline in the EasyEDA copy was extended (82.5 × 57 + corner tab, 4 extra holes, GND pours extended and rebuilt, DRC 0). It's kept there as an experiment for a later revision; nothing in the JLC cart depends on it. The pre-edit checkpoint is `uhwet3tfcm85jcsx`; polvinc's original stays in the `.epro`, the HEMY 2.0 project and the `.eprj2` backup.
