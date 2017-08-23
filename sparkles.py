import numpy as np
from mayavi import mlab

data = np.load('sparkles_nm1_2d.npz')
tdata = np.load('nm1.npz')

arr = data['arr'].astype(float)
#cv = data['cv']
pos = data['pos']

nm1_t = tdata['template']

f1 = mlab.figure(bgcolor=(0,0,0))
im = mlab.imshow(nm1_t[0], vmin=0, vmax=255, figure=f1)

if pos.shape[1] == 2:
    z = np.zeros((pos.shape[0],1))
    pos = np.hstack((pos, z))

f2 = mlab.figure(bgcolor=(0,0,0))
pts = mlab.points3d(pos[:,0], pos[:,1], pos[:,2], colormap='plasma', scale_factor=1, figure=f2)
pts.glyph.scale_mode = 'data_scaling_off'
pts.glyph.color_mode = 'color_by_scalar'

@mlab.show
@mlab.animate(delay=10)
def anim():
    i = 0
    while True:
        
        i += 1
        if i >= arr.shape[1] or i >= nm1_t.shape[0]:
            i = 0

        pts.mlab_source.dataset.point_data.scalars = arr[:,i]
        im.mlab_source.set(scalars=nm1_t[i])
        
        f1.scene.render()
        f2.scene.render()

        yield

anim()


