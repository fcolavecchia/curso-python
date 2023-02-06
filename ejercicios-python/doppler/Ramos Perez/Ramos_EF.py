# Iván Ramos
# Efecto Doppler

# librerias importadas
import numpy as np
from scipy.io import wavfile
import matplotlib.pyplot as plt
import argparse
import matplotlib.animation as animation
from scipy.interpolate import griddata

parser = argparse.ArgumentParser(
description='"ExamenFinal - EfectoDoppler: Ivan Ramos"')
parser.add_argument('-f', '--file', action='store', 
                    dest='file',default='data_train-whistle.wav',
                    help='Nombre del archivo de audio indicado por el usuario')
parser.add_argument('-R', '--Radio', type=float, action='store', 
                    dest='R', default=10,
                    help='Radio del círculo que forma la trayectoria de la fuente de sonido en [m]')
parser.add_argument('-Ve', '--V_emisor', type=float, action='store', 
                    dest='Ve', default=10,
                    help='Velocidad del emisor de sonido en [m/s]')
parser.add_argument('-Ppx', '--Px_persona_', type=float, action='store', 
                    dest='Ppx', default=0,
                    help='Posición inicial de la persona en x en [m]')
parser.add_argument('-Ppy', '--Py_persona_', type=float, action='store', 
                    dest='Ppy', default=0,
                    help='Posición inicial de la persona en y en [m]')

parser.add_argument('--animate', action='store_true',
                    help='Activar modo interactivo')
parser.add_argument('-o', '--nombre', action='store', 
                    dest='nombre',default='out.wav',
                    help='Nombre de archivo de salida')

parser.add_argument('-Vs', '--V_sonido', type=float, action='store', 
                    dest='Vs', default=340,
                    help='Velocidad del sonido en [m/s]')
parser.add_argument('--P_angular_emisor', type=float, action='store', 
                    dest='theta_0', default=0,
                    help='pocision angular inicial del emisor [rad]')

args = parser.parse_args()      


#####
#funciones creadas
def onclick(event,ax):
  """actualiza data al hacer click con el ratón"""                                                            
  #global ax_2 
  if event.xdata==None or event.ydata==None:                                   # evita errores 
      pass
  elif str(ax) == str(event.inaxes):
  #else:
      args.Ppx = event.xdata                                                   # actualiza la posición en el eje y del oyente
      args.Ppy = event.ydata                                                   # actualiza la posición en el eje y del oyente
  # limites de Ppx y Ppy
  #print(ax_2)
  if args.Ppx > 1.1*args.R: args.Ppx = 1.1*args.R  
  if args.Ppy > 1.1*args.R: args.Ppy = 1.1*args.R
  if args.Ppx < -1.1*args.R: args.Ppx = -1.1*args.R
  if args.Ppy < -1.1*args.R: args.Ppy = -1.1*args.R  
  
def shape2(data):                                                              
    """devuelve shape sin error para el caso que data solo tenga 1 canal"""
    try:
        shape = (data.shape[0], data.shape[1])
    except IndexError:
        shape = (data.shape[0], 1)        
    return shape

def distancia_P(theta,R,Px,Py):
    """devuelve la distancia entre el oyente(Px,Py) y el emisor (R,theta)"""
    r_ot = [Px - R*np.cos(theta), Py - R*np.sin(theta)]
    return r_ot, np.sqrt(r_ot[0]**2 + r_ot[1]**2)

def update_plot(num):
    fig.clear()
    
    ############ Data para el subplot 224 ############
    time_i = np.arange(0,shape_data[0])/samplerate                             # tiempo de salida de la onda del emisor 
    theta = args.theta_0 + dtheta * time_i                                     # posicion angular  del emisor 
    r_ot, d_ot = distancia_P(theta,args.R,args.Ppx,args.Ppy)                   # distancia entre persona y emisor |r_ot| 
    time_doppler = time_i + d_ot/args.Vs                                       # tiempo de llegada de la onda a la persona
    
    ############ Data para el subplot 222 ############
    time_p = np.linspace(0,max(time_i),num_steps)
    theta_p = np.linspace(args.theta_0, args.theta_0 + 2*np.pi, num_steps)
    r_p, d_p = distancia_P(theta_p,args.R,args.Ppx,args.Ppy)  
    data222 = np.c_[time_p, d_p].T
    d1 = data222[..., :num]
    
    ############ Data para el subplot 121 ############
    data121 = np.c_[args.R*np.cos(theta_p), args.R*np.sin(theta_p)].T
    d2p = [args.Ppx,args.Ppy]
    d2 = data121[:, num]
    
    #global ax_2, ax_1, ax3 
    ax_2=fig.add_subplot(222)
    ax_2.plot(d1[0],d1[1],'-k')
    ax_2.title.set_text('distancia al observador')
    ax_2.set_xlabel('tiempo (s)')
    ax_2.set_ylabel('Distancia (m)')
    ax_2.set_xlim([0,max(time_i)])
    ax_2.set_ylim([0,max(d_p*3/2)])
    
    ax_3=fig.add_subplot(224)
    ax_3.plot(time_doppler,intensidad_0,'-b')
    ax_3.set_xlabel('tiempo(s)')
    
    ang = np.linspace(0,2*np.pi,100)
    ax_1=fig.add_subplot(121)
    ax_1.plot(1.05*args.R*np.cos(ang),1.05*args.R*np.sin(ang),'--k')
    ax_1.plot(0.95*args.R*np.cos(ang),0.95*args.R*np.sin(ang),'--k')
    ax_1.plot(d2[0],d2[1],'bo',markersize=12)
    ax_1.plot(d2p[0],d2p[1],'ro',markersize=12)
    ax_1.set_xticks([])
    ax_1.set_yticks([])
    ax_1.set_xlim([-1.1*args.R,1.1*args.R])
    ax_1.set_ylim([-1.1*args.R,1.1*args.R])
    ax_1.title.set_text('Tren en movimiento circular')
    fig.canvas.mpl_connect('button_press_event',lambda event: onclick(event, ax_1))
    
  
r_tr0 = [args.R*np.cos(args.theta_0),args.R*np.sin(args.theta_0)]              # Posicion inicial del tren
dtheta = args.Ve/args.R                                                        # velociadad angular del tren [rad/s]
num_steps = 50

samplerate, data = wavfile.read(args.file)                                     # leyendo audio

shape_data = shape2(data)                                                      # dimensiones de la data leida
length = shape_data[0] / samplerate                                            # tiempo total [s]

# creacion de un array de intensidad (promedio en el caso 2 canales )
if shape_data[1]==1:
    intensidad_0 = data
else:
    intensidad_0 = np.mean(data,1)

if args.animate:                                                               # condicional para activar el modo animación
    fig=plt.figure(figsize=(16,8))
    anim = animation.FuncAnimation(fig, update_plot, num_steps,interval=100)
    plt.show()
else:
    time_i = np.arange(0,shape_data[0])/samplerate                             # tiempo de salida de la onda del emisor 
    theta = args.theta_0 + dtheta * time_i                                     # posicion angular  del emisor 
    r_ot, d_ot = distancia_P(theta,args.R,args.Ppx,args.Ppy)                   # distancia entre persona y emisor |r_ot| 
    time_doppler = time_i + d_ot/args.Vs                                       # tiempo de llegada de la onda a la persona
    ti = np.arange(0,shape_data[0])/samplerate+time_doppler[0]
    Ii = griddata(time_doppler,intensidad_0,ti,method='linear')
    wavfile.write(args.nombre, samplerate, Ii.astype(np.int16))