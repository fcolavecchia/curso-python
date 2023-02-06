# -*- coding: utf-8 -*-

print('Franco Caviglia')
print('Trabajo Final')

#################
### Preámbulo ###
#################

import argparse
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import scipy.io.wavfile as wavfile
#import sounddevice as sd
#from matplotlib.widgets import Cursor
from scipy import interpolate  
from os import path

############################
### Comandos por consola ###
############################

parser = argparse.ArgumentParser(description = 'Simula la corrección a una señal de sonido debida al efecto doppler.',
                                 add_help=False)

parser.add_argument('--archivo',     '-a', action="store", dest="f_read",  default="entrada.wav", type=str,
                    help='Nombre del archivo con el audio inicial.')
parser.add_argument('--salida',      '-s', action="store", dest="f_write", default="salida.wav",  type=str,
                    help='Nombre del archivo donde guardar el audio corregido.')
parser.add_argument('--radio',       '-r', action="store", dest="r",       default=200,           type=float,
                    help='Radio del círculo que recorrre el emisor en metros.')
parser.add_argument('--velocidad',   '-v', action="store", dest="v",       default=100,           type=float,
                    help='Velocidad del emisor en metros sobre segundos.')
parser.add_argument('--angulo',      '-t', action="store", dest="theta",   default=0,             type=float,
                    help='Posición inicial del emisor (ángulo en radianes).')
parser.add_argument('--v_sonido',    '-c', action="store", dest="c",       default=343,           type=float,
                    help='Velocidad del sonido en el medio en metros sobre segundos.')
parser.add_argument('--posicion_x',  '-x', action="store", dest="x",       default=0,             type=float,
                    help='Posición inicial del receptor en x respecto del centro del círculo en metros.')
parser.add_argument('--posicion_y',  '-y', action="store", dest="y",       default=100,           type=float,
                    help='Posición inicial del receptor en y respecto del centro del círculo en metros.')
parser.add_argument('--dos-canal',   '-d', action="store", dest="canal",   default=False,         type=bool,
                    help='Indica si desea guardar la salida en dos canales.')
parser.add_argument('--pasos',       '-N', action="store", dest="N",       default=1000,          type=int,
                    help='Cantitdad de frames que se saltea al graficar.')
parser.add_argument('--interactivo', '-i', action="store_true", dest="modo",
                    help='Indica si desea utilizar el gráfico interactivo.')
parser.add_argument('--help',        '-h', action='help', default=argparse.SUPPRESS,
                    help='Muestra este mensaje de ayuda y sale del programa.')

args = parser.parse_args()

### Verifica los nombres de los archivos ###
if args.f_read[-4:]  != ".wav":
    args.f_read  += ".wav"
    
if args.f_write[-4:] != ".wav":
    args.f_write += ".wav"

############################
### Funciones auxiliares ###
############################

def doppler(ts, fs, v, R, theta, pos, c):
    """
    Recibe los datos físicos del problema y retorna una lista con la los tiempos de llegada de la 
    señal de sonido al receptor.
    
    Parámetros
    ----------
    ts : list
        Valores de tiempo. Necesita solo su longitud.
    fs : float
        Frecuencia de sampleo del sonido emitido. Se asume en hertz (inversa de segundo).
    v : float
        Velocidad del emisor en su recorrido por la circunferencia. Se asume en metros por segundo.
    R : float
        Radio de la circunferencia en la que se mueve el emisor. Se asume en metros.
    theta : float
        Posición angular inicial del emisor, medida desde el semieje +x y en radianes.
    pos : list
        Posición del receptor relativa al centro de la circunferencia. Se asume en metros.
    c : float
        Velocidad del sonido en el medio. Por defecto vale . Se asume en metros por segundo.

    Retorna
    -------
    ts_doppler : list
        Tiempos en los que la señal llega al receptor.
    ds : list
        Distancias a cada tiempo entre el receptor y emisor.
    rs : list
        Posición a cada tiempo del emisor.

    """
    
    dtheta = v/(fs*R) # Intervalos de theta 
    rs = R*np.array([[np.cos(theta+n*dtheta), np.sin(theta+n*dtheta)] for n in range(len(ts))])
    ds = np.linalg.norm(rs-np.array(pos), axis = -1)
    ts_doppler = [ts[i]+ ds[i]/c for i in range(len(ts))]

    return ts_doppler, ds, rs

#########################################
### Procesamiento inicial de la señal ###
#########################################

if path.isfile(f"{args.f_read}"):
    fs, audio = wavfile.read(f"{args.f_read}")
else:
    raise Exception("El archivo indicado no se encuentra en el directorio de ejecución.")
    
### Promedia si hay dos canales ###
dos_canales = audio[0].size == 2  # Revisa los canales del archivo de entrada. Se usará al guardar.
if dos_canales:    
    tipo = type(audio[0][0])      # Servirá para luego guardarlo en el mismo formato
    ss = np.average(audio, 1)     # Promedio de los dos canales
else:
    tipo = type(audio[0])
    ss = audio
    
### Calcula las magnitudes iniciales ###
ts = np.linspace(0, ss.shape[0]/fs, ss.shape[0]) # Tiempo real
ts_doppler, ds, rs = doppler(ts, fs, args.v, args.r, args.theta, (args.x, args.y), args.c)
ss_n = ss/max(ss)  # Señal normalizada para graficar 
N = args.N         # Cantidad de puntos de señal entre cada punto a graficar
change = False     # Variable auxiliar que da cuenta de si hay que actualizar la posición.

########################
### Modo interactivo ###
########################

if args.modo:
    
    # No puedo utilizar args.var como variables globales
    x, y = args.x, args.y                     

    ### Primero fabrica el gráfico inicial ### 
    
    plt.ioff()
    
    fig = plt.figure(figsize=(12, 6), dpi = 100)
    grid = plt.GridSpec(2, 4, wspace=0.5, hspace=0.5)
    
    ax1 = fig.add_subplot(grid[0:2, 0:2])
    ax2 = fig.add_subplot(grid[0:1, 2:4])
    ax3 = fig.add_subplot(grid[1:2, 2:4])

    ax1.set_title(f'Tren en movimiento circular con v = {args.v} m/s')
    ax2.set_title('Distancia al observador')
    ax3.set_title('Señal de sonido recibida')

    ax1.set_xlabel('Posición x (m)')
    ax2.set_xlabel('Tiempo (s)')
    ax3.set_xlabel('Tiempo (s)')
    
    ax1.set_ylabel('Posición y (m)')
    ax2.set_ylabel('Distancia (m)')
    ax3.set_ylabel('Intensidad (u.a.)')
    
    ax1.set_xlim(-1.08*args.r, 1.08*args.r)
    ax2.set_xlim(0, ts[-1])
    ax3.set_xlim(0, ts_doppler[-1])
    
    ax1.set_ylim(-1.08*args.r, 1.08*args.r)
    ax2.set_ylim(0, 2.5*args.r)
    ax3.set_ylim(-1.05, 1.05)
    
    rads = np.arange(0, (2 * np.pi), 0.001)
    
    ax1.plot([1.05*args.r]*np.sin(rads), [1.05*args.r]*np.cos(rads), 'b')
    ax1.plot([0.95*args.r]*np.sin(rads), [0.95*args.r]*np.cos(rads), 'b')
    ax1.plot([1.00*args.r]*np.sin(rads), [1.00*args.r]*np.cos(rads), 'r', alpha = 0.3, linestyle = '--')
    
    ### Hasta aquí elementos fijos ###
    
    # D0, = ax2.plot(ts,           ds, color = 'k', alpha = 0.2, linestyle = '--', linewidth=0.7)
    # I0, = ax3.plot(ts_doppler, ss_n, color = 'b', alpha = 0.2, linestyle = '--', linewidth=0.1)

    ### Elementos dinámicos: Emisor, Observador, Intensidad, Distancia ###
    
    E, = ax1.plot([rs[0][0]], [rs[0][1]], marker = 'o', linestyle = '-', color = 'r', ms = 8, alpha = 0.9)
    O, = ax1.plot(       [x],        [y], marker = 'o', linestyle = '-', color = 'g', ms = 8, )
    D, = ax2.plot([], [], '-', color = 'black', linewidth=0.8)
    I, = ax3.plot([], [], '-', color = 'blue',  linewidth=0.3)
    
    I_datos_x, D_datos_x = [], []
    I_datos_y, D_datos_y = [], []
    
    ### Funciones relacionadas con la animación ###
    
    def doppler_gen(v = args.v, R = args.r, 
                    theta = args.theta, pos = (args.x, args.y), c = args.c):
        """ 
        Similar a doppler(), pero devuelve un iterable que es 
        luego manejado por la animation.FuncAnimation.
        """
        
        dtheta = v/(fs*R) # Intervalos de theta 
        i = 0             # Iterador  
        
        while True:
            if change or i > len(ss):  # Resetea el tiempo una vez se llegó al final de ss o se cambió el receptor.
                i = 0
                theta = theta % (2*np.pi)
            theta += N*dtheta
            r = [R*np.cos(theta), R*np.sin(theta)]
            d = np.sqrt(R*R+x*x+y*y-2*R*(np.cos(theta)*x+np.sin(theta)*y))
            t = i/fs
            u = t + d/c

            yield r, d, t, u, ss_n[i], x, y #, theta
            
            i += N        # Salto

    def update(data):
        """
        Actualiza los gráficos a partir de la información dada por doppler_gen().
        """
        
        global change, D_datos_x, D_datos_y, I_datos_x, I_datos_y
        
        if data[2] == 0:
            I_datos_x, D_datos_x = [], []
            I_datos_y, D_datos_y = [], []
           
        if change:
            change = False
            I_datos_x, D_datos_x = [], []
            I_datos_y, D_datos_y = [], []
            
            ### Esta parte vuelve la ejecución terriblemente lenta ###
            #ts_doppler, ds, _ = doppler(ts, fs, args.v, args.r, data[7], (x,y), args.c)
            #D0.set_data(ts, ds)
            #I0.set_data(ts_doppler, ss_n)
                        
        E.set_data([data[0][0]], [data[0][1]])

        D_datos_x.append(data[2])        
        D_datos_y.append(data[1])        
        D.set_data(D_datos_x, D_datos_y)
        
        I_datos_x.append(data[3])       
        I_datos_y.append(data[4])        
        I.set_data(I_datos_x, I_datos_y)
        
        O.set_data([data[5]], [data[6]])
        
        return I, D, E, O, # I0, D0,
          
    
    def click(event):
        """ 
        Dado un click en la gráfica de posición, modifica los valores de ciertas variables globales 
        para hacer efectivo el cambio de la gráfica en el próximo frame.
        """
        global x, y, change
        if event.inaxes == ax1:
            x, y, change = event.xdata, event.ydata, True
  
    ### Dinámica ###    
    fig.canvas.mpl_connect('button_press_event', click)
    ani = animation.FuncAnimation(fig, update, frames = doppler_gen, interval=int(1000*N/fs), blit=True)
    
    ### Muestra ###
    plt.show()

###########################
### Modo no interactivo ###
###########################

else:
    # Revisa primero si existe algún archivo con el mismo nombre para evitar sobreescribir #
    i = 1
    f_name = args.f_write
    while path.isfile(f"{f_name}"):
        f_name = args.f_write[:-4] + f"-({i}).wav"
        i += 1
    # Revisa si hay que guardarlo en uno o dos canales #     
    if args.canal:
        # Revisa si el audio inicial tenía uno o dos canales #
        if dos_canales:
            fl = interpolate.interp1d(ts_doppler, audio[0], kind = 'zero', bounds_error = False, fill_value=0) 
            fr = interpolate.interp1d(ts_doppler, audio[1], kind = 'zero', bounds_error = False, fill_value=0) 
            wavfile.write(f"{f_name}", fs, np.array([fl(ts).astype(tipo), fr(ts).astype(tipo)]).T)   
        else:
            f = interpolate.interp1d(ts_doppler, ss, kind = 'zero', bounds_error = False, fill_value=0) 
            wavfile.write(f"{f_name}", fs, np.array([f(ts).astype(tipo), f(ts).astype(tipo)]).T)    
    else:
        # Para guardar los datos en formato .wav deben tener igual espaciado entre todas las muestras. Uso la frecuencia original fs. #
        f = interpolate.interp1d(ts_doppler, ss, kind = 'zero', bounds_error = False, fill_value=0) 
        wavfile.write(f"{f_name}", fs, f(ts).astype(tipo)) 
    # Informa donde se guardó el audio #
    print(f"Audio guardado en {f_name}")