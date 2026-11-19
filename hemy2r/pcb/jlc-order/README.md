# JLCPCB order: polvinc's boards for build #1

Upload-ready copies of polvinc's files for the two boards HEMY 2R uses. The originals are in [`hardware/pcb/v2.0/gerbers/`](../../../hardware/pcb/v2.0/gerbers/). The base-flange and dovetail adapter boards (PCB5_1, PCB5_2) aren't needed for HEMY 2R.

## Main board: TeenAstro HEMY Redux v2.6.5M (`main-board/`)

| JLC step | File |
|---|---|
| PCB (Gerber) | `Gerber_HEMY_Redux_v2.6.5M_2025-06-23.zip` (4-layer) |
| Assembly BOM | `BOM_HEMY_2.6.5M_JLC.csv` (through-hole parts included) |
| Pick and place | `PickAndPlace_HEMY Redux v2.6.5M_2025-06-23.xlsx` |

**Settings:** 5 boards, assemble 2, top side, Standard PCBA. U13 and H1 not placed; B1 not placed (fit an ML1220 by hand).

**HEMY 2R changes:** CN1 (3.5 mm jack) and DC1 not fitted (remove from the BOM).

**Assembly remark** (PCB Assembly → Advanced Options → Assembly remark):

> RA_TMC and DEC_TMC: each footprint takes two 1×8 female headers (C5224027), one on each 8-pin row (DIR…EN and GND…VMOT), long axis horizontal. PS1: 1×3 2.54 mm male header in the PS1 footprint holes. IN1: 1×2 male header in the IN1 holes. The preview positions of these through-hole parts are offset; please place them by the footprint holes. U13, H1 and B1: do not place.

When JLC sends the placement confirmation, check the TMC headers (two per driver, horizontal), PS1 and IN1 before approving.

**After it arrives:** B1 is an **ML1220 only** (rechargeable; the board charges it), never a CR1220. The power switch's latched contact pair goes to the PS1 pads (VIN and EN).

## Brake driver 1.1 (`brake-driver-1.1/`)

| JLC step | File |
|---|---|
| PCB (Gerber) | `Gerber_HEMY_Brake_Driver_1.1_2025-04-23.zip` (2-layer) |
| Assembly BOM | `BOM_HEMY Brake Driver 1.1_HEMY Brake Driver 1.1_2025-04-23.xlsx` |
| Pick and place | `PickAndPlace_HEMY Brake Driver 1.1_2025-04-23.xlsx` |

It boosts 12 V to ≈ 23 V and PWM-holds the coil of a **24 V SWB-003** brake. It plugs onto the main board's BRAKE header.

**Part substitutions** (polvinc's parts were out of stock in November 2026):

| Ref | polvinc | Use instead | Notes |
|---|---|---|---|
| U1 | SDB628 (C77805) | **MT3608** (C84817) | Same pinout (1 SW, 2 GND, 3 FB, 4 EN, 5 IN, 6 NC), 0.6 V feedback. Not the MT3608L. |
| U2 | DRV103H/2K5 (C544418) | **DRV103H** (C1556557) | Same chip, tube packaging. Pre-order through JLC's parts library if not in stock. |
| P1 | Würth 62100421821 | same (C6699496) | 2 × 2, 2.00 mm female socket; often needs pre-ordering |

**Assembly remark:** "FAULT: do not place (bottom-side test point). P3: 2-pin through-hole terminal in the P3 holes. P1: 2×2 2.00 mm female socket (Würth 62100421821) in the P1 footprint."

**Before use:**
- Mark pin 1 on both boards: the 2 × 2 header also fits rotated ([E7](../../docs/design-review.md#e7)).
- Add a 1 kΩ pull-up from M1_ENA to 3.3 V ([E11](../../docs/design-review.md#e11)).
- First power-up: measure ≈ 23 V at the output before connecting the brake.
