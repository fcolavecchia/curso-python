import argparse
import sys  # esto no se si es necesario
import math as m
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as anim
import matplotlib.gridspec as gridspec
import gzip


def spines_off(ax):
  '''Configura en invisible los bordes
  de un objeto de la clase Axes'''
  ax.spines['left'].set_visible(False)
  ax.spines['right'].set_visible(False)
  ax.spines['top'].set_visible(False)
  ax.spines['bottom'].set_visible(False)


def dist(x0, arr):
  '''Toma un número x0 y un array y devuelve
  otro array con las distancias de cada componente
  del array original a x0'''
  return abs(arr - x0)


def centro(x):
  '''Devuelve el valor promedio de x redondeado
  a dos decimales'''
  x0 = round(x.mean(), 2)
  return x0


def trasl(x, x0):
  '''Devuelve un array x trasladado en un escalar x0'''
  x = x - x0
  return x


def rot(x, y, theta):
  '''A cada vector formado con las componentes
  x_i, y_i de los arrays x e y, lo rota en un
  ángulo theta. Devuelve dos arrays con las
  componentes de los vectores rotados'''
  xx = x.copy()
  yy = y.copy()

  vecs = zip(xx, yy)
  vecs2 = list(vecs)
  v = np.array(vecs2)

  Mrot = np.array([[np.cos(theta), np.sin(theta)],
                  [-np.sin(theta), np.cos(theta)]])
  vrot = v.dot(Mrot.T)
  result = zip(*vrot)
  result = list(result)

  xres = np.array(result[0])
  yres = np.array(result[1])

  return xres, yres


def transformar(x, y):
  '''Toma dos arrays x e y y los devuelve centrados
  en el origen y rotados tal que su eje principal
  quede horizontal'''
  xt = x.copy()
  yt = y.copy()

  xt = trasl(xt, centro(xt))
  yt = trasl(yt, centro(yt))

  p = np.polyfit(xt, yt, 1)
  ajust = p[0] * xt + p[1]
  theta = m.atan2(p[0], 1)

  xtr, ytr = rot(xt, yt, theta)
  while (theta > 0.1):
    p = np.polyfit(xtr, ytr, 1)
    ajust = p[0] * xtr + p[1]
    theta = m.atan2(p[0], 1)
    xtr, ytr = rot(xtr, ytr, theta)

  return xtr, ytr


def cortez(x, y, z, zc, delta=0.5):
  '''Toma los arrays x, y, y z y devuelve
  dos arrays con los elementos de x e y que
  tienen un z en el intervalo zc +- delta'''
  zcinf = zc - delta
  zcsup = zc + delta

  z2 = (zcinf <= z)
  z = z[z2]
  x = x[z2]
  y = y[z2]

  z3 = (z <= zcsup)
  z = z[z3]
  x = x[z3]
  y = y[z3]

  return x, y


def angulo(x, y, z, zc):
  '''Calcula y devuelve el ángulo correspondiente a
  la recta principal de las distribuciones x,y que
  tengan un z=zc'''
  xc, yc = cortez(x, y, z, zc)
  p = np.polyfit(xc, yc, 1)
  ajust = p[0] * xc + p[1]

  return m.atan2(p[0], 1)


def ccentro(x, y, z, zc):
  '''Calcula y devuelve los valores promedios de los
  arrays x e y que tienen un z=zc'''
  xc, yc = cortez(x, y, z, zc)
  x0 = centro(xc)
  y0 = centro(yc)

  return x0, y0


def coord_click(x0, x, y1, y2, y3):
  '''Toma la data que sale de hacer click (x0 es el z clickeado),
  busca y devuelve los valores más cercanos a los puntos de las
  gráficas de ángulos vs z y x e y vs z. El z es el mismo para las
  tres funciones, yp1 el ángulo, yp2 e yp3 es el x y el y correspondientes
  al z clickeado.'''
  idx0 = np.argmin(dist(x0, x))
  xp = x[idx0]
  yp1 = y1[idx0]
  yp2 = y2[idx0]
  yp3 = y3[idx0]
  return xp, yp1, yp2, yp3


def histo2d_1dxey(x, y):
  '''Configura y define lo necesario para graficar
  los histogramas en x e y y el histograma 2d.
  Toma dos arrays y devuelve: H: histograma bidimensional
  para ser usado luego en 'imshow()'; x1, h1, x2,
  b2: arrays y alturas para crear los gráficos de barras;
  y edg0 y egd1 para definir los bordes del gráfico 2d de
  manera que sea cuadrado.'''
  H, xedges, yedges = np.histogram2d(x, y, bins=100)
  H = H.T
  xcenters = (xedges[1:] + xedges[:-1]) / 2
  ycenters = (yedges[1:] + yedges[:-1]) / 2

  h1, b1 = np.histogram(x, bins=50, density=True)
  x1 = (b1[1:] + b1[:-1]) / 2
  h2, b2 = np.histogram(y, bins=50, density=True)
  x2 = (b2[1:] + b2[:-1]) / 2

  edg0 = max(xedges[0], yedges[0], key=abs)
  edg1 = max(xedges[-1], yedges[-1], key=abs)

  return H, x1, h1, x2, h2, edg0, edg1


def ghisto(fig, ax1, x1, h1, ax2, H, edg0, edg1, ax3, x2, h2,
           title='Todos los datos en el plano x-y'):
  '''Configura el aspecto de la figura, agrega los histogramas
  en x e y y el histograma 2d. Devuelve los 'Contenedores de Barras'
  para los histogramas en 1d y la imagen para el histograma 2d de
  manera de poder manipularlos.'''
  fig.suptitle(title)

  xh1d = ax1.bar(x1, h1, align='center', width=1, zorder=2)
  ax1.set_facecolor(color='#cdc9c9')
  ax1.xaxis.tick_top()
  ax1.xaxis.grid(True)
  ax1.grid(axis='x')
  ax1.set_yticks([])
  spines_off(ax1)
  ax1.grid(axis='x')

  ih2d = ax2.imshow(H, origin='lower', cmap='plasma', aspect='auto',
                    extent=[edg0, edg1, edg0, edg1])
  ax2.set_facecolor(color='#cdc9c9')
  ax2.set_xlabel('Dirección x')
  ax2.axes.yaxis.set_visible(False)
  spines_off(ax2)

  yh1d = ax3.barh(x2, h2, align='center', zorder=2)
  ax3.yaxis.tick_right()
  ax3.yaxis.set_label_position("right")
  ax3.set_ylabel('Dirección y')
  ax3.set_xticks([])
  ax3.yaxis.grid(True)
  ax3.set_facecolor(color='#cdc9c9')
  ax3.grid(axis='y')
  spines_off(ax3)
  ax3.grid(axis='y')

  return ih2d, xh1d, yh1d


def h2d(x, y, ajuste=False, title='Todos los datos en el plano x-y'):
  '''Genera la figura, define la grid con los histogramas correspondientes y
  si la variable ajuste es True entonces muestra el centro de la distribución
  2d y la recta principal'''

  H, x1, h1, x2, h2, edg0, edg1 = histo2d_1dxey(x, y)

  fig = plt.figure()
  fig.set_facecolor(color='#cdc9c9')
  gs = fig.add_gridspec(2, 2, wspace=-0.01, hspace=0.01,
                        width_ratios=[0.85, 0.15], height_ratios=[0.15, 0.85])

  # ax1 histo x, ax2 histo y ax3 histo 2d
  ax3 = fig.add_subplot(gs[1, 0])
  ax1 = fig.add_subplot(gs[0, 0], sharex=ax3)
  ax2 = fig.add_subplot(gs[1, 1], sharey=ax3)

  ghisto(fig, ax1, x1, h1, ax3, H, edg0, edg1, ax2, x2, h2, title=title)

  if ajuste:
    x0 = centro(x)
    y0 = centro(y)
    p = np.polyfit(x, y, 1)
    ajust = p[0] * x + p[1]
    ax3.plot(
        x0,
        y0,
        'ok',
        color='white',
        label=f'x0={x0}, y0={y0}, Ángulo={round(m.atan2(p[0],1),3)}')
    ax3.plot(x, ajust, '--', color='white')
    ax3.legend()

  plt.draw()


def graf2(x, y, z, zgr, angle, xcent, ycent, ajuste=False):
  '''Genera la figura, define la grid con los histogramas correspondientes y
  si la variable ajuste es True entonces muestra el centro de la distribución
  2d y la recta principal. Agrega además los subplots que muestran el ángulo
  y x e y en función de z. Define la función onclick que permite mostrar los
  datos x e y para una elección de z0 haciendo click sobre las últimas dos
  gráficas agregadas (ángulo y x e y en función de z)'''

  H, x1, h1, x2, h2, edg0, edg1 = histo2d_1dxey(x, y)

  fig = plt.figure()
  fig.set_facecolor(color='#cdc9c9')
  gs = fig.add_gridspec(3, 3, wspace=0.05, hspace=0.02,
                        width_ratios=[0.35, 0.5, 0.15], height_ratios=[0.2, 0.4, 0.4])

  # ax1 histo x, ax2 2dhisto, ax3 histo y
  ax2 = fig.add_subplot(gs[1:, 1], zorder=1)
  ax1 = fig.add_subplot(gs[0, 1], sharex=ax2)
  ax3 = fig.add_subplot(gs[1:, 2], sharey=ax2)

  ih2d, xh1d, yh1d = ghisto(fig, ax1, x1, h1, ax2, H, edg0, edg1, ax3, x2, h2)

  # angulo vs z
  ax4 = fig.add_subplot(gs[1, 0])
  ax4.set_facecolor(color='#cdc9c9')
  spines_off(ax4)
  ax4.set_xticks([])
  ax4.grid(axis='y')
  anglegrad = angle * 180 / m.pi
  lines4 = ax4.plot(zgr, anglegrad, 'o-', color='#00B2EE')
  ax4.set_ylabel('Ángulo (grados)')

  # x0, y0 vs z
  ax5 = fig.add_subplot(gs[2, 0])
  ax5.set_facecolor(color='#cdc9c9')
  spines_off(ax5)
  ax5.plot(zgr, xcent, 'o-', label='x')
  ax5.plot(zgr, ycent, 'o-', label='y')
  ax5.set_xlabel('z$_0$')
  ax5.set_ylabel('coord. centro')
  ax5.legend()
  ax5.grid()

  if ajuste:
    x0 = centro(x)
    y0 = centro(y)
    p = np.polyfit(x, y, 1)
    ajust = p[0] * x + p[1]
    ax2.plot(x0, y0, 'ok', color='white', label=f'x0={x0}, y0={y0}')
    ax2.plot(x, ajust, '--', color='white')
    ax2.legend()

  def onclick(event):
    '''Si el click está hecho sobre los datos de las gráficas que
    corresponden a ángulos vs z, o x e y vs z, entonces marca el
    punto correspondiente en ambas gráficas y muestra los
    correspondientes histogramas para el valor de z seleccionado'''
    if (len(ax4.lines) > 1):
      ax4.lines.remove(ax4.lines[-1])
      ax5.lines.remove(ax5.lines[-1])
      ax5.lines.remove(ax5.lines[-1])
      ax4.legend('').remove()
      plt.draw()
    global ix, iy
    ix = round(event.xdata, 4)
    ax_list = fig.axes
    for i, ax in enumerate(ax_list):
      if ax == event.inaxes and (i == 3 or i == 4):
        xp, yp1, yp2x, yp2y = coord_click(ix, zgr, anglegrad, xcent, ycent)
        ax4.plot(xp, yp1, 'ok', label=f'z$_0$={xp}')

        ax5.plot(xp, yp2x, 'ok')
        ax5.plot(xp, yp2y, 'ok')
        ax4.legend(loc='upper left')

        z0 = xp
        xx = x.copy()
        yy = y.copy()
        zz = z.copy()

        xc, yc = cortez(xx, yy, zz, z0)

        ax2.clear()
        ax1.clear()
        ax3.clear()

        H, x1, h1, x2, h2, edg0, edg1 = histo2d_1dxey(xc, yc)
        # creo que no es necesario que reasigne xh1d e yhd1
        # xh1d, yh1d = ghisto(fig, ax1, x1, h1, ax2, H, edg0, edg1, ax3, x2, h2, title=f'z$_0$={z0}')[1:]
        ghisto( fig, ax1, x1, h1, ax2, H,
            edg0, edg1, ax3, x2, h2, title=f'z$_0$={z0}')
        x0 = centro(xc)
        y0 = centro(yc)
        p = np.polyfit(xc, yc, 1)
        ajust = p[0] * xc + p[1]
        ax2.plot(x0, y0, 'ok', color='white')
        ax2.plot(xc, ajust, '--', color='white')

        plt.draw()

  cid = fig.canvas.mpl_connect('button_press_event', onclick)


if __name__ == '__main__':
  print('Nair Aucar')
  parser = argparse.ArgumentParser(
      description='Examen final: análisis de datos')

  parser.add_argument('-f', '--file', help='Archivo de entrada', type=str,
                      required=True)
  parser.add_argument('-t', '--todos', action='store_true',
                      help='Grafica cantidad de puntos en x-y ', default=False)
  parser.add_argument('-z', '--corte', type=float, nargs='*',
                      help='Grafica corte en z')
  parser.add_argument(
      '-i',
      '--interactivo',
      action='store_true',
      default=False)
  parser.add_argument('-r', '--transform', action='store_true', default=False)

  args = parser.parse_args()


# Item 1: lectura de datos desde archivo comprimido original
  # fizp = gzip.open(args.file, 'rt')
  # datos = fizp.read()
  # datos = datos.split()
  # dx = datos[0::3]
  # dy = datos[1::3]
  # dz = datos[2::3]

  # xarr = np.array(dx)
  # yarr = np.array(dy)
  # zarr = np.array(dz)

  # x = xarr.astype(float)
  # y = yarr.astype(float)
  # z = zarr.astype(float)

  x, y, z = np.loadtxt(args.file, unpack=True)
# Item 2: grafica todos los datos independientemente de z
  if args.todos:
    h2d(x, y, True)

# Item 4:
  if args.transform:
    if args.corte:
      print('Chequear bien esto')
      zcorte = np.array(args.corte)
      for i in range(len(zcorte)):
        zz = z.copy()
        xx = x.copy()
        yy = y.copy()

        xc, yc = cortez(xx, yy, zz, zcorte[i])
        xtr, ytr = transformar(xc, yc)
        h2d(xtr, ytr, True, f'z$_0$={zcorte[i]}')
      args.corte = False

    else:
      xtr, ytr = transformar(x, y)
      h2d(xtr, ytr, True)

# Item 3: grafica solamente los datos con valores de z en el intervalo z0+-delta z0
# graficando un punto para el centro y el eje principal
  if args.corte:
    zcorte = np.array(args.corte)

    for i in range(len(zcorte)):
      zz = z.copy()
      xx = x.copy()
      yy = y.copy()
      xc, yc = cortez(xx, yy, zz, zcorte[i])
      h2d(xc, yc, True, f'z$_0$={zcorte[i]}')

# Item 5 y 6
  if args.interactivo:
    paso = 0.5
    zgr = np.arange(min(z), max(z) + paso, paso)
    ang = np.empty(len(zgr))
    xcent = np.empty(len(zgr))
    ycent = np.empty(len(zgr))
    for i in range(len(zgr)):
      ang[i] = angulo(x, y, z, zgr[i])
      xcent[i], ycent[i] = ccentro(x, y, z, zgr[i])

    graf2(x, y, z, zgr, ang, xcent, ycent)

  plt.show()
