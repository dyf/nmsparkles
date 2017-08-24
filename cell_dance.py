import numpy as np
from mayavi import mlab
import vtk.util.numpy_support as vtknp
import moviepy.editor as mpy

data = np.load('cell_dance.npz')
arr = data['arr'].astype(float) * 200
pos = data['pos'].astype(float)
cres = data['cres'].astype(float)

print arr.shape
print arr.min(), arr.max()

f = mlab.figure(bgcolor=(0,0,0))

pts = mlab.points3d(pos[:,0], pos[:,1], arr[:,0], cres, colormap='Vega20', scale_factor=1, figure=f, vmin=0, vmax=20)
pts.glyph.scale_mode = 'data_scaling_off'
pts.glyph.color_mode = 'color_by_scalar'

#f.scene.z_minus_view()
#f.scene.camera.roll(90)

@mlab.show
@mlab.animate(delay=10)
def anim():
    i = 0
    while True:
        
        i += 4
        if i >= arr.shape[1]:
            i = 0


        #pts.mlab_source.dataset.point_data.scalars = arr[:,i].copy()
        pts.mlab_source.set(z=arr[:,i])
        #print(pts.mlab_source.dataset.points)
        #print(dir(pts.mlab_source.dataset.points))
       
        
        f.scene.render()

        yield

#anim()

def make_frame(t):
    i = int(t*30*10)
    pts.mlab_source.set(z=arr[:,i])
    f.scene.camera.azimuth(.5)
    f.scene.render()
    return mlab.screenshot(antialiased=True)

animation = mpy.VideoClip(make_frame, duration=30)
animation.write_gif("cell_dance.gif", fps=30)