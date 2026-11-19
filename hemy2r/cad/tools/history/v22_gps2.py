"""Lid GPS window, revision 2: patch flush with the lid top under a sticker.
Fill the 27.2 x 40.2 x 1 mm cover step from v22_gps.py back in, keeping the 25.5 x 25.5 x 5 mm antenna pocket
(R1) and the Ø4 lead hole. The patch sits on a 1 mm foam pad so its top is flush; a non-metallic
'HEMY V2' sticker (~40 x 27 mm) goes over it. Edits the lid in place.
Run:  python3 ~/Developer/HEMY/restyle/v2.2/tools/v22_gps2.py
"""
import os, sys
from OCP.STEPControl import STEPControl_Reader, STEPControl_Writer, STEPControl_AsIs
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakePolygon, BRepBuilderAPI_MakeFace
from OCP.BRepFilletAPI import BRepFilletAPI_MakeFillet2d
from OCP.BRepPrimAPI import BRepPrimAPI_MakePrism
from OCP.BRepAlgoAPI import BRepAlgoAPI_Cut, BRepAlgoAPI_Fuse
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
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'parts', 'HEMY2R - Lid.step')
CX, CY, TOP = -40.0, 0.0, 125.0
def read(p):
    r = STEPControl_Reader()
    if r.ReadFile(p) != IFSelect_RetDone: sys.exit('cannot read ' + p)
    r.TransferRoots(); return r.OneShape()
def vol(s):
    g = GProp_GProps(); BRepGProp.VolumeProperties_s(s, g); return g.Mass()
def valid(s): return BRepCheck_Analyzer(s).IsValid()
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
s = read(P); v0 = vol(s)
s = BRepAlgoAPI_Fuse(s, rr(27.2, 40.2, 3.0, TOP - 1.0, TOP)).Shape()            # fill the cover step (exactly to the lid top)
s = BRepAlgoAPI_Cut(s, rr(25.5, 25.5, 1.0, TOP - 5.0, TOP + 1)).Shape()          # re-open the antenna pocket through it
if not valid(s):
    f = ShapeFix_Shape(s); f.Perform(); s = f.Shape()
u = ShapeUpgrade_UnifySameDomain(s, True, True, False); u.Build(); m = u.Shape()
if valid(m) and abs(vol(m) - vol(s)) < 0.01: s = m
print('  lid GPS pocket (sticker version): volume %+.1f mm3, valid: %s' % (vol(s) - v0, valid(s)))
if not valid(s): sys.exit('  not written')
w = STEPControl_Writer(); w.Transfer(s, STEPControl_AsIs)
if w.Write(P) != IFSelect_RetDone: sys.exit('write failed')
print('  written')
