import numpy as np
import matplotlib.pyplot as plt
import argparse
from matplotlib import gridspec as gs
from matplotlib.widgets import Cursor
import matplotlib

matplotlib.use('TkAgg')

dz = 0.5
bins = 70

parser = argparse.ArgumentParser()

parser.add_argument("filename", type=np.str)
parser.add_argument('-t', "-todos=", '--todos', action='store_true', help="Histograma de la proyección de todos los datos.")
parser.add_argument('-z', "-corte=", '--corte', nargs="+", type=float, help="Histograma de la proyeccion de un corte dado. Acepta argumentos multiples.") 
parser.add_argument('-r', "-trasnform=", '--rotado', action='store_true', help="Hace coincidir la componente principal de la distribución con el eje x y el centro de la misma con la coordenada (0,0). Por default muestra todos los datos. Combinable con las otras opciones (-t, -z, -i)")
parser.add_argument('-i', "-interactivo=", '--interactivo', action='store_true', help="Activa el modo interactivo.")
parser.set_defaults(todos=False, rotado=False, interactivo=False)

args = parser.parse_args()

data = np.genfromtxt(getattr(args, "filename"))

# defino una funcion para cada acción para que quede mas ordenado

def plot_all():
    slice_x, slice_y = np.array([list(point[:2]) for point in data]).T

    grid = gs.GridSpec(2, 2, width_ratios=[4,1], height_ratios=[1,4], hspace=0.005, wspace=0.01)

    fig = plt.figure(figsize=(10,10))

    im_ax = plt.subplot(grid[1,0])
    x_ax = plt.subplot(grid[0,0], sharex=im_ax)
    y_ax = plt.subplot(grid[1,1], sharey=im_ax)

    im_ax.hist2d(slice_x, slice_y, cmap="inferno", bins=bins)
    x_ax.hist(slice_x, bins=int(bins/2), density=True, color="dimgrey");
    y_ax.hist(slice_y, bins=int(bins/2), density=True, orientation=u"horizontal", color="dimgrey");

    x_ax.axis("off")
    y_ax.axis("off")

    im_ax.set_xlabel("$x$", fontsize=15)
    im_ax.set_ylabel("$y$", fontsize=15, rotation=0)

    x_ax.set_title("Todos los datos en plano x-y", fontsize=20,x=.6)

    plt.show()
    
def plot_slice(z0):
    slice_x, slice_y = np.array([list(point[:2]) for point in data if abs(point[2]-z0)<2*dz]).T

    grid = gs.GridSpec(2, 2, width_ratios=[4,1], height_ratios=[1,4], hspace=0.005, wspace=0.01)

    fig = plt.figure(figsize=(10,10))

    im_ax = plt.subplot(grid[1,0])
    x_ax = plt.subplot(grid[0,0], sharex=im_ax)
    y_ax = plt.subplot(grid[1,1], sharey=im_ax)

    im_ax.hist2d(slice_x, slice_y, cmap="inferno", bins=bins)
    x_ax.hist(slice_x, bins=int(bins/2), density=True, color="dimgrey");
    y_ax.hist(slice_y, bins=int(bins/2), density=True, orientation=u"horizontal", color="dimgrey");

    x_ax.axis("off")
    y_ax.axis("off")

    im_ax.set_xlabel("$x$", fontsize=15)
    im_ax.set_ylabel("$y$", fontsize=15, rotation=0)

    cov_mat = np.cov(slice_x,slice_y)
    eig_values, eig_vectors = np.linalg.eig(cov_mat)

    principal_idx = np.argmin(eig_values)
    principal_ax =  eig_vectors[principal_idx]

    x_center = np.mean(slice_x)
    y_center = np.mean(slice_y)

    x = np.linspace(np.amin(slice_x), np.amax(slice_x), 1000)
    principal_ax_plot = y_center + principal_ax[0]/principal_ax[1] * (x-x_center)

    im_ax.plot(x, principal_ax_plot, "--", c="royalblue")
    im_ax.plot([x_center], [y_center], "o", c="royalblue", markersize=10)

    x_ax.set_title("$z_0$ = {}, d$z$ = {}".format(z0,dz), fontsize=20,x=.6)
    
    return fig 
    
def plot_rotation(z0, dz_):
    slice_x, slice_y = np.array([list(point[:2]) for point in data if abs(point[2]-z0)<2*dz_]).T

    cov_mat = np.cov(slice_x,slice_y)
    eig_values, eig_vectors = np.linalg.eig(cov_mat)

    principal_idx = np.argmin(eig_values)
    principal_ax =  eig_vectors[principal_idx]

    x_center = np.mean(slice_x)
    y_center = np.mean(slice_y)

    theta = -np.arctan(principal_ax[0]/principal_ax[1])

    rot_mat = np.array([[np.cos(theta), -np.sin(theta)], [np.sin(theta), np.cos(theta)]])

    slice_x_rot, slice_y_rot = np.array([np.matmul(rot_mat, point.T) for point in np.array([slice_x, slice_y]).T]).T

    grid = gs.GridSpec(2, 2, width_ratios=[4,1], height_ratios=[1,4], hspace=0.005, wspace=0.01)

    fig = plt.figure(figsize=(10,10))

    im_ax = plt.subplot(grid[1,0])
    x_ax = plt.subplot(grid[0,0], sharex=im_ax)
    y_ax = plt.subplot(grid[1,1], sharey=im_ax)

    x_center = np.mean(slice_x_rot)
    y_center = np.mean(slice_y_rot)

    im_ax.hist2d(slice_x_rot-x_center, slice_y_rot-y_center, cmap="inferno", bins=bins)
    x_ax.hist(slice_x_rot-x_center, bins=int(bins/2), density=True, color="dimgrey");
    y_ax.hist(slice_y_rot-y_center, bins=int(bins/2), density=True, orientation=u"horizontal", color="dimgrey");

    x_ax.axis("off")
    y_ax.axis("off")

    im_ax.set_xlabel("$x$", fontsize=15)
    im_ax.set_ylabel("$y$", fontsize=15, rotation=0)

    cov_mat = np.cov(slice_x,slice_y)
    eig_values, eig_vectors = np.linalg.eig(cov_mat)

    principal_idx = np.argmin(eig_values)
    principal_ax =  eig_vectors[principal_idx]

    x = np.linspace(np.amin(slice_x_rot), np.amax(slice_x_rot), 1000)
    principal_ax_plot = [0]*len(x)

    im_ax.plot(x, principal_ax_plot, "--", c="royalblue")
    im_ax.plot([0], [0], "o", c="royalblue", markersize=10)

    x_ax.set_title("$z_0$ = {}, d$z$ = {}".format(z0,dz), fontsize=20,x=.6);
    
    if dz_ != 0.5:
        x_ax.set_title("Todos los datos");
    
    return fig
    
def plot_interactive():
    z0 = -3.5 # default

    slice_x, slice_y = np.array([list(point[:2]) for point in data if abs(point[2]-z0)<2*dz]).T

    grid = gs.GridSpec(3, 3, width_ratios=[4,8,1], height_ratios=[1,4,4], hspace=0.02, wspace=0.01)

    fig = plt.figure(figsize=(14,10))

    x_ax = plt.subplot(grid[0,1])
    y_ax = plt.subplot(grid[1:,2])
    im_ax = plt.subplot(grid[1:,1], sharex=x_ax, sharey=y_ax)
    angle_ax = plt.subplot(grid[1,0])
    coord_ax = plt.subplot(grid[2,0], sharex=angle_ax)

    im_ax.cla()
    x_ax.cla()
    y_ax.cla()

    im_ax.hist2d(slice_x, slice_y, cmap="inferno", bins=bins, range=[[-15,15],[-15,15]])
    x_ax.hist(slice_x, bins=int(bins/2), density=True, color="dimgrey", zorder=100);
    y_ax.hist(slice_y, bins=int(bins/2), density=True, orientation=u"horizontal", color="dimgrey", zorder=100);

    y_ax.yaxis.tick_right()
    y_ax.yaxis.set_label_position("right")

    x_ax.grid(zorder=-1)
    y_ax.grid(zorder=-1)

    plt.setp(x_ax.get_xticklabels(), visible=False)
    plt.setp(x_ax.get_yticklabels(), visible=False)
    plt.setp(y_ax.get_xticklabels(), visible=False)
    plt.setp(im_ax.get_yticklabels(), visible=False)

    im_ax.set_xlabel("$x$", fontsize=15)
    y_ax.set_ylabel("$y$", fontsize=15, rotation=0)

    cov_mat = np.cov(slice_x,slice_y)
    eig_values, eig_vectors = np.linalg.eig(cov_mat)

    principal_idx = np.argmin(eig_values)
    principal_ax =  eig_vectors[principal_idx]

    x_center = np.mean(slice_x)
    y_center = np.mean(slice_y)

    x = np.linspace(np.amin(slice_x), np.amax(slice_x), 1000)
    principal_ax_plot = y_center + principal_ax[0]/principal_ax[1] * (x-x_center)

    im_ax.plot(x, principal_ax_plot, "--", c="royalblue")
    im_ax.plot([x_center], [y_center], "o", c="royalblue", markersize=10)

    x_centers = []
    y_centers = []

    x_slices = []
    y_slices = []

    principal_axs = []

    thetas = []

    z0s = np.arange(-4.5,5.5,1)

    for z0_ in z0s:
        s_x, s_y = np.array([list(point[:2]) for point in data if abs(point[2]-z0_)<2*dz]).T

        x_slices.append(s_x)
        y_slices.append(s_y)

        cov_mat = np.cov(slice_x,slice_y)
        eig_values, eig_vectors = np.linalg.eig(cov_mat)

        x_centers.append(np.mean(s_x))
        y_centers.append(np.mean(s_y))

        cov_mat = np.cov(s_x,s_y)
        eig_values, eig_vectors = np.linalg.eig(cov_mat)

        principal_idx = np.argmin(eig_values)
        principal_ax_ =  eig_vectors[principal_idx]

        principal_axs.append(principal_ax_)

        thetas.append(np.arctan(principal_ax_[0]/principal_ax_[1])*180/np.pi)

    angleline, = angle_ax.plot(z0s, thetas, "--")
    angle_ax.grid()
    angle_ax.set_ylabel("Ángulo [Grados]")

    xline, = coord_ax.plot(z0s, x_centers, "--", label="$x$")
    yline, = coord_ax.plot(z0s, y_centers, "--", label="$y$")
    coord_ax.grid()
    coord_ax.set_xlabel("$z_0$")
    coord_ax.legend()
    coord_ax.set_ylabel("Coord. del centro")

    angledot, = angle_ax.plot([z0],[np.arctan(principal_ax[0]/principal_ax[1])*180/np.pi], "o", color=angleline.get_color())
    xdot, = coord_ax.plot([z0],[np.mean(slice_x)], "o", color=xline.get_color())
    ydot, = coord_ax.plot([z0],[np.mean(slice_y)], "o", color=yline.get_color())

    def select(event):
        z0_ = event.xdata
        idx = int(z0_) - int((1-np.sign(z0_))/2) + 5
        z0_ = z0s[idx]

        im_ax.cla()
        x_ax.cla()
        y_ax.cla()

        slice_x = x_slices[idx]
        slice_y = y_slices[idx]

        im_ax.hist2d(slice_x, slice_y, cmap="inferno", bins=bins, range=[[-15,15],[-15,15]])
        x_ax.hist(slice_x, bins=int(bins/2), density=True, color="dimgrey", zorder=100);
        y_ax.hist(slice_y, bins=int(bins/2), density=True, orientation=u"horizontal", color="dimgrey", zorder=100);

        principal_ax =  principal_axs[idx]

        x_center = x_centers[idx]
        y_center = y_centers[idx]

        x = np.linspace(np.amin(slice_x), np.amax(slice_x), 1000)
        principal_ax_plot = y_center + principal_ax[0]/principal_ax[1] * (x-x_center)

        im_ax.plot(x, principal_ax_plot, "--", c="royalblue")
        im_ax.plot([x_center], [y_center], "o", c="royalblue", markersize=10)

        y_ax.yaxis.tick_right()
        y_ax.yaxis.set_label_position("right")

        x_ax.grid(zorder=-1)
        y_ax.grid(zorder=-1)

        plt.setp(x_ax.get_xticklabels(), visible=False)
        plt.setp(x_ax.get_yticklabels(), visible=False)
        plt.setp(y_ax.get_xticklabels(), visible=False)
        plt.setp(im_ax.get_yticklabels(), visible=False)

        im_ax.set_xlabel("$x$", fontsize=15)
        y_ax.set_ylabel("$y$", fontsize=15, rotation=0)

        angledot.set_data([z0_],[thetas[idx]])
        xdot.set_data([z0_],[x_center])
        ydot.set_data([z0_],[y_center])

        fig.suptitle("$z_0$ = {}, d$z$ = {}".format(round(z0_,2),dz), fontsize=20,x=.6)

    angle_cursor = Cursor(angle_ax, horizOn=False, vertOn=True, useblit=True,
                    color='blue', linewidth=1)
    coord_cursor = Cursor(coord_ax, horizOn=False, vertOn=True, useblit=True,
                    color='blue', linewidth=1)
    fig.canvas.mpl_connect('button_press_event', select)

    fig.suptitle("$z_0$ = {}, d$z$ = {}".format(round(z0,2),dz), fontsize=20,x=.6)
    
    plt.show()
    
def plot_interactive_rotated():
    z0 = -3.5 # default

    slice_x, slice_y = np.array([list(point[:2]) for point in data if abs(point[2]-z0)<2*dz]).T
    
    cov_mat = np.cov(slice_x,slice_y)
    eig_values, eig_vectors = np.linalg.eig(cov_mat)

    principal_idx = np.argmin(eig_values)
    principal_ax =  eig_vectors[principal_idx]

    theta = -np.arctan(principal_ax[0]/principal_ax[1])
    rot_mat = np.array([[np.cos(theta), -np.sin(theta)], [np.sin(theta), np.cos(theta)]])
    
    x_center = np.mean(slice_x)
    y_center = np.mean(slice_y)

    slice_x, slice_y = np.array([np.matmul(rot_mat, point.T) for point in np.array([slice_x, slice_y]).T]).T
    
    x_center_r = np.mean(slice_x)
    y_center_r = np.mean(slice_y)

    grid = gs.GridSpec(3, 3, width_ratios=[4,8,1], height_ratios=[1,4,4], hspace=0.02, wspace=0.01)

    fig = plt.figure(figsize=(14,10))

    x_ax = plt.subplot(grid[0,1])
    y_ax = plt.subplot(grid[1:,2])
    im_ax = plt.subplot(grid[1:,1], sharex=x_ax, sharey=y_ax)
    angle_ax = plt.subplot(grid[1,0])
    coord_ax = plt.subplot(grid[2,0], sharex=angle_ax)

    im_ax.cla()
    x_ax.cla()
    y_ax.cla()

    im_ax.hist2d(slice_x-x_center_r, slice_y-y_center_r, cmap="inferno", bins=bins, range=[[-15,15],[-15,15]])
    x_ax.hist(slice_x-x_center_r, bins=int(bins/2), density=True, color="dimgrey", zorder=100);
    y_ax.hist(slice_y-y_center_r, bins=int(bins/2), density=True, orientation=u"horizontal", color="dimgrey", zorder=100);

    y_ax.yaxis.tick_right()
    y_ax.yaxis.set_label_position("right")

    x_ax.grid(zorder=-1)
    y_ax.grid(zorder=-1)

    plt.setp(x_ax.get_xticklabels(), visible=False)
    plt.setp(x_ax.get_yticklabels(), visible=False)
    plt.setp(y_ax.get_xticklabels(), visible=False)
    plt.setp(im_ax.get_yticklabels(), visible=False)

    im_ax.set_xlabel("$x$", fontsize=15)
    y_ax.set_ylabel("$y$", fontsize=15, rotation=0)
    
    x = np.linspace(-15,15,100)

    im_ax.plot(x, [0]*len(x), "--", c="royalblue")
    im_ax.plot([0], [0], "o", c="royalblue", markersize=10)

    x_centers = []
    y_centers = []

    x_slices = []
    y_slices = []

    principal_axs = []

    thetas = []

    z0s = np.arange(-4.5,5.5,1)

    for z0_ in z0s:
        s_x, s_y = np.array([list(point[:2]) for point in data if abs(point[2]-z0_)<2*dz]).T
        
        cov_mat = np.cov(s_x,s_y)
        eig_values, eig_vectors = np.linalg.eig(cov_mat)

        principal_idx = np.argmin(eig_values)
        principal_ax_ =  eig_vectors[principal_idx]

        theta = -np.arctan(principal_ax_[0]/principal_ax_[1])

        rot_mat = np.array([[np.cos(theta), -np.sin(theta)], [np.sin(theta), np.cos(theta)]])
        
        x_center_ = np.mean(s_x)
        y_center_ = np.mean(s_y)

        s_x, s_y = np.array([np.matmul(rot_mat, point.T) for point in np.array([s_x, s_y]).T]).T

        x_center_r = np.mean(s_x)
        y_center_r = np.mean(s_y)
        
        x_slices.append(s_x-x_center_r)
        y_slices.append(s_y-y_center_r)

        x_centers.append(x_center_)
        y_centers.append(y_center_)

        principal_axs.append(principal_ax_)

        thetas.append(np.arctan(principal_ax_[0]/principal_ax_[1])*180/np.pi)

    angleline, = angle_ax.plot(z0s, thetas, "--")
    angle_ax.grid()
    angle_ax.set_ylabel("Ángulo [Grados]")

    xline, = coord_ax.plot(z0s, x_centers, "--", label="$x$")
    yline, = coord_ax.plot(z0s, y_centers, "--", label="$y$")
    coord_ax.grid()
    coord_ax.set_xlabel("$z_0$")
    coord_ax.legend()
    coord_ax.set_ylabel("Coord. del centro")

    angledot, = angle_ax.plot([z0],[thetas[int(z0-1) - int((1-np.sign(z0_))/2) + 5]], "o", color=angleline.get_color())
    xdot, = coord_ax.plot([z0],[x_center], "o", color=xline.get_color())
    ydot, = coord_ax.plot([z0],[y_center], "o", color=yline.get_color())

    def select(event):
        z0_ = event.xdata
        idx = int(z0_) - int((1-np.sign(z0_))/2) + 5
        z0_ = z0s[idx]

        im_ax.cla()
        x_ax.cla()
        y_ax.cla()

        slice_x = x_slices[idx]
        slice_y = y_slices[idx]
        
        x_center = x_centers[idx]
        y_center = y_centers[idx]

        im_ax.hist2d(slice_x, slice_y, cmap="inferno", bins=bins, range=[[-15,15],[-15,15]])
        x_ax.hist(slice_x, bins=int(bins/2), density=True, color="dimgrey", zorder=100);
        y_ax.hist(slice_y, bins=int(bins/2), density=True, orientation=u"horizontal", color="dimgrey", zorder=100);
        
        x = np.linspace(-15,15,100)

        im_ax.plot(x, [0]*len(x), "--", c="royalblue")
        im_ax.plot([0], [0], "o", c="royalblue", markersize=10)

        y_ax.yaxis.tick_right()
        y_ax.yaxis.set_label_position("right")

        x_ax.grid(zorder=-1)
        y_ax.grid(zorder=-1)

        plt.setp(x_ax.get_xticklabels(), visible=False)
        plt.setp(x_ax.get_yticklabels(), visible=False)
        plt.setp(y_ax.get_xticklabels(), visible=False)
        plt.setp(im_ax.get_yticklabels(), visible=False)

        im_ax.set_xlabel("$x$", fontsize=15)
        y_ax.set_ylabel("$y$", fontsize=15, rotation=0)

        angledot.set_data([z0_],[thetas[idx]])
        xdot.set_data([z0_],[x_center])
        ydot.set_data([z0_],[y_center])

        fig.suptitle("$z_0$ = {}, d$z$ = {}".format(round(z0_,2),dz), fontsize=20,x=.6)

    angle_cursor = Cursor(angle_ax, horizOn=False, vertOn=True, useblit=True,
                    color='blue', linewidth=1)
    coord_cursor = Cursor(coord_ax, horizOn=False, vertOn=True, useblit=True,
                    color='blue', linewidth=1)
    fig.canvas.mpl_connect('button_press_event', select)

    fig.suptitle("$z_0$ = {}, d$z$ = {}".format(round(z0,2),dz), fontsize=20,x=.6)
    
    plt.show()

if getattr(args, "todos") and not getattr(args, "rotado") and not getattr(args, "corte") and not getattr(args, "interactivo"):
    plot_all()
    
elif getattr(args, "todos") and getattr(args, "rotado") and not getattr(args, "corte") and not getattr(args, "interactivo"):
    plot_rotation(0,10)
    plt.show()

elif getattr(args, "corte") and not getattr(args, "rotado") and not getattr(args, "todos") and not getattr(args, "interactivo"):
    figs = []
    for z0 in getattr(args, "corte"):
        figs.append(plot_slice(z0))
    plt.show()
    
elif getattr(args, "rotado") and not getattr(args, "corte") and not getattr(args, "interactivo") and not getattr(args, "todos"):
    plot_rotation(0, 10)
    plt.show()
    
elif getattr(args, "rotado") and getattr(args, "corte") and not getattr(args, "interactivo") and not getattr(args, "todos"):
    figs = []
    for z0 in getattr(args, "corte"):
        figs.append(plot_rotation(z0, 0.5))
    plt.show()
    
elif getattr(args, "interactivo") and not getattr(args, "rotado") and not getattr(args, "corte") and not getattr(args, "todos"):
    plot_interactive()
    
elif getattr(args, "interactivo") and getattr(args, "rotado") and not getattr(args, "corte") and not getattr(args, "todos"):
    plot_interactive_rotated()
    
else:
    print("Combinacion de opciones invalida. -h para ayuda.")