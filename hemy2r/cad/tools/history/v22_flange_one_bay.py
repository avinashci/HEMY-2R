"""Base flange: one bay for the 10 A jack and the LED (2026-11-15). The LED moves into the jack's bay at X -32
(10 mm outboard of the jack at X -22, its original position); the second bay (X ~3.5..22), its wire slot to the centre
hole and the LED hole at X 10 are filled solid. The fill is exactly the empty space of that bay and slot (box minus the
part, minus the centre hole), so no other hole or edge changes.
Run:  python3 v22_flange_one_bay.py <flange in> <flange out>
"""
import sys
from OCP.STEPControl import STEPControl_Reader, STEPControl_Writer, STEPControl_AsIs
from OCP.BRepPrimAPI import BRepPrimAPI_MakeBox, BRepPrimAPI_MakeCylinder
from OCP.BRepAlgoAPI import BRepAlgoAPI_Fuse, BRepAlgoAPI_Cut
from OCP.ShapeUpgrade import ShapeUpgrade_UnifySameDomain
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.ShapeFix import ShapeFix_Shape
from OCP.GProp import GProp_GProps
from OCP.BRepGProp import BRepGProp
from OCP.gp import gp_Pnt, gp_Ax2, gp_Dir
from OCP.IFSelect import IFSelect_RetDone
X0, ZB, ZJ = -6.0, -27.5, -19.5
def read(p):
    r = STEPControl_Reader()
    if r.ReadFile(p) != IFSelect_RetDone: sys.exit('cannot read ' + p)
    r.TransferRoots(); return r.OneShape()
def vol(s):
    g = GProp_GProps(); BRepGProp.VolumeProperties_s(s, g); return g.Mass()
def valid(s): return BRepCheck_Analyzer(s).IsValid()
s = read(sys.argv[1]); v0 = vol(s)
region = BRepPrimAPI_MakeBox(gp_Pnt(X0 + 2.0, 8.0, ZB), gp_Pnt(X0 + 28.6, 39.0, -12.4)).Shape()     # bay + slot, inside the outer faces
voids = BRepAlgoAPI_Cut(region, s).Shape()
voids = BRepAlgoAPI_Cut(voids, BRepPrimAPI_MakeCylinder(gp_Ax2(gp_Pnt(X0, 0, ZB - 1), gp_Dir(0, 0, 1)), 6.5, 30).Shape()).Shape()   # keep the centre hole
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_SOLID
ex = TopExp_Explorer(voids, TopAbs_SOLID); pieces = []
while ex.More(): pieces.append(ex.Current()); ex.Next()
bay = max(pieces, key=vol)                                                       # the bay + slot; leaves the M3 holes in the box alone
s = BRepAlgoAPI_Fuse(s, bay).Shape()
s = BRepAlgoAPI_Fuse(s, BRepPrimAPI_MakeCylinder(gp_Ax2(gp_Pnt(X0 + 16.0, 34.5, ZJ), gp_Dir(0, 1, 0)), 1.56, 5.5).Shape()).Shape()   # old LED hole X 10
s = BRepAlgoAPI_Cut(s, BRepPrimAPI_MakeCylinder(gp_Ax2(gp_Pnt(X0 - 26.0, 34.0, ZJ), gp_Dir(0, 1, 0)), 1.55, 7.0).Shape()).Shape()   # new LED hole X -32
if not valid(s):
    f = ShapeFix_Shape(s); f.Perform(); s = f.Shape()
u = ShapeUpgrade_UnifySameDomain(s, True, True, False); u.Build(); m = u.Shape()
if valid(m) and abs(vol(m) - vol(s)) < 0.01: s = m
print('  flange one bay: volume %+.1f mm3 (%.0f g), valid: %s' % (vol(s) - v0, vol(s) * 2.7e-3, valid(s)))
if not valid(s): sys.exit('  not written')
w = STEPControl_Writer(); w.Transfer(s, STEPControl_AsIs)
if w.Write(sys.argv[2]) != IFSelect_RetDone: sys.exit('write failed')
