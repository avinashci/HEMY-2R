"""v2.2 base flange (flat bottom, corner M5) + base plate. Assembly coords; RA axis at X -6.
Rel coords below = offset from the RA axis; helper P(x,y) adds -6."""
import sys, math; sys.path.insert(0,'.')
exec(open('build_flange.py').read().split("K=solids(load")[0])
from OCP.BRepFilletAPI import BRepFilletAPI_MakeChamfer
from OCP.BRepPrimAPI import BRepPrimAPI_MakeCone
from OCP.BRep import BRep_Builder
from OCP.TopoDS import TopoDS_Shape
def rd(f):
    s=TopoDS_Shape(); BRepTools.Read_s(s,f,BRep_Builder()); return s
X0=-6.0
def cylr(x,y,z,r,h,d=(0,0,1)): return cyl(X0+x,y,z,r,h,d)
def boxr(x0,x1,y0,y1,z0,z1): return box(X0+x0,X0+x1,y0,y1,z0,z1)
def outer_edge_chamfer(shape,z,dist):
    mk=BRepFilletAPI_MakeChamfer(shape); e=TopExp_Explorer(shape,TopAbs_EDGE); n=0
    while e.More():
        ed=TopoDS.Edge(e.Current()); b=bb(ed)
        if abs(b[2]-z)<1e-6 and abs(b[5]-z)<1e-6:
            pts=[(b[0]-X0,b[1]),(b[3]-X0,b[4])]
            if min(max(abs(px),abs(py)) for px,py in pts)>35.9: mk.Add(dist,ed); n+=1
        e.Next()
    return mk.Shape() if n else shape
ZB=-27.5                                   # flange bottom = base plate top
# ---------------- flange ----------------
F=solids(rd('flange80.brep'))[0]; v0=vol(F)
F=BRepAlgoAPI_Common(F,boxr(-50,50,-50,50,ZB,-8.0)).Shape()                  # drop the recess skirt -> flat bottom
for x,y in ((0,17.5),(0,-17.5),(17.5,0),(-17.5,0)):                          # old LA-40B M6 holes filled
    F=fuse(F,cylr(x,y,ZB,2.55,9.1))
F=fuse(F,cut(cut(boxr(-29.7,29.7,21.3,40.0,ZB,-13.3),cylr(0,0,-17.5,22.8,10)),cylr(0,0,-22.5,13.1,5.0)))                               # clear the old side-B layout (refilled, re-cut below)
ZJ,XJ,XL=-19.5,16.0,26.0                                                      # jacks up 1.5 / out 1: bezel stays above the split line
cuts=[]
for s in (-1,1):
    x0,x1=sorted((s*9.5,s*28.0)); cuts.append(vertical_fillets(boxr(x0,x1,21.5,35.0,ZB-0.1,-17.5),1.5,lambda b:True))
    x0,x1=sorted((s*10.0,s*28.0)); cuts.append(vertical_fillets(boxr(x0,x1,22.0,35.0,-17.6,-12.5),1.5,lambda b:True))
    cuts.append(cylr(s*XJ,34.0,ZJ,5.5,6.2,(0,1,0)))                              # M12 tapped (Ø11 tap drill), 5 mm wall
    cuts.append(cylr(s*XL,34.0,ZJ,1.55,6.2,(0,1,0)))                             # LED Ø3.1
    a=(s*12.5,23.0); b2=(s*5.6,11.6); dx,dy=b2[0]-a[0],b2[1]-a[1]; L=math.hypot(dx,dy); nx,ny=-dy/L*3,dx/L*3
    cuts.append(prism([(X0+a[0]+nx,a[1]+ny,ZB),(X0+b2[0]+nx,b2[1]+ny,ZB),(X0+b2[0]-nx,b2[1]-ny,ZB),(X0+a[0]-nx,a[1]-ny,ZB)],(0,0,8.5)))
cuts.append(prism([(X0-0.3,40.01,-16.5),(X0+0.3,40.01,-16.5),(X0,39.7,-16.5)],(0,0,8.2)))   # home mark
for x in (-33,33):
    for y in (-33,33): cuts.append(cylr(x,y,ZB-0.1,2.1,12.1))                 # M5 tap drill Ø4.2, 12 deep (10 thread)
for c in cuts: F=cut(F,c)
F=outer_edge_chamfer(unify(F),ZB,0.5)
print('flange valid',BRepCheck_Analyzer(F).IsValid(),'solids',len(solids(F)),'mass %.0f g'%(vol(F)*2.7e-3),'(was %.0f)'%(v0*2.7e-3))
# ---------------- base plate ----------------
H=40; C=4; Z0=-38.5
P=prism([(X0-H+C,-H,Z0),(X0+H-C,-H,Z0),(X0+H,-H+C,Z0),(X0+H,H-C,Z0),(X0+H-C,H,Z0),(X0-H+C,H,Z0),(X0-H,H-C,Z0),(X0-H,-H+C,Z0)],(0,0,ZB-Z0))
P=outer_edge_chamfer(P,Z0,1.0); P=outer_edge_chamfer(P,ZB,0.5)
cuts=[vertical_fillets(boxr(-30.1,30.1,-30.1,30.1,Z0-0.1,Z0+3.0),4.1,lambda b:True)]    # LA-40B plate recess (ASSUMED 60 x 60)
for x in (-19,19):
    for y in (-19,19):                                                        # countersunk M6 down into the LA-40B corner threads
        cuts.append(cylr(x,y,Z0-0.1,3.3,12))
        cone=BRepPrimAPI_MakeCone(gp_Ax2(gp_Pnt(X0+x,y,ZB-3.0),gp_Dir(0,0,1)),3.2,6.3,3.1).Shape(); cuts.append(cone)
for x in (-33,33):
    for y in (-33,33):
        cuts.append(cylr(x,y,Z0-0.1,2.75,12))                                 # M5 clearance Ø5.5
        cuts.append(cylr(x,y,Z0-0.1,4.5,5.6))                                 # counterbore Ø9 x 5.5 from below
for c in cuts: P=cut(P,c)
P=unify(P)
print('plate valid',BRepCheck_Analyzer(P).IsValid(),'solids',len(solids(P)),'mass %.0f g'%(vol(P)*2.7e-3),fbb(P))
BRepTools.Write_s(F,'flange_v22b.brep'); BRepTools.Write_s(P,'plate_v22.brep')
# envelopes: jacks (unchanged position), LEDs at 25, screws
from OCP.TopoDS import TopoDS_Compound
bld=BRep_Builder(); comp=TopoDS_Compound(); bld.MakeCompound(comp)
for s in (-1,1):
    for e_ in (cylr(s*16,40.0,-19.5,7.5,1.0,(0,1,0)),cylr(s*16,41.0,-19.5,7.0,2.0,(0,1,0)),cylr(s*16,31.0,-19.5,6.0,9.0,(0,1,0)),cylr(s*16,22.0,-19.5,6.0,9.0,(0,1,0)),cylr(s*26,32.0,-19.5,1.5,9.0,(0,1,0))): bld.Add(comp,e_)
BRepTools.Write_s(comp,'jack_env_b.brep')
