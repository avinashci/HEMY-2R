"""Side plate A, USB-C rev 3 (2026-11-14). CN1 and DC1 are left off the board, so:
 1. fill the inner connector relief (38 x 16.1 x 3.8 mm at X -4..34, Z 97.9..114): solid plate again;
 2. re-cut the outer recess as ONE outline: the original 93 x 93 (X -53..40, Z 16..109, R6 corners, 0.8 deep)
    with a smooth tab rising around the USB-C (base X -26..4 on the Z 109 edge, top X -19..-3 at Z 115.5,
    sloped flanks, R4 blends), then chamfer the whole top edge 0.4 x 45 deg (as the original) in one pass;
 3. cut the 13 x 7.5 mm (R2) window to CN2 at X -11, Z 108 (CN2 face ~5.25 mm below the recess floor).
Run:  python3 v22_sideA_usbc.py <in: plate before the USB-C work> <out>
"""
import sys
from OCP.STEPControl import STEPControl_Reader, STEPControl_Writer, STEPControl_AsIs
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakePolygon, BRepBuilderAPI_MakeFace
from OCP.BRepFilletAPI import BRepFilletAPI_MakeFillet2d, BRepFilletAPI_MakeChamfer
from OCP.BRepPrimAPI import BRepPrimAPI_MakePrism, BRepPrimAPI_MakeBox
from OCP.BRepAlgoAPI import BRepAlgoAPI_Cut, BRepAlgoAPI_Fuse
from OCP.ShapeUpgrade import ShapeUpgrade_UnifySameDomain
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.ShapeFix import ShapeFix_Shape
from OCP.GProp import GProp_GProps
from OCP.BRepGProp import BRepGProp
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_VERTEX, TopAbs_EDGE
from OCP.TopoDS import TopoDS
from OCP.BRep import BRep_Tool
from OCP.BRepAdaptor import BRepAdaptor_Curve
from OCP.gp import gp_Pnt, gp_Vec
from OCP.IFSelect import IFSelect_RetDone
VTX = getattr(TopoDS, 'Vertex_s', None) or getattr(TopoDS, 'Vertex')
IN, OUT = sys.argv[1], sys.argv[2]
Y_OUT, Y_FLOOR, Y_IN, CH = -62.5, -61.7, -56.5, 0.4
def read(p):
    r = STEPControl_Reader()
    if r.ReadFile(p) != IFSelect_RetDone: sys.exit('cannot read ' + p)
    r.TransferRoots(); return r.OneShape()
def vol(s):
    g = GProp_GProps(); BRepGProp.VolumeProperties_s(s, g); return g.Mass()
def valid(s): return BRepCheck_Analyzer(s).IsValid()
def unify(s):
    if not valid(s):
        fx = ShapeFix_Shape(s); fx.Perform(); s = fx.Shape()
    u = ShapeUpgrade_UnifySameDomain(s, True, True, False); u.Build(); m = u.Shape()
    return m if valid(m) and abs(vol(m) - vol(s)) < 0.01 else s
def face_xz(pts, y, fillets):
    pg = BRepBuilderAPI_MakePolygon()
    for x, z in pts: pg.Add(gp_Pnt(x, y, z))
    pg.Close()
    f = BRepBuilderAPI_MakeFace(pg.Wire(), True).Face()
    fl = BRepFilletAPI_MakeFillet2d(f); ex = TopExp_Explorer(f, TopAbs_VERTEX); seen = []
    while ex.More():
        v = VTX(ex.Current()); ex.Next()
        if any(v.IsSame(q) for q in seen): continue
        seen.append(v); p = BRep_Tool.Pnt_s(v); k = (round(p.X(), 3), round(p.Z(), 3))
        if k in fillets: fl.AddFillet(v, fillets[k])
    fl.Build(); return fl.Shape()
s = read(IN); v0 = vol(s)
# 1. fill the inner relief; fill the old outer recess (with its chamfer) so it can be re-cut as one outline
s = BRepAlgoAPI_Fuse(s, BRepPrimAPI_MakeBox(gp_Pnt(-4.0, -60.3, 97.9), gp_Pnt(34.0, Y_IN, 114.0)).Shape()).Shape()
s = BRepAlgoAPI_Fuse(s, BRepPrimAPI_MakeBox(gp_Pnt(-53.5, Y_OUT, 15.5), gp_Pnt(40.5, Y_FLOOR + 0.01, 109.5)).Shape()).Shape()
s = unify(s)
# 2. new recess outline: rectangle + tab, one face
CX, ZE, ZT, HB, HT, RB, RT, RC = -11.0, 109.0, 115.5, 15.0, 8.0, 4.0, 4.0, 6.0
X0, X1, Z0 = -53.0, 40.0, 16.0
pts = [(X0, Z0), (X1, Z0), (X1, ZE), (CX + HB, ZE), (CX + HT, ZT), (CX - HT, ZT), (CX - HB, ZE), (X0, ZE)]
fil = {(X0, Z0): RC, (X1, Z0): RC, (X1, ZE): RC, (X0, ZE): RC, (CX + HB, ZE): RB, (CX - HB, ZE): RB, (CX + HT, ZT): RT, (CX - HT, ZT): RT}
outline = face_xz(pts, Y_FLOOR, fil)
s = BRepAlgoAPI_Cut(s, BRepPrimAPI_MakePrism(outline, gp_Vec(0, Y_OUT - 1.0 - Y_FLOOR, 0)).Shape()).Shape()
s = unify(s)
# chamfer every edge of that outline on the outer face (Y = Y_OUT)
ch = BRepFilletAPI_MakeChamfer(s); n = 0
ex = TopExp_Explorer(s, TopAbs_EDGE); seen = []
while ex.More():
    e = TopoDS.Edge_s(ex.Current()); ex.Next()
    if any(e.IsSame(q) for q in seen): continue
    seen.append(e)
    c = BRepAdaptor_Curve(e); p0 = c.Value(c.FirstParameter()); p1 = c.Value(c.LastParameter()); pm = c.Value(0.5 * (c.FirstParameter() + c.LastParameter()))
    if all(abs(p.Y() - Y_OUT) < 1e-4 for p in (p0, p1, pm)) and X0 - 0.1 <= pm.X() <= X1 + 0.1 and Z0 - 0.1 <= pm.Z() <= ZT + 0.1:
        ch.Add(CH, e); n += 1
ch.Build()
if not ch.IsDone(): sys.exit('  chamfer failed')
s = unify(ch.Shape()); print('  chamfered %d outline edges' % n)
# 3. window to CN2
win = face_xz([(-17.5, 104.25), (-4.5, 104.25), (-4.5, 111.75), (-17.5, 111.75)], Y_OUT - 1,
              {(-17.5, 104.25): 2, (-4.5, 104.25): 2, (-4.5, 111.75): 2, (-17.5, 111.75): 2})
s = unify(BRepAlgoAPI_Cut(s, BRepPrimAPI_MakePrism(win, gp_Vec(0, (Y_IN + 1) - (Y_OUT - 1), 0)).Shape()).Shape())
print('  side A USB-C rev 3: volume %+.1f mm3, valid: %s' % (vol(s) - v0, valid(s)))
if not valid(s): sys.exit('  not written')
w = STEPControl_Writer(); w.Transfer(s, STEPControl_AsIs)
if w.Write(OUT) != IFSelect_RetDone: sys.exit('write failed')
print('  written')
