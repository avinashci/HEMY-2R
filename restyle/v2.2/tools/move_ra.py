"""Move the RA reducer seat (bore pocket, through hole, bolt circle) in the
v2.1 L-plate floor 6 mm toward the back wall (-X). Run:
    python3 ~/Developer/HEMY/restyle/v2.1/tools/move_ra.py
Writes option1_cube_Lplate/HEMY2R - L-plate (125 cube, RA -6).step
Already run 2026-11-06; its source (the unshifted L-plate) has since been deleted. Kept as a record of the edit.
"""
import os, sys
from OCP.STEPControl import STEPControl_Reader, STEPControl_Writer, STEPControl_AsIs
from OCP.BRepPrimAPI import BRepPrimAPI_MakeCylinder
from OCP.BRepAlgoAPI import BRepAlgoAPI_Fuse, BRepAlgoAPI_Cut, BRepAlgoAPI_Common
from OCP.BRepBuilderAPI import BRepBuilderAPI_Transform
from OCP.ShapeUpgrade import ShapeUpgrade_UnifySameDomain
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.GProp import GProp_GProps
from OCP.BRepGProp import BRepGProp
from OCP.gp import gp_Ax2, gp_Pnt, gp_Dir, gp_Trsf, gp_Vec
from OCP.IFSelect import IFSelect_RetDone

SHIFT = -6.0          # mm along X (toward the back wall)
R = 41.5              # disc radius: just outside the Ø80.5 pocket (r 40.25)
FLOOR = (0.0, 9.0)    # floor thickness, Z

here = os.path.dirname(os.path.abspath(__file__))
src = os.path.join(here, '..', 'option1_cube_Lplate', 'HEMY2R - L-plate (125 cube).step')
dst = os.path.join(here, '..', 'option1_cube_Lplate', 'HEMY2R - L-plate (125 cube, RA -6).step')

def read(p):
    r = STEPControl_Reader()
    if r.ReadFile(p) != IFSelect_RetDone: sys.exit('cannot read ' + p)
    r.TransferRoots(); return r.OneShape()
def cyl(x, z0, z1, r=R):
    return BRepPrimAPI_MakeCylinder(gp_Ax2(gp_Pnt(x, 0, z0), gp_Dir(0, 0, 1)), r, z1 - z0).Shape()
def vol(s):
    g = GProp_GProps(); BRepGProp.VolumeProperties_s(s, g); return g.Mass()
def op(cls, a, b):
    o = cls(a, b); o.Build()
    if not o.IsDone(): sys.exit('boolean failed: ' + cls.__name__)
    return o.Shape()

L = read(src)
core = op(BRepAlgoAPI_Common, L, cyl(0, FLOOR[0] - 1, FLOOR[1] + 1))   # the seat pattern as it is now
t = gp_Trsf(); t.SetTranslation(gp_Vec(SHIFT, 0, 0))
core_new = BRepBuilderAPI_Transform(core, t, True).Shape()
filled = op(BRepAlgoAPI_Fuse, L, cyl(0, *FLOOR))                       # old spot made solid
cleared = op(BRepAlgoAPI_Cut, filled, cyl(SHIFT, FLOOR[0] - 1, FLOOR[1] + 1))
new = op(BRepAlgoAPI_Fuse, cleared, core_new)                          # pattern put back, shifted
u = ShapeUpgrade_UnifySameDomain(new, True, True, False); u.Build(); new = u.Shape()

v0, v1 = vol(L), vol(new)
print('volume before %.1f mm3, after %.1f mm3, difference %.2f mm3' % (v0, v1, v1 - v0))
print('geometry valid:', BRepCheck_Analyzer(new).IsValid())
w = STEPControl_Writer(); w.Transfer(new, STEPControl_AsIs)
if w.Write(dst) != IFSelect_RetDone: sys.exit('write failed')
print('written:', dst)
