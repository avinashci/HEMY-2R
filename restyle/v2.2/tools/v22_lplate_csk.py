"""v2.2 L-plate: 90° countersinks (Ø6.3) on the outside of both reducer bolt circles,
for M3 ISO 14581 flat-head screws. Reads the CW-ready L-plate, writes
v2.2/parts/HEMY2R - L-plate v2.2.step
Run:  python3 ~/Developer/HEMY/restyle/v2.1/tools/v22_lplate_csk.py
"""
import os, sys, math
from OCP.STEPControl import STEPControl_Reader, STEPControl_Writer, STEPControl_AsIs
from OCP.BRepPrimAPI import BRepPrimAPI_MakeCone
from OCP.BRepAlgoAPI import BRepAlgoAPI_Cut
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.ShapeFix import ShapeFix_Shape
from OCP.GProp import GProp_GProps
from OCP.BRepGProp import BRepGProp
from OCP.BRepAdaptor import BRepAdaptor_Surface
from OCP.GeomAbs import GeomAbs_Cylinder
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_FACE
from OCP.TopoDS import TopoDS
from OCP.gp import gp_Pnt, gp_Dir, gp_Ax2
from OCP.IFSelect import IFSelect_RetDone
FACE = getattr(TopoDS, 'Face_s', None) or getattr(TopoDS, 'Face')

V22 = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'v2.2', 'parts')
SRC = os.path.join(V22, 'HEMY2R - L-plate (125 cube, RA -6, CW-ready).step')
DST = os.path.join(V22, 'HEMY2R - L-plate v2.2.step')
R_CSK = 3.15                                   # Ø6.3 at the surface

def read(p):
    r = STEPControl_Reader()
    if r.ReadFile(p) != IFSelect_RetDone: sys.exit('cannot read ' + p)
    r.TransferRoots(); return r.OneShape()
def vol(s):
    g = GProp_GProps(); BRepGProp.VolumeProperties_s(s, g); return g.Mass()

L = read(SRC); v0 = vol(L)
ra, dec = set(), set()
ex = TopExp_Explorer(L, TopAbs_FACE)
while ex.More():
    a = BRepAdaptor_Surface(FACE(ex.Current())); ex.Next()
    if a.GetType() != GeomAbs_Cylinder: continue
    c = a.Cylinder(); r = c.Radius()
    if not 1.4 < r < 1.8: continue
    p, d = c.Location(), c.Axis().Direction()
    if abs(d.Z()) > 0.99 and abs(math.hypot(p.X() + 6.0, p.Y()) - 37.0) < 0.3:
        ra.add((round(p.X(), 2), round(p.Y(), 2)))           # RA bolt circle around (-6, 0)
    if abs(d.X()) > 0.99 and abs(math.hypot(p.Y(), p.Z() - 70.0) - 37.0) < 0.3:
        dec.add((round(p.Y(), 2), round(p.Z(), 2)))          # DEC bolt circle around (Y 0, Z 70)
print('  RA bolt-circle holes found: %d, DEC: %d' % (len(ra), len(dec)))
for x, y in ra:      # floor underside, Z 0, countersink opens downward
    r0 = R_CSK + 0.5
    L = BRepAlgoAPI_Cut(L, BRepPrimAPI_MakeCone(gp_Ax2(gp_Pnt(x, y, -0.5), gp_Dir(0, 0, 1)), r0, 1.5, r0 - 1.5).Shape()).Shape()
for y, z in dec:     # back wall outside face, X -69
    r0 = R_CSK + 0.5
    L = BRepAlgoAPI_Cut(L, BRepPrimAPI_MakeCone(gp_Ax2(gp_Pnt(-69.5, y, z), gp_Dir(1, 0, 0)), r0, 1.5, r0 - 1.5).Shape()).Shape()
if not BRepCheck_Analyzer(L).IsValid():
    f = ShapeFix_Shape(L); f.Perform(); L = f.Shape()
ok = BRepCheck_Analyzer(L).IsValid()
print('  L-plate v2.2: volume %+.1f mm3, valid: %s' % (vol(L) - v0, ok))
if not ok: sys.exit('  not written')
w = STEPControl_Writer(); w.Transfer(L, STEPControl_AsIs)
if w.Write(DST) != IFSelect_RetDone: sys.exit('write failed')
print('  written:', os.path.abspath(DST))
