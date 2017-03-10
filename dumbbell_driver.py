# Run the simulation
import numpy as np
from scipy import integrate
import pdb

import matplotlib as mpl
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt

import dynamics.asteroid as asteroid
import dynamics.dumbbell as dumbbell
import kinematics.attitude as attitude
import plotting

# ode options
RelTol = 1e-6
AbsTol = 1e-6

ast = asteroid.Asteroid('castalia',32)
dum = dumbbell.Dumbbell()

# time span
t0 = 0
tf = 1e5 # sec
num_steps = 1e5

time = np.linspace(t0,tf,num_steps)

periodic_pos = np.array([1.495746722510590,0.000001002669660,0.006129720493607]) 
periodic_vel = np.array([0.000000302161724,-0.000899607989820,-0.000000013286327])

state = integrate.odeint(dum.eoms_relative_translation, np.hstack((periodic_pos,periodic_vel)), time, args=(ast,), atol=AbsTol, rtol=RelTol)

fig = plt.figure()
ax = fig.gca(projection='3d')

ax.plot(state[:,0], state[:,1], state[:,2])
ax.set_xlim([-3, 3])
ax.set_ylim([-3, 3])
ax.set_zlim([-3, 3])
plt.show()

def inertial_test():
    # set initial state
    initial_pos = np.array([1.495746722510590,0.000001002669660,0.006129720493607]) # km for center of mass in body frame
    # km/sec for COM in asteroid fixed frame
    initial_vel = np.array([0.000000302161724,-0.000899607989820,-0.000000013286327]) + attitude.hat_map(ast.omega*np.array([0,0,1])).dot(initial_pos)
    initial_R = np.eye(3,3).reshape(9) # transforms from dumbbell body frame to the inertial frame
    initial_w = np.array([0,0,0]) # angular velocity of dumbbell wrt to inertial frame represented in sc body frame

    initial_state = np.hstack((initial_pos, initial_vel, initial_R, initial_w))

    state = integrate.odeint(dum.eoms_inertial, initial_state, time, args=(ast,), atol=AbsTol, rtol=RelTol)

    pos = state[:,0:3]
    vel = state[:,3:6]
    R = state[:,6:15]
    ang_vel = state[:,15:18]

    KE, PE = dum.inertial_energy(time,state,ast)

    mpl.rcParams['legend.fontsize'] = 10

    traj_fig = plt.figure()
    # trajectory plot
    plotting.plot_trajectory(pos,traj_fig)

    # kinetic energy
    energy_fig = plt.figure()
    plotting.plot_energy(time,KE,PE,energy_fig)

    plt.show()

def relative_test():
    """Test the relative equations of motion

    """

    """
        pos - position of COM of dumbbell wrt asteroid in asteroid fixed frame
        vel - velocit of COM wrt asteroid in asteroid fixed frame
        R - transforms vectors in SC body frame to asteroid frame
        W - angular velocity of dumbbell wrt inertial frame in asteroid frame
    """
    initial_pos = np.array([1.495746722510590,0.000001002669660,0.006129720493607]) # km for center of mass in body frame
    # km/sec for COM in asteroid fixed frame
    initial_vel = np.array([0.000000302161724,-0.000899607989820,-0.000000013286327]) 
    initial_R = np.eye(3,3).reshape(9) # transforms from dumbbell body frame to the asteroid frame
    initial_w = np.array([0,0,0]) # angular velocity of dumbbell wrt to inertial frame represented in asteroid body frame

    initial_state = np.hstack((initial_pos, initial_vel, initial_R, initial_w))

    state = integrate.odeint(dum.eoms_relative, initial_state, time, args=(ast,), atol=AbsTol, rtol=RelTol)

    pos = state[:,0:3]
    vel = state[:,3:6]
    R = state[:,6:15]
    ang_vel = state[:,15:18]

    # KE, PE = dum.relative_energy(time,state,ast)

    mpl.rcParams['legend.fontsize'] = 10

    traj_fig = plt.figure()
    # trajectory plot
    plotting.plot_trajectory(pos,traj_fig)

    # kinetic energy
    # energy_fig = plt.figure()
    # plotting.plot_energy(time,KE,PE,energy_fig)

    plt.show()

    return state


def eoms_relative_translation(state, t, ast, dum):
    """Translational equations of motion

    Inputs:
        state - 
            pos - 3x1 position vector in asteroid fixed frame
            vel - 3x1 velocity vector in asteroid fixed frame

    Outputs:
        statedot

    """
    # unpack the state
    pos = state[0:3]
    vel = state[3:6]
    # unpack constants
    omega_hat = attitude.hat_map(np.array([0, 0, ast.omega]))
    (_, U_grad, _, _) = ast.polyhedron_potential(pos)

    m = dum.m1 + dum.m2
    # state derivatives
    pos_dot = vel
    vel_dot = U_grad - 2 * omega_hat.dot(vel) - omega_hat.dot(omega_hat.dot(pos))

    state_dot = np.hstack((pos_dot, vel_dot))
    
    return state_dot

def eoms_relative(state, t, ast, dum):
    # unpack the state
        pos = state[0:3] # location of the COM of dumbbell in asteroid fixed frame
        vel = state[3:6] # vel of com wrt to asteroid expressed in the asteroid fixed frame
        
        Ra = attitude.rot3(ast.omega*t, 'c') # asteroid body frame to inertial frame

        # unpack parameters for the dumbbell
        m1 = self.m1
        m2 = self.m2
        m = m1 + m2
        J = self.J
        Jr = R.dot(J).dot(R.T)
        Omega = ast.omega*np.array([0,0,1]) # angular velocity vector of asteroid

        # the position of each mass in the asteroid body frame
        rho1 = self.zeta1
        rho2 = self.zeta2

        # position of each mass in the asteroid frame
        z1 = pos + R.dot(rho1)
        z2 = pos + R.dot(rho2)

        z = pos # position of COM in asteroid frame

        # compute the potential at this state
        (U1, U1_grad, U1_grad_mat, U1laplace) = ast.polyhedron_potential(z1)
        (U2, U2_grad, U2_grad_mat, U2laplace) = ast.polyhedron_potential(z2)

        # force due to each mass expressed in asteroid body frame
        F1 = m1*U1_grad
        F2 = m2*U2_grad
        # F_com = (m1+m2)*U_grad_com

        # compute the moments due to each mass
        M1 = m1 * np.cross(U1_grad, R.dot(rho1))
        M2 = m2 * np.cross(U2_grad, R.dot(rho2))

        # state derivatives
        pos_dot = vel - attitude.hat_map(Omega).dot(pos)
        vel_dot = 1/m * (F1 + F2 - m * attitude.hat_map(Omega).dot(vel))
        # vel_dot = 1/m * (F_com) 
        R_dot = attitude.hat_map(w).dot(R) - attitude.hat_map(Omega).dot(R)
        R_dot = R_dot.reshape(9)
        w_dot = np.linalg.inv(Jr).dot(M1 + M2 - attitude.hat_map(Omega).dot(Jr).dot(w) 
                      + attitude.hat_map(w).dot(Jr).dot(w) - Jr.dot(attitude.hat_map(Omega)).dot(w) 
                      + attitude.hat_map(Omega).dot(Jr).dot(w) - attitude.hat_map(w).dot(Jr).dot(w))

        state_dot = np.hstack((pos_dot,vel_dot,R_dot,w_dot))
        
        return state_dot