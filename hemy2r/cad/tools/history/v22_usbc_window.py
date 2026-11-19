"""Side plate A: USB-C window for the board's own USB-C (CN2), 2026-11-14.
CN2's face sits 0.05 mm inside the plate's inner face (y -56.45), so a cable plugs in from outside through
a 13 x 7.5 mm (R2) through-window centred on CN2 (X -11, Z 108). That passes a plug body up to ~12.5 x 7 mm,
seated ~5.2 mm deep (5.2 mm of plate in the outer recess). The window's right edge would leave a 0.5 mm sliver
against the existing connector relief (X -4..34, 3.8 deep), so the sliver is cut away inside.
Edits the plate in place.  Run:  python3 v22_usbc_window.py [path-to-side-plate-A.step]
"""
import os, sys
from OCP.STEPControl import STEPControl_Reader, STEPControl_Writer, STEPControl_AsIs
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakePolygon, BRepBuilderAPI_MakeFace
from OCP.BRepFilletAPI import BRepFilletAPI_MakeFillet2d
from OCP.BRepPrimAPI import BRepPrimAPI_MakePrism, BRepPrimAPI_MakeBox
from OCP.BRepAlgoAPI import BRepAlgoAPI_Cut
from OCP.ShapeUpgrade import ShapeUpgrade_UnifySameDomain
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.ShapeFix import ShapeFix_Shape
from OCP.GProp import GProp_GProps
from OCP.BRepGProp import BRepGProp
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_VERTEX
from OCP.TopoDS import TopoDS
from OCP.gp import gp_Pnt, gp_Vec
from OCP.IFSelect import IFSelect_RetDone
VTX = getattr(TopoDS, 'Vertex_s', None) or getattr(TopoDS, 'Vertex')
P = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'parts', 'HEMY2R - Side plate A (recessed panel).step')
CX, CZ, W, H, R = -11.0, 108.0, 13.0, 7.5, 2.0
Y_OUT, Y_IN = -62.5, -56.5
def read(p):
    r = STEPControl_Reader()
    if r.ReadFile(p) != IFSelect_RetDone: sys.exit('cannot read ' + p)
    r.TransferRoots(); return r.OneShape()
def vol(s):
    g = GProp_GProps(); BRepGProp.VolumeProperties_s(s, g); return g.Mass()
def valid(s): return BRepCheck_Analyzer(s).IsValid()
x0, x1, z0, z1 = CX - W / 2, CX + W / 2, CZ - H / 2, CZ + H / 2
y0 = Y_OUT - 1
pg = BRepBuilderAPI_MakePolygon(gp_Pnt(x0, y0, z0), gp_Pnt(x1, y0, z0), gp_Pnt(x1, y0, z1), gp_Pnt(x0, y0, z1), True)
f = BRepBuilderAPI_MakeFace(pg.Wire(), True).Face()
fl = BRepFilletAPI_MakeFillet2d(f); ex = TopExp_Explorer(f, TopAbs_VERTEX); seen = []
while ex.More():
    v = VTX(ex.Current()); ex.Next()
    if not any(v.IsSame(q) for q in seen): seen.append(v); fl.AddFillet(v, R)
fl.Build()
win = BRepPrimAPI_MakePrism(fl.Shape(), gp_Vec(0, (Y_IN + 1) - y0, 0)).Shape()
s = read(P); v0 = vol(s)
s = BRepAlgoAPI_Cut(s, win).Shape()
sliver = BRepPrimAPI_MakeBox(gp_Pnt(x1 - 1.0, -60.3, z0), gp_Pnt(-4.0, Y_IN + 1, z1)).Shape()   # join the window to the relief inside
s = BRepAlgoAPI_Cut(s, sliver).Shape()
if not valid(s):
    fx = ShapeFix_Shape(s); fx.Perform(); s = fx.Shape()
u = ShapeUpgrade_UnifySameDomain(s, True, True, False); u.Build(); m = u.Shape()
if valid(m) and abs(vol(m) - vol(s)) < 0.01: s = m
print('  side A USB-C window: volume %+.1f mm3, valid: %s' % (vol(s) - v0, valid(s)))
if not valid(s): sys.exit('  not written')
w = STEPControl_Writer(); w.Transfer(s, STEPControl_AsIs)
if w.Write(P) != IFSelect_RetDone: sys.exit('write failed')
print('  written')
