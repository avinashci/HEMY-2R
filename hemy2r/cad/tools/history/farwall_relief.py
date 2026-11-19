"""Far walls: replace the three inside connector reliefs with one even rectangle,
38 x 16.1 mm, 3.8 mm deep from the inside face, R1.5 corners. Overwrites both
far-wall files in panels_125cube/. Run:
    python3 ~/Developer/HEMY/restyle/v2.1/tools/farwall_relief.py
"""
import os, sys
from OCP.STEPControl import STEPControl_Reader, STEPControl_Writer, STEPControl_AsIs
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakePolygon, BRepBuilderAPI_MakeFace
from OCP.BRepFilletAPI import BRepFilletAPI_MakeFillet2d
from OCP.BRepPrimAPI import BRepPrimAPI_MakePrism, BRepPrimAPI_MakeBox
from OCP.BRepAlgoAPI import BRepAlgoAPI_Cut, BRepAlgoAPI_Fuse
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

INSIDE, FLOOR = 50.0, 53.8              # inside face and relief floor (X)
Y0, Y1, Z0, Z1, R = -36.0, 2.0, 97.9, 114.0, 1.5

here = os.path.dirname(os.path.abspath(__file__))
folder = os.path.join(here, '..', 'panels_125cube')
files = ['HEMY2R - Far wall USB-C.step', 'HEMY2R - Far wall (recessed panel) USB-C notch.step']

def read(p):
    r = STEPControl_Reader()
    if r.ReadFile(p) != IFSelect_RetDone: sys.exit('cannot read ' + p)
    r.TransferRoots(); return r.OneShape()
def op(cls, a, b):
    o = cls(a, b); o.Build()
    if not o.IsDone(): sys.exit('boolean failed: ' + cls.__name__)
    return o.Shape()
def vol(s):
    g = GProp_GProps(); BRepGProp.VolumeProperties_s(s, g); return g.Mass()
def rrect(x):
    pg = BRepBuilderAPI_MakePolygon(gp_Pnt(x, Y0, Z0), gp_Pnt(x, Y1, Z0), gp_Pnt(x, Y1, Z1), gp_Pnt(x, Y0, Z1), True)
    f = BRepBuilderAPI_MakeFace(pg.Wire(), True).Face()
    fl = BRepFilletAPI_MakeFillet2d(f); ex = TopExp_Explorer(f, TopAbs_VERTEX); seen = []
    while ex.More():
        v = VTX(ex.Current()); ex.Next()
        if not any(v.IsSame(s) for s in seen): seen.append(v); fl.AddFillet(v, R)
    fl.Build(); return fl.Shape()

for name in files:
    p = os.path.join(folder, name); W = read(p); v0 = vol(W)
    W = op(BRepAlgoAPI_Fuse, W, BRepPrimAPI_MakeBox(gp_Pnt(INSIDE, Y0, Z0), gp_Pnt(FLOOR, Y1, Z1)).Shape())
    W = op(BRepAlgoAPI_Cut, W, BRepPrimAPI_MakePrism(rrect(INSIDE - 1), gp_Vec(FLOOR - INSIDE + 1, 0, 0)).Shape())
    if not BRepCheck_Analyzer(W).IsValid():
        f = ShapeFix_Shape(W); f.Perform(); W = f.Shape()
    print('%s\n  volume %.1f -> %.1f (removed %.1f mm3), valid: %s' % (name, v0, vol(W), v0 - vol(W), BRepCheck_Analyzer(W).IsValid()))
    if not BRepCheck_Analyzer(W).IsValid(): sys.exit('  not written (invalid)')
    w = STEPControl_Writer(); w.Transfer(W, STEPControl_AsIs)
    if w.Write(p) != IFSelect_RetDone: sys.exit('write failed')
    print('  written')
