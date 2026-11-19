"""Lid: restore the GPS window (2026-11-16). Re-cuts the 25.5 x 25.5 x 5 mm antenna pocket (R1) at (X -40, Y 0),
leaving a 1 mm floor, and the D4 lead hole at (-30, -10) through the floor, as v22_gps.py/v22_gps2.py did before
v22_gps_remove.py filled them. The handle countersinks at X -11 (v22_lid_handle.py) are kept.
Run:  python3 v22_gps_restore.py <in-lid.step> <out-lid.step>
"""
import sys
from OCP.STEPControl import STEPControl_Reader, STEPControl_Writer, STEPControl_AsIs
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakePolygon, BRepBuilderAPI_MakeFace
from OCP.BRepFilletAPI import BRepFilletAPI_MakeFillet2d
from OCP.BRepPrimAPI import BRepPrimAPI_MakePrism, BRepPrimAPI_MakeCylinder
from OCP.BRepAlgoAPI import BRepAlgoAPI_Cut
from OCP.ShapeUpgrade import ShapeUpgrade_UnifySameDomain
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.GProp import GProp_GProps
from OCP.BRepGProp import BRepGProp
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_VERTEX
from OCP.TopoDS import TopoDS
from OCP.gp import gp_Pnt, gp_Vec, gp_Ax2, gp_Dir
from OCP.IFSelect import IFSelect_RetDone
VTX = getattr(TopoDS, 'Vertex_s', None) or getattr(TopoDS, 'Vertex')
IN, OUT = sys.argv[1], sys.argv[2]
CX, CY, TOP, BOT = -40.0, 0.0, 125.0, 119.0
def read(p):
    r = STEPControl_Reader(); assert r.ReadFile(p) == IFSelect_RetDone; r.TransferRoots(); return r.OneShape()
def vol(s):
    g = GProp_GProps(); BRepGProp.VolumeProperties_s(s, g); return g.Mass()
def rr(wx, wy, rad, z0, z1):
    x0, x1, y0, y1 = CX - wx / 2, CX + wx / 2, CY - wy / 2, CY + wy / 2
    pg = BRepBuilderAPI_MakePolygon(gp_Pnt(x0, y0, z0), gp_Pnt(x1, y0, z0), gp_Pnt(x1, y1, z0), gp_Pnt(x0, y1, z0), True)
    f = BRepBuilderAPI_MakeFace(pg.Wire(), True).Face()
    fl = BRepFilletAPI_MakeFillet2d(f); ex = TopExp_Explorer(f, TopAbs_VERTEX); seen = []
    while ex.More():
        v = VTX(ex.Current()); ex.Next()
        if not any(v.IsSame(q) for q in seen): seen.append(v); fl.AddFillet(v, rad)
    fl.Build()
    return BRepPrimAPI_MakePrism(fl.Shape(), gp_Vec(0, 0, z1 - z0)).Shape()
s = read(IN); v0 = vol(s)
s = BRepAlgoAPI_Cut(s, rr(25.5, 25.5, 1.0, BOT + 1.0, TOP + 1.0)).Shape()
s = BRepAlgoAPI_Cut(s, BRepPrimAPI_MakeCylinder(gp_Ax2(gp_Pnt(CX + 10.0, CY - 10.0, BOT - 1), gp_Dir(0, 0, 1)), 2.0, 3.0).Shape()).Shape()
u = ShapeUpgrade_UnifySameDomain(s, True, True, False); u.Build(); m = u.Shape()
if BRepCheck_Analyzer(m).IsValid(): s = m
ok = BRepCheck_Analyzer(s).IsValid()
print('  GPS window restored: volume %+.1f mm3 (expect about -3264), valid: %s' % (vol(s) - v0, ok))
assert ok
w = STEPControl_Writer(); w.Transfer(s, STEPControl_AsIs); assert w.Write(OUT) == IFSelect_RetDone
print('  written', OUT)
