"""Base plate: LA-40B recess resized to the measured top plate (2026-11-15).
Measured LA-40B top plate: 50 x 54-55 mm, 8-9 mm thick, corners ~R3-4; 8 x M6 (corners on 38 x 38, mid-edges at +/-17.5)
+ 1/4"-20 centre, matching the Angeleyes interface drawing. The old recess assumed 60 x 60 R4.1.
New recess: 56.5 x 56.5 mm, R4.5, 3 deep (square, so the plate fits either way round; 0.75-1.25 mm clearance on the
long sides). Refills the old recess and re-cuts the 4 x M6 countersunk holes (+/-19) and the 4 x M5 clearance holes with
their Dia 9 x 5.5 counterbores (+/-33). Counterbore-to-recess wall grows from 1.3 to ~4.1 mm.
Also writes a measured placeholder for the LA-40B top plate (55 x 50 x 8.5, R3.5; long side along X assumed).
Run:  python3 v22_base_recess.py <plate in> <plate out> <placeholder out>
"""
import sys
from OCP.STEPControl import STEPControl_Reader, STEPControl_Writer, STEPControl_AsIs
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakePolygon, BRepBuilderAPI_MakeFace
from OCP.BRepFilletAPI import BRepFilletAPI_MakeFillet2d
from OCP.BRepPrimAPI import BRepPrimAPI_MakePrism, BRepPrimAPI_MakeBox, BRepPrimAPI_MakeCylinder
from OCP.BRepAlgoAPI import BRepAlgoAPI_Cut, BRepAlgoAPI_Fuse
from OCP.ShapeUpgrade import ShapeUpgrade_UnifySameDomain
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.ShapeFix import ShapeFix_Shape
from OCP.GProp import GProp_GProps
from OCP.BRepGProp import BRepGProp
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_VERTEX
from OCP.TopoDS import TopoDS
from OCP.gp import gp_Pnt, gp_Vec, gp_Ax2, gp_Dir
from OCP.IFSelect import IFSelect_RetDone
X0, Z0, ZR = -6.0, -38.5, 3.0            # RA axis X, plate bottom, recess depth
def read(p):
    r = STEPControl_Reader()
    if r.ReadFile(p) != IFSelect_RetDone: sys.exit('cannot read ' + p)
    r.TransferRoots(); return r.OneShape()
def vol(s):
    g = GProp_GProps(); BRepGProp.VolumeProperties_s(s, g); return g.Mass()
def valid(s): return BRepCheck_Analyzer(s).IsValid()
def write(s, p):
    w = STEPControl_Writer(); w.Transfer(s, STEPControl_AsIs)
    if w.Write(p) != IFSelect_RetDone: sys.exit('write failed')
def rrect(hx, hy, r, z0, h):
    pg = BRepBuilderAPI_MakePolygon(gp_Pnt(X0-hx, -hy, z0), gp_Pnt(X0+hx, -hy, z0), gp_Pnt(X0+hx, hy, z0), gp_Pnt(X0-hx, hy, z0), True)
    f = BRepBuilderAPI_MakeFace(pg.Wire(), True).Face()
    fl = BRepFilletAPI_MakeFillet2d(f); ex = TopExp_Explorer(f, TopAbs_VERTEX); seen = []
    while ex.More():
        v = TopoDS.Vertex_s(ex.Current()); ex.Next()
        if not any(v.IsSame(q) for q in seen): seen.append(v); fl.AddFillet(v, r)
    fl.Build(); return BRepPrimAPI_MakePrism(fl.Shape(), gp_Vec(0, 0, h)).Shape()
def cyl(x, y, r, z0, h): return BRepPrimAPI_MakeCylinder(gp_Ax2(gp_Pnt(X0+x, y, z0), gp_Dir(0, 0, 1)), r, h).Shape()
s = read(sys.argv[1]); v0 = vol(s)
s = BRepAlgoAPI_Fuse(s, BRepPrimAPI_MakeBox(gp_Pnt(X0-30.2, -30.2, Z0), gp_Pnt(X0+30.2, 30.2, Z0+ZR)).Shape()).Shape()   # refill old recess
cuts = [rrect(28.25, 28.25, 4.5, Z0-0.1, ZR+0.1)]                                  # new recess 56.5 x 56.5 R4.5
for x in (-19, 19):
    for y in (-19, 19): cuts.append(cyl(x, y, 3.3, Z0-0.1, 6))                   # M6 clearance Dia 6.6 (countersinks above untouched)
for x in (-33, 33):
    for y in (-33, 33): cuts += [cyl(x, y, 2.75, Z0-0.1, 12), cyl(x, y, 4.5, Z0-0.1, 5.6)]   # M5 clearance + Dia 9 x 5.5 counterbore
for c in cuts: s = BRepAlgoAPI_Cut(s, c).Shape()
if not valid(s):
    fx = ShapeFix_Shape(s); fx.Perform(); s = fx.Shape()
u = ShapeUpgrade_UnifySameDomain(s, True, True, False); u.Build(); m = u.Shape()
if valid(m) and abs(vol(m) - vol(s)) < 0.01: s = m
print('  base plate: volume %+.1f mm3 (%.0f g), valid: %s' % (vol(s) - v0, vol(s) * 2.7e-3, valid(s)))
if not valid(s): sys.exit('  not written')
write(s, sys.argv[2])
ph = rrect(27.5, 25.0, 3.5, Z0+ZR-8.5, 8.5)                                         # measured placeholder, top at the recess ceiling (Z0+ZR)
write(ph, sys.argv[3]); print('  placeholder written')
