"""Translate one part's solid inside the v2.2 assembly (keeps names, colours, layers).
Run:  python3 v22_move_part_asm.py <assembly.step> <out.step> "<part name>" dx dy dz      (or with no name: list part names)
"""
import sys
from OCP.STEPCAFControl import STEPCAFControl_Reader, STEPCAFControl_Writer
from OCP.TDocStd import TDocStd_Document
from OCP.TCollection import TCollection_ExtendedString
from OCP.XCAFDoc import XCAFDoc_DocumentTool
from OCP.TDF import TDF_LabelSequence
from OCP.TDataStd import TDataStd_Name
from OCP.IFSelect import IFSelect_RetDone
from OCP.STEPControl import STEPControl_AsIs
from OCP.BRepBuilderAPI import BRepBuilderAPI_Transform
from OCP.gp import gp_Trsf, gp_Vec
from OCP.Bnd import Bnd_Box
from OCP.BRepBndLib import BRepBndLib
A, OUT = sys.argv[1], sys.argv[2]
doc = TDocStd_Document(TCollection_ExtendedString("XmlOcaf"))
r = STEPCAFControl_Reader(); r.SetColorMode(True); r.SetNameMode(True); r.SetLayerMode(True)
assert r.ReadFile(A) == IFSelect_RetDone; r.Transfer(doc)
st = XCAFDoc_DocumentTool.ShapeTool_s(doc.Main())
labs = TDF_LabelSequence(); st.GetShapes(labs)
def name(l):
    n = TDataStd_Name(); return n.Get().ToExtString() if l.FindAttribute(TDataStd_Name.GetID_s(), n) else ''
def bb(s):
    b = Bnd_Box(); BRepBndLib.Add_s(s, b); return tuple(round(v, 2) for v in b.Get())
parts = [labs.Value(i) for i in range(1, labs.Length() + 1) if not st.IsAssembly_s(labs.Value(i))]
if len(sys.argv) < 7:
    for l in parts: print(repr(name(l)), bb(st.GetShape_s(l)))
    sys.exit()
PART = sys.argv[3]; dx, dy, dz = map(float, sys.argv[4:7])
hit = [l for l in parts if name(l).strip() == PART.strip()]
assert len(hit) == 1, 'part not found: ' + PART
s = st.GetShape_s(hit[0]); t = gp_Trsf(); t.SetTranslation(gp_Vec(dx, dy, dz))
n = BRepBuilderAPI_Transform(s, t, True).Shape(); print('moved', bb(s), '->', bb(n))
st.SetShape(hit[0], n); st.UpdateAssemblies()
w = STEPCAFControl_Writer(); w.SetColorMode(True); w.SetNameMode(True); w.SetLayerMode(True)
w.Transfer(doc, STEPControl_AsIs); assert w.Write(OUT) == IFSelect_RetDone; print('written')
