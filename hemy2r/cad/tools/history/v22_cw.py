"""v2.2 optional counterweight far wall + CW-ready L-plate.
Reads v2.2/parts far walls and the v2.1 L-plate (RA -6); writes to v2.2/parts/.
Run:  python3 ~/Developer/HEMY/restyle/v2.1/tools/v22_cw.py
"""
import os, sys
from OCP.STEPControl import STEPControl_Reader, STEPControl_Writer, STEPControl_AsIs
from OCP.BRepPrimAPI import BRepPrimAPI_MakeBox, BRepPrimAPI_MakeCylinder, BRepPrimAPI_MakeCone
from OCP.BRepAlgoAPI import BRepAlgoAPI_Cut, BRepAlgoAPI_Fuse
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.ShapeFix import ShapeFix_Shape
from OCP.GProp import GProp_GProps
from OCP.BRepGProp import BRepGProp
from OCP.gp import gp_Pnt, gp_Dir, gp_Ax2
from OCP.IFSelect import IFSelect_RetDone

here = os.path.dirname(os.path.abspath(__file__))
V22 = os.path.join(here, '..', '..', 'v2.2', 'parts')
LPLATE = os.path.join(here, '..', 'option1_cube_Lplate', 'HEMY2R - L-plate (125 cube, RA -6).step')

def read(p):
    r = STEPControl_Reader()
    if r.ReadFile(p) != IFSelect_RetDone: sys.exit('cannot read ' + p)
    r.TransferRoots(); return r.OneShape()
def vol(s):
    g = GProp_GProps(); BRepGProp.VolumeProperties_s(s, g); return g.Mass()
def op(cls, a, b):
    o = cls(a, b); o.Build()
    if not o.IsDone(): sys.exit('boolean failed')
    return o.Shape()
fuse = lambda a, b: op(BRepAlgoAPI_Fuse, a, b)
cut = lambda a, b: op(BRepAlgoAPI_Cut, a, b)
def box(x0, y0, z0, x1, y1, z1): return BRepPrimAPI_MakeBox(gp_Pnt(x0, y0, z0), gp_Pnt(x1, y1, z1)).Shape()
def cylX(y, z, x0, x1, r): return BRepPrimAPI_MakeCylinder(gp_Ax2(gp_Pnt(x0, y, z), gp_Dir(1, 0, 0)), r, x1 - x0).Shape()
def cylZ(x, y, z0, z1, r): return BRepPrimAPI_MakeCylinder(gp_Ax2(gp_Pnt(x, y, z0), gp_Dir(0, 0, 1)), r, z1 - z0).Shape()
def cone(p, d, r1, r2, h): return BRepPrimAPI_MakeCone(gp_Ax2(p, d), r1, r2, h).Shape()
def save(s, name, v0):
    if not BRepCheck_Analyzer(s).IsValid():
        f = ShapeFix_Shape(s); f.Perform(); s = f.Shape()
    ok = BRepCheck_Analyzer(s).IsValid()
    print('  %-58s volume %+8.1f mm3  valid: %s' % (name, vol(s) - v0, ok))
    if not ok: sys.exit('  not written')
    w = STEPControl_Writer(); w.Transfer(s, STEPControl_AsIs)
    if w.Write(os.path.join(V22, name)) != IFSelect_RetDone: sys.exit('write failed')

FOOT_Y = (-28.0, 0.0, 28.0)       # M5 positions along the foot, X 45
LUG_X = 68.0                      # lug outer face (far wall outer face is X 56)

from OCP.BRepBuilderAPI import BRepBuilderAPI_MakePolygon, BRepBuilderAPI_MakeFace, BRepBuilderAPI_MakeVertex
from OCP.BRepFilletAPI import BRepFilletAPI_MakeFillet2d, BRepFilletAPI_MakeChamfer
from OCP.BRepPrimAPI import BRepPrimAPI_MakePrism
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_VERTEX, TopAbs_EDGE
from OCP.TopoDS import TopoDS
from OCP.BRepAdaptor import BRepAdaptor_Curve
from OCP.gp import gp_Vec
VTX = getattr(TopoDS, 'Vertex_s', None) or getattr(TopoDS, 'Vertex')
EDG = getattr(TopoDS, 'Edge_s', None) or getattr(TopoDS, 'Edge')
def lug():
    """32 (Y) x 24 (Z) mm, R4 corners, from inside the plate (X 55) out to X 68, 1 mm chamfer on the outer edge."""
    x0 = 55.0
    pg = BRepBuilderAPI_MakePolygon(gp_Pnt(x0, -16, 58), gp_Pnt(x0, 16, 58), gp_Pnt(x0, 16, 82), gp_Pnt(x0, -16, 82), True)
    f = BRepBuilderAPI_MakeFace(pg.Wire(), True).Face()
    fl = BRepFilletAPI_MakeFillet2d(f); ex = TopExp_Explorer(f, TopAbs_VERTEX); seen = []
    while ex.More():
        v = VTX(ex.Current()); ex.Next()
        if not any(v.IsSame(q) for q in seen): seen.append(v); fl.AddFillet(v, 4.0)
    fl.Build()
    L = BRepPrimAPI_MakePrism(fl.Shape(), gp_Vec(LUG_X - x0, 0, 0)).Shape()
    ch = BRepFilletAPI_MakeChamfer(L); ex = TopExp_Explorer(L, TopAbs_EDGE); done = []
    while ex.More():
        e = EDG(ex.Current()); ex.Next()
        if any(e.IsSame(d) for d in done): continue
        c = BRepAdaptor_Curve(e)
        if all(abs(c.Value(c.FirstParameter() + t * (c.LastParameter() - c.FirstParameter())).X() - LUG_X) < 1e-6 for t in (0, .5, 1)):
            ch.Add(1.0, e); done.append(e)
    ch.Build()
    return ch.Shape() if ch.IsDone() else L

# ---- counterweight far walls (flat + recessed) ----
for src, dst in [('HEMY2R - Far wall.step', 'HEMY2R - Far wall CW.step'),
                 ('HEMY2R - Far wall (recessed panel).step', 'HEMY2R - Far wall CW (recessed panel).step')]:
    W = read(os.path.join(V22, src)); v0 = vol(W)
    W = fuse(W, lug())                                          # SAL-33 style lug, 12 mm proud
    W = fuse(W, box(40.0, -40.0, 9.0, 50.5, 40.0, 19.0))        # bottom foot
    W = cut(W, cylX(0, 70, 49.0, 69.0, 5.1))                    # M12 tap drill Ø10.2 through lug + plate
    W = cut(W, cone(gp_Pnt(LUG_X + 0.6, 0, 70), gp_Dir(-1, 0, 0), 6.6, 5.1, 1.5))   # 1 mm entry chamfer
    for y in FOOT_Y: W = cut(W, cylZ(45.0, y, 8.0, 17.0, 2.1))  # M5 tap drill Ø4.2, 8 deep
    save(W, dst, v0)

# ---- CW-ready L-plate: 3 x M5 countersunk through the floor from below ----
L = read(LPLATE); v0 = vol(L)
for y in FOOT_Y:
    L = cut(L, cylZ(45.0, y, -1.0, 10.0, 2.75))                 # Ø5.5 clearance
    L = cut(L, cone(gp_Pnt(45.0, y, -0.5), gp_Dir(0, 0, 1), 5.7, 2.75, 2.95))  # 90° csk Ø10.4 at the bottom face
save(L, 'HEMY2R - L-plate (125 cube, RA -6, CW-ready).step', v0)
print('done')
