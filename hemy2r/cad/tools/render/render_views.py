import pickle, sys, numpy as np, vtk
from vtk.util.numpy_support import numpy_to_vtk, numpy_to_vtkIdTypeArray
d=pickle.load(open('asm.pkl','rb'))
# home pose: dovetail group turned 180 deg about the DEC axis (X, through Y 0, Z 70)
d2=[]
for n,V,F,c in d:
    if 'DOVETAIL group' in n:
        V=V.copy(); V[:,1]=-V[:,1]; V[:,2]=140.0-V[:,2]
    d2.append((n,V,F,c))
d=d2
AL=(0.80,0.81,0.83); AL2=(0.74,0.75,0.77); DARK=(0.16,0.16,0.17); BLACK=(0.05,0.05,0.05)
def mat(n):
    s=n.lower()
    if 'envelope' in s or 'option b brass' in s: return None
    if 'insert' in s and 'red' in s: return ((0.72,0.06,0.08),0.5,30)
    if 'option a bronze' in s: return ((0.66,0.48,0.27),0.6,40)
    if 'la-40b' in s: return ((0.12,0.12,0.13),0.3,10)
    if 'reducer, motor' in s: return ((0.22,0.22,0.23),0.4,20)
    if 'antenna' in s or 'handle' in s: return (BLACK,0.3,20)
    if 'counterweight bar' in s: return ((0.30,0.30,0.32),0.5,30)
    if 'electronics (board' in s: return ((0.10,0.35,0.18),0.3,10)
    if 'switch' in s: return ((0.70,0.70,0.72),0.6,40)
    if 'knob' in s: return ((0.78,0.79,0.81),0.5,30)
    if 'lid' == s.split('/')[-1].strip().lower(): return (AL,0.25,8)
    return (AL,0.25,8)
def actor(V,F,m):
    pd=vtk.vtkPolyData(); pts=vtk.vtkPoints(); pts.SetData(numpy_to_vtk(V.astype(np.float64),deep=True)); pd.SetPoints(pts)
    cells=np.hstack([np.full((len(F),1),3,dtype=np.int64),F.astype(np.int64)]).ravel()
    ca=vtk.vtkCellArray(); ca.SetCells(len(F),numpy_to_vtkIdTypeArray(cells,deep=True)); pd.SetPolys(ca)
    cl=vtk.vtkCleanPolyData(); cl.SetInputData(pd); cl.SetTolerance(1e-6)
    nm=vtk.vtkPolyDataNormals(); nm.SetInputConnection(cl.GetOutputPort()); nm.SetFeatureAngle(35); nm.SplittingOn(); nm.ConsistencyOff(); nm.AutoOrientNormalsOff()
    mp=vtk.vtkPolyDataMapper(); mp.SetInputConnection(nm.GetOutputPort())
    a=vtk.vtkActor(); a.SetMapper(mp); p=a.GetProperty()
    c,spec,pw=m; p.SetColor(*c); p.SetAmbient(0.18); p.SetDiffuse(0.8); p.SetSpecular(spec); p.SetSpecularPower(pw); p.SetInterpolationToPhong()
    return a
def render(out, az, el, size=(1800,1300), zoom=1.15, roll=0):
    r=vtk.vtkRenderer(); r.SetBackground(1,1,1); r.SetBackground2(0.88,0.90,0.93); r.GradientBackgroundOn()
    for n,V,F,c in d:
        m=mat(n)
        if m is None or len(F)==0: continue
        r.AddActor(actor(V,F,m))
    w=vtk.vtkRenderWindow(); w.SetOffScreenRendering(1); w.AddRenderer(r); w.SetSize(*size); w.SetMultiSamples(8)
    r.ResetCamera(); cam=r.GetActiveCamera(); cam.SetViewUp(0,0,1)
    cam.Azimuth(az); cam.Elevation(el); cam.OrthogonalizeViewUp(); cam.Roll(roll); r.ResetCamera(); cam.Zoom(zoom)
    r.RemoveAllLights()
    k=vtk.vtkLightKit(); k.SetKeyLightIntensity(0.85); k.AddLightsToRenderer(r)
    try:
        r.UseSSAOOn(); r.SetSSAORadius(8); r.SetSSAOBias(0.05); r.SetSSAOKernelSize(64)
    except Exception: pass
    w.Render()
    f=vtk.vtkWindowToImageFilter(); f.SetInput(w); f.Update()
    pw=vtk.vtkPNGWriter(); pw.SetFileName(out); pw.SetInputConnection(f.GetOutputPort()); pw.Write()
# default camera looks along -Z? set initial position along -Y (side A) by first placing camera
import math
def view(out, direction, size=(1800,1300), zoom=1.15, focal=None):
    r=vtk.vtkRenderer(); r.SetBackground(1,1,1); r.SetBackground2(0.86,0.88,0.92); r.GradientBackgroundOn()
    for n,V,F,c in d:
        m=mat(n)
        if m is None or len(F)==0: continue
        r.AddActor(actor(V,F,m))
    w=vtk.vtkRenderWindow(); w.SetOffScreenRendering(1); w.AddRenderer(r); w.SetSize(*size); w.SetMultiSamples(8)
    cam=r.GetActiveCamera(); dx,dy,dz=direction
    r.ResetCamera(); fx,fy,fz=focal or cam.GetFocalPoint()
    cam.SetFocalPoint(fx,fy,fz); cam.SetPosition(fx+dx*900,fy+dy*900,fz+dz*900); cam.SetViewUp(0,0,1); cam.SetViewAngle(24)
    r.ResetCameraClippingRange(); cam.Zoom(zoom)
    k=vtk.vtkLightKit(); k.SetKeyLightIntensity(0.9); k.AddLightsToRenderer(r)
    w.Render()
    f=vtk.vtkWindowToImageFilter(); f.SetInput(w); f.Update()
    pw=vtk.vtkPNGWriter(); pw.SetFileName(out); pw.SetInputConnection(f.GetOutputPort()); pw.Write()
views={'hero':((-0.45,-0.8,0.42),1.3,(30,0,40)),
       'sideB_ports':((-0.6,0.75,0.3),1.3,(30,0,40)),
       'dovetail_ports':((-0.25,0.95,0.15),2.0,(-88,30,72)),
       'base_power':((0.05,1.0,0.12),2.0,(-6,40,-4))}
for k in sys.argv[1:]:
    dirn,z,f=views[k]; view(k+'.png', dirn, zoom=z, focal=f); print(k)
