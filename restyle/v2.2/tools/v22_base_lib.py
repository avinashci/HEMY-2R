from OCP.STEPControl import STEPControl_Reader
from OCP.Bnd import Bnd_Box
from OCP.BRepBndLib import BRepBndLib
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_SOLID
from OCP.TopoDS import TopoDS
from OCP.GProp import GProp_GProps
from OCP.BRepGProp import BRepGProp
def load(f):
    r=STEPControl_Reader(); r.ReadFile(f); r.TransferRoots(); return r.OneShape()
def bb(s):
    b=Bnd_Box(); BRepBndLib.Add_s(s,b,False); p=b.CornerMin();q=b.CornerMax(); return (p.X(),p.Y(),p.Z(),q.X(),q.Y(),q.Z())
def fbb(s): return "X%.2f..%.2f Y%.2f..%.2f Z%.2f..%.2f"%tuple(bb(s)[i] for i in (0,3,1,4,2,5))
def solids(s):
    e=TopExp_Explorer(s,TopAbs_SOLID); out=[]
    while e.More(): out.append(TopoDS.Solid(e.Current())); e.Next()
    return out
def vol(s):
    g=GProp_GProps(); BRepGProp.VolumeProperties_s(s,g); return g.Mass()
