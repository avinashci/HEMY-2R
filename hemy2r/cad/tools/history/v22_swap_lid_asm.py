"""Swap the Lid solid in the v2.2 assembly for the updated parts/HEMY2R - Lid.step, keeping names, colours and layers.
Run:  python3 v22_swap_lid_asm.py <assembly.step> <lid.step> <out.step> go
"""
import sys
from OCP.STEPCAFControl import STEPCAFControl_Reader, STEPCAFControl_Writer
from OCP.TDocStd import TDocStd_Document
from OCP.TCollection import TCollection_ExtendedString
from OCP.XCAFDoc import XCAFDoc_DocumentTool
from OCP.TDF import TDF_LabelSequence, TDF_Label
from OCP.TDataStd import TDataStd_Name
from OCP.IFSelect import IFSelect_RetDone
from OCP.STEPControl import STEPControl_Reader, STEPControl_AsIs
from OCP.Bnd import Bnd_Box
from OCP.BRepBndLib import BRepBndLib
from OCP.GProp import GProp_GProps
from OCP.BRepGProp import BRepGProp
from OCP.XSControl import XSControl_WorkSession
A, NEW, OUT = sys.argv[1:4]
doc = TDocStd_Document(TCollection_ExtendedString("XmlOcaf"))
r = STEPCAFControl_Reader(); r.SetColorMode(True); r.SetNameMode(True); r.SetLayerMode(True)
assert r.ReadFile(A) == IFSelect_RetDone; r.Transfer(doc)
st = XCAFDoc_DocumentTool.ShapeTool_s(doc.Main())
labs = TDF_LabelSequence(); st.GetShapes(labs)
def name(l):
    n = TDataStd_Name()
    return n.Get().ToExtString() if l.FindAttribute(TDataStd_Name.GetID_s(), n) else ''
def bb(s):
    b = Bnd_Box(); BRepBndLib.Add_s(s, b); return tuple(round(v,2) for v in b.Get())
def vol(s):
    g = GProp_GProps(); BRepGProp.VolumeProperties_s(s, g); return g.Mass()
rr = STEPControl_Reader(); rr.ReadFile(NEW); rr.TransferRoots(); new = rr.OneShape()
hit = []
for i in range(1, labs.Length()+1):
    l = labs.Value(i)
    if name(l) == 'Lid' and not st.IsAssembly_s(l):
        s = st.GetShape_s(l); print('lid label', bb(s), 'vol', round(vol(s),1)); hit.append(l)
# also the instance label(s) in the assembly
users = TDF_LabelSequence()
print('new', bb(new), round(vol(new),1))
if len(sys.argv) > 4 and hit:
    st.SetShape(hit[0], new); st.UpdateAssemblies()
    w = STEPCAFControl_Writer(); w.SetColorMode(True); w.SetNameMode(True); w.SetLayerMode(True)
    w.Transfer(doc, STEPControl_AsIs); assert w.Write(OUT) == IFSelect_RetDone; print('written')
