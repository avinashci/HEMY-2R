"""Put the dovetail bay (v22_dovetail_bay.py outputs) into the v2.2 assembly, keeping names, colours and layers.
Works on an assembly that has either polvinc's stock dovetail parts or an earlier bay version:
- the dovetail part             -> new dovetail solid
- the stock DC/USB/PCB or cover -> the bay cover
- the bay envelopes             -> updated envelopes (added if missing)
- the CH340E insert             -> updated insert (added if missing, red)
Run:  python3 v22_dovetail_bay_asm.py <assembly.step> <dovetail.step> <cover.step> <insert.step> <envelopes.step> <out.step>
"""
import sys
from OCP.STEPCAFControl import STEPCAFControl_Reader, STEPCAFControl_Writer
from OCP.TDocStd import TDocStd_Document
from OCP.TCollection import TCollection_ExtendedString
from OCP.XCAFDoc import XCAFDoc_DocumentTool, XCAFDoc_ColorGen, XCAFDoc_ColorSurf
from OCP.TDF import TDF_LabelSequence, TDF_Label
from OCP.TDataStd import TDataStd_Name
from OCP.IFSelect import IFSelect_RetDone
from OCP.STEPControl import STEPControl_Reader, STEPControl_AsIs
from OCP.TopLoc import TopLoc_Location
from OCP.Quantity import Quantity_Color, Quantity_TOC_RGB
A, DV, COV, INS, ENV, OUT = sys.argv[1:7]
DV_NAME = 'Dovetail (CH340E insert + 10 A bay, DEC index mark)'
COV_NAME = 'Dovetail bay cover (3 mm, 2 x M2.5 countersunk)'
INS_NAME = 'Dovetail CH340E insert (6061, red anodize)'
ENV_NAME = 'Dovetail bay envelopes (CH340E 16x16, 10 A jack, LED; clearance only, not machined)'
GROUP_NEW = 'DOVETAIL group (plate, clamp knobs, CH340E insert + 10 A bay)'
def is_dv(n): return n.startswith('Dovetail (')
def is_cov(n): return n.startswith('Dovetail stock DC jack') or n.startswith('Dovetail bay cover')
def is_env(n): return n.startswith('Dovetail bay envelopes')
def is_ins(n): return n.startswith('Dovetail CH340E insert')
def is_grp(n): return n.startswith('DOVETAIL group')

def read(p):
    r = STEPControl_Reader(); assert r.ReadFile(p) == IFSelect_RetDone; r.TransferRoots(); return r.OneShape()
new = {'DV': (read(DV), DV_NAME), 'COV': (read(COV), COV_NAME), 'INS': (read(INS), INS_NAME), 'ENV': (read(ENV), ENV_NAME)}
doc = TDocStd_Document(TCollection_ExtendedString("XmlOcaf"))
r = STEPCAFControl_Reader(); r.SetColorMode(True); r.SetNameMode(True); r.SetLayerMode(True)
assert r.ReadFile(A) == IFSelect_RetDone; r.Transfer(doc)
st = XCAFDoc_DocumentTool.ShapeTool_s(doc.Main()); ct = XCAFDoc_DocumentTool.ColorTool_s(doc.Main())
labs = TDF_LabelSequence(); st.GetShapes(labs)
def name(l):
    n = TDataStd_Name()
    return n.Get().ToExtString() if l.FindAttribute(TDataStd_Name.GetID_s(), n) else ''
def setname(l, s): TDataStd_Name.Set_s(l, TCollection_ExtendedString(s))
def colour(l, rgb):
    c = Quantity_Color(*rgb, Quantity_TOC_RGB)
    ct.SetColor(l, c, XCAFDoc_ColorGen); ct.SetColor(l, c, XCAFDoc_ColorSurf)
done, group = {}, None
for i in range(1, labs.Length() + 1):
    l = labs.Value(i); n = name(l).strip()
    if st.IsAssembly_s(l):
        if is_grp(n): group = l
        continue
    for key, test in (('DV', is_dv), ('COV', is_cov), ('ENV', is_env), ('INS', is_ins)):
        if test(n):
            shp, nm = new[key]; st.SetShape(l, shp); setname(l, nm); done[key] = l; print('  replaced:', n, '->', nm)
assert 'DV' in done and 'COV' in done, done
assert group is not None, 'dovetail group not found'
for key, rgb in (('ENV', (0.15, 0.55, 0.25)), ('INS', (0.80, 0.08, 0.10))):
    if key not in done:
        shp, nm = new[key]; el = st.AddShape(shp, False); setname(el, nm)
        cl = st.AddComponent(group, el, TopLoc_Location()); setname(cl, nm); done[key] = el; print('  added:', nm)
    colour(done[key], rgb)
setname(group, GROUP_NEW)
users = TDF_LabelSequence(); st.GetUsers_s(group, users)
for i in range(1, users.Length() + 1): setname(users.Value(i), GROUP_NEW)
comps = TDF_LabelSequence(); st.GetComponents_s(group, comps)
for i in range(1, comps.Length() + 1):
    c = comps.Value(i); ref = TDF_Label(); st.GetReferredShape_s(c, ref); setname(c, name(ref))
st.UpdateAssemblies()
w = STEPCAFControl_Writer(); w.SetColorMode(True); w.SetNameMode(True); w.SetLayerMode(True)
w.Transfer(doc, STEPControl_AsIs); assert w.Write(OUT) == IFSelect_RetDone; print('  written', OUT)
