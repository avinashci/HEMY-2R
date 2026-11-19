"""Remove the RA home marks from side B, the power side (2026-11-15). Knobs east: the base 10 A jack and the dovetail
ports face side B (west) at home, so home is checked from side A (DEC + RA marks there). Fills the RA V-groove on
side plate B's bottom border (X -6, Z 0..8) and on the base flange's side B face (X -6, top 8 mm). Each fill is the groove
volume taken from the same part shifted 3 mm along X, so the edge chamfers come back exactly as the plain edge.
Side B keeps its DEC mark (it lines up with the dovetail only with the knobs west).
Run:  python3 v22_unmark_sideB.py <side plate B in> <out> <flange in> <out>
"""
import sys
from OCP.STEPControl import STEPControl_Reader, STEPControl_Writer, STEPControl_AsIs
from OCP.BRepPrimAPI import BRepPrimAPI_MakeBox
from OCP.BRepBuilderAPI import BRepBuilderAPI_Transform
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common, BRepAlgoAPI_Fuse
from OCP.ShapeUpgrade import ShapeUpgrade_UnifySameDomain
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.ShapeFix import ShapeFix_Shape
from OCP.GProp import GProp_GProps
from OCP.BRepGProp import BRepGProp
from OCP.gp import gp_Pnt, gp_Trsf, gp_Vec
from OCP.IFSelect import IFSelect_RetDone
def read(p):
    r = STEPControl_Reader()
    if r.ReadFile(p) != IFSelect_RetDone: sys.exit('cannot read ' + p)
    r.TransferRoots(); return r.OneShape()
def vol(s):
    g = GProp_GProps(); BRepGProp.VolumeProperties_s(s, g); return g.Mass()
def valid(s): return BRepCheck_Analyzer(s).IsValid()
def unmark(pin, pout, box, label, dx=3.0):
    s = read(pin); v0 = vol(s)
    t = gp_Trsf(); t.SetTranslation(gp_Vec(dx, 0, 0))
    patch = BRepAlgoAPI_Common(BRepBuilderAPI_Transform(s, t, True).Shape(), BRepPrimAPI_MakeBox(gp_Pnt(*box[0]), gp_Pnt(*box[1])).Shape()).Shape()
    s = BRepAlgoAPI_Fuse(s, patch).Shape()
    if not valid(s):
        f = ShapeFix_Shape(s); f.Perform(); s = f.Shape()
    u = ShapeUpgrade_UnifySameDomain(s, True, True, False); u.Build(); m = u.Shape()
    if valid(m) and abs(vol(m) - vol(s)) < 0.01: s = m
    print('  %s: volume %+.2f mm3, valid: %s' % (label, vol(s) - v0, valid(s)))
    if not valid(s): sys.exit('  not written')
    w = STEPControl_Writer(); w.Transfer(s, STEPControl_AsIs); w.Write(pout)
b_in, b_out, f_in, f_out = sys.argv[1:5]
unmark(b_in, b_out, ((-7.0, 61.5, -1.0), (-5.0, 63.0, 9.5)), 'side plate B, RA mark filled')
unmark(f_in, f_out, ((-7.0, 39.0, -17.5), (-5.0, 41.0, -8.0)), 'base flange, side B RA mark filled')
