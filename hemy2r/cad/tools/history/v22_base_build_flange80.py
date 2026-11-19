"""HEMY 2R base flange v2.2, 80 x 80. Rel coords (origin RA axis, +Y side B), translated X -6 at the end.
Core (reducer interface, M6s, cavity) transplanted from the filled 70 x 70 concept; new 80 x 80 block;
side B: 10 A M12 jacks screwed into tapped holes (no nut), LEDs, home mark."""
import sys, math; sys.path.insert(0,'.')
exec(open('build_flange.py').read().split("K=solids(load")[0])
from OCP.BRepFilletAPI import BRepFilletAPI_MakeChamfer
K=solids(load(sys.argv[1]))[0]
# filled 70 version (same fill as before)
F=prism([(-16,11,-27.5),(-16,35,-27.5),(-16,35,-9.5),(-16,34,-8.5),(-16,11,-8.5)],(32,0,0))
for keep in (cyl(0,0,-17.5,22.8,10),cyl(0,0,-22.5,13.1,5.0),cyl(0,17.5,-27.6,2.5,9.15)): F=cut(F,keep)
K1=unify(fuse(K,F))
VOIDS=cut(cyl(0,0,-27.5,30.9,19.1),K1)                     # every internal feature inside r 30.9
# 80 x 80 block, 4 mm vertical corner chamfers, 1 mm top/bottom edge chamfers
H=40; C=4
B=prism([(-H+C,-H,-30.5),(H-C,-H,-30.5),(H,-H+C,-30.5),(H,H-C,-30.5),(H-C,H,-30.5),(-H+C,H,-30.5),(-H,H-C,-30.5),(-H,-H+C,-30.5)],(0,0,22))
ch=BRepFilletAPI_MakeChamfer(B); e=TopExp_Explorer(B,TopAbs_EDGE)
while e.More():
    ed=TopoDS.Edge(e.Current()); b=bb(ed)
    if abs(b[2]-b[5])<1e-6: ch.Add(1.0,ed)
    e.Next()
B=ch.Shape()
REC=vertical_fillets(box(-30.1,30.1,-30.1,30.1,-30.6,-27.5),4.1,lambda b:True)
N=cut(cut(B,REC),VOIDS)
print('core+block', round(vol(N)), 'valid', BRepCheck_Analyzer(N).IsValid())
# ---- side B features (face at Y 40)
ZJ, XJ, XL = -21.0, 15.0, 27.0
cuts=[]
for s in (-1,1):
    cuts.append(cyl(s*XJ,34.0,ZJ,5.5,7,(0,1,0)))             # M12 x 1 tapped (Ø11.0 tap drill), 5 mm wall
    cuts.append(cyl(s*XL,34.0,ZJ,1.55,7,(0,1,0)))            # LED Ø3.1
    x0,x1=sorted((s*6.0,s*29.0)); lo=vertical_fillets(box(x0,x1,21.5,35.0,-30.6,-17.5),1.5,lambda b:True)
    x0,x1=sorted((s*10.0,s*29.0)); hi=vertical_fillets(box(x0,x1,22.0,35.0,-17.6,-13.5),1.5,lambda b:True)
    cuts+=[lo,hi]                                             # jack/LED bay, machined from below (through the skirt inside the face)
    a=(s*12.5,23.0); b2=(s*5.6,11.6); dx,dy=b2[0]-a[0],b2[1]-a[1]; L=math.hypot(dx,dy); nx,ny=-dy/L*3,dx/L*3
    cuts.append(prism([(a[0]+nx,a[1]+ny,-27.5),(b2[0]+nx,b2[1]+ny,-27.5),(b2[0]-nx,b2[1]-ny,-27.5),(a[0]-nx,a[1]-ny,-27.5)],(0,0,8.5)))  # 6 mm lead slot to the cavity
cuts.append(prism([(-0.3,40.01,-16.5),(0.3,40.01,-16.5),(0,39.7,-16.5)],(0,0,8.2)))   # home mark V-groove
for c in cuts: N=cut(N,c)
N=unify(N)
print('final valid',BRepCheck_Analyzer(N).IsValid(),'solids',len(solids(N)))
t=gp_Trsf(); t.SetTranslation(gp_Vec(-6,0,0)); N=BRepBuilderAPI_Transform(N,t,True).Shape()
BRepTools.Write_s(N,'flange80.brep'); print('volume %.0f mm3 = %.0f g'%(vol(N),vol(N)*2.70e-3), fbb(N))
# jack envelopes (assembly coords): bezel Ø14x2 + cap ring 1 mm outside, thread Ø12 x 9, body Ø12 x 9, leads
from OCP.BRep import BRep_Builder
from OCP.TopoDS import TopoDS_Compound
bld=BRep_Builder(); comp=TopoDS_Compound(); bld.MakeCompound(comp); env=[]
for s in (-1,1):
    x=-6+s*XJ
    env+=[cyl(x,40.0,ZJ,7.5,1.0,(0,1,0)),cyl(x,41.0,ZJ,7.0,2.0,(0,1,0)),cyl(x,31.0,ZJ,6.0,9.0,(0,1,0)),cyl(x,22.0,ZJ,6.0,9.0,(0,1,0)),
          cyl(-6+s*XL,32.0,ZJ,1.5,9.0,(0,1,0))]
for e_ in env: bld.Add(comp,e_)
BRepTools.Write_s(comp,'jack10a_env.brep')
