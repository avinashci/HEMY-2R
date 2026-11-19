"""Dovetail DEC index mark: move it from the outer end to the inner (body) end of the side B face.
Fill the old groove (X -108.5..-100), re-cut the 0.5 mm outer edge chamfer there, cut the new groove
at Z 70 from the inner edge (X -80.5) outward 8 mm, then merge flush faces.
Run:  python3 ~/Developer/HEMY/restyle/v2.2/tools/v22_marks3.py
"""
import os, sys
from OCP.STEPControl import STEPControl_Reader, STEPControl_Writer, STEPControl_AsIs
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakePolygon, BRepBuilderAPI_MakeFace
from OCP.BRepPrimAPI import BRepPrimAPI_MakePrism, BRepPrimAPI_MakeBox
from OCP.BRepAlgoAPI import BRepAlgoAPI_Cut, BRepAlgoAPI_Fuse, BRepAlgoAPI_Common
from OCP.ShapeUpgrade import ShapeUpgrade_UnifySameDomain
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.ShapeFix import ShapeFix_Shape
from OCP.GProp import GProp_GProps
from OCP.BRepGProp import BRepGProp
from OCP.gp import gp_Pnt, gp_Vec
from OCP.IFSelect import IFSelect_RetDone
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'parts', 'HEMY2R - Dovetail (indicator LED hole).step')
D, OUT = 0.3, 0.3; k = D + OUT
def read(p):
    r = STEPControl_Reader()
    if r.ReadFile(p) != IFSelect_RetDone: sys.exit('cannot read ' + p)
    r.TransferRoots(); return r.OneShape()
def vol(s):
    g = GProp_GProps(); BRepGProp.VolumeProperties_s(s, g); return g.Mass()
def prism(a, b, c, along):
    pg = BRepBuilderAPI_MakePolygon(gp_Pnt(*a), gp_Pnt(*b), gp_Pnt(*c), True)
    return BRepPrimAPI_MakePrism(BRepBuilderAPI_MakeFace(pg.Wire(), True).Face(), gp_Vec(*along)).Shape()
def valid(s): return BRepCheck_Analyzer(s).IsValid()
s = read(P); v0 = vol(s)
old = prism((-108.6, 50 - D, 70.0), (-108.6, 50 + OUT, 70.0 - k), (-108.6, 50 + OUT, 70.0 + k), (8.6, 0, 0))
s = BRepAlgoAPI_Fuse(s, BRepAlgoAPI_Common(old, BRepPrimAPI_MakeBox(gp_Pnt(-108.5, 49.5, 69), gp_Pnt(-100.0, 50.0, 71)).Shape()).Shape()).Shape()
ch = prism((-108.6, 49.4, 69.0), (-108.6, 50.1, 69.0), (-107.9, 50.1, 69.0), (0, 0, 2.0))     # 0.5 mm 45° edge chamfer, local
s = BRepAlgoAPI_Cut(s, ch).Shape()
v1 = vol(s)
new = prism((-80.2, 50 - D, 70.0), (-80.2, 50 + OUT, 70.0 - k), (-80.2, 50 + OUT, 70.0 + k), (-8.3, 0, 0))
s = BRepAlgoAPI_Cut(s, new).Shape()
if not valid(s):
    f = ShapeFix_Shape(s); f.Perform(); s = f.Shape()
u = ShapeUpgrade_UnifySameDomain(s, True, True, False); u.Build(); m = u.Shape()
if valid(m) and abs(vol(m) - vol(s)) < 0.01: s = m; merged = 'faces merged'
else: merged = 'faces left as is'
print('  old groove filled: %+.2f mm3; new groove: %+.2f mm3; %s; valid: %s' % (v1 - v0, vol(s) - v1, merged, valid(s)))
if not valid(s): sys.exit('  not written')
w = STEPControl_Writer(); w.Transfer(s, STEPControl_AsIs)
if w.Write(P) != IFSelect_RetDone: sys.exit('write failed')
print('  written: dovetail with the DEC mark at the inner end')
