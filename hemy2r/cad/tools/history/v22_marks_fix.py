"""Re-cut the 1.5 mm x 45° edge chamfer where v22_marks2.py filled the old grooves
(side plate A bottom-outer edge at X -6; lid back-top edge at Y 0). Removes a ~0.13 mm3 nub at each.
Run:  python3 ~/Developer/HEMY/restyle/v2.2/tools/v22_marks_fix.py
"""
import os, sys
from OCP.STEPControl import STEPControl_Reader, STEPControl_Writer, STEPControl_AsIs
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakePolygon, BRepBuilderAPI_MakeFace
from OCP.BRepPrimAPI import BRepPrimAPI_MakePrism
from OCP.BRepAlgoAPI import BRepAlgoAPI_Cut
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.ShapeFix import ShapeFix_Shape
from OCP.GProp import GProp_GProps
from OCP.BRepGProp import BRepGProp
from OCP.gp import gp_Pnt, gp_Vec
from OCP.IFSelect import IFSelect_RetDone
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'parts')
def read(p):
    r = STEPControl_Reader()
    if r.ReadFile(p) != IFSelect_RetDone: sys.exit('cannot read ' + p)
    r.TransferRoots(); return r.OneShape()
def vol(s):
    g = GProp_GProps(); BRepGProp.VolumeProperties_s(s, g); return g.Mass()
def prism(a, b, c, along):
    pg = BRepBuilderAPI_MakePolygon(gp_Pnt(*a), gp_Pnt(*b), gp_Pnt(*c), True)
    return BRepPrimAPI_MakePrism(BRepBuilderAPI_MakeFace(pg.Wire(), True).Face(), gp_Vec(*along)).Shape()
def fix(name, tool):
    p = os.path.join(P, name); s = read(p); v0 = vol(s)
    s = BRepAlgoAPI_Cut(s, tool).Shape()
    if not BRepCheck_Analyzer(s).IsValid():
        f = ShapeFix_Shape(s); f.Perform(); s = f.Shape()
    ok = BRepCheck_Analyzer(s).IsValid()
    print('  %-48s volume %+6.2f mm3  valid: %s' % (name, vol(s) - v0, ok))
    if not ok: sys.exit('  not written')
    w = STEPControl_Writer(); w.Transfer(s, STEPControl_AsIs)
    if w.Write(p) != IFSelect_RetDone: sys.exit('write failed')
# side plate A: chamfer between (Y -62.5, Z 1.5) and (Y -61.0, Z 0), local at X -7..-5
sa = prism((-7, -62.6, -0.1), (-7, -62.6, 1.6), (-7, -60.9, -0.1), (2, 0, 0))
for n in ['HEMY2R - Side plate A.step', 'HEMY2R - Side plate A (recessed panel).step']: fix(n, sa)
# lid: chamfer between (X -69, Z 123.5) and (X -67.5, Z 125), local at Y -1..1
ld = prism((-69.1, -1, 123.4), (-69.1, -1, 125.1), (-67.4, -1, 125.1), (0, 2, 0))
fix('HEMY2R - Lid.step', ld)
print('done')
