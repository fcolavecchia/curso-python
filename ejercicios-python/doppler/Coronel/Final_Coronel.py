"""
Thomas Coronel

Examen Final 2022
"""

#---------------------------------------

# Para poder aceptar lineas de comando 
import argparse

#Para manejo de datos con arrays
import numpy as np

#Para poder abrir archivos de audio

from scipy.io import wavfile

#Para realizar graficos
import matplotlib.pyplot as plt

# Para realizar graficos con animacion

import matplotlib.animation as animation

plt.ioff()


#Declaracion para poder utilizar el cursor y realizar interactividad en un grafico
from matplotlib.widgets import Cursor

#---------------------------------------

parser = argparse.ArgumentParser(description = 'Efecto Doppler')
'''
# Archivo de audio a abrir
'''
parser.add_argument('-audio', '--Archivo de audio a abrir', dest='audio', type = str, default = 'data_train-whistle.wav')

'''
# Posicion inicial de la persona
'''
parser.add_argument('-x_i', '--Posicion inicial en eje x', dest='x_i', type = float, default = 2.0)
parser.add_argument('-y_i', '--Posicion inicial en eje y', dest='y_i', type = float, default = 7.2)

'''
# Radio del círculo que forma la trayectoria de la fuente de sonido
'''

parser.add_argument('-r_0', '--Radio del circulo', dest='r_0', type = float, default = 10.0)

'''
# Velocidad angular del emisor de sonido
'''

parser.add_argument('-w_i', '--Velocidad angular inicial', dest='w_i', type = float, default = 60)

'''
# Aceleracion angular del emisor de sonido
'''

parser.add_argument('-eta_i', '--Aceleracion angular inicial', dest='eta_i', type = float, default = 0)

'''
# Posicion inicial del tren
'''

parser.add_argument('-theta_i', '--Posicion inicial', dest='theta_i', type = float, default = 0.0)

'''
# Modo interactivo o no. Valor por defecto: no-interactivo
# Valores posibles y:yes or n:no
'''

parser.add_argument("-an", "--Animate",dest='an',  type=str, default = 'n')

'''
# Nombre de archivo de salida de audio con el Efecto Dopler
'''

parser.add_argument('-salida', '--Archivo de audio a guardar', dest='salida', type = str, default = 'Efecto_Doppler.wav')

'''
#Declaracion de las variablesingresadas por argumento y/o por defecto
'''

'''
Este scrip esta pensado para que el movimiento del tren se halle en 
Movimiento Circular Uniforme (MCU)
Movimiento Circular Uniformemente Acelerado (MCUA)

r_o en metros
theta en grados 
x_i en metros
y_i en metros

w_i en \frac{grados}{s}
eta_i en \frac{grados}{s^2}

'''



args = parser.parse_args()

audio = args.audio

x_i = args.x_i
y_i = args.y_i
r_0 = args.r_0
w_i = args.w_i
eta_i = args.eta_i
theta_i = args.theta_i
an = args.an
salida = args.salida

#---------------------------------------
'''
# Lectura del archivo de audio
'''

samplerate, data = wavfile.read(audio)

t_max = data.shape[0] /samplerate

time = np.arange(0, t_max,1/samplerate)

'''
#Por si el audio tiene canales stereos
'''

if (len(data.shape)>1):
    data = (data[:,0] + data[:,1])/2

#---------------------------------------
'''
# Definiciones de funciones que calculan la posicion y distancia del emisor al 
#   receptor (oyente)
'''

def theta_f (time, w_i = 360,theta_i = 0, eta_i = 0):
    
    return theta_i + w_i * time + 0.5 * eta_i * (time**2)

def x_inst (r_0, theta):
    
    return r_0 * np.cos(np.deg2rad(theta))

def y_inst (r_0, theta):
    
    return r_0 * np.sin(np.deg2rad(theta))

    
def dist_f (x, y, x_i, y_i):
                  
    return ((x-x_i)**2 + (y-y_i)**2 )**0.5



'''
# Calculo de la Intensidad de la onda sonora debido al Efecto Doppler
# https://es.wikipedia.org/wiki/Intensidad_de_sonido (Formula de la Intensidad del Sonido)
# I(r) = \frac{P}{4 * \pi * r^2 } 
# Para cuando r = 0 tenemos una singularidad, por lo que se adopta que 
# Po es la Potencia sonora en la fuente y la formula queda de la siguiente maneera:
# I(r) = Po * \frac{1}{(r+0.5)^2} ; debido que para I(0) = Po
'''

def intensidad_sonido(data ,r):
 
    return (1/(r +0.5)**2)* data

#---------------------------------------
# Funciones que se utilizan para realizar los graficos interactivos y/o animacion

'''
# Funcion que actualiza la trayectoria del tren
'''
def update_pto(num, data, P):
  # p.set_data(data[:, :num])
  P.set_data(data[0,num+1], data[1,num+1])
  return P,

'''
# Funcion que actualiza los datos de la distancia del oyente al tren
'''

def update_dist(num, data, line):
  line.set_data(data[:, :num])
  return line,


x0 =x_i
y0 =y_i

def click(event):
  """Secuencia:
  1. Encuentro el punto donde el mouse hizo 'click'
  2. Le doy valores a un punto dado de el grafico de la izquierda
  3. Grafico los nuevos valores
  """
  x0 = event.xdata
  y0 = event.ydata
  # xx0 = int(x0)
  # yy0 = int(y0)
  
  print (x0)
  print (y0)
  
  p, = plt.plot(x0, y0, 'og',linewidth = 1)

  p.figure.canvas.draw()
  
#---------------------------------------

# Realizo un bucle infinito para realizar el cambio del valor del punto con los click
# (No es la solucion mas elegante, pero es la que encontre para que funcione el programa)



Boolean = 1


while Boolean < 3 :
        
    '''
    #Calculo de la posicion y distancia del receptor
    '''
    
    theta  = theta_f(time, w_i , theta_i, eta_i) 
    x_data = x_inst(r_0, theta)
    y_data = y_inst(r_0, theta)
    dist   = dist_f (x_data, y_data, x_i , y_i )
    
    '''
    # Calculo de la intensidad del sonido que obtiene el oyente:
    '''
      
    int_sonido = intensidad_sonido(data, dist)
    
    #---------------------------------------
    '''
    # Variables utiles para los graficos
    '''
    
    Npt = 50
    
    x_ext = x_inst(r_0 + 0.5, theta)
    y_ext = y_inst(r_0 + 0.5, theta)
    
    x_ext = x_ext[::int(x_ext.shape[0]/Npt)]
    y_ext = y_ext[::int(y_ext.shape[0]/Npt)]
    
    x_int = x_inst((r_0-0.5), theta)
    y_int = y_inst((r_0-0.5), theta)
    
    x_int = x_int[::int(x_int.shape[0]/Npt)]
    y_int = y_int[::int(y_int.shape[0]/Npt)]
    
    
    '''
    # Debido a la enorme cantidad de muestras del archivo de audio
    # es que se decide tomar una porcion de los datos para mostrar la animacion
    '''
    
    Npt_1 = 50
    x_mini = x_data[::int(x_data.shape[0]/Npt_1)]
    y_mini = y_data[::int(y_data.shape[0]/Npt_1)]
    
    data_movi_mini = np.vstack([x_mini, y_mini])
    
    Npt_2 = 50
    d_mini = dist[::int(dist.shape[0]/Npt_2)]
    t_mini = time[::int(time.shape[0]/Npt_2)]
    
    data_mini = np.vstack([t_mini, d_mini])
    
    
    #---------------------------------------
    # Graficos
    
    fig = plt.figure()
    
    '''
    ### Grafico  1
    '''
    
    ax1 = plt.subplot2grid((2, 4), (0, 0), colspan=2, rowspan=2)
    
    ax1.set_title('Tren en Movimiento Circular')
    
    
    # Punto que representa al tren
    P, = plt.plot([], [], 'o r',linewidth = 1)
    
    
    # Punto que representa al oyente
    
      
    p, = plt.plot(x0, y0, 'og',linewidth = 1)
    
    
    # Circunferencias que delimitan por donde el tren se mueve
    plt.plot(x_int,y_int,'b',linewidth = 0.5)
    plt.plot(x_ext,y_ext,'b',linewidth = 0.5)
    
    ax1.set_xlim(x_data.min() - 1,x_data.max() + 1)
    ax1.set_ylim(y_data.min() - 1,y_data.max() + 1)
    
    
    p_ani = animation.FuncAnimation(fig, update_pto, Npt_1,
                                        fargs=(data_movi_mini, P), interval=50, blit=True)
    
    # Conecto el cursor para que se genere el evento y se me actualice el valor del punto
    # Donde se encuentra el oyente
   
    if  an == 'y' :
        cursor = Cursor(ax1, horizOn=False, vertOn=False, useblit=True,
                        color='r', linewidth=1)
    
    
        
    cid = fig.canvas.mpl_connect('button_press_event', click)
    p, = plt.plot(x0, y0, 'og',linewidth = 1)
    
    '''
    ### Grafico 2
    '''
    
    
    
    ax2 = plt.subplot2grid((2, 4), (0, 2), colspan=2)
    
    
    
    ax2.set_title('Distancia al Observador')    
    ax2.set_ylabel('Distancia (m)', fontsize=10)
    ax2.set_xlabel(r'Tiempo (s)'  , fontsize='x-large')
    
    ax2.set_xlim(0, t_max)
    ax2.set_ylim(-1.1, int(d_mini.max()+2))
    
    L, = plt.plot([], [], '-k')
    
    line_ani = animation.FuncAnimation(fig, update_dist, Npt_2,
                                       fargs=(data_mini, L), interval=100, blit=True)
    
    
    # fig.canvas.mpl_connect('button_press_event', click)
    
    
    
    '''
    ### Grafico 3
    '''
    
    ax3 = plt.subplot2grid((2, 4), (1, 2), colspan=2)
    # plt.plot(time,data)
    plt.plot(time,int_sonido, 'c')
    
    
    # Configuracion para que sea mas agradable los graficos realizados
    fig.subplots_adjust(left=0.025, bottom=0.05, right=0.975, top=0.95, wspace=0.25, hspace=0.2)
    
    ax3.set_xlim(0, t_max)
    ax3.set_ylim( int(int_sonido.min() -2) , int(int_sonido.max()+2))
    
    
    #---------------------------------------
    # Salida de audio dependiendo de si es interactivo o no
    
         
    
    
    
    plt.show()
    
    if an == 'n' :
        wavfile.write(salida, samplerate, int_sonido.astype(np.int16))
        Boolean = 3
    
    Boolean += 1

# runfile('Final_Coronel.py','-an y')
                      