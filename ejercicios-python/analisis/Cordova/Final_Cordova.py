import argparse
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os
import matplotlib.patches as patches
from scipy.optimize import minimize


def distancias(theta, data, xc, yc):
    # Calcula la suma de las distancias de los puntos hacia una recta que pasa por el centro. Se utilizará para
    # minimizar y hallar el eje principal
    return np.sum(np.abs(np.sin(theta) * (data['x'] - xc) - np.cos(theta) * (data['y'] - yc)))


def centro_y_eje(data):
    xc, yc = np.array([data['x'].sum(), data['y'].sum()]) / len(data.index)
    result = minimize(distancias, 0., args=(data, xc, yc))  # hallo el theta que minimiza la funcion distancias
    thetac = result.x  # con métodos numéricos
    return xc, yc, thetac[0]


def histogramas(datos, ax2d, axx, axy):
    #   dibujo los histogramas en los ejes ax2d axx y axy
    axx.patch.set_facecolor('0.9')
    axy.patch.set_facecolor('0.9')
    axy.spines[:].set_color('0.9')
    axx.spines[:].set_color('0.9')
    axy.yaxis.tick_right()
    axy.tick_params(
        axis='x',
        which='both',
        bottom=False,
        top=False,
        labelbottom=False)
    ax2d.tick_params(
        axis='y',
        which='both',
        left=False,
        right=False,
        labelbottom=False)
    axx.tick_params(
        axis='y',
        which='both',
        left=False,
        right=False,
        labelbottom=False)
    axy.yaxis.set_label_position("right")
    ax2d.set_yticklabels([])
    axx.set_yticklabels([])
    axx.xaxis.tick_top()
    ax2d.set_xlabel('Direccion X')
    axy.set_ylabel('Direccion Y')
    axx.hist(datos['x'], bins=100)
    axx.grid(True, axis='x', color='k')
    axy.hist(datos['y'], orientation='horizontal', bins=100)
    axy.grid(True, axis='y', color='k')
    ax2d.hist2d(datos['x'], datos['y'], bins=100)
    axx.set_xlim([datos['x'].min(), datos['x'].max()])
    ax2d.set_xlim([datos['x'].min(), datos['x'].max()])
    axy.set_ylim([datos['y'].min(), datos['y'].max()])
    ax2d.set_ylim([datos['y'].min(), datos['y'].max()])


def agregar_eje(datos, ax, xc, yc, thetac):
    #   dibujo el eje principal sobre la distribucion 2d
    ax.plot(xc, yc, 'or', markersize=5, alpha=0.5)
    xmin = datos['x'].min()
    xmax = datos['x'].max()
    ax.plot([xmin, xmax], [yc + np.tan(thetac) * (xmin - xc), yc + np.tan(thetac) * (xmax - xc)], '--r')
    leyenda = 'ángulo = {:.2f} \ncentro = {:.2f}, {:.2f}'.format(thetac, xc, yc)
    props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
    ax.text(0.05, 0.95, leyenda, transform=ax.transAxes, fontsize=14,
            verticalalignment='top', bbox=props)


def onpick(event):
    global rotado  # Esta variable indica si el boton "rotar los datos" está activado o no
    global ind  # Esta variable sirve para recordar el último corte graficado, si z0=0 se grafican todos los datos
    if event.artist == boton2:  # si se clickea el boton de rotar se cambia el valor de la variable rotado
        rotado = not rotado
    if event.artist == boton:  # Este boton sirve para graficar todos los datos en lugar de un corte
        ind = 10
        p3.set_data([], [])
        p4.set_data([], [])
        leg.texts[0].set_text('Todos los datos')
    if event.artist == line1 or event.artist == line2 or event.artist == line3:  # selecciona el valor de z0 clickeado
        ind = event.ind  # en las curvas
        z0 = z[ind]
        leg.texts[0].set_text('z0 = {:.1f}'.format(z0[0]))
        p3.set_data(z0, coord_angulos[int(z0 + 4.5), 2])
        p4.set_data([[z0, z0], [coord_angulos[int(z0 + 4.5), 0], coord_angulos[int(z0 + 4.5), 1]]])
    if ind == 10:
        cortec = df.copy()
    else:
        cortec = cortar_datos(df, np.asscalar(z[ind]))
    ax1.cla()
    ax2.cla()
    ax0.cla()
    if rotado:
        histogramas(transform_data(cortec, np.asscalar(coord_angulos[ind, 0]), np.asscalar(coord_angulos[ind, 1]),
                                   np.asscalar(coord_angulos[ind, 2])), ax0, ax1, ax2)
    else:
        histogramas(cortec, ax0, ax1, ax2)
        agregar_eje(cortec, ax0, np.asscalar(coord_angulos[ind, 0]), np.asscalar(coord_angulos[ind, 1]),
                    np.asscalar(coord_angulos[ind, 2]))
    p3.figure.canvas.draw()


def cortar_datos(data, c):  # esta funcion extrae los datos correspondientes al rango de z0 +/- 0.5 indicado
    cortado = data.loc[(data['z'] >= c - 0.5) & (data['z'] <= c + 0.5)]
    cortado.drop(['z'], axis=1)
    return cortado


def transform_data(data, xc, yc, thetac):  # Esta función rota los datos para que el eje principal sea horizontal
    radios = np.sqrt(np.square(data['x'] - xc) + np.square(data['y'] - yc))
    angulos = np.arctan2(data['y'] - yc, data['x'] - xc)
    data.loc[:, 'x'] = np.multiply(radios, np.cos(angulos - thetac))
    data.loc[:, 'y'] = np.multiply(radios, np.sin(angulos - thetac))
    return data


def centros_y_ejes(data):
    # halla los centros y ángulos de todos los intervalos de z0 para realizar el gráfico
    # interactivo
    resultado = np.zeros((11, 3))
    i = 0
    for c in np.arange(-4.5, 5):
        resultado[i, :] = centro_y_eje(cortar_datos(data, c))
        i += 1
    resultado[i, :] = centro_y_eje(data)
    return resultado


def graficar(datos, con_corte=False, c=0., rotated=False):  # Realiza los gráficos no interactivos
    figc = plt.figure(constrained_layout=False, facecolor='0.9')
    gsc = figc.add_gridspec(nrows=4, ncols=4, hspace=0.1, wspace=0.05)
    ax0c = figc.add_subplot(gsc[1:, :-1])
    ax1c = figc.add_subplot(gsc[0, :-1])
    ax2c = figc.add_subplot(gsc[1:, -1])
    histogramas(datos, ax0c, ax1c, ax2c)
    if con_corte:
        if rotated:
            leyenda = 'ángulo = {:.2f} \ncentro = {:.2f}, {:.2f}'.format(theta, x0, y0)
            props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
            ax0c.text(0.05, 0.95, leyenda, transform=ax0c.transAxes, fontsize=14,
                      verticalalignment='top', bbox=props)

        else:
            agregar_eje(datos, ax0c, x0, y0, theta)
        plt.title('Corte z={}'.format(c))
    else:
        plt.title('Todos los datos')
    plt.show()


parser = argparse.ArgumentParser(
    description='Analysis de datos 3D', )

parser.add_argument('-t', '--todos=', type=bool, dest='todos', default=False)
parser.add_argument('-z', '--corte', dest='cortes', help='delimited list input', type=str, default='1.5')
parser.add_argument('-i', '--interactivo', type=bool, dest='interactivo', default=True)
parser.add_argument('-r', '--transform', dest='transform', default=False)

args = parser.parse_args()
todos = args.todos
cortes = []
if args.cortes != '':
    cortes = [float(item) for item in args.cortes.split(',')]
interactivo = bool(args.interactivo)
transform = args.transform

filename = input('Ingrese la dirección del archivo: ')
while not os.path.exists(filename):
    filename = input('No se encontró el archivo, revise la dirección e intente nuevamente: ')
df = pd.read_csv(filename, sep='\s+')
df.columns = ['x', 'y', 'z']

if todos:
    graficar(df)
for zi in cortes:
    corte = cortar_datos(df, zi)
    x0, y0, theta = centro_y_eje(corte)
    if transform:
        corte = transform_data(corte, x0, y0, theta)
    graficar(corte, True, zi, transform)
if interactivo:
    fig = plt.figure(constrained_layout=False, facecolor='0.9')
    gs = fig.add_gridspec(nrows=7, ncols=7, hspace=0.1, wspace=0.05)
    ax0 = fig.add_subplot(gs[1:, 3:-1])
    ax1 = fig.add_subplot(gs[0, 3:-1])
    ax2 = fig.add_subplot(gs[1:, -1])
    ax3 = fig.add_subplot(gs[1:4, 0:3])
    ax4 = fig.add_subplot(gs[4:, 0:3])
    botones = fig.add_subplot(gs[0:1, 0:3])
    botones.axis('off')
    botones.set_xlim([0, 4])
    botones.set_ylim([0, 4])
    ax3.patch.set_facecolor('0.9')
    ax4.patch.set_facecolor('0.9')
    ax3.grid(True)
    ax3.set_ylabel('Angulo')
    ax4.grid(True)
    ax4.set_ylabel('Coord. centro')
    ax4.set_xlabel('z')
    ax3.spines[:].set_color('0.9')
    ax4.spines[:].set_color('0.9')
    ax3.set_xticklabels([])
    z = np.arange(-4.5, 5)
    ind = 10
    coord_angulos = centros_y_ejes(df)
    patch = patches.Rectangle((0., 0.2), 3, 1.5, color='0.4', picker=True, ec='k', linewidth=2)
    patch2 = patches.Rectangle((0., 2.2), 3, 1.5, color='0.4', picker=True, ec='k', linewidth=2)
    boton = botones.add_patch(patch)
    boton2 = botones.add_patch(patch2)
    rx1, ry1 = patch.get_xy()
    cx1 = rx1 + patch.get_width() / 2.0
    cy1 = ry1 + patch.get_height() / 2.0
    botones.annotate("Graficar todos los datos", (cx1, cy1), color='white', weight='bold', fontsize=8, ha='center',
                     va='center')
    rx2, ry2 = patch2.get_xy()
    cx2 = rx2 + patch2.get_width() / 2.0
    cy2 = ry2 + patch2.get_height() / 2.0
    botones.annotate("Rotar la distribución", (cx2, cy2), color='white', weight='bold', fontsize=8, ha='center',
                     va='center')
    line1, = ax3.plot(z, coord_angulos[:-1, 2], '-o', picker=True, pickradius=5)
    line2, = ax4.plot(z, coord_angulos[:-1, 1], '-o', picker=True, pickradius=5)
    line3, = ax4.plot(z, coord_angulos[:-1, 0], '-o', picker=True, pickradius=5)
    p3, = ax3.plot([], [], 'og')
    p4, = ax4.plot([], [], 'og')
    leg = ax3.legend([p3], ['Todos los datos'], loc='best')
    ax4.legend(['x', 'y'])
    histogramas(df, ax0, ax1, ax2)
    agregar_eje(df, ax0, coord_angulos[ind, 0], coord_angulos[ind, 1], coord_angulos[ind, 2])
    rotado = False
    fig.canvas.mpl_connect('pick_event', onpick)
    plt.show()
