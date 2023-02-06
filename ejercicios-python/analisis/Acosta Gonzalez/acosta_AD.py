import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import optimize
from matplotlib.widgets import Cursor
import argparse

plt.style.use('ggplot')


# Funciones Implementadas
def func(x, a, b):
  """
  Para usar con curve_fit
  :param x: valores a ajustar
  :param a: pendiente
  :param b:
  :return: Ecuacion de la recta
  """
  return a * x + b


def scatter_hist(x, y, ax, ax_histx, ax_histy, bw=.25,
                 title='', rlabel=False, rr=False):
  """
  Plot main figure
  Matplotlib Gallery
  :param x: datos eje x
  :param y: datos eje y
  :param ax: axis plot plano x-y
  :param ax_histx: axis plot histograma datos en x
  :param ax_histy: axis plot histograma datos en y
  :param bw: ancho de las columnas de los histogramas
  :param title: titulo de la imagen
  :param rlabel: Mostrar y-label a la derecha
  :param rr: Diferenciar entre el modo interactivo
  :return: plot figure
  """

  ax_histx.tick_params(axis="x", labelbottom=False)
  ax_histy.tick_params(axis="y", labelleft=False)
  ax_histy.yaxis.tick_right()

  # Calcular el numero de bins para el ancho deseado
  x_lim = int(np.max(np.abs(x))) + 1
  y_lim = int(np.max(np.abs(y))) + 1
  xymax = max(np.max(np.abs(x)), np.max(np.abs(y)))
  lim = (int(xymax / bw) + 1) * bw
  bins = np.arange(-lim, lim + bw, bw)

  # Plot main Figure
  ax.hist2d(x, y, bins=bins, range=(
      [-x_lim, x_lim], [-y_lim, y_lim]), cmap=plt.get_cmap('terrain'))

  if rlabel:
    ax.yaxis.tick_right()

    yticks = ax.get_yticks()
    if rr:  # Figura de rotacion
      ax_histy.set_ylabel('Dirección Y', fontsize=20, labelpad=-135)
      for tick in ax.get_yaxis().get_major_ticks():
        tick.set_pad(95)
    else:  # Modo Interactivo
      ax_histy.set_ylabel('Dirección Y', fontsize=20, labelpad=-110)
      for tick in ax.get_yaxis().get_major_ticks():
        tick.set_pad(65)

    ax_histy.axis('On')
    ax_histx.axis('Off')
    ax_histy.set_xticks([])
  else:
    ax.set_ylabel('Dirección Y', fontsize=20)
    ax_histx.axis('Off')
    ax_histy.axis('Off')

  ax.set_xlabel('Dirección X', fontsize=20)

  ax_histx.hist(x, bins=bins)  # Histograma para datos de x
  # Histograma para datos de y
  ax_histy.hist(y, bins=bins, orientation='horizontal')
  ax_histx.set_title(title, fontsize=20)


def get_corte(z_cut, data_x, data_y):
  """
  Devuelve el corte de los datos según el valor de z
  :param z_cut: valor del corte para los datos en el eje z
  :param data_x: datos en el eje x
  :param data_y: datos en el eje y
  :return: alpha: parametros de la recta, idx: posicion de los valores del corte
           p_val: array valores entre minimo y maximo de datos del corte en eje x
           result_pol: recta que describe los datos del corte en el plano x-y
           mean_x, mean_y: Valores medios de los datos del corte en x e y.
  """

  lim_inf = z_cut - 0.5
  lim_sup = z_cut + 0.5
  idx = (lim_inf < df.Z) & (lim_sup > df.Z)
  alpha = optimize.curve_fit(func, data_x[idx], data_y[idx],
                             bounds=(data_x[idx].min(), data_x[idx].max()))[0]
  # p_val = np.linspace(data_x[idx].min(), data_x[idx].max(), data_x[idx].shape[0])
  p_val = np.linspace(data_x.min(), data_x.max(), data_x.shape[0])
  result_pol = alpha[0] * p_val + alpha[1]
  mean_x, mean_y = data_x[idx].mean(), data_y[idx].mean()

  return alpha, idx, p_val, result_pol, mean_x, mean_y


def get_rot(alpha, idx, data_x, data_y):
  """
  Rotar y trasladar los datos del plano x-y
  :param alpha: valores de la recta
  :param idx: posicion de los valores del corte
  :param data_x: datos en el eje x
  :param data_y: datos en el eje y
  :param flog_rot: Bandera para una rotacion de angulo 0
  :return: val_X, val_Y: Valores de los datos x e y rotados, alpha_r: parametros de la recta de los datos rotados,
           p_p_valores_r: array valores entre minimo y maximo de datos del corte en eje x rotados,
           result_pol_r: recta que describe los datos rotados del corte en el plano x-y
           mean_x_r, mean_y_r: Valores medios de los datos rotados del corte en x e y
  """

  if alpha[0] < 0:
    theta = np.deg2rad(360 + np.rad2deg(np.arctan(alpha[0])))
  elif alpha[0] > 0:
    theta = np.arctan(alpha[0])

  mean_x = np.mean(data_x[idx])
  mean_y = np.mean(data_y[idx])
  r = np.array([np.cos(theta), np.sin(theta), -
                np.sin(theta), np.cos(theta)]).reshape(2, 2)
  temp_data = np.vstack((data_x[idx], data_y[idx]))
  temp = r.dot(temp_data)
  val_X = temp[0, :] - mean_x  # Estos valores son los ajustados
  val_Y = temp[1, :] - mean_y
  alpha_r = optimize.curve_fit(
      func, val_X, val_Y, bounds=(
          min(val_X), max(val_X)))[0]
  # p_valores_r = np.linspace(min(val_X), max(val_X), val_X.shape[0])
  p_valores_r = np.linspace(min(data_x), max(data_x), data_x.shape[0])
  result_pol_r = alpha_r[0] * p_valores_r + alpha_r[1]
  mean_x_r, mean_y_r = np.mean(val_X), np.mean(val_Y)

  return val_X, val_Y, alpha_r, p_valores_r, result_pol_r, mean_x_r, mean_y_r


def click_action(event):
  """
  Funcion para interactividad con los graficos
  :param event: Evento detectado
  :return:
  """

  z_click = event.xdata  # Valor del eje X seleccionado con el click
  # Aproximar al valor mas cercano
  z_index = np.argmin(np.abs(z_values - z_click))
  print(f'{z_index = }')
  # Centro - z
  axc.cla()
  l1, = axc.plot(z_values, centros[:, 1], marker='.', label=r'$y_0$', zorder=1)
  l2, = axc.plot(z_values, centros[:, 0], marker='.', label=r'$x_0$', zorder=2)
  l3 = axc.set_xlabel(r'$z_0$')
  l4 = axc.scatter(z_values[z_index], centros[z_index, 1],
                   color='green', marker='o', zorder=6)
  l5 = axc.scatter(z_values[z_index], centros[z_index, 0],
                   color='green', marker='o', zorder=7)
  axc.set_ylim(-2, 2)
  axc.set_xlim(-5.0, 5.0)
  axc.set_ylabel('coord. centro')
  axc.grid(linestyle='--')
  axc.legend()

  # Grados - z
  axg.cla()
  axg.plot(z_values, val_alpha_deg, marker='.', zorder=2)
  axg.set_ylabel(r'$\Theta$ (grados)')
  axg.tick_params(axis="x", labelbottom=False)
  axg.grid(linestyle='--')
  axg.scatter(z_values[z_index], val_alpha_deg[z_index], color='green', marker='o',
              label=r'$z_0 = {:.1f}$'.format(z_values[z_index]), zorder=4)
  axg.legend()
  ax.cla()
  ax_histx.cla()
  ax_histy.cla()
  # Resto de figuras
  scatter_hist(df.X[all_index_c[z_index]], df.Y[all_index_c[z_index]],
               ax, ax_histx, ax_histy, .25, f'', rlabel=True)
  ax.plot(all_pValores_c[z_index], all_rPol_c[z_index], 'r--', lw=2)
  ax.scatter(
      all_meanX_c[z_index],
      all_meanY_c[z_index],
      marker='o',
      c='r',
      s=100)


if __name__ == '__main__':

  parser = argparse.ArgumentParser(description='"Analisis de Datos"')
  parser.add_argument(
      '-fn',
      '--filename',
      default='medicion3D.dat.gz',
      type=str,
      dest='filename')
  parser.add_argument('-t', '--todos', default=1, type=int, dest='todos')
  parser.add_argument('-z', '--corte', action='store',
                      default="-4.5 -4.0 -3.5 -3.0 -2.5 -2.0 -1.5 -1.0 -.5 0 .5 1.0 1.5 2.0 2.5 3.0 3.5 4.0 4.5",
                      type=str, dest='corte')
  parser.add_argument(
      '-i',
      '--interactivo',
      default=1,
      type=int,
      dest='interactivo')
  parser.add_argument(
      '-r',
      '--transform',
      default=1,
      type=int,
      dest='transform')
  args = parser.parse_args()

  # Cargar Datos
  data = np.recfromtxt(args.filename)
  df = pd.DataFrame(data, columns=['X', 'Y', 'Z'])

  # Todos los valores de corte
  z_all_values = '-4.5,-4.0,-3.5,-3.0,-2.5,-2.0,-1.5,-1.0,-.5,0,.5,1.0, \
                        1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5'

  flag_corte = args.corte == ''
  if not flag_corte:
    # Obtener todos los valores de cortes
    z_val_select = [float(val) for val in args.corte.split(' ')]

  z_values = [float(val) for val in z_all_values.split(',')]
  all_val = np.array([get_corte(val, df.X, df.Y)
                     for val in z_values])  # Obtener todos los cortes
  centros = all_val[:, 4:6].copy()
  val_alpha = all_val[:, 0].copy()
  val_alphaAll = val_alpha.copy()
  val_alpha = np.asarray([val[0] for val in val_alpha])
  val_alpha_deg = (np.rad2deg(np.arctan(val_alpha)))
  all_index_c = all_val[:, 1]
  all_pValores_c = all_val[:, 2]
  all_rPol_c = all_val[:, 3]
  all_meanX_c = all_val[:, 4]
  all_meanY_c = all_val[:, 5]

  if args.todos:  # Todos los datos sin cortes
    fig1 = plt.figure(figsize=(8, 6))
    gs = fig1.add_gridspec(2, 2, width_ratios=(7, 2), height_ratios=(2, 7),
                           left=0.1, right=0.9, bottom=0.1, top=0.9,
                           wspace=0.05, hspace=0.05)
    ax = fig1.add_subplot(gs[1, 0])
    ax_histx = fig1.add_subplot(gs[0, 0], sharex=ax)
    ax_histy = fig1.add_subplot(gs[1, 1], sharey=ax)
    scatter_hist(df.X, df.Y, ax, ax_histx, ax_histy, .25,
                 'Todos los datos en plano X-Y')

  if not flag_corte and not args.transform:  # Solos los Cortes
    for _, z in enumerate(z_val_select):
      index = z_values.index(z)
      print(index)
      fig2 = plt.figure(figsize=(8, 8))
      gs = fig2.add_gridspec(2, 2, width_ratios=(7, 2), height_ratios=(2, 7),
                             left=0.1, right=0.9, bottom=0.1, top=0.9,
                             wspace=0.05, hspace=0.05)

      ax = fig2.add_subplot(gs[1, 0])
      ax_histx = fig2.add_subplot(gs[0, 0], sharex=ax)
      ax_histy = fig2.add_subplot(gs[1, 1], sharey=ax)

      scatter_hist(df.X[all_index_c[index]], df.Y[all_index_c[index]],
                   ax, ax_histx, ax_histy, .25, f'$z_0$={z}')
      ax.plot(all_pValores_c[index], all_rPol_c[index], 'r--', lw=2)
      ax.scatter(
          all_meanX_c[index],
          all_meanY_c[index],
          marker='o',
          c='r',
          s=100)

  if not flag_corte and args.transform:  # Cortes y rotaciones
    for _, z in enumerate(z_val_select):
      index = z_values.index(z)
      datos_X, datos_Y = df.X.copy(), df.Y.copy()  # Copia de los Datos Originales

      val_X, val_Y, alpha_r, p_valores_r, result_pol_r, mean_x_r, mean_y_r = get_rot(val_alphaAll[index],
                                                                                     all_index_c[index], datos_X,
                                                                                     datos_Y)
      # Add nuevos datos rotados
      datos_X[all_index_c[index]] = val_X
      datos_Y[all_index_c[index]] = val_Y

      for _ in range(100):  # Loop para disminuir el angulo de rotacion
        if alpha_r[0] < 0:
          val_X, val_Y, alpha_r, p_valores_r, result_pol_r, mean_x_r, mean_y_r = get_rot(alpha_r,
                                                                                         all_index_c[index], datos_X,
                                                                                         datos_Y)
          datos_X[all_index_c[index]] = val_X
          datos_Y[all_index_c[index]] = val_Y

        elif alpha_r[0] >= 0:
          val_X, val_Y, alpha_r, p_valores_r, result_pol_r, mean_x_r, mean_y_r = get_rot(alpha_r,
                                                                                         all_index_c[index], datos_X,
                                                                                         datos_Y)
          datos_X[all_index_c[index]] = val_X
          datos_Y[all_index_c[index]] = val_Y

      # Plot Figure
      fig3 = plt.figure(figsize=(16, 8))
      gs = fig3.add_gridspec(2, 4, width_ratios=(7, 2, 7, 2), height_ratios=(2, 7),
                             left=0.1, right=0.9, bottom=0.1, top=0.9,
                             wspace=0.02, hspace=0.04)

      ax = fig3.add_subplot(gs[1, 0])
      ax_r = fig3.add_subplot(gs[1, 2])
      ax_histx = fig3.add_subplot(gs[0, 0], sharex=ax)
      ax_histy = fig3.add_subplot(gs[1, 1], sharey=ax)
      ax_histx_r = fig3.add_subplot(gs[0, 2], sharex=ax_r)
      ax_histy_r = fig3.add_subplot(gs[1, 3], sharey=ax_r)
      # Rotando
      scatter_hist(val_X, val_Y, ax_r, ax_histx_r, ax_histy_r, .25,
                   f'$Angle$={np.abs((np.rad2deg(np.arctan(alpha_r[0])))):.2f}º\nRotado', rlabel=True, rr=True)
      ax_r.plot(p_valores_r, result_pol_r, 'r--', lw=2)
      ax_r.scatter(mean_x_r, mean_y_r, marker='o', c='r', s=100)
      # Sin Rotar
      scatter_hist(df.X[all_index_c[index]], df.Y[all_index_c[index]], ax, ax_histx, ax_histy,
                   .25, f'$z_0$={z}\nSin Rotar')
      ax.plot(all_pValores_c[index], all_rPol_c[index], 'r--', lw=2)
      ax.scatter(
          all_meanX_c[index],
          all_meanY_c[index],
          marker='o',
          c='r',
          s=100)

  if args.interactivo:  # Interactivo
    fig4 = plt.figure(figsize=(16, 8))
    gs = fig4.add_gridspec(3, 3, width_ratios=(6, 6, 1), height_ratios=(2, 3.5, 3.5),
                           left=0.1, right=0.9, bottom=0.1, top=0.9,
                           wspace=0.005, hspace=0.07)
    axc = fig4.add_subplot(gs[2, 0])  # Centro - z
    axg = fig4.add_subplot(gs[1, 0], sharex=axc)  # Grados - z
    ax = fig4.add_subplot(gs[1:3, 1])
    ax_histx = fig4.add_subplot(gs[0, 1], sharex=ax)
    ax_histy = fig4.add_subplot(gs[1:3, 2], sharey=ax)

    # Centro - z
    l1, = axc.plot(z_values, centros[:, 1],
                   marker='.', label=r'$y_0$', zorder=1)
    l2, = axc.plot(z_values, centros[:, 0],
                   marker='.', label=r'$x_0$', zorder=2)
    l3 = axc.set_xlabel(r'$z_0$')
    l4 = axc.scatter(z_values[-1], centros[-1, 1],
                     color='green', marker='o', zorder=6)
    l5 = axc.scatter(z_values[-1], centros[-1, 0],
                     color='green', marker='o', zorder=7)
    axc.set_ylim(-2, 2)
    axc.set_xlim(-5.0, 5.0)
    axc.set_ylabel('coord. centro')
    axc.grid(linestyle='--')
    axc.legend()

    # Grados - z
    axg.plot(z_values, val_alpha_deg, marker='.', zorder=2)
    axg.set_ylabel(r'$\Theta$ (grados)')
    axg.tick_params(axis="x", labelbottom=False)
    axg.grid(linestyle='--')
    axg.scatter(z_values[-1], val_alpha_deg[-1], color='green', marker='o',
                label=r'$z_0 = {:.1f}$'.format(z_values[-1]), zorder=4)
    axg.legend()

    # Resto de figuras
    scatter_hist(df.X[all_index_c[-1]], df.Y[all_index_c[-1]],
                 ax, ax_histx, ax_histy, .25, f'', rlabel=True)
    ax.plot(all_pValores_c[-1], all_rPol_c[-1], 'r--', lw=2)
    ax.scatter(all_meanX_c[-1], all_meanY_c[-1], marker='o', c='r', s=100)

    # Click Button
    click_A = Cursor(
        axg,
        vertOn=True,
        useblit=True,
        color='black',
        linewidth=2)
    click_B = Cursor(
        axc,
        vertOn=True,
        useblit=True,
        color='black',
        linewidth=2)
    fig4.canvas.mpl_connect('button_press_event', click_action)

  plt.show()
