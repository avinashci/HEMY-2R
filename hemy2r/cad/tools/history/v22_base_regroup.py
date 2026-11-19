import sys; sys.path.insert(0,'.')
exec(open('ra.py').read().split("seq=Sequence_TDF_Label()")[0])
from OCP.XCAFDoc import XCAFDoc_ColorType, XCAFDoc_ColorTool
from OCP.Quantity import Quantity_Color, Quantity_TypeOfColor
from OCP.STEPCAFControl import STEPCAFControl_Writer
from OCP.STEPControl import STEPControl_AsIs
from OCP.BRep import BRep_Builder
from OCP.TopoDS import TopoDS_Compound, TopoDS_Shape
from OCP.BRepTools import BRepTools
from OCP.TopLoc import TopLoc_Location
from OCP.gp import gp_Trsf, gp_Vec
from OCP.BRepBuilderAPI import BRepBuilderAPI_Transform
from OCP.TCollection import TCollection_ExtendedString
from OCP.Interface import Interface_Static
ct=XCAFDoc_DocumentTool.ColorTool_s(doc.Main())
SURF=XCAFDoc_ColorType.XCAFDoc_ColorSurf; GEN=XCAFDoc_ColorType.XCAFDoc_ColorGen
free=Sequence_TDF_Label(); st.GetFreeShapes(free); top=free.Value(1)
comps=Sequence_TDF_Label(); st.GetComponents_s(top,comps)
ra_comp=None
for i in range(1,comps.Length()+1):
    c=comps.Value(i); ref=TDF_Label(); st.GetReferredShape_s(c,ref)
    if name(ref).startswith('RA drive'): ra_comp,ra_ref=c,ref
RA=st.GetShape_s(ra_ref); S=solids(RA)
stock={43,48,39,10,11,23,30,204}
def colour_of(s):
    c=Quantity_Color()
    return c if (ct.GetColor(s,SURF,c) or ct.GetColor(s,GEN,c)) else None
ncol=sum(1 for s in S if colour_of(s))
print('RA solids',len(S),'with colour',ncol)
def make_part(nm,shapes,cols=None,whole=None):
    b=BRep_Builder(); c=TopoDS_Compound(); b.MakeCompound(c)
    for s in shapes: b.Add(c,s)
    lab=st.AddShape(c,False)
    TDataStd_Name.Set_s(lab,TCollection_ExtendedString(nm))
    if whole is not None: ct.SetColor(lab,whole,SURF)
    if cols:
        for s,col in zip(shapes,cols):
            if col is not None:
                sl=st.AddSubShape(lab,s)
                if not sl.IsNull(): ct.SetColor(sl,col,SURF)
    cl=st.AddComponent(top,lab,TopLoc_Location())
    TDataStd_Name.Set_s(cl,TCollection_ExtendedString(nm))
    return lab
keep=[s for k,s in enumerate(S) if k not in stock]; old=[S[k] for k in sorted(stock)]
st.RemoveComponent(ra_comp)
print('old RA label removed:',st.RemoveShape(ra_ref,True))
make_part('RA drive (reducer, motor, belt)',keep,[colour_of(s) for s in keep])
def rd(f):
    s=TopoDS_Shape(); BRepTools.Read_s(s,f,BRep_Builder()); return s
fl=solids(rd('flange_v22b.brep'))[0]
make_part('BASE flange v2.2 80x80 (flat bottom, 4 x M5 corner threads; 10 A jacks + home mark on side B)',[fl],whole=Quantity_Color(0.80,0.82,0.85,Quantity_TypeOfColor.Quantity_TOC_RGB))
ph=rd('placeholder_v22b.brep')
pl=solids(rd('plate_v22.brep'))[0]
make_part('BASE plate v2.2 80x80 (countersunk M6 into the LA-40B corner threads; LA-40B plate recess ASSUMED)',[pl],whole=Quantity_Color(0.74,0.77,0.80,Quantity_TypeOfColor.Quantity_TOC_RGB))
make_part('PLACEHOLDER LA-40B top plate (assumed 60 x 60 x 10, measure the real one)',solids(ph),whole=Quantity_Color(0.85,0.25,0.25,Quantity_TypeOfColor.Quantity_TOC_RGB))
# stock A11 + Vixen saddle + DC jack dropped (replaced by the base flange)
st.UpdateAssemblies()
Interface_Static.SetCVal_s("write.step.schema","AP214IS")
w=STEPCAFControl_Writer(); w.SetNameMode(True); w.SetColorMode(True)
w.Transfer(doc,STEPControl_AsIs); print('write',w.Write(sys.argv[2]))
# standalone part files (assembly coordinates)
from OCP.STEPControl import STEPControl_Writer
for shp,fn in ((fl,sys.argv[3]),(ph,sys.argv[4]),(pl,sys.argv[5])):
    ww=STEPControl_Writer(); ww.Transfer(shp,STEPControl_AsIs); print(fn,ww.Write(fn))
