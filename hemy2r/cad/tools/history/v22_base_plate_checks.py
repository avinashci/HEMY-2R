import sys, math; sys.path.insert(0,'.')
exec(open('env.py').read().split("FL=solids")[0])
from OCP.BRepClass3d import BRepClass3d_SolidClassifier
from OCP.gp import gp_Pnt, gp_Trsf, gp_Vec
from OCP.TopAbs import TopAbs_IN
from OCP.BRepBuilderAPI import BRepBuilderAPI_Transform
F=solids(rd('flange_v22b.brep'))[0]; P=solids(rd('plate_v22.brep'))[0]; ENV=solids(rd('jack_env_b.brep'))
S=solids(rd('ra_solids.brep')); stock={43,48,39,10,11,23,30,204}
ov=[(k,round(vol(BRepAlgoAPI_Common(F,s).Shape()),2)) for k,s in enumerate(S) if k not in stock]
print('flange vs RA drive overlaps:',[o for o in ov if o[1]>1e-3])
print('plate vs flange overlap %.3f mm3'%vol(BRepAlgoAPI_Common(F,P).Shape()))
print('plate vs RA drive min gap %.2f'%min(BRepExtrema_DistShapeShape(P,s).Value() for k,s in enumerate(S) if k not in stock))
names=['ring','bezel','thread','body','led']*2
for n,e in zip(names,ENV):
    v=vol(BRepAlgoAPI_Common(F,e).Shape())
    if n!='thread' and v>0.2: print('  env',n,'in flange %.2f'%v)
print('jack/LED vs plate min gap %.2f'%min(BRepExtrema_DistShapeShape(e,P).Value() for e in ENV))
print('jack/LED vs RA min gap %.2f'%min(BRepExtrema_DistShapeShape(e,s).Value() for e in ENV for k,s in enumerate(S) if k not in stock))
PH=load(sys.argv[1])  # LA-40B top plate placeholder STEP (hemy2r/cad/reference/)
t=gp_Trsf(); t.SetTranslation(gp_Vec(-6,0,-8)); PH=BRepBuilderAPI_Transform(PH,t,True).Shape()
print('placeholder (moved -8) vs plate overlap %.3f'%vol(BRepAlgoAPI_Common(PH,P).Shape()), fbb(PH))
BRepTools.Write_s(PH,'placeholder_v22b.brep')
def mat(Sh,x,y,z): return BRepClass3d_SolidClassifier(Sh,gp_Pnt(x-6,y,z),1e-6).State()==TopAbs_IN
def wall(Sh,p,q,n=600):
    runs=[];run=0;prev=None
    for i in range(n+1):
        t=i/n; pt=[p[k]+(q[k]-p[k])*t for k in range(3)]; m=mat(Sh,*pt)
        if m: run+=1
        elif run: runs.append(run); run=0
    if run: runs.append(run)
    L=math.dist(p,q); return [round(r*L/n,2) for r in runs]
print('flange: corner M5 -> side-B bay (runs along X at Y 30, Z -24):', wall(F,(33,30,-24),(26,30,-24)))
print('flange: upper bay -> top pocket (Z -15):', wall(F,(9.2,21.0,-15),(5,17,-15)), ' roof:', wall(F,(16,28,-12.6),(16,28,-8.4)), ' bay floor gone below bay? split', wall(F,(16,28,-27.4),(16,28,-25)))
print('flange: corner M5 -> side face / chamfer:', wall(F,(33,33,-24),(41,33,-24)), wall(F,(33,33,-24),(39,39,-24)))
print('plate: M5 counterbore -> recess wall (Z -37):', wall(P,(33,33,-37),(27,27,-37)))
print('plate: M5 hole -> side face (Z -30):', wall(P,(33,33,-30),(41,33,-30)))
print('plate: floor above recess (at 0,0):', wall(P,(0,0,-38.6),(0,0,-27.4)), ' at countersink (19,19):', wall(P,(19,19,-38.6),(19,19,-27.4)))
print('plate: countersink -> recess-corner region ok; countersink -> M5 cbore:', wall(P,(19,19,-34),(33,33,-34)))
