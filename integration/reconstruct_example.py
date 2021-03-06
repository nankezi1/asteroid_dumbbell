# Reconstruction example and testing

from visualization import graphics
from point_cloud import wavefront
from lib import surface_mesh, reconstruct, mesh_data

from kinematics import attitude
import numpy as np
import scipy.io

import pdb

# sphere= surface_mesh.SurfMesh(0.5, 0.5, 0.5, 10, 0.15, 0.5)
# vs, fs = sphere.verts(), sphere.faces()

vs, fs = wavefront.read_obj('./data/shape_model/CASTALIA/castalia.obj')

# max_angle = wavefront.spherical_surface_area(0.5, surf_area=0.03)
max_angle = 0.5

mfig = graphics.mayavi_figure()

# mesh_param = wavefront.polyhedron_parameters(v, f)
pt = np.array([0, 0, 1])

vert_weight = np.full(vs.shape[0], (np.pi * np.max(np.linalg.norm(vs, axis=1)) )**2)

vs_new, vw_new = wavefront.spherical_incremental_mesh_update(pt, vs, fs,
                                                     vertex_weight=vert_weight,
                                                     max_angle=max_angle)


# view the mesh
graphics.mayavi_addMesh(mfig, vs_new, fs, representation='surface',
                        scalars=vw_new, colormap='viridis', color=None)
graphics.mayavi_addPoint(mfig, pt)

# duplicate the same thing with c++
mfig_cpp = graphics.mayavi_figure()

vw = np.full(vs.shape[0], (np.pi * np.max(np.linalg.norm(vs, axis=1)))**2)
# mesh = mesh_data.MeshData(vs, fs)
rmesh = reconstruct.ReconstructMesh(vs, fs, vw)

rmesh.update(pt, max_angle)

graphics.mayavi_addMesh(mfig_cpp, rmesh.get_verts(), rmesh.get_faces(), representation='surface',
                        scalars=np.squeeze(rmesh.get_weights()), colormap='viridis', color=None)
graphics.mayavi_addPoint(mfig_cpp, pt)
