"""Merge flush faces (remove leftover seam lines) on the parts the index-mark scripts touched.
Keeps a part's merged version only if it stays valid and its volume is unchanged.
Run:  python3 ~/Developer/HEMY/restyle/v2.2/tools/v22_merge_faces.py
"""
import os, sys
from OCP.STEPControl import STEPControl_Reader, STEPControl_Writer, STEPControl_AsIs
from OCP.ShapeUpgrade import ShapeUpgrade_UnifySameDomain
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.GProp import GProp_GProps
from OCP.BRepGProp import BRepGProp
from OCP.IFSelect import IFSelect_RetDone
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'parts')
def read(p):
    r = STEPControl_Reader()
    if r.ReadFile(p) != IFSelect_RetDone: sys.exit('cannot read ' + p)
    r.TransferRoots(); return r.OneShape()
def vol(s):
    g = GProp_GProps(); BRepGProp.VolumeProperties_s(s, g); return g.Mass()
for n in ['HEMY2R - Lid.step', 'HEMY2R - Side plate A.step', 'HEMY2R - Side plate A (recessed panel).step',
          'HEMY2R - Side plate B.step', 'HEMY2R - Side plate B (recessed panel).step',
          'HEMY2R - Dovetail (indicator LED hole).step']:
    p = os.path.join(P, n); s = read(p); v0 = vol(s)
    u = ShapeUpgrade_UnifySameDomain(s, True, True, False); u.Build(); m = u.Shape()
    ok = BRepCheck_Analyzer(m).IsValid() and abs(vol(m) - v0) < 0.01
    if ok:
        w = STEPControl_Writer(); w.Transfer(m, STEPControl_AsIs)
        if w.Write(p) != IFSelect_RetDone: sys.exit('write failed')
    print('  %-48s %s' % (n, 'merged' if ok else 'kept as is (merge would not stay valid)'))
print('done')
