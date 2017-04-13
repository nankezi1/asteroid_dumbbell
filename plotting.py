import dynamics.asteroid as asteroid
import kinematics.attitude as attitude

import numpy as np
import scipy as sp
import pdb

import matplotlib as mpl
from mpl_toolkits.mplot3d import axes3d
import matplotlib.pyplot as plt
import matplotlib.colors as colors
from matplotlib import animation

def vertex_plotter(ast, fig=plt.figure()):

    ax = axes3d.Axes3D(fig)

    for ii in np.arange(len(ast.F)):
        facet = [ast.asteroid_grav.get('V1')[ii,:], ast.asteroid_grav.get('V2')[ii,:], ast.asteroid_grav.get('V3')[ii,:]]
        tri = axes3d.art3d.Poly3DCollection([facet])
        tri.set_color('g')    
        tri.set_edgecolor('k')
        tri.set_alpha(1.0)
        ax.add_collection3d(tri)

    return 0

def plot_trajectory(pos, fig=plt.figure()):
    """Plot the state trajectory in a 3D view

    """

    traj_ax = fig.gca(projection='3d')
    traj_ax.set_xlim([-3, 3])
    traj_ax.set_ylim([-3, 3])
    traj_ax.set_zlim([-3, 3])
    # plotting.vertex_plotter(ast, traj_fig)

    traj_ax.plot(pos[:,0],pos[:,1],pos[:,2])

    return 0
    
def plot_energy(time,KE, PE, fig=plt.figure()):
    """Plot the energy behavior

    """

    E = KE + PE
    Ediff = np.absolute(E - E[0])

    energy_ax = fig.add_subplot(111)
    energy_ax.plot(time,Ediff, label=r'$\Delta E$')
    energy_ax.set_xlabel('Time')
    energy_ax.set_ylabel(r'$\Delta E$')
    energy_ax.legend()
    energy_ax.grid(True)

    return 0

def animate_inertial_trajectory(t, state, ast, dum, filename=''):
    """Animate inertial trajectory

    Plot the motion of the dumbbell around the asteroid
    """

    # First set up the figure, the axis, and the plot element we want to animate
    fig = plt.figure()
    ax = axes3d.Axes3D(fig)

    ax.set_xlim3d([-2.0, 2.0])
    ax.set_xlabel('X')

    ax.set_ylim3d([-2.0, 2.0])
    ax.set_ylabel('Y')

    ax.set_zlim3d([-2.0, 2.0])
    ax.set_zlabel('Z')

    ax_colors = ['r', 'g', 'b'] # b1, b2, b3
    db_colors = ['r', 'b', 'k'] # m1, m2, COM

    # initialize the animation elements
    ast_frame = [ax.plot([], [], [], '-', lw=2, c=c)[0] for c in ax_colors]
    db_masses = [ax.plot([], [], [], 'o', c=c)[0] for c in db_colors]
    db_frame = [ax.plot([], [], [], '-', lw=2, c=c)[0] for c in ax_colors]
    db_body = [ax.plot([], [], [], '-', lw=2, c='k')[0]]

    # ax.view_init(90,0)

    # initialization function: plot the background of each frame
    def init():
        for ast_line, db_line, db_pt in zip(ast_frame, db_frame, db_masses):
            ast_line.set_data([], [])
            ast_line.set_3d_properties([])

            db_line.set_data([], [])
            db_line.set_3d_properties([])

            db_pt.set_data([], [])
            db_pt.set_3d_properties([])

        db_body[0].set_data([], [])
        db_body[0].set_3d_properties([])
        return ast_frame + db_masses + db_frame + db_body

    # animation function.  This is called sequentially
    def animate(ii):
        # multiple time steps per frame
        ii = (ii) % t.shape[0]
        pos = state[:, 0:3]
        vel = state[:, 3:6]
        Rdb2i = state[:, 6:15]
        w = state[:, 15:18]

        # convert the asteroid body frame to the inertial frame and plot
        Ra2i = attitude.rot3(ast.omega*t[ii], 'c')

        for jj, tup in enumerate(zip(ast_frame, db_frame, db_masses)):
            ast_line, db_line, db_pt = tup
            xi, yi, zi = Ra2i[:, jj]

            ast_line.set_data([0, xi], [0, yi])
            ast_line.set_3d_properties([0, zi])

            # first body fixed axis of dumbbell in inertial frame
            db1_i = Rdb2i[ii, :].reshape((3, 3))[:, 0].T

            # draw the dumbbell frame
            dbxi, dbyi, dbzi = Rdb2i[ii,:].reshape((3,3))[:, jj]
            xcom, ycom, zcom = pos[ii,:]
            db_line.set_data([xcom, xcom + dbxi], [ycom, ycom + dbyi])
            db_line.set_3d_properties([zcom, zcom + dbzi])

            # compute position of this mass
            if jj == 0:  # mass 1
                x1, y1, z1 = pos[ii, :] - db1_i * dum.mratio
                db_pt.set_data(x1, y1)
                db_pt.set_3d_properties(z1)
            elif jj == 1:  # mass 2
                x2, y2, z2 = pos[ii, :] + db1_i * (1-dum.mratio)
                db_pt.set_data(x2, y2)
                db_pt.set_3d_properties(z2)
            elif jj == 2:  # COM
                db_pt.set_data(xcom, ycom)
                db_pt.set_3d_properties(zcom)
            else:
                print('There are only 3 dumbbell masses')
                break

        db_body[0].set_data([x1, x2], [y1, y2])
        db_body[0].set_3d_properties([z1, z2])

        # fig.canvas.draw()
        return ast_frame + db_frame + db_masses + db_body
        
        
    # instantiate the animator
    anim = animation.FuncAnimation(fig, animate, init_func=init, frames=t.shape[0], interval=1/30*1e3, blit=True)

    # Save as mp4. This requires mplayer or ffmpeg to be installed
    if filename:
        anim.save(filename + '.mp4', fps=30, extra_args=['-vcodec', 'libx264'])

    plt.show() 

def animate_relative_trajectory(t, state, ast, dum, filename=''):
    """Animate the relative trajectory defined wrt asteroid body fixed frame

        Plot the motion of the dumbbell around the asteroid

        Inputs: 
            t - simulation time
            state - state of dumbbell with respect to asteroi
            ast
            dum 
            filename

        Outputs:

    """

    # First set up the figure, the axis, and the plot elements we want to animate
    fig = plt.figure()
    ax = axes3d.Axes3D(fig)

    ax.set_xlim3d([-2.0, 2.0])
    ax.set_xlabel('X')

    ax.set_ylim3d([-2.0, 2.0])
    ax.set_ylabel('Y')

    ax.set_zlim3d([-2.0, 2.0])
    ax.set_zlabel('Z')

    ax_colors = ['r', 'g', 'b'] # b1, b2, b3
    db_colors = ['r', 'b', 'k'] # m1, m2, COM

    # initialize the animation elements
    ast_frame = [ax.plot([], [], [], '-', lw=2, c=c)[0] for c in ax_colors]
    db_masses = [ax.plot([], [], [], 'o', c=c)[0] for c in db_colors]
    db_frame = [ax.plot([], [], [], '-', lw=2, c=c)[0] for c in ax_colors]
    db_body = [ax.plot([], [], [], '-', lw=2, c='k')[0]]

    # ax.view_init(90,0)

    # initialization function: plot the background of each frame
    def init():
        Identity = np.eye(3,3)
        for jj,tup in enumerate(zip(ast_frame, db_frame, db_masses)):
            ast_line, db_line, db_pt = tup
            xi, yi, zi = Identity[:,jj]
            ast_line.set_data([0, xi], [0, yi])
            ast_line.set_3d_properties([0, zi])

            db_line.set_data([], [])
            db_line.set_3d_properties([])

            db_pt.set_data([], [])
            db_pt.set_3d_properties([])

        db_body[0].set_data([], [])
        db_body[0].set_3d_properties([])
        return ast_frame + db_masses + db_frame + db_body

    # animation function.  This is called sequentially
    def animate(ii):
        # multiple time steps per frame
        ii = (10 * ii) % t.shape[0]
        pos = state[:, 0:3]
        vel = state[:, 3:6]
        Rdb2a = state[:, 6:15]
        w = state[:, 15:18]

        # Asteroid body frame 
        Identity = np.eye(3,3)

        for jj, tup in enumerate(zip(ast_frame, db_frame, db_masses)):
            ast_line, db_line, db_pt = tup
            xi, yi, zi = Identity[:, jj]

            ast_line.set_data([0, xi], [0, yi])
            ast_line.set_3d_properties([0, zi])

            # first body fixed axis of dumbbell in asteroid frame
            db1_i = Rdb2a[ii, :].reshape((3, 3))[:, 0].T

            # draw the dumbbell frame
            dbxi, dbyi, dbzi = Rdb2a[ii,:].reshape((3,3))[:, jj]
            xcom, ycom, zcom = pos[ii,:]
            db_line.set_data([xcom, xcom + dbxi], [ycom, ycom + dbyi])
            db_line.set_3d_properties([zcom, zcom + dbzi])

            # compute position of each
            if jj == 0:  # mass 1
                x1, y1, z1 = pos[ii, :] - db1_i * dum.mratio
                db_pt.set_data(x1, y1)
                db_pt.set_3d_properties(z1)
            elif jj == 1:  # mass 2
                x2, y2, z2 = pos[ii, :] + db1_i * (1-dum.mratio)
                db_pt.set_data(x2, y2)
                db_pt.set_3d_properties(z2)
            elif jj == 2:  # COM
                db_pt.set_data(xcom, ycom)
                db_pt.set_3d_properties(zcom)
            else:
                print('There are only 3 dumbbell masses')
                break

        db_body[0].set_data([x1, x2], [y1, y2])
        db_body[0].set_3d_properties([z1, z2])

        # fig.canvas.draw()
        return ast_frame + db_frame + db_masses + db_body
        
        
    # instantiate the animator
    anim = animation.FuncAnimation(fig, animate, init_func=init, frames=t.shape[0], interval=1/30*1e3, blit=True)

    # Save as mp4. This requires mplayer or ffmpeg to be installed
    if filename:
        anim.save(filename + '.mp4', fps=30, extra_args=['-vcodec', 'libx264'])

    plt.show()

def plot_inertial_comparison(ast_time, body_time, ast_state, body_state, ast, dum):
    """Compare the EOMS in the inertial frame, everything transformed to the inertial frame
    
    Inputs:
        ast_time - time vector from eoms_relative
        body_time - time vector from eoms_inertial
        ast_state - state vector from eoms_relative
        body_state - state vector from eoms_inertial
        ast - instance of Asteroid class
        dum - instance of Dumbbell class

    Outputs:

    """
    # convert simulations into the inertial frame    
    inertial_state = body2inertial(body_time, body_state, ast, dum) 
    ast2inertial_state,_,_ = ast2inertial(ast_time, ast_state, ast, dum)
    
     # extract out the states
    inertial_pos = inertial_state[:,0:3]
    inertial_vel = inertial_state[:,3:6]
    inertial_R_sc2inertial = inertial_state[:,6:15]
    inertial_w = inertial_state[:,15:18]
   
    a2i_pos = ast2inertial_state[:,0:3]
    a2i_vel = ast2inertial_state[:,3:6]
    a2i_R = ast2inertial_state[:,6:15]
    a2i_w = ast2inertial_state[:,15:18]
    
    # position comparison
    pos_fig, pos_axarr = plt.subplots(3,1, sharex=True)
    pos_axarr[0].plot(body_time, inertial_pos[:,0], label='Inertial EOMs')
    pos_axarr[0].plot(ast_time, a2i_pos[:,0], label='Transformed Relative')
    pos_axarr[0].set_ylabel(r'$X$ (km)')
        
    pos_axarr[1].plot(body_time, inertial_pos[:,1], label='Inertial EOMs')
    pos_axarr[1].plot(ast_time, a2i_pos[:,1], label='Transformed Relative')
    pos_axarr[1].set_ylabel(r'$Y$ (km)')
        
    pos_axarr[2].plot(body_time, inertial_pos[:,2], label='Inertial EOMs')
    pos_axarr[2].plot(ast_time, a2i_pos[:,2], label='Transformed Relative')
    pos_axarr[2].set_ylabel(r'$Z$ (km)')
     
    pos_axarr[2].set_xlabel('Time (sec)')
    plt.suptitle('Position Comparison')
    plt.legend()  

    posdiff_fig, posdiff_axarr = plt.subplots(3,1, sharex=True)
    posdiff_axarr[0].plot(body_time, np.absolute(inertial_pos[:,0]-a2i_pos[:,0]))
    posdiff_axarr[0].set_ylabel(r'$\Delta X$ (km)')
        
    posdiff_axarr[1].plot(body_time, np.absolute(inertial_pos[:,1]-a2i_pos[:,1]))
    posdiff_axarr[1].set_ylabel(r'$\Delta Y$ (km)')
        
    posdiff_axarr[2].plot(body_time, np.absolute(inertial_pos[:,2]-a2i_pos[:,2]))
    posdiff_axarr[2].set_ylabel(r'$\Delta Z$ (km)')
     
    posdiff_axarr[2].set_xlabel('Time (sec)')
    plt.suptitle('Position Difference')

    # velocity comparison
    vel_fig, vel_axarr = plt.subplots(3,1, sharex=True)
    vel_axarr[0].plot(body_time, inertial_vel[:,0], label='inertial EOMs')
    vel_axarr[0].plot(ast_time, a2i_vel[:,0], label='Transformed relative')
    vel_axarr[0].set_ylabel(r'$\dot X$ (km)')
        
    vel_axarr[1].plot(body_time, inertial_vel[:,1], label='inertial EOMs')
    vel_axarr[1].plot(ast_time, a2i_vel[:,1], label='Transformed relative')
    vel_axarr[1].set_ylabel(r'$\dot Y$ (km)')
        
    vel_axarr[2].plot(body_time, inertial_vel[:,2], label='inertial EOMs')
    vel_axarr[2].plot(ast_time, a2i_vel[:,2], label='Transformed relative')
    vel_axarr[2].set_ylabel(r'$\dot Z$ (km)')
     
    vel_axarr[2].set_xlabel('Time (sec)')
    plt.suptitle('Velocity Comparison')
    plt.legend()

    veldiff_fig, veldiff_axarr = plt.subplots(3,1, sharex=True)
    veldiff_axarr[0].plot(body_time, np.absolute(inertial_vel[:,0]-a2i_vel[:,0]))
    veldiff_axarr[0].set_ylabel(r'$\Delta \dot X$ (km)')
        
    veldiff_axarr[1].plot(body_time, np.absolute(inertial_vel[:,1]-a2i_vel[:,1]))
    veldiff_axarr[1].set_ylabel(r'$\Delta \dot Y$ (km)')
        
    veldiff_axarr[2].plot(body_time, np.absolute(inertial_vel[:,2]-a2i_vel[:,2]))
    veldiff_axarr[2].set_ylabel(r'$\Delta \dot Z$ (km)')
     
    veldiff_axarr[2].set_xlabel('Time (sec)')
    plt.suptitle('Velocity Difference')

    # angular velocity comparison
    angvel_fig, angvel_axarr = plt.subplots(3,1, sharex=True)
    angvel_axarr[0].plot(body_time, inertial_w[:,0], label='Inertial EOMs')
    angvel_axarr[0].plot(ast_time, a2i_w[:,0], label='Transformed Relative')
    angvel_axarr[0].set_ylabel(r'$\dot \Omega_1$ (rad/sec)')
        
    angvel_axarr[1].plot(body_time, inertial_w[:,1], label='Inertial EOMs')
    angvel_axarr[1].plot(ast_time, a2i_w[:,1], label='Transformed Relative')
    angvel_axarr[1].set_ylabel(r'$\dot \Omega_2$ (rad/sec)')
        
    angvel_axarr[2].plot(body_time, inertial_w[:,2], label='Inertial EOMs')
    angvel_axarr[2].plot(ast_time, a2i_w[:,2], label='Transformed Relative')
    angvel_axarr[2].set_ylabel(r'$\dot \Omega_3$ (rad/sec)')
     
    angvel_axarr[2].set_xlabel('Time (sec)')
    plt.suptitle('Angular Velocity Comparison')
    plt.legend()

    angveldiff_fig, angveldiff_axarr = plt.subplots(3,1, sharex=True)
    angveldiff_axarr[0].plot(body_time, np.absolute(inertial_w[:,0]-a2i_w[:,0]))
    angveldiff_axarr[0].set_ylabel(r'$\Delta \dot \Omega$ (rad/sec)')
        
    angveldiff_axarr[1].plot(body_time, np.absolute(inertial_w[:,1]-a2i_w[:,1]))
    angveldiff_axarr[1].set_ylabel(r'$\Delta \dot \Omega_2$ (rad/sec)')
        
    angveldiff_axarr[2].plot(body_time, np.absolute(inertial_w[:,2]-a2i_w[:,2]))
    angveldiff_axarr[2].set_ylabel(r'$\Delta \dot \Omega_3$ (rad/sec)')
     
    angveldiff_axarr[2].set_xlabel('Time (sec)')
    plt.suptitle('Angular Velocity Difference')

    # attitude matrix comparison
    att_fig, att_axarr = plt.subplots(3,3, sharex=True, sharey=True)
    plt.suptitle('Rotation Matrix')
    for ii in range(9):
        row, col = np.unravel_index(ii, [3,3])
        att_axarr[row,col].plot(body_time, inertial_R_sc2inertial[:,ii])
        att_axarr[row,col].plot(ast_time, a2i_R[:,ii])

    # attitude matrix difference
    attdiff_fig, attdiff_axarr = plt.subplots(3,3, sharex=True, sharey=True)
    plt.suptitle('Rotation Matrix Difference')
    for ii in range(9):
        row, col = np.unravel_index(ii, [3,3])
        attdiff_axarr[row,col].plot(body_time, np.absolute(inertial_R_sc2inertial[:,ii]-a2i_R[:,ii]))

    plt.show()

    return 0

def plot_asteroid_comparision(ast_time, body_time, ast_state, body_state, ast, dum):
    """Plot the states in the asteroid fixed frame
    
    Inputs:
        ast_time - 
        body_time
        ast_state - 
        body_state
        ast
        dum -

    Outputs:
        
    """

    # convert simulations into the asteroid frame    
    int2ast_state = body2ast(body_time, body_state, ast, dum) 
    
    # extract out the states
    i2a_pos = int2ast_state[:,0:3]
    i2a_vel = int2ast_state[:,3:6]
    i2a_R_sc2inertial = int2ast_state[:,6:15]
    i2a_w = inertial_state[:,15:18]
   
    ast_pos = ast_state[:,0:3]
    ast_vel = ast_state[:,3:6]
    ast_R = ast_state[:,6:15]
    ast_w = ast_state[:,15:18]
    
    # position comparison
    pos_fig, pos_axarr = plt.subplots(3,1, sharex=True)
    pos_axarr[0].plot(body_time, inertial_pos[:,0], label='Inertial EOMs')
    pos_axarr[0].plot(ast_time, a2i_pos[:,0], label='Transformed Relative')
    pos_axarr[0].set_ylabel(r'$X$ (km)')
        
    pos_axarr[1].plot(body_time, inertial_pos[:,1], label='Inertial EOMs')
    pos_axarr[1].plot(ast_time, a2i_pos[:,1], label='Transformed Relative')
    pos_axarr[1].set_ylabel(r'$Y$ (km)')
        
    pos_axarr[2].plot(body_time, inertial_pos[:,2], label='Inertial EOMs')
    pos_axarr[2].plot(ast_time, a2i_pos[:,2], label='Transformed Relative')
    pos_axarr[2].set_ylabel(r'$Z$ (km)')
     
    pos_axarr[2].set_xlabel('Time (sec)')
    plt.suptitle('Position Comparison')
    plt.legend()  

    posdiff_fig, posdiff_axarr = plt.subplots(3,1, sharex=True)
    posdiff_axarr[0].plot(body_time, np.absolute(inertial_pos[:,0]-a2i_pos[:,0]))
    posdiff_axarr[0].set_ylabel(r'$\Delta X$ (km)')
        
    posdiff_axarr[1].plot(body_time, np.absolute(inertial_pos[:,1]-a2i_pos[:,1]))
    posdiff_axarr[1].set_ylabel(r'$\Delta Y$ (km)')
        
    posdiff_axarr[2].plot(body_time, np.absolute(inertial_pos[:,2]-a2i_pos[:,2]))
    posdiff_axarr[2].set_ylabel(r'$\Delta Z$ (km)')
     
    posdiff_axarr[2].set_xlabel('Time (sec)')
    plt.suptitle('Position Difference')

    # velocity comparison
    vel_fig, vel_axarr = plt.subplots(3,1, sharex=True)
    vel_axarr[0].plot(body_time, inertial_vel[:,0], label='inertial EOMs')
    vel_axarr[0].plot(ast_time, a2i_vel[:,0], label='Transformed relative')
    vel_axarr[0].set_ylabel(r'$\dot X$ (km)')
        
    vel_axarr[1].plot(body_time, inertial_vel[:,1], label='inertial EOMs')
    vel_axarr[1].plot(ast_time, a2i_vel[:,1], label='Transformed relative')
    vel_axarr[1].set_ylabel(r'$\dot Y$ (km)')
        
    vel_axarr[2].plot(body_time, inertial_vel[:,2], label='inertial EOMs')
    vel_axarr[2].plot(ast_time, a2i_vel[:,2], label='Transformed relative')
    vel_axarr[2].set_ylabel(r'$\dot Z$ (km)')
     
    vel_axarr[2].set_xlabel('Time (sec)')
    plt.suptitle('Velocity Comparison')
    plt.legend()

    veldiff_fig, veldiff_axarr = plt.subplots(3,1, sharex=True)
    veldiff_axarr[0].plot(body_time, np.absolute(inertial_vel[:,0]-a2i_vel[:,0]))
    veldiff_axarr[0].set_ylabel(r'$\Delta \dot X$ (km)')
        
    veldiff_axarr[1].plot(body_time, np.absolute(inertial_vel[:,1]-a2i_vel[:,1]))
    veldiff_axarr[1].set_ylabel(r'$\Delta \dot Y$ (km)')
        
    veldiff_axarr[2].plot(body_time, np.absolute(inertial_vel[:,2]-a2i_vel[:,2]))
    veldiff_axarr[2].set_ylabel(r'$\Delta \dot Z$ (km)')
     
    veldiff_axarr[2].set_xlabel('Time (sec)')
    plt.suptitle('Velocity Difference')

    # angular velocity comparison
    angvel_fig, angvel_axarr = plt.subplots(3,1, sharex=True)
    angvel_axarr[0].plot(body_time, inertial_w[:,0], label='Inertial EOMs')
    angvel_axarr[0].plot(ast_time, a2i_w[:,0], label='Transformed Relative')
    angvel_axarr[0].set_ylabel(r'$\dot \Omega_1$ (rad/sec)')
        
    angvel_axarr[1].plot(body_time, inertial_w[:,1], label='Inertial EOMs')
    angvel_axarr[1].plot(ast_time, a2i_w[:,1], label='Transformed Relative')
    angvel_axarr[1].set_ylabel(r'$\dot \Omega_2$ (rad/sec)')
        
    angvel_axarr[2].plot(body_time, inertial_w[:,2], label='Inertial EOMs')
    angvel_axarr[2].plot(ast_time, a2i_w[:,2], label='Transformed Relative')
    angvel_axarr[2].set_ylabel(r'$\dot \Omega_3$ (rad/sec)')
     
    angvel_axarr[2].set_xlabel('Time (sec)')
    plt.suptitle('Angular Velocity Comparison')
    plt.legend()

    angveldiff_fig, angveldiff_axarr = plt.subplots(3,1, sharex=True)
    angveldiff_axarr[0].plot(body_time, np.absolute(inertial_w[:,0]-a2i_w[:,0]))
    angveldiff_axarr[0].set_ylabel(r'$\Delta \dot \Omega$ (rad/sec)')
        
    angveldiff_axarr[1].plot(body_time, np.absolute(inertial_w[:,1]-a2i_w[:,1]))
    angveldiff_axarr[1].set_ylabel(r'$\Delta \dot \Omega_2$ (rad/sec)')
        
    angveldiff_axarr[2].plot(body_time, np.absolute(inertial_w[:,2]-a2i_w[:,2]))
    angveldiff_axarr[2].set_ylabel(r'$\Delta \dot \Omega_3$ (rad/sec)')
     
    angveldiff_axarr[2].set_xlabel('Time (sec)')
    plt.suptitle('Angular Velocity Difference')

    # attitude matrix comparison
    att_fig, att_axarr = plt.subplots(3,3, sharex=True, sharey=True)
    plt.suptitle('Rotation Matrix')
    for ii in range(9):
        row, col = np.unravel_index(ii, [3,3])
        att_axarr[row,col].plot(body_time, inertial_R_sc2inertial[:,ii])
        att_axarr[row,col].plot(ast_time, a2i_R[:,ii])

    # attitude matrix difference
    attdiff_fig, attdiff_axarr = plt.subplots(3,3, sharex=True, sharey=True)
    plt.suptitle('Rotation Matrix Difference')
    for ii in range(9):
        row, col = np.unravel_index(ii, [3,3])
        attdiff_axarr[row,col].plot(body_time, np.absolute(inertial_R_sc2inertial[:,ii]-a2i_R[:,ii]))

    plt.show()
    return 0
if __name__ == '__main__':
    ast = asteroid.Asteroid('itokawa', 1024)
    vertex_plotter(ast,plt.figure())

    plt.show()
