import sys, pickle
from OCP.STEPCAFControl import STEPCAFControl_Reader
from OCP.TDocStd import TDocStd_Document
from OCP.TCollection import TCollection_ExtendedString
from OCP.XCAFDoc import XCAFDoc_DocumentTool, XCAFDoc_ColorType, XCAFDoc_ColorTool
from OCP.TDF import TDF_LabelSequence, TDF_Label
from OCP.TDataStd import TDataStd_Name
from OCP.Quantity import Quantity_Color
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_FACE, TopAbs_REVERSED
from OCP.TopoDS import TopoDS
from OCP.BRep import BRep_Tool
from OCP.TopLoc import TopLoc_Location
import numpy as np
doc=TDocStd_Document(TCollection_ExtendedString("doc"))
r=STEPCAFControl_Reader(); r.SetColorMode(True); r.SetNameMode(True)
r.ReadFile(sys.argv[1]); r.Transfer(doc)
st=XCAFDoc_DocumentTool.ShapeTool_s(doc.Main()); ct=XCAFDoc_DocumentTool.ColorTool_s(doc.Main())
def name(l):
    a=TDataStd_Name()
    return l.FindAttribute(TDataStd_Name.GetID_s(),a) and a.Get().ToExtString() or ''
def color(l, shape=None):
    c=Quantity_Color()
    for t in (XCAFDoc_ColorType.XCAFDoc_ColorSurf, XCAFDoc_ColorType.XCAFDoc_ColorGen):
        if XCAFDoc_ColorTool.GetColor_s(l,t,c): return (c.Red(),c.Green(),c.Blue())
    return None
parts=[]
def walk(l, loc, path, inh):
    if st.IsReference_s(l):
        ref=TDF_Label(); st.GetReferredShape_s(l,ref)
        cl=color(l) or inh
        walk(ref, loc.Multiplied(st.GetLocation_s(l)), path+[name(l)], cl)
        return
    nm=name(l); cl=color(l) or inh
    if st.IsAssembly_s(l):
        ch=TDF_LabelSequence(); st.GetComponents_s(l,ch,False)
        for i in range(1,ch.Length()+1): walk(ch.Value(i), loc, path+[nm], cl)
        return
    shp=st.GetShape_s(l).Moved(loc)
    parts.append(('/'.join(p for p in path+[nm] if p), shp, cl))
roots=TDF_LabelSequence(); st.GetFreeShapes(roots)
for i in range(1,roots.Length()+1): walk(roots.Value(i), TopLoc_Location(), [], None)
out=[]
for nm,shp,cl in parts:
    BRepMesh_IncrementalMesh(shp,0.08,False,0.3,True)
    V=[];F=[];off=0
    e=TopExp_Explorer(shp,TopAbs_FACE)
    while e.More():
        f=TopoDS.Face_s(e.Current()); L=TopLoc_Location(); tri=BRep_Tool.Triangulation_s(f,L)
        if tri is not None:
            T=L.Transformation()
            for i in range(1,tri.NbNodes()+1):
                p=tri.Node(i).Transformed(T); V.append((p.X(),p.Y(),p.Z()))
            rev=f.Orientation()==TopAbs_REVERSED
            for i in range(1,tri.NbTriangles()+1):
                a,b,c=tri.Triangle(i).Get()
                F.append((off+a-1,off+c-1,off+b-1) if rev else (off+a-1,off+b-1,off+c-1))
            off+=tri.NbNodes()
        e.Next()
    out.append((nm,np.array(V,dtype=np.float32),np.array(F,dtype=np.int32),cl))
pickle.dump(out,open(sys.argv[2],'wb'))
for nm,V,F,cl in out: print(len(F), cl and tuple(round(x,2) for x in cl), nm[:110])
