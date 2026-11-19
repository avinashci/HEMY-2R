"""Remove the DEC home mark from side plate B (2026-11-16). Home is set and checked from side A only (knobs east), so
side B carries just the HEMY 2R logo. Fills the 8 mm V-groove on side B's DEC-end border (X -69..-61, Z 70) with the
groove volume taken from the same part shifted 4 mm along Z, so the edge chamfer comes back as the plain edge.
Run:  python3 v22_unmark_sideB_dec.py <side plate B in> <out>
"""
import sys
from OCP.STEPControl import STEPControl_Reader, STEPControl_Writer, STEPControl_AsIs
from OCP.BRepPrimAPI import BRepPrimAPI_MakeBox
from OCP.BRepBuilderAPI import BRepBuilderAPI_Transform
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common, BRepAlgoAPI_Fuse
from OCP.ShapeUpgrade import ShapeUpgrade_UnifySameDomain
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.GProp import GProp_GProps
from OCP.BRepGProp import BRepGProp
from OCP.gp import gp_Pnt, gp_Trsf, gp_Vec
from OCP.IFSelect import IFSelect_RetDone
def vol(s):
    g = GProp_GProps(); BRepGProp.VolumeProperties_s(s, g); return g.Mass()
r = STEPControl_Reader(); assert r.ReadFile(sys.argv[1]) == IFSelect_RetDone; r.TransferRoots(); s = r.OneShape(); v0 = vol(s)
t = gp_Trsf(); t.SetTranslation(gp_Vec(0, 0, 4.0))
patch = BRepAlgoAPI_Common(BRepBuilderAPI_Transform(s, t, True).Shape(),
                           BRepPrimAPI_MakeBox(gp_Pnt(-70.0, 60.5, 68.0), gp_Pnt(-59.5, 63.0, 72.0)).Shape()).Shape()
s = BRepAlgoAPI_Fuse(s, patch).Shape()
u = ShapeUpgrade_UnifySameDomain(s, True, True, False); u.Build(); m = u.Shape()
if BRepCheck_Analyzer(m).IsValid() and abs(vol(m) - vol(s)) < 0.01: s = m
ok = BRepCheck_Analyzer(s).IsValid()
print('  side plate B, DEC mark filled: volume %+.2f mm3, valid: %s' % (vol(s) - v0, ok)); assert ok
w = STEPControl_Writer(); w.Transfer(s, STEPControl_AsIs); assert w.Write(sys.argv[2]) == IFSelect_RetDone; print('  written')
