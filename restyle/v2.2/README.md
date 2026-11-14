# HEMY 2R (HEMY v2 restyle): v2.2

Based on [HEMY](https://github.com/polvinc/HEMY) by polvinc, GPL-3.0.

Current design (cleaned up 2026-11-13). A HEMY v2 harmonic mount in a 125 mm cube shell with a SAL-33-style exterior: one-piece L-plate frame, 6 mm panels, M4 corner cubes, a lid handle and a counterweight far wall. Internals (HBK17 100:1 reducers, motors, pulleys, belts, board) are stock HEMY v2; only the shell, frame, base, dovetail hardware and a few positions change.

**Waiting on parts:** the LA-40B (base plate recess, screws, round vs square flange) and HBK17 reducer #1 (dovetail screw re-layout, dovetail bay, internal wiring layout). Section 10 lists what to do when each arrives.

## Contents
1. Folders
2. Parts to machine
3. Design decisions
4. Power and data
5. Counterweight far wall
6. Home-position index marks
7. Hardware (screws, bought parts)
8. Build and assembly notes
9. Checks done
10. Open items and to-do
11. Credits

## 1. Folders
| Folder | Contents |
|---|---|
| `parts/` | Everything to machine (section 2), plus `stock_hemy_parts/`. |
| `assemblies/` | **`HEMY2R v2.2 - assembly.step`**: chosen panels only (recessed side plates A and B, recessed counterweight far wall); counterweight bar + weight; **BASE flange**, **BASE plate** and **PLACEHOLDER LA-40B top plate** as their own groups; **DOVETAIL group** (plate; jaws **OPTION A BRONZE** and **OPTION B BRASS**, same solids, hide one; knurled knobs; polvinc's stock DC/USB/PCB + bay cover, to be replaced); **ELECTRONICS + accessories** group (board, spacers, switch, antenna, handle). |
| `tools/` | The OCP scripts that made the edits (`cadquery-ocp`). Records only. Older scripts point at v2.1 paths. |
| `logo/` | Side plate B HEMY 2R logo for laser marking (`HEMY_2R_sideplate_logo_LASER_70mm.svg`); side plate A owner badge (`Avinash_badge_LASER_70mm_600dpi.png`); GPS sticker print file (`HEMY_2R_GPS_sticker_PRINT.svg`); previews and older vinyl layers. |
| `reference/` | Not machined: LA-40B placeholder plate (assumed 60 × 60 × 10; replace with the measured plate), LA-40B interface drawing and front view, EM31Pro reference. |
| `docs/` | Base views and concept, dovetail brass-jaw concept render (reference only), serial-link diagram, v2.1-era render. |
| `_archive/` | Not in git. Flat panels, plain far walls, the old all-variants assembly, the skipped dovetail accessories. Older CAD also in `restyle/_snapshots/`. |

## 2. Parts to machine (`parts/`)
| Part | Qty | Notes |
|---|---|---|
| **HEMY2R - L-plate v2.2** | 1 | One piece (floor + back wall). RA reducer seat moved 6 mm toward the back wall (RA axis at X −6). 90° countersinks Ø6.3 on the outside of both reducer bolt circles (10 holes each; RA skips 180°/270°, DEC skips 0°/270°, as stock). 3 × M5 countersunk under the floor for the counterweight wall's foot. |
| Side plate A, recessed | 1 | Inner connector relief 38 × 16.1 mm, 3.8 deep, R1.5 (the board edge faces this side); 1.4 mm web behind it. M4 at all corners. Laser-marked owner badge in the recess. **Gets the RA and DEC home marks** (section 6) and possibly the backup USB-C port (section 4). |
| Side plate B, recessed | 1 | M4 at all corners. Laser-marked HEMY 2R logo. (Its current home-mark grooves are to be removed, section 6.) |
| Far wall CW, recessed | 1 | Counterweight far wall, the only far wall (section 5). |
| Lid | 1 | M4 corners; board-spacer M3 threads at (32, −3), (−14, −3), (10.5, −29); TechEss switch Ø16.2 at (37.5, 18); Wi-Fi SMA at (37.5, 38); handle holes (M5) at (−12.5, ±44); GPS window at the back-centre (section 3). |
| Dovetail (indicator LED hole) | 1 | + `09_Dovetail_threads_drawing.pdf`. polvinc's saddle (dual Vixen + Losmandy) and clamp mechanism kept. Electronics bay on side A to rework for the CH340E + 10 A ACC jack (section 4). Keep polvinc's 8 × M5 holes on the side A face (spare). Screw holes to re-lay on the real reducer (section 10). |
| Dovetail jaws (polvinc's geometry) | 2 | **Bronze or brass**: quote both at JLCCNC, bronze if only a few dollars more (harder, less galling); check JLCCNC offers a bronze grade. Delete the other option from the assembly once chosen. |
| Dovetail bay cover (new) | 1 | To design: replaces polvinc's 31.6 × 25 × 5 mm cover on the body side of the dovetail, same 2 × M3, carries the CH340E (section 4). |
| 07 Pulley 70T | 2 | Unchanged. |
| 08 Brake support | 2 | Unchanged; fitted from day one (section 8). |
| stock_hemy_parts 10 Motor support | 2 | Unchanged. |
| stock_hemy_parts 11 Dovetail fix clamp | 2 | Unchanged. |
| stock_hemy_parts 13 SWB-003 shaft coupling | 1 | **Needed**: the 5 × 40 brake shaft has a 4.5 mm flat (hardened, not filed); the brake's own coupling needs 4.0. |
| **HEMY2R - Base flange v2.2 80x80** | 1 | 80 × 80 × 19 mm, ~241 g, flat bottom; replaces the A11 flange and the Vixen saddle. Bolts to the RA reducer output with A11's 12 × M3. 4 × M5 × 12 deep (Ø4.2 × 14 drill) at the corners. **CAD still has 2 jacks + 2 LEDs; redo for the single input** (1 jack + 1 LED) and decide round vs square when the LA-40B arrives. |
| **HEMY2R - Base plate v2.2 80x80 (LA-40B recess ASSUMED)** | 1 | 80 × 80 × 11 mm, ~150 g. 4 × countersunk M6 down into the LA-40B's corner threads; the flange bolts to it with 4 × M5 from below at the corners. Recess waits for the measured LA-40B plate. |

Finish: bead blast + regular anodize, natural/silver, matte. Order note: **break all sharp edges 0.3 mm**.

## 3. Design decisions
- **125 mm cube, one-piece L-plate.** RA reducer moved 6 mm toward the back wall: shorter payload arm, more room behind the RA motor, RA axis almost centred under the cube. Reducers stay half-embedded as in polvinc's design (fully-outside reducers are a v3 idea).
- **Board turned 90°** so its edge connectors face side plate A; it sits under the lid at X −17…35. Board spacers move with it.
- **12 mm M4 cubes in all 8 corners**, so every panel and lid screw is M4. Cubes are cheap and sacrificial and keep the panels plain 6 mm plates.
- **Handle kept** (clears the board by 5.2 mm).
- **GPS window in the lid** at the back-centre (X −40, Y 0): pocket **25.5 × 25.5 × 5 mm (R1)** with a Ø4 lead hole. A **25 × 25 × 4 passive ceramic GPS patch** (U.FL to the board's JP1) on a **1 mm foam pad** sits flush under the **"HEMY 2R" sticker** (gear version, credit line "based on HEMY by polvinc", 40 × 32 mm, R3, red #D62A2A with white artwork; printed die-cut vinyl with laminate, **non-metallic**), long side along the handle, overlapping the pocket 3.25 mm on the sides and 7.25 mm on the ends to seal out dew.
- **Base: flange + base plate on the LA-40B** (modelled 2026-11-11). Stack top to bottom: **flange 80 × 80 × 19** (Z −27.5…−8.5) → **base plate 80 × 80 × 11** (Z −38.5…−27.5), 0.5 mm chamfers meeting in a fine V split line → LA-40B top plate in the plate's recess.
  - **Flange:** reducer interface copied from A11 (12 × M3 at Ø54, counterbored from below; empty positions at 0/90/180/270° match the reducer's four larger features). Flat bottom; 4 × M5 corner threads at (±33, ±33) from the RA axis.
  - **Base plate:** 3 mm recess underneath for the LA-40B plate (**assumed** 60 × 60 R4.1; the real one is smaller, maybe ~54 × 50); 4 × countersunk M6 into the LA-40B's corner threads (±19, ±19); 4 × M5 clearance holes with Ø9 × 5.5 counterbores from below at the corners, outside the LA-40B plate.
  - **Order:** plate onto the LA-40B (M6 from above) → flange onto the reducer on the bench (12 × M3 from below) → mount onto the plate, 4 × M5 up from below.
  - **4 × M5 corners are enough:** ≈20 kN clamp vs ≈0.2 kN tipping pull; friction ≈150–200 N·m vs a few tens of N·m RA reaction. Mid-edge extras only fit if the LA-40B plate is ≤ ~54 mm (counterbores otherwise break into the recess).
  - **Round Ø84 neck vs square 80 × 80: decide with the real LA-40B plate.** With a single jack the jack face fits a Ø84 flat; the plate screws would move to r ≈ 36 and their counterbores must clear the LA-40B plate (works if it's smaller than ~60 mm where the screws sit).
  - **Jack bay and slot** (machined from the flat bottom, closed by the base plate): keep the slot narrow; the solid around it ribs the 1.5 mm floor under the reducer pocket (don't merge or widen). Consider a shallower slot to thicken that floor. Leads go up the reducer's **Ø19 H7 through-bore**.
- **Dovetail:** polvinc's saddle and clamp kept (dual Vixen + Losmandy). His M6 clamp screw passes through the jaw, crosses under the groove and threads into the saddle body (Ø5.2 tap drill, Y 25.5 → 6; ≈14.5 mm engagement); tightening pulls the knob face against the jaw. Changes: jaws in bronze or brass, knurled D20 knobs (section 7). **Knob head must stay ≤ Ø32**: the knob axis is 17.3 mm from the body face's plane as DEC turns.
- **Knobs east via the DEC home pose, no dovetail change** (2026-11-11). The saddle is symmetric along its groove, so the knob side at home is set by the DEC position. Turned 180° in DEC from the CAD pose, the knobs face east (right for a right-hander loading from the south, as in polvinc's photo) and the dovetail's CH340/ACC face points west. At assembly, route the DEC wires untwisted in this pose and set it as home in OnStepX.
- **No TMC5160 driver heatsinks** (not needed at 0.8–0.9 A).
- **Weight:** about 4.6 kg without the base, ~5.8 kg with the LA-40B, flange and plate.
- **RA load budget:** HBK17 100:1 rated 31 N·m (max average 51, start/stop peak 70, momentary 143; listed backlash ≤ 10″, but the seller says real backlash is ~40–50″: negligible in RA, handle DEC with PHD2 one-direction DEC guiding or backlash compensation and a slight DEC imbalance). Output M3 threads are 6 mm deep: check screw engagement. Dovetail face ≈ 0.10 m from the RA axis. FRA300 rig ≈ 4.5–5.5 kg with its balance point ≈ 0.07 m above the dovetail → ≈ 7.5–9 N·m without a counterweight (≈ 25–30% of rated). Same class as the Proxisky Ragdoll 17 Pro (< 40 N·m).

## 4. Power and data
- **Single 12 V input at the base** (decided 2026-11-13; like polvinc's original): one 10 A 5.5 × 2.1 panel jack + one dim red LED on the flange (side B face). Inside the box: **10 A main fuse** → junction → **~3 A fuse → mount board** and **~8 A fuse → ACC line** (18 AWG) up the DEC bore → **dovetail 10 A ACC jack** → StellaVita. A scope-side short blows only the ACC fuse. Typical draw ≈ 5–7 A, worst case ≈ 10 A. Field kit: one 10 A cable from the Jackery (check its plug rating; cheap 5.5 × 2.1 plugs are often 5 A). No DC splitter cables.
- **Jack:** 10 A 5.5 × 2.1 panel socket, M12 thread 9 mm + body 9 mm, Ø14 bezel, 18 AWG leads, tethered cap; screwed into a tapped M12 hole (no nut). Confirm the M12 pitch on the real jack.
- **Dovetail USB-C (main control link):** CH340E module **"BTE17-06"** (16 × 16 mm, 4 holes on 9.5 × 13 mm, likely M2; **Type-C variant**) on the new bay cover, USB-C edge at the side A opening; tethered silicone dust plug; right-angle cable at the saddle. Only **UART** crosses DEC (TXD, RXD, GND), not USB data, so thin twisting wires are fine. Solder wires straight to the pads; use **TXD, RXD, GND only** (don't connect +5V or 3V3; DTR open). Needs its own hardware serial port on the board, separate from the Wi-Fi module's.
- **Logic level:** the module has no 3.3/5 V jumper and is likely 5 V TTL; the Teensy 4.0 is 3.3 V only. Bench check (section 8); if TXD idles at ~5 V, add **1 kΩ in series + 2 kΩ to GND** on module TXD → board RX.
- **Backup USB-C (option B):** a short panel-mount USB-C extension from the board's own (Teensy) USB-C to a capped port on the body (side plate A's lower edge or near the base; place it in the wiring layout). Full control port (NINA/PHD2/ASCOM/INDI) and the firmware port; never passes through DEC. OnStepX accepts several ports at once; don't run two control programs together. Try it once at home so the PC knows it.
- **Dovetail bay depth (open):** the bay is ~12.6 mm deep and polvinc's 5 mm cover leaves ~7.5 mm, so the 10 A jack's Ø12 body doesn't fit as is. Options: pocket in the cover over the jack, thinner cover there, or deeper bay.
- **Wireless:** LilyGO T-01C3 Wi-Fi as a second link.

## 5. Counterweight far wall
The only far wall (decided 2026-11-11).
- **Socket:** SAL-33-style lug outside, 32 × 24 mm, R4, 12 mm proud, on the DEC axis (Y 0, Z 70). **M12 × 1.75** through lug and wall (~18 mm of thread), tapped by JLCCNC. **M12 cap** with thread ≤ 12 mm for when the bar is off (longer pokes into the box).
- **Load path:** foot inside along the bottom edge (X 40–50.5, Y ±40, Z 9–19), held by **3 × M5 countersunk screws up through the floor** (X 45, Y −28 / 0 / +28) into M5 threads (8 deep), plus the 4 M4 corners.
- **Bar and weight:** Angeleyes stainless bar Ø20 × 164 mm (M12; confirm the thread) and the 5 kg weight; bar-end stop already owned. With a 5.5 kg rig the weight balances about **mid-bar**. The weight can't hit the mount anywhere on the bar; check tripod-leg clearance at home and through the meridian.
- **Balance:** no clutch (not needed on a strain-wave mount; rough balance within ~1 N·m is enough). Unpowered, the reducer and motor detent resist, so **bracket it**: slide the weight in until the scope side drifts down, out until the counterweight side drifts down, mark the midpoint on the bar. Belt off makes it more precise. Never plug or unplug a stepper with the driver powered.
- **Without the brake:** with too little counterweight (e.g. 1–1.5 kg, ~6 N·m scope-heavy) a power loss can let the scope swing down. Balance properly, or fit the brake (check its position: on the motor side it gives ~20 N·m at RA, on the reducer input only ~6).
- **Build options (decide on cost):** one piece from a ~29 mm block, or three parts (6 mm plate + bolt-on lug + foot bar, v1.1 C10 style).

## 6. Home-position index marks (move to side A)
90° V-grooves, 0.3 mm deep, 8 mm long. Fill with white engraving crayon or paint pen.
- **Home** = counterweight down, scope parallel to the RA axis, knobs east (section 3).
- **DEC:** the dovetail's existing mark (between the knobs) faces east at home, so its partner goes on **side plate A**, horizontal at Z 70, running 8 mm in from the back edge.
- **RA:** **side plate A's** bottom border, vertical at X −6, plus a partner on the **base flange's side A face**.
- **To remove:** the current side B grooves on the flange and side plate B. Do it with the reducer/LA-40B updates.

## 7. Hardware (screws, bought parts)
Flat-heads to match the 90° countersinks: **ISO 14581 Torx, stainless A2-70**, no threadlocker on panels, a little anti-seize into aluminium. Stainless rather than titanium (Gr5 titanium only for a few visible accents if wanted).
| Where | Part | Qty |
|---|---|---|
| Reducer clamps, RA + DEC (hex nuts inside) | M3 × 30 (T10), QCTI 50-pack | 20 |
| Corner screws: side plates 8, far wall 4, lid 4, floor 4, back wall 2 | M4 × 10 (T20), QCTI 50-pack | 22 |
| Counterweight wall foot (up through the floor) | M5 × 16 (T25) | 3 |
| Handle, from inside the lid | M5 × 12, any head | 2 |
| Dovetail clamp knobs | Knurled aluminium head D20 × 20, M6 × **40** stainless, POM tip (XIN SHENG DA) — **not 45** (bottoms out) | 2 (+1 spare) |
| Counterweight hole cap | M12, thread ≤ 12 mm (knurled to match) | 1 |
| Base plate → LA-40B / plate → flange | M6 countersunk (ISO 10642) / M5 × 16 socket head | 4 / 4 (lengths after the LA-40B is measured) |
| Internal tie-downs | M3 × 5–6 button heads + cable-tie bases / P-clips | per wiring layout |
| Still open (buy at design freeze, pulled from the assembly with ~20% spares) | dovetail → DEC reducer M3s, brake/board/fuse mounting, T10/T20/T25 bits | — |

## 8. Build and assembly notes
- **Reducers:** RA into the floor first, then slide the DEC reducer into the back wall. Clamp screws from outside (countersunk), hex nuts inside, only at the 10 holes with a matching frame hole; the reducer's counterbored holes are its own factory screws.
- **Corner screws:** M4 × 10 everywhere, so the three screws meeting in one cube stop short of each other.
- **Brake stack, from day one:** both brake supports, the 5 × 40 shaft on two 625ZZ, the 16T pulley and the **200 mm** RA belt over all three pulleys; tension once. Until the SWB-003 (24 V) is fitted, leave the coupling (part 13) off so the 16T idles.
- **Brake board:** plugs onto the main board's BRAKE header. On first power-up, **measure ≈ 23 V at its output before connecting the brake**.
- **CH340E bench check:** USB powered, measure **TXD → GND at idle**: ~3.3 V → wire directly; ~5 V → the 1 kΩ / 2 kΩ divider. Wire TXD → board RX, RXD → board TX, GND → GND. Practise soldering on scrap wire and a spare module first (63/37 rosin-core, flux, ~330 °C, heat-shrink every joint).
- **DEC wiring:** 4-core **26–28 AWG high-flex** cable (TX, RX, GND + spare) and the ACC pair in fine-stranded **18 AWG silicone**. Leave **~80–120 mm of free twist length** through the bore; **tie down both ends right behind the joints** so flexing never happens at a solder joint. Crimped JST (PH/XH) at the board end so the dovetail unplugs. OnStepX serial at 9600–115200 baud.
- **Internal wiring layout** (with the reducer in hand): every lead tied to fixed points (M3 tie-down holes, ≤ 3.5 mm deep, on the panels' inside faces; keep off side plate A's 1.4 mm relief web) and clear of the 70T pulleys and belts; no external belt cage needed (the panels enclose them). **Bore liners:** the base leads pass the RA reducer's spinning input bore (~100× RA speed in slews) and the dovetail leads the DEC bore; if wires can touch a spinning surface, fit a thin PTFE/nylon liner fixed to the non-rotating side. Lever connectors (CMK-642, 47.6 × 15.7 × 11.2) as the power junction only if they fit; check they can't mate flipped (polarity).
- **Power switch (TechEss 16 mm latching):** find the contact pair that closes when latched, wire it to the PS1 pads (VIN and EN), insulate the rest. Hand-tighten the 19 mm nut before the lid goes on.
- **Lid:** the board hangs from it; lift the lid for bench work.
- **Desiccant:** small silica-gel pack inside against dew.
- **Electronics reminders:** B1 must be an **ML1220** (rechargeable; never a CR1220). Never power DC1 and IN1 together. NEMA17 holes may be only 4 mm deep: a thin washer under the M3 FM spacers. Mount the DEC motor with its leads toward −Y. Keyed headers only.
- **Firmware (OnStepX):** time and location from GPS; reducer ratio 100:1 × belt ratio; motor current 0.8–0.9 A; set home in the knobs-east pose.
- **Commissioning:** PHD2 Guiding Assistant with guiding off, ~30 min near the celestial equator = our own PE report; let it measure DEC backlash. Before trusting GOTO, slew slowly through home and the meridian to check counterweight and cable clearances.

## 9. Checks done
- **Shell (2026-11-06/07):** every M4 hole lands on a cube; turned board clears the corner cube (3.0 mm), DEC motor (1.3), switch (6.7), handle (5.2); side-A connectors inside the relief. Reducer insertion RA then DEC with ≥ 1.0 mm along the DEC slide; RA motor to far wall 8.2 mm, to back wall 15.5 mm.
- **Base (2026-11-11):** flange/plate clear the RA parts (an 82 mm³ overlap inside the reducer pocket is in polvinc's model too); plate ≥ 3 mm from the reducer; walls: jack bay ↔ reducer pocket 1.9 mm, corner M5 ↔ bay 5.0 mm, corner M5 ↔ outside 4.2–4.9 mm, plate counterbore ↔ recess 1.3 mm (grows with the smaller real LA-40B plate).
- **Dovetail (2026-11-12):** knurled D20 knob ~7 mm clear of the body as DEC turns; M6 × 40 leaves ≈ 5 mm in the threaded hole.
- **Counterweight (2026-11-13):** the weight can't reach the mount or base at any RA angle; 5 kg balances the 5.5 kg rig about mid-bar.

## 10. Open items and to-do
**When the LA-40B arrives:**
- Measure the top plate: L × W, corner radius, thickness, anything raised on top, long side vs the hinge, hole positions. Then: base plate recess, M6/M5 lengths, mid-edge screws (if ≤ ~54 mm), **round vs square flange**, flange redo for the **single jack + LED**, overhang vs the red cheeks and pitch knob (25–50°), hex-key reach to the corner M5s.
- Also capture for v3: how the black tilt arm attaches (pivot diameter, arm width, latitude screw position and travel), photos; run the play test in the "HEMY v3 Base Ideas" project doc.

**When reducer #1 arrives:**
- Photo of the output face, square on, one factory screw marked. Then re-lay the dovetail's screw holes to avoid the 4 factory screws (polvinc's 11-screw pattern overlaps them); confirm the flange orientation (its free 0/90/180/270° set is fine).
- Dovetail bay: CH340E + 10 A jack layout, solve the bay depth, design the new bay cover.
- Internal wiring layout (section 8), backup USB-C port position, tie-down holes, power junction and fuses; check how polvinc routes leads through the bores.
- Move the home marks to side A (section 6).
- Check the small block (4.5 × 9.8 × 10 mm at r 26) inside the reducer model.

**Other:**
- **Lid Ø10 features at (−57, ±44):** probably the rounded ends of a slot the back wall's top tucks into. Confirm in Onshape.
- **Brake board fit** under the lid: not in the model (on paper X 19–34, Y −46…−27, up to Z 115, ~4 mm from the corner cube). Check on the bench.
- **Jack:** confirm the M12 pitch and body length on arrival; red = centre pin.
- **Thread and tolerance drawings:** L-plate (bores Ø80.5 / Ø65 ±0.05, perpendicular axes, threads), lid, counterweight wall (M12 × 1.75 through; 3 × M5 × 8 deep), base flange (M12 tapped for the jack; 4 × M5 × 12 deep; 12 × M3 clearance + counterbore), base plate (4 × M6 countersinks, 4 × Ø5.5 + Ø9 counterbores), dovetail, M3 tie-down holes.
- **Laser marking:** side plate B: HEMY 2R logo (70 mm wide); side plate A: owner badge (1-bit PNG, 600 dpi, 70.0 × 58.7 mm). Both centred in the 93 × 93 recess. JLCCNC lists DWG/DXF: ask whether the PNG is accepted, else auto-trace to DXF.
- **GPS sticker:** order the print file as printed die-cut vinyl with outdoor laminate.
- **JLCCNC quote:** all parts; counterweight wall one-piece vs three-part; dovetail jaws in bronze and brass.
- **Version control:** local branch `hemy2r-restyle` (main = upstream). Git tracks scripts, README, artwork, docs; STEP / x_t / PSD / zip are ignored. Make a dated zip in `restyle/_snapshots/` before each big CAD change.

Skipped (2026-11-13): dovetail low-end stop (the long bar overhangs the saddle; a stop belongs on the bar) and cable tie plate; files in `_archive/parts/`. Parked for v3 (see the "HEMY v3 Base Ideas" project doc): custom base / replacement LA-40B arm, reducers fully outside the box, full saddle hub, latitude presets.

## 11. Credits
- **HEMY** harmonic mount by **polvinc**: <https://github.com/polvinc/HEMY>, GPL-3.0. HEMY 2R keeps his mechanism and electronics; only the shell, frame and a few parts are restyled. Any shared files from this restyle go out under GPL-3.0 with this credit.
- **HEMY 2R** restyle by Avinash C. Indirabai, with design work, CAD scripts and checks done together with Claude (Anthropic).
