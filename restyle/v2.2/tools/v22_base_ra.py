import sys; sys.path.insert(0,'.')
from lib import *
from OCP.STEPCAFControl import STEPCAFControl_Reader
from OCP.TDocStd import TDocStd_Document
from OCP.TCollection import TCollection_ExtendedString
from OCP.XCAFDoc import XCAFDoc_DocumentTool
from OCP.TDF import TDF_Label, TDF_ChildIterator
from OCP.collections import Sequence_TDF_Label
from OCP.TDataStd import TDataStd_Name
doc=TDocStd_Document(TCollection_ExtendedString("XmlOcaf"))
r=STEPCAFControl_Reader(); r.SetNameMode(True); r.ReadFile(sys.argv[1]); r.Transfer(doc)
st=XCAFDoc_DocumentTool.ShapeTool_s(doc.Main())
def name(l):
    a=TDataStd_Name(); return a.Get().ToExtString() if l.FindAttribute(TDataStd_Name.GetID_s(),a) else '?'
seq=Sequence_TDF_Label(); st.GetShapes(seq)
print('all shape labels:',seq.Length())
for i in range(1,seq.Length()+1):
    l=seq.Value(i); n=name(l)
    if any(k in n for k in sys.argv[2:]):
        s=st.GetShape_s(l); print(n,'| asm' if st.IsAssembly_s(l) else '| part', fbb(s))
        if not st.IsAssembly_s(l):
            for k,so in enumerate(solids(s)): print('   solid',k,fbb(so),round(vol(so)))
