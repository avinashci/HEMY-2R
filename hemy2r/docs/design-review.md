# Design review

[← Back to README](../../README.md)

A structured review of the v2.2 design (November 2026), covering the CAD, polvinc's Redux v2.6.5M and Brake Driver 1.1 schematics, and the datasheets of the DPS1135, TMC5160 and 17HM15-0904S. It was done with AI assistance and has **not yet been checked by an independent engineer**. That's what [reviewing.md](reviewing.md) asks for.

## Status summary

| ID | Severity | Topic | Status |
|---|---|---|---|
| [E1](#e1) | Critical | Dovetail UART ground becomes a second power return | Open: isolator planned on the single board; inline module for build #1 |
| [E2](#e2) | High | Teensy back-powered through the UART | Open: same fix as E1 |
| [E3](#e3) | High | No reverse-polarity protection | Open: ideal diode planned |
| [E11](#e11) | Medium | Brake releases while the Teensy boots | **Fixed** on the single board (R50); pull-up at the header for build #1 |
| [M1](#m1) | High | Torque values assume dry threads | **Fixed**: lubricated torque table |
| [M2](#m2) | Medium | Reducer clamp-hole tolerances | Drawing notes |
| [M3](#m3) | Medium | Anodize on threads and fits | Drawing notes + thread inserts |
| [M4](#m4) | Medium | Water path onto the board | Partly: RTV on the GPS lead hole; no lid gasket yet |
| [M5](#m5) | Medium | RA balance vs 40–50″ backlash | **Procedure**: east-heavy offset |
| [M6](#m6) | Medium | Wire fatigue through the bores | Axis limits ±120°, liners, slack |
| [E4](#e4) | Medium | No transient suppression on 12 V | Open: TVS + bulk planned |
| [E5](#e5) | Medium | Fuse coordination | **Decided**: 10 A main, 5 A mount, 7.5 A ACC |
| [E6](#e6) | Medium | GPS patch in a metal pocket | Accepted: test time-to-first-fix with the lid on |
| [E7](#e7) | Medium | Connector durability and keying | Partly: CN1 off; BRAKE header gone on the single board |
| [E8](#e8) | Low–Med | Motor current mostly turns into heat | **Firmware**: lower IRUN/IHOLD |
| [M7](#m7) | Low | Thin sections in the base flange | Drawing notes |
| [M8](#m8) | Low | L-plate datums | Drawing notes |
| [M9](#m9) | Low | Galvanic couples (bronze/brass jaws) | Open: barrier or stainless jaws |
| [M10](#m10) | Low | Pinch point at the knobs | Procedure |
| [E9](#e9) | Low | TMC5160 CLK pin floats during reset | Open: firmware or 10 kΩ pull-downs |
| [E10](#e10) | Low | Grounding and EMI | Wiring practice |

---

## Electrical

<a id="e1"></a>
### E1 · Critical · The UART ground becomes a second power return

The telescope-side controller's USB ground is almost certainly tied to its 12 V negative. With the USB-serial module's GND wired to the board, the controller's return current has two paths: the 18 AWG ACC negative through two barrel contacts (≈ 40–60 mΩ), and the UART ground through the USB cable, the module and a 26–28 AWG core (≈ 250–300 mΩ). Normally 10–20 % takes the signal path; with a dirty or half-seated barrel plug, nearly all of it does. That can overheat the thin core or the module and damage the controller's USB port.

**Fix:** a 2-channel digital isolator (ISO7721 / ADuM1201 class, default-high output) on the body side. Board side powered from 3.3 V, far side from the module's I/O supply on the spare fourth core. It also does the 5 V → 3.3 V level shift. Insulate the USB-C shells from the aluminium, or the loop re-forms through the structure.

<a id="e2"></a>
### E2 · High · The Teensy gets back-powered

The ACC line is upstream of the lid switch, so the telescope controller is live whenever the base is plugged in. Its USB powers the module, whose TXD idles high and feeds the unpowered 3.3 V rail through the input protection. The rail sits half-powered and I/O pins go above their supply. **Fix:** the isolator from E1. Minimum fix: a 74LVC single-gate buffer powered from the board's 3.3 V.

<a id="e3"></a>
### E3 · High · No reverse-polarity protection

The DPS1135 blocks reverse current from output to input, but its input is only rated to −0.3 V: a reversed supply kills it, and the ACC output passes −12 V straight to the telescope. **Fix:** a 10–15 A ideal-diode (LM74700-class + FET) right after the main fuse, ahead of the split. Use polarized connectors inside the box.

<a id="e4"></a>
### E4 · Medium · No transient suppression on the 12 V bus

Hot-plugging over 1–2 m of cable can ring well above 12 V. The DPS1135 cuts off at ≈ 24.5 V (30 V absolute max); the ACC output has nothing. **Fix:** SMBJ15A / SMCJ15A TVS and 100–220 µF / 35 V after the ideal diode.

<a id="e5"></a>
### E5 · Medium · Fuse coordination

**Decided:** 10 A main, 5 A mount branch (the fuse protects the wiring; the DPS1135 protects the board), 7.5 A ACC sized for a cooled camera, accepting that a hard ACC short may also blow the main. Measure the real draw at commissioning; a fuse run above ≈ 75–80 % of its rating can blow without a fault.

<a id="e6"></a>
### E6 · Medium · GPS patch in a metal pocket

The 25 × 25 ceramic patch sits in a 25.5 mm aluminium pocket, close to the walls where its edges radiate, under a non-metallic sticker. Expect reduced gain. OnStepX only reads the GPS at boot, and a phone can supply the site instead. **Check:** time-to-first-fix with the lid fully assembled. Options if poor: open the pocket to ≈ 35 × 35 with a non-metal insert, or an active patch (the ATGM336H supplies antenna bias). A passive patch must read DC-open at the U.FL.

<a id="e7"></a>
### E7 · Medium · Connector durability and keying

- **BRAKE header** (2 × 2, 2.00 mm) also fits rotated; rotated 180° it puts 12 V on M1_ENA and 3.3 V on the brake board's ground. Mark pin 1 on both boards. Removed on the single board.
- **CN1** (3.5 mm jack) drags the plug tip across +5 V. Left off; the UART is soldered to its pads.
- **10 A jacks** screw into tapped M12 with no nut, so twisting the plug can unscrew them. Use plastic-safe threadlocker or an anti-rotation flat.
- **Dovetail USB-C** is on a small module's solder joints. The insert's window takes the plug's side loads in aluminium.

<a id="e8"></a>
### E8 · Low–Medium · Motor current mostly turns into heat

0.85 A on 6 Ω motors is ≈ 8.7 W per motor, 11–17 W inside a sealed box. Tracking needs only ≈ 0.03 N·m at the motor. **Fix:** IRUN ≈ 0.4–0.5 A, IGOTO 0.8–0.9 A, IHOLD ≈ 0.3 A, then confirm no missed steps.

<a id="e9"></a>
### E9 · Low · TMC5160 CLK pin

Driver pin 6 (CLK) is wired to Teensy GPIOs (net Mx_M4). Trinamic says CLK must never float; during Teensy reset it does. **Fix:** confirm OnStepX drives it low at boot, or add 10 kΩ pull-downs.

<a id="e10"></a>
### E10 · Low · Grounding and EMI

Return the ACC negative at the junction, never through the board. Twist motor phase pairs, the ACC pair, and TX/RX each with a ground. Pick a chassis strategy (insulated connector shells plus one 1 MΩ bleed from chassis to input negative). UART at 9600–38400 baud.

<a id="e11"></a>
### E11 · Medium · The brake releases while the Teensy boots

On polvinc's brake board, M1_ENA drives an NPN that pulls the DRV103 input low. While the Teensy is in reset, M1_ENA is pulled low by the base resistor, the NPN is off, the DRV103 input is high, and the coil is energised: **the brake releases before the firmware has configured RA.** **Fix:** 1 kΩ pull-up from M1_ENA to 3.3 V. During boot M1_ENA then sits at ≈ 2.8 V: Q1 on (brake engaged) and above the TMC5160's enable threshold (RA driver disabled). Done on the single board as R50. Confirm on the bench.

---

## Mechanical

<a id="m1"></a>
### M1 · High · Torque values assume dry threads

1.2 N·m (M3) and 2.85 N·m (M4) are dry values at μ ≈ 0.2. Anti-seize brings μ to ≈ 0.1, giving ≈ 80 % more clamp force: ≈ 2.1 kN on an A2-70 M3 whose safe limit is ≈ 1.8 kN. **Fixed:** the [lubricated torque table](02-mechanical-parts.md#torque-lubricated).

<a id="m2"></a>
### M2 · Medium · Reducer clamp holes

The frame's countersinks fix each screw's axis, so all the float comes from the reducer's Ø3.5 holes (≈ 0.25 mm radial). General tolerances could use that up. **Fix:** Ø3.2 holes positioned ±0.1 on the drawing. Switch to DIN 7984 low-head screws in counterbores only if a reducer's holes are > 0.15 mm off its CAD.

<a id="m3"></a>
### M3 · Medium · Anodize on threads and fits

Type II anodize takes ≈ 20–40 µm off a thread's pitch diameter. **Fix:** "dimensions and threads apply after finish; mask or chase threads" on every drawing; stainless wire-thread inserts in the dovetail M6 and the counterweight M12.

<a id="m4"></a>
### M4 · Medium · Water path onto the board

In use the lid faces the sky with the board under it. Dew can creep under the GPS sticker and drip through the lead hole. **Fix:** RTV or a grommet in the Ø4 hole; consider a thin closed-cell foam lid gasket and O-rings on the switch and SMA; a 1–2 mm skirt over the rotating gaps. Desiccant handles vapour, not water.

<a id="m5"></a>
### M5 · Medium · RA balance vs backlash

At ≈ 4.1″/px, 45″ of backlash is ≈ 11 px; perfectly balanced, wind can rock the scope inside it. **Fix:** ≈ 0.5 N·m east-heavy after bracketing ([balancing](05-assembly.md#balancing)). Load and unload only with the motors holding.

<a id="m6"></a>
### M6 · Medium · Wire fatigue through the bores

±180° of RA travel means up to 360° of twist, and the RA leads pass the wave generator, which spins ≈ 100× faster than the axis. **Fix:** ±120° limits in OnStepX, liners fixed to the non-rotating side, service slack.

<a id="m7"></a>
### M7 · Low · Thin sections in the base flange

The 1.5 mm floor and 1.9 mm jack-bay wall are in the only load path from RA to the base. Strength is fine; the risk is a machining breakthrough. **Fix:** mark them as minimum walls.

<a id="m8"></a>
### M8 · Low · L-plate datums

The reducers sit in clearance bores; the seating faces set each axis's direction. Two setups can leave the faces 0.05–0.1 mm per 100 mm off square (≈ 2–3′, harmless with plate solving). **Fix:** flatness and perpendicularity on the seating faces, one datum for both pockets; an R3–R5 inside fillet if it clears the reducers.

<a id="m9"></a>
### M9 · Low · Galvanic couples

Bronze or brass jaws sliding on aluminium are a worse pairing than stainless screws once the anodize is scratched. **Fix:** a barrier (Tef-Gel or a thin PTFE shim) on an anodized seat, or 303 stainless / hard-anodized jaws.

<a id="m10"></a>
### M10 · Low · Pinch point at the knobs

The knobs pass 7 mm from the body as DEC turns, under 31 N·m of drive. Keep hands clear during slews.

## Checked and fine

Thermal expansion (≈ 0.02 mm over 80 mm for 25 °C); no 3D-printed parts in the load path; base screw margins; USB-C CC pull-downs; separate UARTs (Serial1 remote, Serial2 GPS, Serial4 Wi-Fi); FRAM pull-ups; ML1220 charge path; brake boost 0.6 × (1 + 82/2.2) ≈ 23.0 V; DRV103 at 100 kHz / 50 %. The 3.3 V and 5 V rails are limited to ≈ 0.6 A continuous by their inductors: fine as built, but don't add loads.
