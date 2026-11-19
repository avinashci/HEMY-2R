"""Base flange: single 10 A input (M7, 2026-11-15). The side B face had two M12 jacks (X -22 and X 10) and two Dia 3.1
LEDs (X -32 and X 20). Keeps the jack at X -22 (16 mm one side of the RA home mark at X -6), fills the X 10 jack and both
old LED holes, and cuts one Dia 3.1 LED hole at X 10 (16 mm the other side of the mark), into the existing bay.
All at Z -19.5. The 5 mm wall (Y 35..40) is refilled where needed.
Run:  python3 v22_flange_single_jack.py <flange in> <flange out>
"""
import sys
from OCP.STEPControl import STEPControl_Reader, STEPControl_Writer, STEPControl_AsIs
from OCP.BRepPrimAPI import BRepPrimAPI_MakeCylinder
from OCP.BRepAlgoAPI import BRepAlgoAPI_Cut, BRepAlgoAPI_Fuse
from OCP.ShapeUpgrade import ShapeUpgrade_UnifySameDomain
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.ShapeFix import ShapeFix_Shape
from OCP.GProp import GProp_GProps
from OCP.BRepGProp import BRepGProp
from OCP.gp import gp_Pnt, gp_Ax2, gp_Dir
from OCP.IFSelect import IFSelect_RetDone
ZJ, Y_BAY, Y_FACE = -19.5, 35.0, 40.0
def read(p):
    r = STEPControl_Reader()
    if r.ReadFile(p) != IFSelect_RetDone: sys.exit('cannot read ' + p)
    r.TransferRoots(); return r.OneShape()
def vol(s):
    g = GProp_GProps(); BRepGProp.VolumeProperties_s(s, g); return g.Mass()
def valid(s): return BRepCheck_Analyzer(s).IsValid()
def ycyl(x, r, y0, y1): return BRepPrimAPI_MakeCylinder(gp_Ax2(gp_Pnt(x, y0, ZJ), gp_Dir(0, 1, 0)), r, y1 - y0).Shape()
s = read(sys.argv[1]); v0 = vol(s)
for x, r in ((10.0, 5.51), (-32.0, 1.56), (20.0, 1.56)): s = BRepAlgoAPI_Fuse(s, ycyl(x, r, Y_BAY, Y_FACE)).Shape()
s = BRepAlgoAPI_Cut(s, ycyl(10.0, 1.55, Y_BAY - 1, Y_FACE + 1)).Shape()
if not valid(s):
    f = ShapeFix_Shape(s); f.Perform(); s = f.Shape()
u = ShapeUpgrade_UnifySameDomain(s, True, True, False); u.Build(); m = u.Shape()
if valid(m) and abs(vol(m) - vol(s)) < 0.01: s = m
print('  flange single jack: volume %+.1f mm3 (%.0f g), valid: %s' % (vol(s) - v0, vol(s) * 2.7e-3, valid(s)))
if not valid(s): sys.exit('  not written')
w = STEPControl_Writer(); w.Transfer(s, STEPControl_AsIs)
if w.Write(sys.argv[2]) != IFSelect_RetDone: sys.exit('write failed')
