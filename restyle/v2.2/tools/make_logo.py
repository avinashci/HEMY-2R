from matplotlib.textpath import TextPath
from matplotlib.font_manager import FontProperties
from matplotlib.path import Path
FONT='/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf'   # Arial-metric regular
def text_path(txt, width):
    fp=FontProperties(fname=FONT)
    tp=TextPath((0,0),txt,size=1.0,prop=fp)
    v=tp.vertices; w=v[:,0].max()-v[:,0].min(); k=width/w
    xmin=v[:,0].min()
    X=lambda p:'%.3f %.3f'%((p[0]-xmin)*k,-p[1]*k)
    d=[];i=0;c=tp.codes
    while i<len(c):
        if c[i]==Path.MOVETO: d.append('M '+X(v[i])); i+=1
        elif c[i]==Path.LINETO: d.append('L '+X(v[i])); i+=1
        elif c[i]==Path.CURVE3: d.append('Q '+X(v[i])+' '+X(v[i+1])); i+=2
        elif c[i]==Path.CURVE4: d.append('C '+X(v[i])+' '+X(v[i+1])+' '+X(v[i+2])); i+=3
        elif c[i]==Path.CLOSEPOLY: d.append('Z'); i+=1
        else: i+=1
    return ' '.join(d), v[:,1].max()*k, -v[:,1].min()*k
CREDIT='Based on HEMY by polvinc'

MARK='''<g transform="translate(3,17) scale(0.9) skewX(-12)">
      <rect x="0" y="-9" width="2.2" height="9"/><rect x="5.4" y="-9" width="2.2" height="9"/><rect x="2.2" y="-5.6" width="3.2" height="2.2"/>
      <g transform="translate(8.6,0)"><rect x="0" y="-9" width="2.2" height="9"/><rect x="2.2" y="-9" width="4.0" height="2.0"/><rect x="2.2" y="-5.5" width="3.2" height="2.0"/><rect x="2.2" y="-2.0" width="4.0" height="2.0"/></g>
      <polygon transform="translate(15.8,0)" points="0,0 0,-9 2.6,-9 4.6,-5.0 6.6,-9 9.2,-9 9.2,0 7.0,0 7.0,-5.2 5.3,-2.0 3.9,-2.0 2.2,-5.2 2.2,0"/>
      <polygon transform="translate(26.0,0)" points="0,-9 2.4,-9 3.7,-6.3 5.0,-9 7.4,-9 4.8,-4.2 4.8,0 2.6,0 2.6,-4.2"/>
    </g>
    <path d="M 2.6 21.6 Q 15 19.7 29.2 19.3 L 29.5 20.7 Q 16 20.9 2.6 21.6 Z"/>
    <g transform="translate(31.0,24.2) scale(0.78) skewX(-12)">
      <path d="M 0 -4.5 L 2.6 -4.5 A 1 1 0 0 1 3.6 -3.5 L 3.6 -2.7 A 1 1 0 0 1 2.6 -1.7 L 1.1 -1.7 L 1.1 -1.1 L 3.6 -1.1 L 3.6 0 L 0 0 L 0 -2.3 A 0.5 0.5 0 0 1 0.5 -2.8 L 2.5 -2.8 L 2.5 -3.4 L 0 -3.4 Z"/>
      <path transform="translate(4.4,0)" fill-rule="evenodd" d="M 0 -4.5 L 2.6 -4.5 A 1 1 0 0 1 3.6 -3.5 L 3.6 -2.8 A 1 1 0 0 1 2.9 -1.85 L 3.7 0 L 2.5 0 L 1.8 -1.7 L 1.1 -1.7 L 1.1 0 L 0 0 Z M 1.1 -3.5 L 2.5 -3.5 L 2.5 -2.75 L 1.1 -2.75 Z"/>
    </g>
    <path transform="translate(36.8,6.0)" fill-rule="evenodd" d="M 0.55 -2.6 L 0.75 -1.85 L 1.45 -1.5 L 2.15 -1.9 L 1.9 -1.15 L 2.0 -0.4 L 2.6 0 L 2.0 0.4 L 1.9 1.15 L 2.15 1.9 L 1.45 1.5 L 0.75 1.85 L 0.55 2.6 L 0 2.0 L -0.55 2.6 L -0.75 1.85 L -1.45 1.5 L -2.15 1.9 L -1.9 1.15 L -2.0 0.4 L -2.6 0 L -2.0 -0.4 L -1.9 -1.15 L -2.15 -1.9 L -1.45 -1.5 L -0.75 -1.85 L -0.55 -2.6 L 0 -2.0 Z M 0.8 0 A 0.8 0.8 0 1 0 -0.8 0 A 0.8 0.8 0 1 0 0.8 0 Z"/>'''
# raw mark bbox: x 2.6..39.4 (36.8), y 3.4..24.2 (20.8)
def block(mark_w, gap_ratio=0.125, credit_ratio=0.92):
    """returns svg group (origin top-left of the block), block width and height"""
    s=mark_w/36.8
    cw=mark_w*credit_ratio
    d,asc,desc=text_path(CREDIT,cw)
    gap=mark_w*gap_ratio*0.67
    mh=20.8*s
    g='<g transform="translate(%.4f,%.4f) scale(%.5f)">%s</g>'%(-2.6*s,-3.4*s,s,MARK)
    g+='<path transform="translate(%.4f,%.4f)" d="%s"/>'%((mark_w-cw)/2, mh+gap+asc, d)
    return g, mark_w, mh+gap+asc+desc

# 1. sticker 40 x 32, red, white
g,w,h=block(31.3)
ox,oy=(40-w)/2,(32-h)/2
sticker='''<svg xmlns="http://www.w3.org/2000/svg" width="43mm" height="35mm" viewBox="-1.5 -1.5 43 35">
  <!-- HEMY 2R GPS sticker. Finished 40 x 32 mm, R3 corners; 1.5 mm bleed; magenta hairline = cut line. All text outlined. -->
  <title>HEMY 2R sticker (print, 40 x 32 mm + 1.5 mm bleed)</title>
  <rect x="-1.5" y="-1.5" width="43" height="35" fill="#D62A2A"/>
  <g fill="#FFFFFF" transform="translate(%.3f,%.3f)">%s</g>
  <rect x="0" y="0" width="40" height="32" rx="3" fill="none" stroke="#FF00FF" stroke-width="0.1"/>
</svg>
'''%(ox,oy,g)
open('HEMY_2R_GPS_sticker_PRINT.svg','w').write(sticker)
open('HEMY_2R_GPS_sticker_preview.svg','w').write('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 256"><rect width="320" height="256" fill="#f4f4f2"/><g transform="translate(40,32) scale(6)"><rect width="40" height="32" rx="3" fill="#D62A2A"/><g fill="#fff" transform="translate(%.3f,%.3f)">%s</g></g></svg>'%(ox,oy,g))
print('sticker block %.2f x %.2f, margins %.2f / %.2f'%(w,h,ox,oy))

# 2. side plate laser marking, 70 mm wide (fits the 93 x 93 recessed pocket), black = mark
g,w,h=block(70.0)
laser='''<svg xmlns="http://www.w3.org/2000/svg" width="%.2fmm" height="%.2fmm" viewBox="0 0 %.3f %.3f">
  <!-- HEMY 2R side-plate logo for LASER MARKING. Black = marked area. Actual size %.1f x %.1f mm. No background. All text outlined. -->
  <title>HEMY 2R logo, laser marking, %.0f mm wide</title>
  <g fill="#000000">%s</g>
</svg>
'''%(w,h,w,h,w,h,w,g)
open('HEMY_2R_sideplate_logo_LASER_70mm.svg','w').write(laser)
# preview on a side plate (125 x 125 face, 93 x 93 pocket R6), logo centred
px,py=62.5-w/2,62.5-h/2
prev='''<svg xmlns="http://www.w3.org/2000/svg" viewBox="-5 -5 135 135">
  <rect x="-5" y="-5" width="135" height="135" fill="#f4f4f2"/>
  <rect x="0" y="0" width="125" height="125" rx="1.5" fill="#c9ced3"/>
  <rect x="16" y="16" width="93" height="93" rx="6" fill="#bfc5cb" stroke="#a9b0b7" stroke-width="0.4"/>
  <g fill="#eef1f3" transform="translate(%.3f,%.3f)">%s</g>
</svg>'''%(px,py,g)
open('HEMY_2R_sideplate_logo_preview.svg','w').write(prev)
print('laser logo %.1f x %.1f mm'%(w,h))
