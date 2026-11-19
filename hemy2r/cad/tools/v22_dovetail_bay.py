"""Dovetail bay v2.2 (2026-11-18): closes polvinc's open side bay. The 10 A ACC jack and the LED sit in a 6 mm aluminium
port wall; above them a T-slot cut from the back face takes a red-anodized 6061 insert (tray) carrying the CH340E, its
own USB-C in a window in the insert's 0.8 mm front skin. A 3 mm cover closes the back and holds the insert.

Coordinates are assembly coordinates (CAD pose): DEC axis along X through (Y 0, Z 70); back face (on the DEC reducer)
at X -77.5; saddle groove floor at X -102; port face (side A in the CAD pose, west at home) at Y -50.

Run:  python3 v22_dovetail_bay.py <in-dovetail.step> <out-dovetail.step> <out-cover.step> <out-insert.step> [<out-envelopes.step>]

Every size the bought parts set is a parameter below. Re-run with measured values when the CH340E and the jacks arrive.
"""
import sys
import cadquery as cq

# ---------- parameters ----------
FACE_Y = -50.0            # port face
WALL = 6.0                # port wall (jack thread engagement, LED)
BACK_X = -77.5            # back face
PORT_X = -92.5            # USB-C and jack centreline on the face
# 10 A jack + LED stay in the aluminium
JACK_Z, JACK_TAP, JACK_BORE, JACK_YEND = 58.0, 11.0, 13.0, -28.5  # M12x1 tap drill (confirm pitch); body bore
LED = dict(x=-83.0, z=62.5, d=3.1)
LOWER = dict(x0=-95.7, y=(FACE_Y + WALL, -29.5), z=(60.5, 66.0))   # wiring space behind the wall (jack lugs, LED)
# red insert (CH340E) in a T-slot cut from the back face
SLOT_FACE_Z = (66.5, 85.0)   # opening in the port face (red panel)
SLOT_IN_Z = (65.5, 87.0)     # wider behind a 2 mm lip: the insert can't pull out through the face
SLOT_LIP = 2.0
SLOT_YEND = -29.5            # insert stops against the bay end wall here
CLR = 0.1                    # insert clearance per side (after anodize)
INS_FLOOR = 2.0              # insert floor (M2 threads for the module)
SKIN = 0.8                   # insert front skin = CH340E USB-C overhang past the PCB edge
INS_WALL = 0.8
PCB_T, RCPT_H = 1.6, 3.26    # BTE17-06 board, top-mount USB-C shell height
FLOOR_X = PORT_X - RCPT_H / 2 - PCB_T - INS_FLOOR   # slot floor (insert underside)
USB_Z = (SLOT_FACE_Z[0] + SLOT_FACE_Z[1]) / 2
USB_W, USB_H = 9.1, 3.4
PCB_EDGE_Y = FACE_Y + SKIN
# BTE17-06 drawing: holes 1.5 and 11.0 mm from the USB edge, 13 apart across it; pads on the far edge
MODULE_HOLES = [(PCB_EDGE_Y + 1.5, USB_Z + 6.5), (PCB_EDGE_Y + 11.0, USB_Z - 6.5)]
M2_TAP = 1.6
# tab (back boss) raised to carry the taller bay; cover
TAB_TOP = 90.5
CB_DEPTH = 3.0
CB_Y = (FACE_Y - 0.5, -24.0)     # open to the face: the cover edge shows as a 3 mm silver strip
CB_Z = (59.0, 88.5)
NOTCH = dict(x=(-90.0, BACK_X), y=(-30.0, -24.5), z=(66.0, 75.5))  # bay -> polvinc's centre channel
COVER_SCREWS = [(-27.0, 62.5), (-27.0, 79.5)]
M25_TAP, M25_DEPTH = 2.05, 5.0

def fcut(a, b, fuzz=1e-3):
    """Boolean cut with a small fuzzy tolerance (tools share faces with polvinc's channel)."""
    from OCP.BRepAlgoAPI import BRepAlgoAPI_Cut
    from OCP.TopTools import TopTools_ListOfShape
    la, lb = TopTools_ListOfShape(), TopTools_ListOfShape()
    la.Append(a.wrapped); lb.Append(b.wrapped)
    op = BRepAlgoAPI_Cut(); op.SetArguments(la); op.SetTools(lb); op.SetFuzzyValue(fuzz); op.Build()
    assert op.IsDone()
    return cq.Shape.cast(op.Shape())

def box(x0, x1, y0, y1, z0, z1):
    return cq.Solid.makeBox(x1 - x0, y1 - y0, z1 - z0, cq.Vector(x0, y0, z0))

def yz_profile(rects, x0, x1, r):
    """Union of (y0, y1, z0, z1) rectangles in the YZ plane, outer corners rounded r, extruded X x0 -> x1."""
    sk = cq.Sketch()
    for (y0, y1, z0, z1) in rects:
        sk = sk.push([((y0 + y1) / 2, (z0 + z1) / 2)]).rect(y1 - y0, z1 - z0).reset()
    sk = sk.clean().reset().vertices().fillet(r)
    wp = cq.Workplane(cq.Plane(origin=(x0, 0, 0), xDir=(0, 1, 0), normal=(1, 0, 0)))
    return wp.placeSketch(sk).extrude(x1 - x0).val()

def cyl_y(x, z, d, y0, y1):
    return cq.Solid.makeCylinder(d / 2, y1 - y0, cq.Vector(x, y0, z), cq.Vector(0, 1, 0))

def cyl_x(y, z, d, x0, x1):
    return cq.Solid.makeCylinder(d / 2, x1 - x0, cq.Vector(x0, y, z), cq.Vector(1, 0, 0))

def stadium_y(x, z, w, h, y0, y1):
    """Window through a Y-facing wall; long axis along Z."""
    wp = cq.Workplane(cq.Plane(origin=(x, y0, z), xDir=(1, 0, 0), normal=(0, 1, 0)))
    return wp.slot2D(w, h, angle=90).extrude(y1 - y0).val()

def xz_prism(pts, y0, y1):
    wp = cq.Workplane(cq.Plane(origin=(0, y0, 0), xDir=(1, 0, 0), normal=(0, 1, 0)))
    return wp.polyline([(x, -z) for x, z in pts]).close().extrude(y1 - y0).val()

def main(IN, OUT, OUT_COVER, OUT_INSERT, OUT_PH=None):
    dv = cq.importers.importStep(IN).val()
    v0 = dv.Volume()
    # 1. close polvinc's open bay, the mating-ring sliver and his two groove-floor holes
    pcs = sorted(box(-100, BACK_X, FACE_Y, -25, 50, 90).cut(dv).Solids(), key=lambda s: -s.Volume())
    rec = cyl_x(0, 70, 45.1, -86.5, BACK_X + 1)
    nz = box(-90, BACK_X + 1, -26, -18, *NOTCH['z'])
    sl = box(-86.5, BACK_X, -25, -18, 57.5, 83.5).cut(dv).cut(rec).cut(nz)
    stubs = [cyl_x(-29.5, z, 2.6, -102.0, -99.0) for z in (63.0, 78.0)]
    # 2. raise the back tab's top edge (56.4..84.6 -> 56.4..TAB_TOP), same 45 deg chamfer
    tab = xz_prism([(-80.5, 70), (-80.5, TAB_TOP + 3), (BACK_X, TAB_TOP), (BACK_X, 70)], FACE_Y, -22.0).cut(rec)
    d = dv.fuse(pcs[0], *sl.Solids(), *stubs, tab).clean().Solids()[0]
    v_filled = d.Volume()
    # 3. cuts
    fy, sy = FACE_Y - 1, FACE_Y + SLOT_LIP
    slot = yz_profile([(fy, sy) + SLOT_FACE_Z, (sy - 0.01, SLOT_YEND) + SLOT_IN_Z], FLOOR_X, BACK_X + 1, 1.0)
    lower = yz_profile([LOWER['y'] + LOWER['z']], LOWER['x0'], BACK_X + 1, 1.5)
    cb = yz_profile([CB_Y + CB_Z], BACK_X - CB_DEPTH, BACK_X + 1, 1.5)
    notch = box(NOTCH['x'][0], NOTCH['x'][1] + 1, *NOTCH['y'], *NOTCH['z'])
    jack = cyl_y(PORT_X, JACK_Z, JACK_TAP, FACE_Y - 1, FACE_Y + WALL).fuse(
        cyl_y(PORT_X, JACK_Z, JACK_BORE, FACE_Y + WALL, JACK_YEND))
    led = cyl_y(LED['x'], LED['z'], LED['d'], FACE_Y - 1, FACE_Y + WALL + 0.5)
    holes = [cyl_x(y, z, M25_TAP, BACK_X - CB_DEPTH - M25_DEPTH, BACK_X - CB_DEPTH + 0.1) for (y, z) in COVER_SCREWS]
    for t in [slot, lower, cb, notch, jack, led] + holes:
        d = fcut(d, t)
        assert d.Volume() > 1e5, 'boolean failed'
    d = d.clean()
    assert d.isValid() and len(d.Solids()) == 1
    print('  dovetail: original %.0f, filled %.0f, final %.0f mm3 (%+.0f)' % (v0, v_filled, d.Volume(), d.Volume() - v0))
    cq.exporters.export(cq.Workplane().add(d), OUT, 'STEP')
    # 4. cover: fills the counterbore, flush with the back face and the port face
    cov = yz_profile([(FACE_Y, CB_Y[1] - CLR, CB_Z[0] + CLR, CB_Z[1] - CLR)], BACK_X - CB_DEPTH, BACK_X, 1.4)
    for (y, z) in COVER_SCREWS:
        cov = cov.cut(cyl_x(y, z, 2.7, BACK_X - CB_DEPTH - 1, BACK_X + 1))
        cov = cov.cut(cq.Solid.makeCone(0, 3.0, 3.0, cq.Vector(BACK_X - 2.5, y, z), cq.Vector(1, 0, 0)))
    cov = cov.clean()
    print('  cover: %.0f mm3, %.1f g' % (cov.Volume(), cov.Volume() * 2.7e-3))
    cq.exporters.export(cq.Workplane().add(cov), OUT_COVER, 'STEP')
    # 5. red insert: T-profile tray, open toward the cover, from the floor to the cover's inner face
    xt = BACK_X - CB_DEPTH - CLR
    fz, iz = SLOT_FACE_Z, SLOT_IN_Z
    ins = yz_profile([(FACE_Y, sy) + (fz[0] + CLR, fz[1] - CLR),
                      (sy - 0.01, SLOT_YEND - CLR) + (iz[0] + CLR, iz[1] - CLR)], FLOOR_X + CLR, xt, 0.9)
    cav_z = (fz[0] + CLR + INS_WALL, fz[1] - CLR - INS_WALL)
    cav = yz_profile([(PCB_EDGE_Y, SLOT_YEND - CLR - INS_WALL) + cav_z,
                      (sy, SLOT_YEND - CLR - INS_WALL) + (iz[0] + CLR + INS_WALL, iz[1] - CLR - INS_WALL)],
                     FLOOR_X + CLR + INS_FLOOR, xt + 1, 0.5)
    ins = fcut(ins, cav)
    ins = fcut(ins, stadium_y(PORT_X, USB_Z, USB_W, USB_H, FACE_Y - 1, PCB_EDGE_Y + 0.5))
    ins = fcut(ins, box(FLOOR_X + CLR + INS_FLOOR, xt + 1, SLOT_YEND - 3, SLOT_YEND + 1, NOTCH['z'][0] + 1.5, NOTCH['z'][1] - 0.5))  # rear wire slot
    ins = fcut(ins, box(FLOOR_X + CLR + INS_FLOOR, xt + 1, SLOT_YEND - 4.5, SLOT_YEND - CLR - INS_WALL, iz[0] - 1, iz[0] + CLR + INS_WALL + 0.5))  # jack/LED wires up from below
    for (y, z) in MODULE_HOLES:
        ins = fcut(ins, cyl_x(y, z, M2_TAP, FLOOR_X - 1, FLOOR_X + CLR + INS_FLOOR + 0.5))
    ins = ins.clean()
    assert ins.isValid() and len(ins.Solids()) == 1
    print('  insert: %.0f mm3, %.1f g, face %.1f x %.1f mm' % (ins.Volume(), ins.Volume() * 2.7e-3, xt - FLOOR_X - CLR, fz[1] - fz[0] - 2 * CLR))
    cq.exporters.export(cq.Workplane().add(ins), OUT_INSERT, 'STEP')
    if OUT_PH:  # envelopes of the bought parts, for clearance checks
        x0 = FLOOR_X + CLR + INS_FLOOR
        pcb = box(x0, x0 + PCB_T, PCB_EDGE_Y, PCB_EDGE_Y + 16, USB_Z - 8, USB_Z + 8)
        rcpt = box(x0 + PCB_T, x0 + PCB_T + RCPT_H, FACE_Y + 0.05, FACE_Y + 7.35, USB_Z - 4.3, USB_Z + 4.3)
        chip = box(x0 + PCB_T, x0 + PCB_T + 1.6, PCB_EDGE_Y + 8.5, PCB_EDGE_Y + 12.5, USB_Z - 2.5, USB_Z + 2.5)
        hdr = box(x0 + PCB_T, x0 + PCB_T + 2.5, PCB_EDGE_Y + 13.6, PCB_EDGE_Y + 15.6, USB_Z - 7.5, USB_Z + 7.5)
        jk = cyl_y(PORT_X, JACK_Z, 14, FACE_Y - 2, FACE_Y).fuse(cyl_y(PORT_X, JACK_Z, 12, FACE_Y, FACE_Y + 18)).fuse(
            box(PORT_X - 1.5, PORT_X + 1.5, FACE_Y + 18, FACE_Y + 21.5, JACK_Z - 4, JACK_Z + 4))
        ld = cyl_y(LED['x'], LED['z'], 3.0, FACE_Y + WALL - 5.3, FACE_Y + WALL).fuse(
            cyl_y(LED['x'], LED['z'], 3.8, FACE_Y + WALL, FACE_Y + WALL + 1.0))
        cq.exporters.export(cq.Workplane().add(cq.Compound.makeCompound([pcb.fuse(rcpt).fuse(chip).fuse(hdr), jk, ld])), OUT_PH, 'STEP')

if __name__ == '__main__':
    main(*sys.argv[1:])
