# JLCPCB order: HEMY main board + brake driver (one shipment)

Two boards in one JLC order to share shipping. Base-flange (PCB5_1) and dovetail (PCB5_2) boards skipped.
Copies of the repo files; the originals stay in `hardware/pcb/v2.0/gerbers/`.

# Main board (TeenAstro HEMY Redux v2.6.5M), folder `main-board/`

## What to upload
| JLC step | File |
|---|---|
| PCB (Gerber) | `Gerber_HEMY_Redux_v2.6.5M_2025-06-23.zip` (4-layer) |
| PCB Assembly: BOM | `BOM_HEMY_2.6.5M_JLC.csv` (complete, through-hole parts included) |
| PCB Assembly: CPL | `PickAndPlace_HEMY Redux v2.6.5M_2025-06-23.xlsx` |

`main-board/reference/`: the original BOM from the repo and the schematic (for the PS1 pads and wiring).

## Settings (quoted 2026-11-05: $148.21 before shipping)
- 5 boards, assemble 2, top side, Standard PCBA.
- U9 AP63203WU-7: select it from My Inventory (pre-bought batch COB202611060936163) once the transfer completes.
- RA_TMC / DEC_TMC: the second 1×8 female header per footprint comes from the extra headers in My Inventory.
- Leave out U13 and H1. B1 not placed.

## Remark to paste
Where: PCB Assembly, Advanced Options, **Assembly remark: Yes**, then paste into the text box.

> RA_TMC and DEC_TMC: each footprint takes two 1×8 female headers (C5224027), one on each 8-pin row (DIR…EN and GND…VMOT), long axis horizontal; the second header comes from my inventory. PS1: 1×3 2.54 mm male header in the PS1 footprint holes (top right). IN1: 1×2 male header in the IN1 holes. The preview positions of these through-hole parts are offset; please place them by the footprint holes. U13, H1 and B1: do not place.

When JLC sends the placement confirmation, check the TMC headers (two per driver, horizontal), PS1 and IN1 before approving.

## After it arrives
- Coin cell B1: **ML1220 (rechargeable) only**, never CR1220; the board charges it.
- TMC5160 SilentStepSticks: no heatsinks needed at 0.8–0.9 A.
- Power switch: the TechEss pair that closes when latched goes to the PS1 pads (VIN and EN).

# Brake driver 1.1, folder `brake-driver-1.1/`

| JLC step | File |
|---|---|
| PCB (Gerber) | `Gerber_HEMY_Brake_Driver_1.1_2025-04-23.zip` (2-layer) |
| PCB Assembly: BOM | `BOM_HEMY Brake Driver 1.1_HEMY Brake Driver 1.1_2025-04-23.xlsx` |
| PCB Assembly: CPL | `PickAndPlace_HEMY Brake Driver 1.1_2025-04-23.xlsx` |

`brake-driver-1.1/reference/`: schematic.

What it does: boosts 12 V to about 23 V (SDB628, R1 82k / R2 2.2k), then the DRV103 PWM-holds the coil. **The brake must be the 24 V SWB-003.** It plugs onto the main board's BRAKE header (P1) and sits on the lid side of the main board.

## Part changes and checks before ordering
- U1: keep SDB628 (C77805) if in stock, else **MSDB628** (C30197563). Pinout checked identical (1 SW, 2 GND, 3 FB, 4 EN, 5 VIN, 6 NC). Feedback assumed 0.6 V like all B628 parts: **on first power-up measure the boost output (≈23 V) before plugging in the brake.**
- U2: not in JLC stock. Pre-ordered DRV103H/2K5 (C544418) ×2 with P1, order COB202611071614372 (2026-11-07; supplement paid 2026-11-10). **2026-11-11: JLC cancelled the C544418 line (out of stock at their suppliers); refund due. P1 (Würth 62100421821 ×7) is unaffected.**
  - **Replacement (preferred): DRV103H, plain tube packaging, LCSC C1556557** — the same chip, same SO-8 PowerPAD package; /2K5 only means a 2,500-piece reel. LCSC showed ~900 in stock (~$4.00) on 2026-11-11. Pre-order it ×2 through JLC's parts library, then change U2's LCSC number in the BOM from C544418 to C1556557 so the PCBA order picks it from My Inventory.
  - Backup: DRV103U (C1556551), plain SOIC-8, 1.5 A version without the exposed pad. Fits the same land pattern (pad left unsoldered); the brake only draws ~60 mA. Confirm the pinout in the TI datasheet before using it.
- P1 Würth 62100421821 (C6699496, 2×2, 2 mm, SMD female socket to the main board's BRAKE header): **pre-ordered ×7** in the same order.
- P3 MX128 2-pin terminal (brake leads): through-hole, add in the part picker.
- **Do not place "FAULT"** (bottom-side test pad), so the board stays single-side assembly.
- Quote it with 5 boards, assemble 2, as for the main board. Rough estimate about $60.
- Assembly remark: "FAULT: do not place (bottom-side test point). P3: 2-pin through-hole terminal in the P3 holes. P1: 2×2 2.00 mm female socket (Würth 62100421821) in the P1 footprint."
- Main board waits in the cart; check out both together once the pre-ordered parts are in inventory.

## Coupons
Claim on checkout day (most run 30 days from claiming): JLCONE PCBA $20 (over $100), JLCONE 4-layer $5, PCBA $9/$6 (expire Nov 29), EasyEDA $10s (expire Dec 5).
