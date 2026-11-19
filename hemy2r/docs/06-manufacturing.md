# 6. Manufacturing

[← Assembly and setup](05-assembly.md) · Back to [README](../../README.md)

## CNC (JLCCNC)

Upload the STEP files from [`cad/parts/`](../cad/parts/) (JLCCNC takes 10 files per upload, so split into two). Set quantities by hand: most parts are ×1; pulleys, brake supports, motor supports and dovetail clamps are ×2 (the quantity is in the file name).

| Setting | Value |
|---|---|
| Material | Aluminium 6061 |
| Finish | Bead blast + anodize, natural (clear); **dovetail insert: red** |
| Edges | Break all sharp edges 0.3 mm |
| Threads | Tapped by the shop (callouts below) |
| Laser marking | Side plate B: logo (`cad/logo/HEMY_2R_sideplate_logo_LASER_70mm.svg`). Side plate A: owner badge (your own artwork). Both centred in the 93 × 93 recess. |

For reference, the full housing set quoted at about US $580 at JLCCNC in November 2026, before shipping and duty.

### Notes for the drawings

These come from the [design review](design-review.md) (M2, M3, M7, M8). Put them on every drawing or in the order remark:

- **"Dimensions and threads apply after finish. Mask or chase all threads after anodizing."** Type II anodize takes ≈ 20–40 µm off a thread's pitch diameter, and stainless screws gall in tight threads.
- **Thread inserts** (stainless wire-thread) in threads used every session: the dovetail's M6 clamp threads and the far wall's M12.
- **L-plate:** precision on the reducer seating faces, not the bores. Each pocket floor flat to 0.02; DEC seating face ⟂ RA seating face to 0.05; both pockets dimensioned from one datum. Bores Ø80.5 / Ø65 at ±0.1 (they are clearance; the reducers are located by their faces and screws).
- **L-plate clamp holes:** Ø3.2 (ISO 273 fine), positioned ±0.1 to the pocket.
- **Base flange:** the 1.5 mm floor under the reducer pocket and the 1.9 mm jack-bay wall are **minimum** walls.

### Thread callouts

| Part | Threads |
|---|---|
| Lid | 3 × M3 board spacers |
| Far wall | M12 × 1.75 through lug and wall; 3 × M5 × 8 deep in the foot |
| Base flange | M12 (jack, confirm pitch); 4 × M5 × 12 deep; 12 × M3 clearance + counterbore |
| Base plate | 4 × M6 countersinks; 4 × Ø5.5 + Ø9 counterbores |
| Dovetail | polvinc's drawing `09_Dovetail_threads_drawing.pdf` + M12 jack, 2 × M2.5 cover |
| Dovetail insert | 2 × M2 |
| Corner cubes (bought) | M4 |

## PCBs (JLCPCB)

Build #1 uses polvinc's boards. Upload-ready files, settings and the assembly remark are in [`pcb/jlc-order/README.md`](../pcb/jlc-order/README.md):

| Board | Layers | Files |
|---|---|---|
| TeenAstro HEMY Redux v2.6.5M | 4 | Gerber, BOM (JLC format), pick-and-place |
| HEMY Brake Driver 1.1 | 2 | Gerber, BOM, pick-and-place |

Order both boards and the CNC parts together where you can; shipping and import duty are a large share of the cost.

The single-board experiment is **not ready to order**.

## Stickers

`cad/logo/HEMY_2R_GPS_sticker_PRINT.svg`: printed die-cut vinyl with outdoor laminate, 40 × 32 mm, over the lid's GPS pocket. It must be non-metallic.
