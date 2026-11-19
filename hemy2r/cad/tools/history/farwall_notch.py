"""Recessed far wall: step the panel pocket around the USB-C window, leaving a
7.3 mm raised land round the window (same as port-to-edge), notch corner R6, turns R5. Run:
    python3 ~/Developer/HEMY/restyle/v2.1/tools/farwall_notch.py
Writes panels_125cube/HEMY2R - Far wall (recessed panel) USB-C notch.step
Already run 2026-11-06; its source (the old recessed far wall) has since been deleted. Kept as a record.
"""
import os, sys
from OCP.STEPControl import STEPControl_Reader, STEPControl_Writer, STEPControl_AsIs
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakePolygon, BRepBuilderAPI_MakeFace
from OCP.BRepFilletAPI import BRepFilletAPI_MakeFillet2d
from OCP.BRepOffsetAPI import BRepOffsetAPI_MakeOffset, BRepOffsetAPI_ThruSections
from OCP.BRepPrimAPI import BRepPrimAPI_MakePrism, BRepPrimAPI_MakeBox
from OCP.BRepAlgoAPI import BRepAlgoAPI_Cut, BRepAlgoAPI_Fuse
from OCP.ShapeUpgrade import ShapeUpgrade_UnifySameDomain
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.GProp import GProp_GProps
from OCP.BRepGProp import BRepGProp
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_VERTEX, TopAbs_FACE
from OCP.TopoDS import TopoDS
from OCP.BRepTools import BRepTools
from OCP.GeomAbs import GeomAbs_Arc
from OCP.gp import gp_Pnt, gp_Vec
from OCP.IFSelect import IFSelect_RetDone

def _cast(name):
    f = getattr(TopoDS, name + '_s', None) or getattr(TopoDS, name)
    return f
VTX, WIRE, FACE_ = _cast('Vertex'), _cast('Wire'), _cast('Face')
OUTER_WIRE = getattr(BRepTools, 'OuterWire_s', None) or getattr(BRepTools, 'OuterWire')

FLOOR, LIP, FACE = 55.2, 55.6, 56.0          # pocket floor, chamfer start, outer face (X)
POCKET = (-40.5, 40.5, 16.0, 109.0, 6.0)      # Y0, Y1, Z0, Z1, corner R
WINDOW = (-49.2, -36.8, 104.7, 111.3, 1.6)    # USB-C window
LAND, INNER_R, CH = 7.3, 5.0, 0.4
LAND_R = 6.0                                  # land corner radius (matches pocket R6)

here = os.path.dirname(os.path.abspath(__file__))
src = os.path.join(here, '..', 'panels_125cube', 'HEMY2R - Far wall (recessed panel) USB-C.step')
dst = os.path.join(here, '..', 'panels_125cube', 'HEMY2R - Far wall (recessed panel) USB-C notch.step')

def read(p):
    r = STEPControl_Reader()
    if r.ReadFile(p) != IFSelect_RetDone: sys.exit('cannot read ' + p)
    r.TransferRoots(); return r.OneShape()
def rrect(x, y0, y1, z0, z1, rad):
    pg = BRepBuilderAPI_MakePolygon(gp_Pnt(x, y0, z0), gp_Pnt(x, y1, z0), gp_Pnt(x, y1, z1), gp_Pnt(x, y0, z1), True)
    f = BRepBuilderAPI_MakeFace(pg.Wire(), True).Face()
    fl = BRepFilletAPI_MakeFillet2d(f)
    ex = TopExp_Explorer(f, TopAbs_VERTEX); seen = []
    while ex.More():
        v = VTX(ex.Current())
        if not any(v.IsSame(s) for s in seen): seen.append(v); fl.AddFillet(v, rad)
        ex.Next()
    fl.Build(); return fl.Shape()
def op(cls, a, b):
    o = cls(a, b); o.Build()
    if not o.IsDone(): sys.exit('boolean failed: ' + cls.__name__)
    return o.Shape()
def first_face(s):
    ex = TopExp_Explorer(s, TopAbs_FACE); return FACE_(ex.Current())
def offset(face, d):
    o = BRepOffsetAPI_MakeOffset(face, GeomAbs_Arc); o.Perform(d); return o.Shape()   # a wire
def face_of(wire_shape):
    return BRepBuilderAPI_MakeFace(WIRE(wire_shape), True).Face()
def vol(s):
    g = GProp_GProps(); BRepGProp.VolumeProperties_s(s, g); return g.Mass()

y0, y1, z0, z1, r = POCKET; wy0, wy1, wz0, wz1, wr = WINDOW
pocket = rrect(FLOOR, y0, y1, z0, z1, r)
land = rrect(FLOOR, wy0 - LAND, wy1 + LAND, wz0 - LAND, wz1 + LAND, LAND_R)
P = first_face(op(BRepAlgoAPI_Cut, pocket, land))
P = face_of(offset(face_of(offset(P, -INNER_R)), INNER_R))    # round the two new inside corners

from OCP.gp import gp_Trsf
from OCP.BRepBuilderAPI import BRepBuilderAPI_Transform
def at_x(shape, x):
    t = gp_Trsf(); t.SetTranslation(gp_Vec(x - FLOOR, 0, 0)); return BRepBuilderAPI_Transform(shape, t, True).Shape()
W = read(src); v0 = vol(W)
def ok(tag, shape):
    print('  %-28s valid: %s' % (tag, BRepCheck_Analyzer(shape).IsValid()))
    return shape
ok('original far wall', W)
fill = BRepPrimAPI_MakeBox(gp_Pnt(FLOOR, y0 - 1, z0 - 1), gp_Pnt(FACE, y1 + 1, z1 + 1)).Shape()
W = ok('old pocket filled', op(BRepAlgoAPI_Fuse, W, fill))
tool = BRepPrimAPI_MakePrism(P, gp_Vec(FACE - FLOOR + 0.5, 0, 0)).Shape()
W = ok('new pocket cut', op(BRepAlgoAPI_Cut, W, tool))
win = BRepPrimAPI_MakePrism(rrect(49.0, wy0, wy1, wz0, wz1, wr), gp_Vec(8, 0, 0)).Shape()
W = ok('window re-cut', op(BRepAlgoAPI_Cut, W, win))
u = ShapeUpgrade_UnifySameDomain(W, True, True, False); u.Build()
if BRepCheck_Analyzer(u.Shape()).IsValid(): W = ok('faces merged', u.Shape())
else: print('  faces merged                 skipped (merge made it invalid)')
# lip chamfer: cut a 45-degree loft from the pocket outline at X 55.6 to the outline grown 0.4 at X 56.0
OUTER = getattr(BRepTools, 'OuterWire_s', None) or getattr(BRepTools, 'OuterWire')
w_lo = WIRE(at_x(OUTER(P), LIP))
w_hi = WIRE(at_x(offset(P, CH), FACE))
lo = BRepOffsetAPI_ThruSections(True, True); lo.AddWire(w_lo); lo.AddWire(w_hi); lo.CheckCompatibility(True); lo.Build()
cham = lo.Shape()
print('  %-28s valid: %s' % ('chamfer tool', BRepCheck_Analyzer(cham).IsValid()))
Wc = op(BRepAlgoAPI_Cut, W, cham)
if BRepCheck_Analyzer(Wc).IsValid(): W = ok('lip chamfer cut', Wc)
else: print('  lip chamfer cut              skipped (would be invalid) - pocket edge left sharp')
if not BRepCheck_Analyzer(W).IsValid():
    from OCP.ShapeFix import ShapeFix_Shape
    f = ShapeFix_Shape(W); f.Perform(); W = ok('after ShapeFix', f.Shape())
print('volume before %.1f, after %.1f, added %.1f mm3 (the new land)' % (v0, vol(W), vol(W) - v0))
print('geometry valid:', BRepCheck_Analyzer(W).IsValid())
w = STEPControl_Writer(); w.Transfer(W, STEPControl_AsIs)
if w.Write(dst) != IFSelect_RetDone: sys.exit('write failed')
print('written:', dst)
