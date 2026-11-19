"""Remove whole top-level parts (free shapes) from an assembly STEP by name prefix, keeping everything else
(names, colours, layers). 2026-11-16: removed the cable tie plate and its 2 x M5x12 accessory screws.
Run:  python3 v22_remove_parts_asm.py <in.step> <out.step> "<name prefix>" ["<name prefix>" ...]
"""
import sys
from OCP.STEPCAFControl import STEPCAFControl_Reader, STEPCAFControl_Writer
from OCP.STEPControl import STEPControl_AsIs
from OCP.TDocStd import TDocStd_Document
from OCP.TCollection import TCollection_ExtendedString
from OCP.XCAFDoc import XCAFDoc_DocumentTool
from OCP.TDF import TDF_LabelSequence
from OCP.TDataStd import TDataStd_Name
from OCP.IFSelect import IFSelect_RetDone
A, OUT, prefixes = sys.argv[1], sys.argv[2], sys.argv[3:]
doc = TDocStd_Document(TCollection_ExtendedString("XmlOcaf"))
r = STEPCAFControl_Reader(); r.SetColorMode(True); r.SetNameMode(True); r.SetLayerMode(True)
assert r.ReadFile(A) == IFSelect_RetDone; r.Transfer(doc)
st = XCAFDoc_DocumentTool.ShapeTool_s(doc.Main())
def name(l):
    n = TDataStd_Name(); return n.Get().ToExtString() if l.FindAttribute(TDataStd_Name.GetID_s(), n) else ''
fs = TDF_LabelSequence(); st.GetFreeShapes(fs)
targets = [fs.Value(i) for i in range(1, fs.Length() + 1) if any(name(fs.Value(i)).startswith(p) for p in prefixes)]
for l in targets: print('  removing:', name(l)); st.RemoveShape(l, True)
assert len(targets) == len(prefixes), 'expected %d matches, found %d' % (len(prefixes), len(targets))
st.UpdateAssemblies()
w = STEPCAFControl_Writer(); w.SetColorMode(True); w.SetNameMode(True); w.SetLayerMode(True)
w.Transfer(doc, STEPControl_AsIs); assert w.Write(OUT) == IFSelect_RetDone; print('  written', OUT)
