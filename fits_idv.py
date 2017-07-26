import sys
sys.path.insert(0, "/Users/CEiffel/yt")
import yt
import time
import yt.visualization.volume_rendering.interactive_vr as ivr
from yt.visualization.volume_rendering.interactive_loop import \
    RenderingContext
import h5py
import numpy as np
from yt.visualization.volume_rendering import glfw_inputhook 

ds = yt.load("/Volumes/Transcend/R_Tony/interpolated_co/xycut_co/done/NGC5908.co.xycut.K.fits", nan_mask = 0.0)
ds.periodicity = (True, True, True)
shape = ds.domain_dimensions
v = ds.r[::1j*shape[0],::1j*shape[1],::1j*shape[2]]["intensity"]
print(v.min(), v.max())
v -= v.min()
v /= (v.max() - v.min())
v = 10**v
print(v.min(), v.max())

ds = yt.load_uniform_grid({'response': v}, v.shape,
    bbox=np.array([[0.0, 1.0] for _ in 'xyz']))
rc = RenderingContext(960, 960)

rc = RenderingContext(960, 960, always_on_top = True)

dd = ds.all_data()
collection = ivr.BlockCollection(data_source = dd)
collection.add_data("response")

br = ivr.BlockRendering(data = collection,
        vertex_shader = "default.v",
        fragment_shader = "max_intensity.f",
        colormap_vertex = "passthrough.v",
        colormap_fragment = "apply_colormap.f")

scene = ivr.SceneGraph()
scene.data_objects.append(collection)
scene.components.append(br)

# Create default camera
position = (0.0, 0.0, 0.0)
c = ivr.TrackballCamera(position=position,
        focus=ds.domain_center, near_plane=0.1)
scene.camera = c

# Start rendering loop
with yt.parallel_profile("opengl"):
    rc.start_loop(scene, c)
