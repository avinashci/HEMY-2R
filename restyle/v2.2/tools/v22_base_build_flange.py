"""HEMY 2R base flange v2.2 from the Nov-2 concept. Rel coords: origin on the RA axis, +Y toward side B, Z = assembly Z.
Fills the concept's old Ø8 jacks / LEDs / channels on the side-B face, then cuts the DC-099 layout:
LED - MOUNT - RA mark - ACC - LED. Output is translated by X -6 to the v2.2 RA axis."""
import sys, math; sys.path.insert(0,'.')
from lib import *
from OCP.gp import gp_Pnt, gp_Dir, gp_Ax2, gp_Vec, gp_Trsf
from OCP.BRepPrimAPI import BRepPrimAPI_MakeBox, BRepPrimAPI_MakeCylinder, BRepPrimAPI_MakePrism
from OCP.BRepAlgoAPI import BRepAlgoAPI_Cut, BRepAlgoAPI_Fuse, BRepAlgoAPI_Common
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakePolygon, BRepBuilderAPI_MakeFace, BRepBuilderAPI_Transform
from OCP.BRepFilletAPI import BRepFilletAPI_MakeFillet
from OCP.ShapeUpgrade import ShapeUpgrade_UnifySameDomain
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.BRepTools import BRepTools
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_EDGE
from OCP.TopoDS import TopoDS
def box(x0,x1,y0,y1,z0,z1): return BRepPrimAPI_MakeBox(gp_Pnt(x0,y0,z0),gp_Pnt(x1,y1,z1)).Shape()
def cyl(x,y,z,r,h,d=(0,0,1)): return BRepPrimAPI_MakeCylinder(gp_Ax2(gp_Pnt(x,y,z),gp_Dir(*d)),r,h).Shape()
def prism(pts,vec):
    p=BRepBuilderAPI_MakePolygon()
    for q in pts: p.Add(gp_Pnt(*q))
    p.Close(); f=BRepBuilderAPI_MakeFace(p.Wire()).Face()
    return BRepPrimAPI_MakePrism(f,gp_Vec(*vec)).Shape()
cut=lambda a,b: BRepAlgoAPI_Cut(a,b).Shape()
fuse=lambda a,b: BRepAlgoAPI_Fuse(a,b).Shape()
def vertical_fillets(shape,r,test):
    mk=BRepFilletAPI_MakeFillet(shape); e=TopExp_Explorer(shape,TopAbs_EDGE); n=0
    while e.More():
        ed=TopoDS.Edge(e.Current()); b=bb(ed)
        if abs(b[0]-b[3])<1e-6 and abs(b[1]-b[4])<1e-6 and test(b): mk.Add(r,ed); n+=1
        e.Next()
    return mk.Shape() if n else shape
def unify(s):
    u=ShapeUpgrade_UnifySameDomain(s,True,True,True); u.Build(); t=u.Shape()
    return t if BRepCheck_Analyzer(t).IsValid() and abs(vol(t)-vol(s))<1e-3 else s

K=solids(load(sys.argv[1]))[0]; v0=vol(K)
# ---- 1. fill old features: region X ±16, Y 11..35 (face, 1 mm top chamfer), Z -27.5..-8.5, minus voids we keep
F=prism([(-16,11,-27.5),(-16,35,-27.5),(-16,35,-9.5),(-16,34,-8.5),(-16,11,-8.5)],(32,0,0))
for keep in (cyl(0,0,-17.5,22.8,10),           # top pocket (reducer output ring sits in it)
             cyl(0,0,-22.5,13.1,5.0),          # Ø26.2 wire cavity
             cyl(0,17.5,-27.6,2.5,9.15)):      # M6 tap drill (side position toward side B)
    F=cut(F,keep)
K1=unify(fuse(K,F)); print('fill  +%.1f mm3'%(vol(K1)-v0))
# ---- 2. new features
ZJ, XJ, XL = -19.5, 17.5, 28.0
cuts=[]
for s in (-1,1):
    cuts.append(cyl(s*XJ,29.0,ZJ,5.5,7,(0,1,0)))            # DC-099 panel hole Ø11 (wall 4.9 mm)
    cuts.append(cyl(s*XL,29.0,ZJ,1.55,7,(0,1,0)))           # LED Ø3.1
    xa,xb=sorted((s*9.8,s*30.0))
    pk=box(xa,xb,22.0,30.1,-27.5,-11.8)                     # nut/body/LED pocket, machined from below
    pk=vertical_fillets(pk,2.0,lambda b:True)
    cuts.append(pk)
    # wire slot from the pocket to the Ø26 cavity, from below, Z -27.5..-20 (4 wide)
    a=(s*12.5,23.5); b2=(s*5.6,11.6); dx,dy=b2[0]-a[0],b2[1]-a[1]; L=math.hypot(dx,dy); nx,ny=-dy/L*2,dx/L*2
    cuts.append(prism([(a[0]+nx,a[1]+ny,-27.5),(b2[0]+nx,b2[1]+ny,-27.5),(b2[0]-nx,b2[1]-ny,-27.5),(a[0]-nx,a[1]-ny,-27.5)],(0,0,7.5)))
# RA home index: 90° V-groove, 0.3 deep, 8 mm long, vertical at X 0 on the side-B face, from the top edge down
cuts.append(prism([(-0.3,35.01,-16.5),(0.3,35.01,-16.5),(0,34.7,-16.5)],(0,0,8.2)))
K2=K1
for c in cuts: K2=cut(K2,c)
K2=unify(K2)
print('cuts  %.1f mm3, valid %s, solids %d'%(vol(K2)-vol(K1),BRepCheck_Analyzer(K2).IsValid(),len(solids(K2))))
t=gp_Trsf(); t.SetTranslation(gp_Vec(-6,0,0)); K3=BRepBuilderAPI_Transform(K2,t,True).Shape()
BRepTools.Write_s(K3,'flange_v22.brep'); print('volume %.0f mm3 = %.0f g (6061)'%(vol(K3),vol(K3)*2.70e-3), fbb(K3))
