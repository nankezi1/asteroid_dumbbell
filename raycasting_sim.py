"""Simulation of a spacecraft with a LIDAR taking measurements 
around an asteroid
"""
from __future__ import absolute_import, division, print_function, unicode_literals
from dynamics import asteroid, dumbbell, eoms, controller
from kinematics import attitude
from visualization import plotting, graphics

import numpy as np
from scipy import integrate

# create the sensor and raycaster

# create an asteroid and dumbbell

# simulate dumbbell moving aroudn asteroid
ast = asteroid.Asteroid('castalia', 4092, 'mat')
dum = dumbbell.Dumbbell(m1=500, m2=500, l=0.003)
des_att_func = controller.body_fixed_pointing_attitude
des_tran_func = controller.inertial_fixed_state
AbsTol = 1e-9
RelTol = 1e-9

num_steps = int(1e4)
time = np.linspace(0, num_steps, num_steps)
t0, tf = time[0], time[-1]
dt = time[1] - time[0]

initial_pos = np.array([1.5, 0, 0])
initial_vel = np.array([0, 0, 0])
initial_R = np.eye(3,3).reshape(-1)
initial_w = np.array([0, 0, 0])
initial_state = np.hstack((initial_pos, initial_vel, initial_R, initial_w))

# try both a controlled and uncontrolled simulation
# t, istate, astate, bstate = eoms.inertial_eoms_driver(initial_state, time, ast, dum)

system = integrate.ode(eoms.eoms_controlled_inertial)
system.set_integrator('lsoda', atol=AbsTol, rtol=RelTol, nsteps=num_steps)
system.set_initial_value(initial_state, t0)
system.set_f_params(ast, dum, des_att_func, des_tran_func)

state = np.zeros((num_steps+1, 18))
t = np.zeros(num_steps+1)
state[0, :] = initial_state

ii = 1
while system.successful() and system.t < tf:
    # integrate the system and save state to an array
    t[ii] = (system.t + dt)
    state[ii, :] = system.integrate(system.t + dt)
    ii+= 1

# plot the simulation
# plotting.animate_inertial_trajectory(t, istate, ast, dum)
# plotting.plot_inertial(t, istate, ast, dum, fwidth=1)

# TODO: animation in mayavi
mfig = graphics.mayavi_figure()

graphics.draw_polyhedron_mayavi(ast.V, ast.F, mfig)
graphics.mayavi_plot_trajectory(mfig, state[:, 0:3])
