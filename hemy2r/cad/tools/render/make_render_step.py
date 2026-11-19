"""Make a render-ready copy of the HEMY 2R assembly for Onshape (or any renderer).

- Home pose: the DOVETAIL group turned 180 deg about the DEC axis (X axis through Y 0, Z 70), so the knobs face
  side A (east) and the dovetail ports face side B (west), as at the home position.
- Removes the parts that shouldn't show: the brass jaw option (bronze is kept) and the clearance envelopes.
- Sets appearance colours: natural aluminium body, red insert, bronze jaws, dark counterweight and LA-40B, black antenna.
  Drives and electronics keep the colours they came with.

Run:  python3 make_render_step.py "<HEMY2R v2.2 - assembly.step>" "<out render STEP>"
"""
import sys, math
from OCP.STEPCAFControl import STEPCAFControl_Reader, STEPCAFControl_Writer
from OCP.STEPControl import STEPControl_AsIs
from OCP.IFSelect import IFSelect_RetDone
from OCP.TDocStd import TDocStd_Document
from OCP.TCollection import TCollection_ExtendedString
from OCP.XCAFDoc import XCAFDoc_DocumentTool, XCAFDoc_ColorType, XCAFDoc_Location
from OCP.TDF import TDF_LabelSequence, TDF_Label
from OCP.TDataStd import TDataStd_Name
from OCP.Quantity import Quantity_Color, Quantity_TOC_RGB
from OCP.TopLoc import TopLoc_Location
from OCP.gp import gp_Trsf, gp_Ax1, gp_Pnt, gp_Dir

src, out = sys.argv[1], sys.argv[2]
doc = TDocStd_Document(TCollection_ExtendedString("doc"))
r = STEPCAFControl_Reader(); r.SetColorMode(True); r.SetNameMode(True); r.SetLayerMode(True)
if r.ReadFile(src) != IFSelect_RetDone: sys.exit("cannot read " + src)
r.Transfer(doc)
st = XCAFDoc_DocumentTool.ShapeTool_s(doc.Main())
ct = XCAFDoc_DocumentTool.ColorTool_s(doc.Main())

def name(l):
    a = TDataStd_Name()
    return a.Get().ToExtString() if l.FindAttribute(TDataStd_Name.GetID_s(), a) else ""

def components(l):
    seq = TDF_LabelSequence(); st.GetComponents_s(l, seq, False)
    return [seq.Value(i) for i in range(1, seq.Length() + 1)]

def referred(l):
    ref = TDF_Label(); st.GetReferredShape_s(l, ref); return ref

AL = (0.80, 0.81, 0.83)
RULES = [  # (substring in lower-case name, colour), first match wins; only parts (not groups) are coloured
    ("frame", AL), ("panel", AL), ("lid", AL), ("base flange", AL), ("base plate", AL),
    ("bay cover", AL), ("knob", AL), ("dovetail (", AL),
    ("red anodize", (0.75, 0.05, 0.08)),
    ("option a bronze", (0.70, 0.50, 0.28)),
    ("antenna", (0.05, 0.05, 0.05)),
    ("counterweight", (0.25, 0.25, 0.27)), ("washer", (0.25, 0.25, 0.27)),
    ("la-40b", (0.12, 0.12, 0.13)),
    ("switch", (0.70, 0.70, 0.72)),
    ("handle", (0.60, 0.61, 0.63)),
]
SKIP_COLOUR = ("reducer, motor", "electronics (board", "board spacers")
REMOVE = ("option b brass", "envelopes")

def colour_for(n):
    s = n.lower()
    if any(k in s for k in SKIP_COLOUR): return None
    for k, c in RULES:
        if k in s: return c
    return None

rot = gp_Trsf(); rot.SetRotation(gp_Ax1(gp_Pnt(0, 0, 70), gp_Dir(1, 0, 0)), math.pi)
removed, coloured, rotated = [], [], []

def walk(asm_label, inside_dovetail=False):
    for comp in components(asm_label):
        n = name(comp) or name(referred(comp))
        s = n.lower()
        if any(k in s for k in REMOVE):
            ref = referred(comp)
            st.RemoveComponent(comp); removed.append(n)
            st.RemoveShape(ref, True)   # drop the now-unused part so it doesn't come back as a free shape
            continue
        if "dovetail group" in s and not inside_dovetail:
            old = st.GetLocation_s(comp)
            XCAFDoc_Location.Set_s(comp, TopLoc_Location(rot).Multiplied(old))
            rotated.append(n)
        c = colour_for(n) if not st.IsAssembly_s(referred(comp)) else None
        if c is not None:
            col = Quantity_Color(c[0], c[1], c[2], Quantity_TOC_RGB)
            ref = referred(comp)
            for lab in (comp, ref):
                ct.SetColor(lab, col, XCAFDoc_ColorType.XCAFDoc_ColorGen)
                ct.SetColor(lab, col, XCAFDoc_ColorType.XCAFDoc_ColorSurf)
            coloured.append(n)
        ref = referred(comp)
        if st.IsAssembly_s(ref):
            walk(ref, inside_dovetail or "dovetail group" in s)

roots = TDF_LabelSequence(); st.GetFreeShapes(roots)
for i in range(1, roots.Length() + 1):
    walk(roots.Value(i))
st.UpdateAssemblies()

w = STEPCAFControl_Writer(); w.SetColorMode(True); w.SetNameMode(True); w.SetLayerMode(True)
w.Transfer(doc, STEPControl_AsIs)
if w.Write(out) != IFSelect_RetDone: sys.exit("cannot write " + out)
print("rotated:", rotated)
print("removed:", removed)
print("coloured:", len(coloured))
