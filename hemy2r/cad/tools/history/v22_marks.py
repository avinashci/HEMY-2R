"""Home-position index marks (90° V-groove, 0.3 deep, 8 long), cut into the v2.2 parts in place.
DEC: lid top face, centred (Y 0), from the back edge (X -69) inward.
RA:  both side plates (outer faces Y -62.5 and +62.5), bottom border, vertical, in line with the RA axis (X -6).
Run:  python3 ~/Developer/HEMY/restyle/v2.2/tools/v22_marks.py
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
D, W, L, OUT = 0.3, 0.3, 8.0, 0.3       # depth, half-width at surface (90° V), length, overshoot outside the face

def read(p):
    r = STEPControl_Reader()
    if r.ReadFile(p) != IFSelect_RetDone: sys.exit('cannot read ' + p)
    r.TransferRoots(); return r.OneShape()
def vol(s):
    g = GProp_GProps(); BRepGProp.VolumeProperties_s(s, g); return g.Mass()
def vgroove(p_apex, p_left, p_right, along):
    pg = BRepBuilderAPI_MakePolygon(gp_Pnt(*p_apex), gp_Pnt(*p_left), gp_Pnt(*p_right), True)
    return BRepPrimAPI_MakePrism(BRepBuilderAPI_MakeFace(pg.Wire(), True).Face(), gp_Vec(*along)).Shape()
def apply(name, tool):
    p = os.path.join(P, name); s = read(p); v0 = vol(s)
    s = BRepAlgoAPI_Cut(s, tool).Shape()
    if not BRepCheck_Analyzer(s).IsValid():
        f = ShapeFix_Shape(s); f.Perform(); s = f.Shape()
    ok = BRepCheck_Analyzer(s).IsValid()
    print('  %-48s volume %+6.2f mm3  valid: %s' % (name, vol(s) - v0, ok))
    if not ok: sys.exit('  not written')
    w = STEPControl_Writer(); w.Transfer(s, STEPControl_AsIs)
    if w.Write(p) != IFSelect_RetDone: sys.exit('write failed')

# DEC: lid top (Z 125); groove runs along +X from X -69.5 (just past the back edge) to -61
k = D + OUT                                       # profile in the YZ plane, apex down
dec = vgroove((-69.5, 0.0, 125 - D), (-69.5, -k, 125 + OUT), (-69.5, k, 125 + OUT), (L + 0.5, 0, 0))
apply('HEMY2R - Lid.step', dec)

# RA: side plate A outer face (Y -62.5); groove runs along +Z from Z -0.5 (just below the bottom edge) to 8
ra = vgroove((-6.0, -62.5 + D, -0.5), (-6.0 - k, -62.5 - OUT, -0.5), (-6.0 + k, -62.5 - OUT, -0.5), (0, 0, L + 0.5))
for n in ['HEMY2R - Side plate A.step', 'HEMY2R - Side plate A (recessed panel).step']:
    apply(n, ra)
# RA mirror: side plate B outer face (Y +62.5)
rb = vgroove((-6.0, 62.5 - D, -0.5), (-6.0 - k, 62.5 + OUT, -0.5), (-6.0 + k, 62.5 + OUT, -0.5), (0, 0, L + 0.5))
for n in ['HEMY2R - Side plate B.step', 'HEMY2R - Side plate B (recessed panel).step']:
    apply(n, rb)
print('done')
