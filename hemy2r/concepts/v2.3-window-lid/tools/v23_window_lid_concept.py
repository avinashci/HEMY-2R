"""HEMY 2R v2.3 concept: flat lid with a red window, board flipped components-up, bigger board outline.
Builds new part solids in assembly coordinates from the v2.2 parts (exported as p*.brep from asm17)."""
import sys
# needs the helper module build.py (CadQuery/OCP shortcuts) on sys.path; not included
from build import L, box, cyl, rrect, U, C, clean, mv, W
from OCP.gp import gp_Trsf, gp_Ax1, gp_Pnt, gp_Dir, gp_Vec, gp_Ax2
from OCP.BRepBuilderAPI import BRepBuilderAPI_Transform
from OCP.BRepPrimAPI import BRepPrimAPI_MakeCone
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_SOLID
from OCP.BRep import BRep_Builder
from OCP.TopoDS import TopoDS_Compound
from OCP.Bnd import Bnd_Box
from OCP.BRepBndLib import BRepBndLib
def bb(s):
    b=Bnd_Box(); BRepBndLib.Add_s(s,b); return b.Get()
def rot_y(s, x0, z0, ang=3.141592653589793):
    t=gp_Trsf(); t.SetRotation(gp_Ax1(gp_Pnt(x0,0,z0),gp_Dir(0,1,0)),ang); return BRepBuilderAPI_Transform(s,t,True).Shape()
def comp(shapes):
    c=TopoDS_Compound(); b=BRep_Builder(); b.MakeCompound(c)
    for s in shapes: b.Add(c,s)
    return c
# ---------------- parameters ----------------
ZB = 99.5                     # new PCB bottom face (PCB 99.5..101.1), components up to ~117.4
ZT = ZB + 1.6
HANDLE_X = -30.0
SW = (37.0, 28.0)             # switch centre (clears frame ~5.6, DEC ~3, far wall ~2 mm)
STANDOFFS = [(-21,-3),(25,-3)]          # polvinc's two 3.2 mm board holes, M3 FF standoffs
MX1 = (0.5,-29.0)                        # Teensy MicroMod screw post: M2.5 FF standoff, card top Z 104.91
# brake board: held by 2.5 mm VHB foam tape on its back (no screw: the DEC-end corner cube is at its notch)
WIN_REB = (6,-46,39,-7)     # window rebate (3 deep), pane sits here; clear of the corner screw
WIN_THRU = (9,-43,36,-10)   # through opening (3 mm ledge)
# ---------------- lid ----------------
lid = L('p06.brep')
fills = [cyl(-11,44,119,6,5.4), cyl(-11,-44,119,6,5.4),            # old handle holes + countersinks
         cyl(37.5,18,119,6,8.3), cyl(37.5,38,119,6,4.5),            # old switch + SMA holes
         cyl(32,-3,119,6,1.8), cyl(-14,-3,119,6,1.8), cyl(10.5,-29,119,6,1.8)]  # old spacer threads
lid = U(lid,*fills)
lid = C(lid, rrect(WIN_REB[0],WIN_REB[1],WIN_REB[2],WIN_REB[3],122,126,4),
             rrect(WIN_THRU[0],WIN_THRU[1],WIN_THRU[2],WIN_THRU[3],118,126,3))
for y in (44,-44):   # handle: 5.5 bore + 90 deg countersink from below (D10.4, 2.45 deep)
    lid = C(lid, cyl(HANDLE_X,y,118,8,2.75),
            BRepPrimAPI_MakeCone(gp_Ax2(gp_Pnt(HANDLE_X,y,119-0.01),gp_Dir(0,0,1)),5.2,2.75,2.45+0.01).Shape())
lid = C(lid, cyl(SW[0],SW[1],118,8,8.1))
for x,y in STANDOFFS: lid = C(lid, cyl(x,y,118.99,5,1.25))     # M3 tap drill, 5 deep from below
lid = C(lid, cyl(MX1[0],MX1[1],118.99,5,1.025))                       # M2.5 tap drill
lid = clean(lid)
pane = rrect(WIN_REB[0]+0.2,WIN_REB[1]+0.2,WIN_REB[2]-0.2,WIN_REB[3]-0.2,122.05,125.0,3.8)
# ---------------- electronics: flip components-up, drop CN1/DC1 ----------------
el = L('p13.brep'); keep=[]; dropped=[]
e=TopExp_Explorer(el,TopAbs_SOLID)
while e.More():
    s=e.Current(); x0,y0,z0,x1,y1,z1=bb(s)
    (dropped if y0 < -56.5 else keep).append(s); e.Next()
# rotate 180 deg about a Y-parallel axis: X' = 11 - X, Z' = 210.5 - Z  (axis X 5.5, Z 105.25)
el2 = rot_y(comp(keep), 5.5, (210.5)/2)
# brake board beside the main board, components DOWN, back face on VHB foam under the lid (bottom face Z 116.5)
from OCP.gp import gp_Trsf as _T, gp_Ax1 as _A, gp_Pnt as _P, gp_Dir as _D, gp_Vec as _V
bk = L('brake3d.brep')
t1=_T(); t1.SetRotation(_A(_P(0,0,0),_D(1,0,0)),3.141592653589793)        # (x,y,z)->(x,-y,-z)
t2=_T(); t2.SetTranslation(_V(-50-2.0, -37+19.5, 116.5))                   # x 2 -> X -50 ; y 19.5 -> Y -37 ; z 0 -> Z 116.5
t=t2.Multiplied(t1); brake = BRepBuilderAPI_Transform(bk,t,True).Shape()
plate = brake
placeholders = comp([box(-47,-51,116.5,-32,-40,119)])                    # VHB foam pad 2.5 mm thick, ~15 x 11 mm
stand = comp([cyl(x,y,ZT,119-ZT,2.75) for x,y in STANDOFFS] + [cyl(MX1[0],MX1[1],104.91,119-104.91,2.5)])
# ---------------- handle, switch ----------------
handle = mv(L('p15.brep'), HANDLE_X-(-11.0), 0, 0)
switch = mv(L('p17.brep'), SW[0]-37.5, SW[1]-18.0, 0)
# ---------------- side plate A: fill old window + tab, new window at CN2 ----------------
cn2_x, cn2_z = 11-(-11.0), 210.5-108.0
sa = L('p03.brep')
sa = U(sa, box(-17.6,-62.5,104.2,-4.4,-56.5,111.8), box(-27,-62.5,109.0,5,-61.65,117.0))
sa = C(sa, rrect(cn2_x-6.5,-63,cn2_x+6.5,-56,cn2_z-3.75,cn2_z+3.75,2))
sa = clean(sa)
for n,s in dict(lid=lid,pane=pane,el=el2,plate=plate,ph=placeholders,stand=stand,handle=handle,switch=switch,sideA=sa).items():
    W(s,f'v23_{n}.brep')
print('dropped solids (CN1/DC1):',len(dropped),' kept',len(keep),' CN2 new X,Z',cn2_x,cn2_z)
print('el2 bbox',[round(v,2) for v in bb(el2)])
