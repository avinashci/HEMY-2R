"""Home index marks on both sides (2026-11-14). Side B already has them (DEC groove at Z 70 from the back edge to the
recess; RA groove at X -6 from the bottom edge to the recess); the flange's +Y face has the RA partner and the dovetail's
+Y (knob) face the DEC partner. Side B's marks are 8 mm long. This adds the same 8 mm marks on side A:
  side plate A  : DEC groove Z 70, X -69..-61 (from the back edge) ; RA groove X -6, Z 0..8 (from the bottom edge)  (-Y face)
  base flange   : RA groove X -6, Z -16.5..-8.5 (from the top edge) on the -Y face
The dovetail keeps its single mark (knob face, Z 70, X -88.5..-80.5): at home (knobs east = DEC turned 180 deg from
the CAD pose) it lines up with side A; with knobs west it lines up with side B. No mark on the port face.
All 90 deg V-grooves, 0.3 mm deep, as the existing ones. Fill with white engraving crayon.
Run:  python3 v22_marks_both.py <sideA in> <sideA out> <flange in> <flange out>
"""
import sys
from OCP.STEPControl import STEPControl_Reader, STEPControl_Writer, STEPControl_AsIs
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakePolygon, BRepBuilderAPI_MakeFace
from OCP.BRepPrimAPI import BRepPrimAPI_MakePrism
from OCP.BRepAlgoAPI import BRepAlgoAPI_Cut
from OCP.ShapeUpgrade import ShapeUpgrade_UnifySameDomain
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.ShapeFix import ShapeFix_Shape
from OCP.GProp import GProp_GProps
from OCP.BRepGProp import BRepGProp
from OCP.gp import gp_Pnt, gp_Vec
from OCP.IFSelect import IFSelect_RetDone
D, OUT = 0.3, 0.3; K = D + OUT
def read(p):
    r = STEPControl_Reader()
    if r.ReadFile(p) != IFSelect_RetDone: sys.exit('cannot read ' + p)
    r.TransferRoots(); return r.OneShape()
def vol(s):
    g = GProp_GProps(); BRepGProp.VolumeProperties_s(s, g); return g.Mass()
def valid(s): return BRepCheck_Analyzer(s).IsValid()
def vgroove_y(yface, out_sign, along, fixed, a0, a1):
    """V-groove on a face normal to Y at y=yface (outward = out_sign); runs along 'x' (at z=fixed) or 'z' (at x=fixed)."""
    ya, yb = yface - out_sign * D, yface + out_sign * OUT
    if along == 'x':
        tri = [(a0, ya, fixed), (a0, yb, fixed - K), (a0, yb, fixed + K)]; vec = gp_Vec(a1 - a0, 0, 0)
    else:
        tri = [(fixed, ya, a0), (fixed - K, yb, a0), (fixed + K, yb, a0)]; vec = gp_Vec(0, 0, a1 - a0)
    pg = BRepBuilderAPI_MakePolygon(*[gp_Pnt(*p) for p in tri], True)
    return BRepPrimAPI_MakePrism(BRepBuilderAPI_MakeFace(pg.Wire(), True).Face(), vec).Shape()
def apply(pin, pout, grooves, label):
    s = read(pin); v0 = vol(s)
    for g in grooves: s = BRepAlgoAPI_Cut(s, g).Shape()
    if not valid(s):
        f = ShapeFix_Shape(s); f.Perform(); s = f.Shape()
    u = ShapeUpgrade_UnifySameDomain(s, True, True, False); u.Build(); m = u.Shape()
    if valid(m) and abs(vol(m) - vol(s)) < 0.01: s = m
    print('  %s: volume %+.2f mm3, valid: %s' % (label, vol(s) - v0, valid(s)))
    if not valid(s): sys.exit('  not written')
    w = STEPControl_Writer(); w.Transfer(s, STEPControl_AsIs)
    if w.Write(pout) != IFSelect_RetDone: sys.exit('write failed')
a_in, a_out, f_in, f_out = sys.argv[1:5]
apply(a_in, a_out, [vgroove_y(-62.5, -1, 'x', 70.0, -69.5, -61.0), vgroove_y(-62.5, -1, 'z', -6.0, -0.5, 8.0)], 'side plate A')
apply(f_in, f_out, [vgroove_y(-40.0, -1, 'z', -6.0, -16.5, -8.0)], 'base flange')
