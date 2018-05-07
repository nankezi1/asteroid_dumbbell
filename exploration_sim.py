"""Exploration Simulation

Simulation of a spacecraft exploring an asteroid

States are chosen to minimize a cost function tied to the uncertainty of the 
shape. Full SE(3) dynamics and the polyhedron potential model is used

Author
------
Shankar Kulumani		GWU		skulumani@gwu.edu
"""
from __future__ import absolute_import, division, print_function, unicode_literals

import pdb
import logging
import os
import tempfile
import argparse
from collections import defaultdict

import h5py
import numpy as np
from scipy import integrate

from lib import asteroid, surface_mesh, cgal, mesh_data, reconstruct
from lib import surface_mesh
from lib import controller as controller_cpp

from dynamics import dumbbell, eoms, controller
from point_cloud import wavefront
from kinematics import attitude

def initialize(output_file):
    """Initialize all the things for the simulation

    Output_file : the actual HDF5 file to save the data/parameters to

    """
    logger = logging.getLogger(__name__)
    logger.info('Initialize asteroid and dumbbell objects')

    AbsTol = 1e-9
    RelTol = 1e-9
    
    # true asteroid and dumbbell
    v, f = wavefront.read_obj('./data/shape_model/CASTALIA/castalia.obj')

    true_ast_meshdata = mesh_data.MeshData(v, f)
    true_ast_meshparam = asteroid.MeshParam(true_ast_meshdata)
    true_ast = asteroid.Asteroid('castalia', true_ast_meshparam)
    dum = dumbbell.Dumbbell(m1=500, m2=500, l=0.003)
    
    # estimated asteroid (starting as an ellipse)
    surf_area = 0.01
    max_angle = np.sqrt(surf_area / true_ast.get_axes()[0]**2)
    min_angle = 10
    max_distance = 0.5
    max_radius = 0.03

    ellipsoid = surface_mesh.SurfMesh(true_ast.get_axes()[0], true_ast.get_axes()[1], true_ast.get_axes()[2],
                                      min_angle, max_radius, max_distance)

    est_ast_meshdata = mesh_data.MeshData(ellipsoid.verts(), ellipsoid.faces())
    est_ast_rmesh = reconstruct.ReconstructMesh(est_ast_meshdata)

    # controller functions 
    complete_controller = controller_cpp.Controller()
    
    # lidar object
    lidar = cgal.Lidar()
    lidar = lidar.view_axis(np.array([1, 0, 0]))
    lidar = lidar.up_axis(np.array([0, 0, 1]))
    lidar = lidar.fov(np.deg2rad(np.array([7, 7]))).dist(2).num_steps(3)

    # raycaster from c++
    caster = cgal.RayCaster(true_ast_meshdata)

    return (true_ast_meshdata, true_ast, complete_controller, est_ast_meshdata, 
            est_ast_rmesh, lidar, caster, AbsTol, RelTol)

def simulate(output_filename="/tmp/exploration_sim.hdf5"):
    """Actually run the simulation around the asteroid
    """
    logger = logging.getLogger(__name__)

    num_steps = int(1e3)
    time = np.linspace(0, num_steps, num_steps)
    t0, tf = time[0], time[-1]
    dt = time[1] - time[0]

    # define the initial condition
    initial_pos = np.array([1.5, 0, 0])
    initial_vel = np.array([0, 0, 0])
    initial_R = attitude.rot3(np.pi / 2).reshape(-1)
    initial_w = np.array([0, 0, 0])
    initial_state = np.hstack((initial_pos, initial_vel, initial_R, initial_w))
    
    with h5py.File(output_filename, 'w') as hf:
        hf.create_dataset('time', data=time)

        # initialize the simulation objects
        (true_ast_meshdata, true_ast, complete_controller,
         est_ast_meshdata, est_ast_rmesh, lidar, caster, AbsTol, RelTol) = initialize(hf)
        
        # initialize the ODE function
        system = integrate.ode(eoms.eoms_controlled_inertial_pybind)
        system.set_integrator("lsoda", atol=AbsTol, rtol=RelTol, nsteps=num_steps)
        system.set_initial_value(initial_state, t0)
        system.set_f_params(true_ast, dum, complete_controller, est_ast_rmesh)
        
        point_cloud = defaultdict(list)
        
        state = np.zeros((num_steps + 1, 18))
        t = np.zeros(num_steps + 1)
        int_array = []
        state[0, :] = initial_state

        ii = 1
        while system.successful() and system.t < tf:
            # integrate the system
            t[ii] = (system.t + dt)
            state[ii, :] = system.integrate(system.t + dt)

            logger.info("Step: {} Time: {}".format(ii, t[ii]))

            if not (np.floor(t[ii]) % 1):
                logger.info("RayCasting at t: {}".format(t[ii]))

                targets = lidar.define_targets(state[ii, 0:3],
                                               state[ii, 6:15].reshape((3, 3)),
                                               np.linalg.norm(state[ii, 0:3]))
                # update the asteroid inside the caster
                nv = true_ast.rotate_vertices(t[ii])
                Ra = true_ast.rot_ast2int(t[ii])
                
                true_ast_meshdata.update_mesh(nv, true_ast_meshdata.get_faces())
                caster.update_mesh(true_ast_meshdata)

                # do the raycasting
                intersections = caster.castarray(state[ii, 0:3], targets)

                # reconstruct the mesh with new measurements



if __name__ == "__main__":
    logging_file = tempfile.mkstemp(suffix='.txt.')[1]

    logging.basicConfig(filename=logging_file,
                        filemode='w', level=logging.INFO,
                        format='%(asctime)s %(levelname)-8s %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    print("Logging to {}".format(logging_file))

    parser = argparse.ArgumentParser(description="Exploration and asteroid reconstruction simulation",
                                      formatter_class=argparse.RawTextHelpFormatter)
    
    parser.add_argument("simulation_data",
                        help="Filename to store the simulation data")
    parser.add_argument("reconstruct_data",
                        help="Filename to store the reconstruction data")

    group = parser.add_mutually_exclusive_group()
    group.add_argument("-s", "--simulate", help="Run the exploration simulation",
                       action="store_true")
    
    args = parser.parse_args()
                                                                
    if args.simulate:
        simulate(args.simulation_data)
    elif args.reconstruct:
        output_path = tempfile.mkdtemp()



