"""Lid: GPS window at the back-centre (X -40, Y 0), long side along Y (same direction as the handle).
Cover step 27.2 x 40.2 x 1.0 (R3) for a 1 mm red acrylic 'HEMY V2' cover, flush;
antenna pocket 25.5 x 25.5, 4 mm deeper (R1) for a 25 x 25 x 4 ceramic patch; 1 mm floor;
Ø4 lead hole at the pocket's inner corner (toward the board). Edits the lid in place.
Run:  python3 ~/Developer/HEMY/restyle/v2.2/tools/v22_gps.py
"""
import os, sys
from OCP.STEPControl import STEPControl_Reader, STEPControl_Writer, STEPControl_AsIs
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakePolygon, BRepBuilderAPI_MakeFace
from OCP.BRepFilletAPI import BRepFilletAPI_MakeFillet2d
from OCP.BRepPrimAPI import BRepPrimAPI_MakePrism, BRepPrimAPI_MakeCylinder
from OCP.BRepAlgoAPI import BRepAlgoAPI_Cut
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
VTX = getattr(TopoDS, 'Vertex_s', None) or getattr(TopoDS, 'Vertex')
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'parts', 'HEMY2R - Lid.step')
CX, CY, TOP = -40.0, 0.0, 125.0
def read(p):
    r = STEPControl_Reader()
    if r.ReadFile(p) != IFSelect_RetDone: sys.exit('cannot read ' + p)
    r.TransferRoots(); return r.OneShape()
def vol(s):
    g = GProp_GProps(); BRepGProp.VolumeProperties_s(s, g); return g.Mass()
def valid(s): return BRepCheck_Analyzer(s).IsValid()
def pocket(wx, wy, rad, z0, z1):
    x0, x1, y0, y1 = CX - wx / 2, CX + wx / 2, CY - wy / 2, CY + wy / 2
    pg = BRepBuilderAPI_MakePolygon(gp_Pnt(x0, y0, z0), gp_Pnt(x1, y0, z0), gp_Pnt(x1, y1, z0), gp_Pnt(x0, y1, z0), True)
    f = BRepBuilderAPI_MakeFace(pg.Wire(), True).Face()
    fl = BRepFilletAPI_MakeFillet2d(f); ex = TopExp_Explorer(f, TopAbs_VERTEX); seen = []
    while ex.More():
        v = VTX(ex.Current()); ex.Next()
        if not any(v.IsSame(q) for q in seen): seen.append(v); fl.AddFillet(v, rad)
    fl.Build()
    return BRepPrimAPI_MakePrism(fl.Shape(), gp_Vec(0, 0, z1 - z0)).Shape()
s = read(P); v0 = vol(s)
s = BRepAlgoAPI_Cut(s, pocket(27.2, 40.2, 3.0, TOP - 1.0, TOP + 1)).Shape()      # cover step, 1 mm
s = BRepAlgoAPI_Cut(s, pocket(25.5, 25.5, 1.0, TOP - 5.0, TOP + 1)).Shape()      # antenna pocket, 5 mm total
hole = BRepPrimAPI_MakeCylinder(gp_Ax2(gp_Pnt(CX + 10.0, CY - 10.0, TOP - 7.0), gp_Dir(0, 0, 1)), 2.0, 4.0).Shape()
s = BRepAlgoAPI_Cut(s, hole).Shape()                                            # Ø4 lead hole through the 1 mm floor
if not valid(s):
    f = ShapeFix_Shape(s); f.Perform(); s = f.Shape()
u = ShapeUpgrade_UnifySameDomain(s, True, True, False); u.Build(); m = u.Shape()
if valid(m) and abs(vol(m) - vol(s)) < 0.01: s = m
print('  lid GPS window: volume %+.1f mm3, valid: %s' % (vol(s) - v0, valid(s)))
if not valid(s): sys.exit('  not written')
w = STEPControl_Writer(); w.Transfer(s, STEPControl_AsIs)
if w.Write(P) != IFSelect_RetDone: sys.exit('write failed')
print('  written')
