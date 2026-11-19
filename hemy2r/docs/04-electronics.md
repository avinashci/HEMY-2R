# 4. Electronics and firmware

[← Power and wiring](03-power-and-wiring.md) · Next: [Assembly and setup →](05-assembly.md)

There are two tracks:

| Track | Boards | Status |
|---|---|---|
| **Build #1** | polvinc's **TeenAstro HEMY Redux v2.6.5M** main board and **HEMY Brake Driver 1.1**, with a few part substitutions | Upload-ready in [`pcb/jlc-order/`](../pcb/jlc-order/) |
| **Single board (experiment)** | Both boards merged into one, with the design review's protection fixes built in | Schematic in progress in [`pcb/single-board/`](../pcb/single-board/); **needs an electronics review before anyone orders it** |

## Build #1: polvinc's boards

**Main board** (4-layer): Teensy 4.0 MicroMod, 2 × TMC5160 SilentStepStick sockets (SPI), DPS1135 input protection, AP63205/AP63203 regulators (5 V / 3.3 V), FRAM, ATGM336H GPS with U.FL, LilyGO T-01C3 Wi-Fi header, ML1220 RTC cell, USB-C.

Changes from polvinc's BOM:
- **CN1 (3.5 mm jack) and DC1 left off.** Nothing then reaches into side plate A. The dovetail UART is soldered to CN1's pads (leave its +5 V pad open).
- **B1 must be an ML1220** (rechargeable). Never a CR1220: the board charges it.
- U13 and H1 not placed.

**Brake board** (2-layer): MT3608 boost to ≈ 23 V (replaces the out-of-stock SDB628; same pinout, 0.6 V feedback with 82k/2.2k) and a DRV103H (LCSC C1556557, the tube-packaged equivalent of DRV103H/2K5) that PWM-holds the 24 V SWB-003 brake coil.

- It plugs onto the main board's 2 × 2, 2.00 mm BRAKE header. **That header isn't keyed: mark pin 1 on both boards** ([E7](design-review.md#e7)).
- Add a **1 kΩ pull-up from M1_ENA to 3.3 V** at the header so the brake stays engaged while the Teensy boots ([E11](design-review.md#e11)).
- On first power-up, **measure ≈ 23 V at its output before connecting the brake.**

## Single-board experiment

Goal: one clean board for the cube, laid out with room to spare (polvinc's board had to be dense; this one doesn't), every off-board cable on a keyed plug, and the electrical fixes from the [design review](design-review.md) built in.

| Step | What | Status |
|---|---|---|
| 1 | Brake circuit added to the main schematic as its own page (MT3608, DRV103H), joined by net names; BRAKE header removed; E11 pull-up added; brake coil on a keyed JST-XH | **Done** |
| 2 | Input reverse-polarity + TVS + bulk capacitor (E3/E4), 2-channel isolator for the dovetail UART (E1/E2), 10 kΩ pull-downs on the driver CLK pins (E9), CN1 replaced by a keyed UART header | Next |
| 3 | Place parts on the full outline (82.5 × 57 mm + corner tab), connectors on the edges, nothing near the belts | |
| 4 | Route, DRC, review list | |

Open questions for a reviewer are listed in [reviewing.md](reviewing.md#electronics-questions).

### Brake page parts

| Ref | Part | LCSC | Role |
|---|---|---|---|
| U14 | MT3608 | C84817 | Boost 12 V → ≈ 23 V |
| L4 | 22 µH, 3 A (Chilisin BMRA00060630220MA1) | C2838326 | Boost inductor |
| D7 | SS34 | C8678 | Boost diode |
| R43 / R44 | 82k / 2.2k | C23254 / C4190 | Feedback: 0.6 × (1 + 82/2.2) ≈ 23.0 V |
| C85, C87 | 22 µF 35 V 0805 | C6119901 | Input / output |
| U15 | DRV103H | C1556557 | Coil PWM driver |
| R45 / R46 + C88 / C89 | 47k / 33k + 100 pF / 100 nF | | Oscillator, duty cycle, delay |
| D8 | ES3DB | C64975 | Coil flyback |
| J10 | JST XH 2-pin | C158012 | Brake coil |
| Q1, R47–R49 | MMBT3904, 3 × 4.7k | C20526, C23162 | M1_ENA → DRV103 input inverter |
| R50 | 1k | C21190 | M1_ENA pull-up (E11) |

**Logic:** M1_ENA high (RA driver disabled) → Q1 on → DRV103 input low → coil off → brake engaged. M1_ENA low (RA enabled) → coil on → brake released. R50 keeps M1_ENA high while the Teensy is in reset.

## Firmware settings

OnStepX, configured for polvinc's pin map. Check the exact `Config.h` names in your OnStepX version.

| Setting | Value | Why |
|---|---|---|
| Gear ratio | 100 × (70 / 20) = 350 per axis | Reducer × belt (20T motor pulley, 70T on the reducer) |
| IRUN | ≈ 400–500 mA | Tracking needs very little torque; ≈ 2.5 W per motor instead of ≈ 8.7 W in a sealed box ([E8](design-review.md#e8)) |
| IGOTO | 800–900 mA | |
| IHOLD | ≈ 300 mA | |
| Axis limits | RA and DEC ≈ ±120° | Cable twist through the bores ([M6](design-review.md#m6)) |
| Driver CLK pins (Mx_M4) | Driven low from boot | TMC5160 CLK must never float ([E9](design-review.md#e9)) |
| Serial1 (dovetail) | 9600–38400 baud | Noise margin on the long UART |
| GPS | On (Serial2), read at boot | Time and site |
| Home | Knobs-east pose ([assembly](05-assembly.md#home-position)) | |

Confirm no missed steps at the worst imbalance and on a cold night before trusting the lower currents.
