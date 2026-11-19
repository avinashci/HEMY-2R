"""Lid: handle moved to X -11 (in line with the side A USB-C window), holes countersunk from below (2026-11-14).
Fills the old M5 clearance holes at (X -12.5, Y +/-44) and cuts new ones at (X -11, Y +/-44): Dia 5.5 through, with a
90 deg countersink on the underside (Dia 10.4 at the underside, 2.45 deep) for ISO 10642 M5 flat-head screws, which sit
flush inside the box. 3.55 mm of straight bore remains.
Run:  python3 v22_lid_handle.py <lid in> <lid out>
"""
import sys, math
from OCP.STEPControl import STEPControl_Reader, STEPControl_Writer, STEPControl_AsIs
from OCP.BRepPrimAPI import BRepPrimAPI_MakeCylinder, BRepPrimAPI_MakeCone
from OCP.BRepAlgoAPI import BRepAlgoAPI_Cut, BRepAlgoAPI_Fuse
from OCP.ShapeUpgrade import ShapeUpgrade_UnifySameDomain
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.ShapeFix import ShapeFix_Shape
from OCP.GProp import GProp_GProps
from OCP.BRepGProp import BRepGProp
from OCP.gp import gp_Pnt, gp_Ax2, gp_Dir
from OCP.IFSelect import IFSelect_RetDone
BOT, TOP = 119.0, 125.0
OLD_X, NEW_X, YS = -12.5, -11.0, (-44.0, 44.0)
R_HOLE, R_CSK = 2.75, 5.2
def read(p):
    r = STEPControl_Reader()
    if r.ReadFile(p) != IFSelect_RetDone: sys.exit('cannot read ' + p)
    r.TransferRoots(); return r.OneShape()
def vol(s):
    g = GProp_GProps(); BRepGProp.VolumeProperties_s(s, g); return g.Mass()
def valid(s): return BRepCheck_Analyzer(s).IsValid()
def cyl(x, y, r, z0, z1): return BRepPrimAPI_MakeCylinder(gp_Ax2(gp_Pnt(x, y, z0), gp_Dir(0, 0, 1)), r, z1 - z0).Shape()
s = read(sys.argv[1]); v0 = vol(s)
for y in YS: s = BRepAlgoAPI_Fuse(s, cyl(OLD_X, y, R_HOLE + 0.01, BOT, TOP)).Shape()       # fill the old holes
for y in YS:
    s = BRepAlgoAPI_Cut(s, cyl(NEW_X, y, R_HOLE, BOT - 1, TOP + 1)).Shape()
    h = R_CSK - R_HOLE                                                                    # 90 deg: depth = radius step
    cone = BRepPrimAPI_MakeCone(gp_Ax2(gp_Pnt(NEW_X, y, BOT - 1), gp_Dir(0, 0, 1)), R_CSK + 1, R_HOLE, h + 1).Shape()
    s = BRepAlgoAPI_Cut(s, cone).Shape()
if not valid(s):
    f = ShapeFix_Shape(s); f.Perform(); s = f.Shape()
u = ShapeUpgrade_UnifySameDomain(s, True, True, False); u.Build(); m = u.Shape()
if valid(m) and abs(vol(m) - vol(s)) < 0.01: s = m
exp = 2 * (-(math.pi / 3) * h * (R_CSK**2 + R_CSK * R_HOLE + R_HOLE**2) + math.pi * R_HOLE**2 * h)
print('  lid handle holes: volume %+.2f mm3 (expected %+.2f), valid: %s' % (vol(s) - v0, exp, valid(s)))
if not valid(s): sys.exit('  not written')
w = STEPControl_Writer(); w.Transfer(s, STEPControl_AsIs)
if w.Write(sys.argv[2]) != IFSelect_RetDone: sys.exit('write failed')
