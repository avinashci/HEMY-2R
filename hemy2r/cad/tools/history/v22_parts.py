"""v2.2 parts: board turned to face side plate A, no external USB-C,
12 mm M4 cubes in both far top corners. Reads v2.1 parts, writes v2.2/parts/.
Run:  python3 ~/Developer/HEMY/restyle/v2.1/tools/v22_parts.py
"""
import os, sys
from OCP.STEPControl import STEPControl_Reader, STEPControl_Writer, STEPControl_AsIs
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakePolygon, BRepBuilderAPI_MakeFace, BRepBuilderAPI_Transform
from OCP.BRepFilletAPI import BRepFilletAPI_MakeFillet2d
from OCP.BRepPrimAPI import BRepPrimAPI_MakePrism, BRepPrimAPI_MakeBox, BRepPrimAPI_MakeCylinder, BRepPrimAPI_MakeCone
from OCP.BRepAlgoAPI import BRepAlgoAPI_Cut, BRepAlgoAPI_Fuse, BRepAlgoAPI_Common
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.ShapeFix import ShapeFix_Shape
from OCP.GProp import GProp_GProps
from OCP.BRepGProp import BRepGProp
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_VERTEX
from OCP.TopoDS import TopoDS
from OCP.gp import gp_Pnt, gp_Vec, gp_Dir, gp_Ax2, gp_Trsf
from OCP.IFSelect import IFSelect_RetDone
VTX = getattr(TopoDS, 'Vertex_s', None) or getattr(TopoDS, 'Vertex')

here = os.path.dirname(os.path.abspath(__file__))
V21 = os.path.join(here, '..')
OUT = os.path.join(here, '..', '..', 'v2.2', 'parts')

def read(p):
    r = STEPControl_Reader()
    if r.ReadFile(p) != IFSelect_RetDone: sys.exit('cannot read ' + p)
    r.TransferRoots(); return r.OneShape()
def write(s, name):
    w = STEPControl_Writer(); w.Transfer(s, STEPControl_AsIs)
    if w.Write(os.path.join(OUT, name)) != IFSelect_RetDone: sys.exit('write failed ' + name)
def vol(s):
    g = GProp_GProps(); BRepGProp.VolumeProperties_s(s, g); return g.Mass()
def valid(s): return BRepCheck_Analyzer(s).IsValid()
def op(cls, a, b):
    o = cls(a, b); o.Build()
    if not o.IsDone(): sys.exit('boolean failed: ' + cls.__name__)
    return o.Shape()
fuse = lambda a, b: op(BRepAlgoAPI_Fuse, a, b)
cut = lambda a, b: op(BRepAlgoAPI_Cut, a, b)
def box(x0, y0, z0, x1, y1, z1): return BRepPrimAPI_MakeBox(gp_Pnt(x0, y0, z0), gp_Pnt(x1, y1, z1)).Shape()
AX = {'X': gp_Dir(1, 0, 0), 'Y': gp_Dir(0, 1, 0), 'Z': gp_Dir(0, 0, 1)}
def pt(axis, a, u, v):
    # point with axial coord a and the two other coords (u, v) in X,Y,Z order
    c = {'X': (a, u, v), 'Y': (u, a, v), 'Z': (u, v, a)}[axis]; return gp_Pnt(*c)
def cyl(axis, uv, a0, a1, r):
    return BRepPrimAPI_MakeCylinder(gp_Ax2(pt(axis, a0, *uv), AX[axis]), r, a1 - a0).Shape()
def rrect_prism(axis, a0, a1, u0, u1, v0, v1, rad):
    P = lambda u, v: pt(axis, a0, u, v)
    pg = BRepBuilderAPI_MakePolygon(P(u0, v0), P(u1, v0), P(u1, v1), P(u0, v1), True)
    f = BRepBuilderAPI_MakeFace(pg.Wire(), True).Face()
    fl = BRepFilletAPI_MakeFillet2d(f); ex = TopExp_Explorer(f, TopAbs_VERTEX); seen = []
    while ex.More():
        vv = VTX(ex.Current()); ex.Next()
        if not any(vv.IsSame(s) for s in seen): seen.append(vv); fl.AddFillet(vv, rad)
    fl.Build()
    d = {'X': gp_Vec(a1 - a0, 0, 0), 'Y': gp_Vec(0, a1 - a0, 0), 'Z': gp_Vec(0, 0, a1 - a0)}[axis]
    return BRepPrimAPI_MakePrism(fl.Shape(), d).Shape()
def csk_M4(axis, uv, face, inward):
    """DIN 7991 M4: Ø4.5 through + 90° countersink Ø8.4 at the outer face. inward = +1/-1 along axis."""
    t = 6.0
    a0, a1 = (face, face + inward * t) if inward > 0 else (face - t, face)
    hole = cyl(axis, uv, min(a0, a1) - 1, max(a0, a1) + 1, 2.25)
    d = gp_Dir(*[inward * c for c in ({'X': (1, 0, 0), 'Y': (0, 1, 0), 'Z': (0, 0, 1)}[axis])])
    cone = BRepPrimAPI_MakeCone(gp_Ax2(pt(axis, face - inward * 0.5, *uv), d), 4.2 + 0.5, 2.25, 4.2 + 0.5 - 2.25).Shape()
    return fuse(hole, cone)
def fill(axis, uv, a0, a1, r): return cyl(axis, uv, a0, a1, r)
def finish(s, name, v0):
    if not valid(s):
        f = ShapeFix_Shape(s); f.Perform(); s = f.Shape()
    print('  %-52s volume %+8.1f mm3  valid: %s' % (name, vol(s) - v0, valid(s)))
    if not valid(s): sys.exit('  not written (invalid)')
    write(s, name)

os.makedirs(OUT, exist_ok=True)
P = os.path.join(V21, 'panels_125cube')

# ---- far walls: plain, no USB-C, no inner relief, M4 top corners ----
for src, dst, recessed in [('HEMY2R - Far wall USB-C.step', 'HEMY2R - Far wall.step', False),
                           ('HEMY2R - Far wall (recessed panel) USB-C notch.step', 'HEMY2R - Far wall (recessed panel).step', True)]:
    W = read(os.path.join(P, src)); v0 = vol(W)
    W = fuse(W, box(50, -49.3, 104.6, 56, -36.7, 111.4))                 # close the USB window
    W = fuse(W, box(50, -36.0, 97.9, 53.8, 2.0, 114.0))                   # close the inner relief
    if recessed:
        W = fuse(W, box(55.2, -41.5, 15.0, 56, 41.5, 110.0))             # flatten old pocket + notch
        W = cut(W, rrect_prism('X', 55.2, 57, -40.5, 40.5, 16, 109, 6))   # standard R6 pocket
    for y in (-51.5, 51.5): W = fuse(W, fill('X', (y, 116), 50, 56, 3.5))     # close old M3
    for y in (-50.5, 50.5): W = cut(W, csk_M4('X', (y, 113), 56, -1))         # new M4 at cube centre
    finish(W, dst, v0)

# ---- side plates: M4 top-far corner; side A gets the connector relief ----
for side, yin, yout in [('A', -56.5, -62.5), ('B', 56.5, 62.5)]:
    inward = 1 if side == 'A' else -1
    for rec in ['', ' (recessed panel)']:
        S = read(os.path.join(P, 'HEMY2R - Side plate %s%s.step' % (side, rec))); v0 = vol(S)
        a0, a1 = min(yin, yout), max(yin, yout)
        S = fuse(S, fill('Y', (45, 116), a0, a1, 3.5))
        S = cut(S, csk_M4('Y', (44, 113), yout, inward))
        if side == 'A':
            S = cut(S, rrect_prism('Y', yin - 3.8, yin + 1, -4.0, 34.0, 97.9, 114.0, 1.5))
        finish(S, 'HEMY2R - Side plate %s%s.step' % (side, rec), v0)

# ---- lid: spacer threads moved, M4 far corners ----
L = read(os.path.join(V21, 'common', 'HEMY2R - Lid.step')); v0 = vol(L)
old = [(-3.5, 0.0), (-3.5, -46.0), (22.5, -21.5)]
new = [(y + 32.0, -x - 6.5) for x, y in old]          # board turned 90 deg, moved to X -17..35
cores = [op(BRepAlgoAPI_Common, L, fill('Z', c, 118.5, 125.5, 2.0)) for c in old]
for c in old: L = fuse(L, fill('Z', c, 119, 125, 2.0))
for (cx, cy), (nx, ny), core in zip(old, new, cores):
    L = cut(L, fill('Z', (nx, ny), 118.5, 125.5, 2.0))
    t = gp_Trsf(); t.SetTranslation(gp_Vec(nx - cx, ny - cy, 0))
    L = fuse(L, BRepBuilderAPI_Transform(core, t, True).Shape())
for y in (-51.5, 51.5): L = fuse(L, fill('Z', (45, y), 119, 125, 3.5))
for y in (-50.5, 50.5): L = cut(L, csk_M4('Z', (44, y), 125, -1))
print('  lid spacer threads now at', [(round(a, 1), round(b, 1)) for a, b in new])
finish(L, 'HEMY2R - Lid.step', v0)
print('done ->', os.path.abspath(OUT))
