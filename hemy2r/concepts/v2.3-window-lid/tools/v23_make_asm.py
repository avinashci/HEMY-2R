"""Make 'HEMY2R v2.3 concept - window lid.step' from the v2.2 assembly: swap lid, handle, switch, board, spacers,
side plate A; remove the Wi-Fi SMA antenna; add the red window, the bigger board outline and placeholders."""
import sys  # needs the helper module build.py (CadQuery/OCP shortcuts) on sys.path; not included
from build import L
from OCP.STEPCAFControl import STEPCAFControl_Reader, STEPCAFControl_Writer
from OCP.STEPControl import STEPControl_AsIs
from OCP.TDocStd import TDocStd_Document
from OCP.TCollection import TCollection_ExtendedString
from OCP.XCAFDoc import XCAFDoc_DocumentTool, XCAFDoc_ColorGen, XCAFDoc_ColorSurf
from OCP.TDF import TDF_LabelSequence, TDF_Label
from OCP.TDataStd import TDataStd_Name
from OCP.TopLoc import TopLoc_Location
from OCP.Quantity import Quantity_Color, Quantity_TOC_RGB
from OCP.IFSelect import IFSelect_RetDone
A,OUT=sys.argv[1:3]
doc=TDocStd_Document(TCollection_ExtendedString("XmlOcaf"))
r=STEPCAFControl_Reader(); r.SetColorMode(True); r.SetNameMode(True); r.SetLayerMode(True)
assert r.ReadFile(A)==IFSelect_RetDone; r.Transfer(doc)
st=XCAFDoc_DocumentTool.ShapeTool_s(doc.Main()); ct=XCAFDoc_DocumentTool.ColorTool_s(doc.Main())
def name(l):
    n=TDataStd_Name(); return n.Get().ToExtString() if l.FindAttribute(TDataStd_Name.GetID_s(),n) else ''
def setname(l,s): TDataStd_Name.Set_s(l,TCollection_ExtendedString(s))
labs=TDF_LabelSequence(); st.GetShapes(labs)
by={}
for i in range(1,labs.Length()+1):
    l=labs.Value(i); by.setdefault(name(l).strip(),[]).append(l)
def part(prefix):
    for k,v in by.items():
        if k.startswith(prefix):
            for l in v:
                if not st.IsAssembly_s(l): return l
    raise KeyError(prefix)
swaps=[('Lid','v23_lid','Lid v2.3 CONCEPT: red window (rebate 33x39, 3 deep; opening 27x33) clear of the MX1 standoff, handle M5 csk at X -30, switch D16.2 at (37,28), 2 x M3 + 1 x M2.5 standoff threads'),
       ('Handle','v23_handle','Handle + 2 x M5x12 (moved to X -30)'),
       ('Power switch','v23_switch','Power switch TechEss 16 mm latching (envelope) at (37, 28)'),
       ('Electronics','v23_el','Electronics v2.3 CONCEPT: polvinc main board (unchanged) flipped components-up (PCB Z 99.5-101.1), CN1/DC1 not fitted'),
       ('Board spacers','v23_stand','Board supports: 2 x M3 FF ~18 mm at polvinc holes + M2.5 FF ~14 mm onto the MicroMod screw post (MX1)'),
       ('PANEL Side plate A','v23_sideA','PANEL Side plate A v2.3 CONCEPT: USB-C window moved to CN2 at X 22, Z 102.5 (old window/tab filled)')]
for pre,f,newname in swaps:
    l=part(pre); st.SetShape(l,L(f+'.brep')); setname(l,newname)
# remove the Wi-Fi SMA antenna instance(s)
ant=part('Wi-Fi antenna')
asms=TDF_LabelSequence(); st.GetFreeShapes(asms); root=asms.Value(1)
def walk(a):
    comps=TDF_LabelSequence(); st.GetComponents_s(a,comps,False)
    for i in range(1,comps.Length()+1):
        c=comps.Value(i); ref=TDF_Label()
        if st.GetReferredShape_s(c,ref):
            if ref.IsEqual(ant): st.RemoveComponent(c); print('removed antenna instance')
            elif st.IsAssembly_s(ref): walk(ref)
walk(root)
print('antenna label removed:', st.RemoveShape(ant, True))
setname(root,'HEMY2R v2.3 CONCEPT - window lid (from v2.2 recessed panels, counterweight far wall)')
# find the electronics group to add into
grp=root
for k,v in by.items():
    if k.upper().startswith('ELECTRONICS') and st.IsAssembly_s(v[0]): grp=v[0]; break
def add(f,nm,rgb):
    lab=st.AddShape(L(f+'.brep'),False); setname(lab,nm)
    ct.SetColor(lab,Quantity_Color(*rgb,Quantity_TOC_RGB),XCAFDoc_ColorGen)
    st.AddComponent(grp,lab,TopLoc_Location())
add('v23_pane','WINDOW red polycarbonate 3 mm (UV-stabilised, deep red) in the lid rebate',(0.75,0.03,0.03))
add('v23_plate','BRAKE board 1.1 (polvinc) beside the main board, components down, P1 replaced by a 2x2 2.0 mm TH header + 4-wire jumper to BRAKE',(0.10,0.30,0.55))
add('v23_ph','VHB foam tape 2.5 mm holding the brake board to the lid',(0.15,0.15,0.15))
st.UpdateAssemblies()
w=STEPCAFControl_Writer(); w.SetColorMode(True); w.SetNameMode(True); w.SetLayerMode(True)
w.Transfer(doc,STEPControl_AsIs); assert w.Write(OUT)==IFSelect_RetDone; print('written',OUT)
