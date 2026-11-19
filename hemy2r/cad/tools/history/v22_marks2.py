"""Index marks, revision 2 (all on the sides):
- remove the DEC mark from the lid top (fill the groove back in);
- DEC: horizontal V-groove at Z 70 on side plate B (outer face), from the back edge X -69 inward 8 mm;
- DEC: matching horizontal V-groove at Z 70 on the dovetail's side B face (Y +50), at the outer end X -108..-100.
RA: the side-plate-A groove from v22_marks.py is filled; the side-B RA groove stays. All marks are on side B.
Run:  python3 ~/Developer/HEMY/restyle/v2.2/tools/v22_marks2.py
"""
import os, sys
from OCP.STEPControl import STEPControl_Reader, STEPControl_Writer, STEPControl_AsIs
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakePolygon, BRepBuilderAPI_MakeFace
from OCP.BRepPrimAPI import BRepPrimAPI_MakePrism
from OCP.BRepAlgoAPI import BRepAlgoAPI_Cut, BRepAlgoAPI_Fuse, BRepAlgoAPI_Common
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.ShapeFix import ShapeFix_Shape
from OCP.GProp import GProp_GProps
from OCP.BRepGProp import BRepGProp
from OCP.gp import gp_Pnt, gp_Vec
from OCP.IFSelect import IFSelect_RetDone
from OCP.BRepPrimAPI import BRepPrimAPI_MakeBox

P = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'parts')
D, L, OUT = 0.3, 8.0, 0.3
k = D + OUT

def read(p):
    r = STEPControl_Reader()
    if r.ReadFile(p) != IFSelect_RetDone: sys.exit('cannot read ' + p)
    r.TransferRoots(); return r.OneShape()
def vol(s):
    g = GProp_GProps(); BRepGProp.VolumeProperties_s(s, g); return g.Mass()
def prism(a, b, c, along):
    pg = BRepBuilderAPI_MakePolygon(gp_Pnt(*a), gp_Pnt(*b), gp_Pnt(*c), True)
    return BRepPrimAPI_MakePrism(BRepBuilderAPI_MakeFace(pg.Wire(), True).Face(), gp_Vec(*along)).Shape()
def save(name, s, v0):
    if not BRepCheck_Analyzer(s).IsValid():
        f = ShapeFix_Shape(s); f.Perform(); s = f.Shape()
    ok = BRepCheck_Analyzer(s).IsValid()
    print('  %-48s volume %+6.2f mm3  valid: %s' % (name, vol(s) - v0, ok))
    if not ok: sys.exit('  not written')
    w = STEPControl_Writer(); w.Transfer(s, STEPControl_AsIs)
    if w.Write(os.path.join(P, name)) != IFSelect_RetDone: sys.exit('write failed')

# 1. lid: fill the old DEC groove (same V prism as v22_marks.py, clipped to the lid's top layer)
s = read(os.path.join(P, 'HEMY2R - Lid.step')); v0 = vol(s)
old = prism((-69.5, 0.0, 125 - D), (-69.5, -k, 125 + OUT), (-69.5, k, 125 + OUT), (L + 0.5, 0, 0))
fillv = BRepAlgoAPI_Common(old, BRepPrimAPI_MakeBox(gp_Pnt(-69.0, -1, 124), gp_Pnt(-60, 1, 125)).Shape()).Shape()
s = BRepAlgoAPI_Fuse(s, fillv).Shape()
save('HEMY2R - Lid.step', s, v0)

# 1b. side plate A: fill the RA groove from v22_marks.py (all marks now on side B only)
ra_old = prism((-6.0, -62.5 + D, -0.5), (-6.0 - k, -62.5 - OUT, -0.5), (-6.0 + k, -62.5 - OUT, -0.5), (0, 0, L + 0.5))
ra_fill = BRepAlgoAPI_Common(ra_old, BRepPrimAPI_MakeBox(gp_Pnt(-7, -62.5, 0), gp_Pnt(-5, -62.0, 8.0)).Shape()).Shape()
for rec in ['', ' (recessed panel)']:
    n = 'HEMY2R - Side plate A%s.step' % rec
    s1 = read(os.path.join(P, n)); v0 = vol(s1)
    save(n, BRepAlgoAPI_Fuse(s1, ra_fill).Shape(), v0)

# 2. side plates: horizontal DEC groove at Z 70 from X -69.5 to -61
for side, yf, sgn in [('B', 62.5, -1)]:                         # DEC marks on side B only
    g = prism((-69.5, yf + sgn * D, 70.0), (-69.5, yf - sgn * OUT, 70.0 - k), (-69.5, yf - sgn * OUT, 70.0 + k), (L + 0.5, 0, 0))
    for rec in ['', ' (recessed panel)']:
        n = 'HEMY2R - Side plate %s%s.step' % (side, rec)
        s = read(os.path.join(P, n)); v0 = vol(s)
        save(n, BRepAlgoAPI_Cut(s, g).Shape(), v0)

# 3. dovetail: matching horizontal grooves at Z 70 on both side faces, outer end X -108.5 .. -100
n = 'HEMY2R - Dovetail (indicator LED hole).step'
s = read(os.path.join(P, n)); v0 = vol(s)
for yf, sgn in [(50.0, -1)]:                                   # side B face only (side A has the USB pocket)
    g = prism((-108.6, yf + sgn * D, 70.0), (-108.6, yf - sgn * OUT, 70.0 - k), (-108.6, yf - sgn * OUT, 70.0 + k), (L + 0.6, 0, 0))
    s = BRepAlgoAPI_Cut(s, g).Shape()
save(n, s, v0)
print('done')
