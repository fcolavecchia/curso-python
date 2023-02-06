"""
==============
Efecto Doppler
==============
Mauro Gentile
Abril de 2022

"""

import argparse
import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from scipy.io import wavfile
import scipy.interpolate as interpolate

##busqueda de archivos .wav en la carpeta

fname = ''
fileslist = os.listdir()
for i in fileslist:         #si no se especifica el audio se toma uno al azar
    if '.wav' in i and '_dopp' not in i:
        fname = i
        break


##entradas por línea de comandos 

parser = argparse.ArgumentParser(
      description=
      '''"Programa que genera un audio afectado por el efecto doppler
          y muestra gráficos interactivos"
      ''',
      epilog= 'Para ejecutarse debe haber un archivo .wav en la carpeta')
                    
parser.add_argument('-iname', '--inputname', type=str, dest='imput', 
                                default = fname, 
                                help='Nombre del archivo de audio a modificar\
                                ej. audio.wav \
                                default: el primer archivo .wav que se \
                                encuentre en la carpeta')
                                
parser.add_argument('-oname', '--outputname', type=str, dest='output',
                                default = str(fname[:-4])+'_dopp.wav',
                                help='Nombre del archivo de audio modificado\
                                ej. audio_dopp.wav\
                                default: nombre del archivo original seguido de\
                                "_dopp.wav"')
                                            
parser.add_argument('-r', '--radio', type=float, dest='r', default = 50., 
                                help='Radio del circulo por el cual se mueve \
                                la fuente de sonido en m. \
                                El valor por defecto es 50')
                                
parser.add_argument('-v', '--velocidad', type=float, dest='vel', default = 80., 
                                help='Velocidad lineal a la cual se mueve la \
                                fuente en km/h. \
                                El valor por defecto es 80')                              
                                
parser.add_argument('-p', '--posicion', type=float, dest='pos', nargs=2,
                                default=[0., 0. ], 
                                help='Pocisión inicial del observador en x, y \
                                en m. \
                                El valor por defecto es 0 0')   
                                                            
parser.add_argument('-i', '--interactivo', action='store_true', 
                                help='Modo interactivo para la graficación. \
                                No guarda archivos')

parser.add_argument('-lap',  action='store_true', 
                                help='genera un audio que complete la vuelta\
                                del movil')
          
args = parser.parse_args()

if args.imput == '':
    raise Exception('no hay archivos .wav en la carpeta')

##parámetros

wav_fname = args.imput  #nómbre del archivo .wav

r = args.r              #radio en m
v = args.vel/3.6        #velocidad en m/s
p = np.array(args.pos)  #posición del observador
w = v/r                 #velocidad angular 
t_lap = 2*np.pi/abs(w)  #tiempo en dar una vuelta el móvil


##lectura del archivo de audio

sr, data = wavfile.read(wav_fname)     #leo el archivo de audio. sr:
                                       #sampleRate; data: np.array de amplitudes
if len(data.shape)>1:                  #si hay más de un canal tomo el promedio
    data = data.mean(axis=1)


if args.lap == True:            #si el audio es muy corto lo repito para que 
                                #esté presente en toda la vuelta  
    t_audio = len(data)/sr
    if t_audio < t_lap:                    
        n_rep = int(t_lap / t_audio)
        data0 = data
        for i in range(n_rep):
            data = np.hstack([data, data0])

        
##función que afecta con doppler

def doppler(data, sr, r, w, p, c = 343):
    '''
    Función que afecta con el efecto doppler a una señal de audio que se mueve 
    en una trayectoria circular.
    
    <<args>>
    data: audio original como un np.array
    sr: sampleRate
    w: velocidad angular del movil
    p: posición del observador como un np.array
    c: velocidad de propagación del sonido en el medio. Default: 343 m/s
    
    <<return>>
    data_dopp: audio modificado como un np.array
    '''
    
    N = len(data)               #número de datos equiespaciados
    t = np.linspace(0, N/sr, N) #vector de tiempos equiespaciados
    
    ps = np.array([r*np.cos(w*t), r*np.sin(w*t)]).T #posición de la fuente 
    d = np.linalg.norm(ps - p, axis=1)              #distancias
    td = d/c                                        #tiempos de propagación
    t_dopp = t - td                                 #tiempos observados
    f = interpolate.interp1d(t_dopp, data)          #función de interpolación
    t_eq = np.arange(t_dopp[0], t_dopp[-1], 1/sr)   #tiempos equiespaciados
    
    data_dopp = f(t_eq)                             #audio modificado                     
    
    return data_dopp
    
data_dopp = doppler(data, sr, r, w, p)
    
##gráficos interactivos

#función que actualiza los datos de la animación del vehículo
def update_line0(num, puntos, line, punto):
    if num < 5:
        line.set_data(np.vstack(puntos[:,:num]))
    else:
        line.set_data(np.vstack(puntos[:,num-5:num]))
    return line, punto

#función que actualiza los datos de la animación de las distancias
def update_line1(num, line1, distancias):
    if i == 0:                      #i=0 cuando no se detecta ningun clic
        line1.set_data(np.vstack(distancias[:,:num]))
    else:
        distancias = dis
        line1.set_data(np.vstack(distancias[:,:num]))
    return line1,
        

#administracion del clic
def onclick(event):
    #print('button=%d, x=%d, y=%d, xdata=%f, ydata=%f' %
    #      (event.button, event.x, event.y, event.xdata, event.ydata))
    
    line_ani.pause()            
    line1_ani.pause()  

    p = np.array([event.xdata, event.ydata]) #actualiza la pos. del observador

    if p[0] != None:
        
        #subplot posiciones
        data_dopp = doppler(data, sr, r, w, p)   #recalcula las amplitudes del audio
        punto.set_data(p)                        #asigna el nuevo punto al grafico   
        
        #subplot distancias  
        global i
        i = 1;
        dgraf = np.linalg.norm(puntos.T - p, axis=1)   #distancias fuente-observador
        global dis
        dis = np.vstack([tgraf, dgraf.reshape(Ngraf,)]) #matriz distancias vs tiempo
               
        #subplot audio  
        L2.set_data(np.linspace(0, len(data_dopp)/sr,   #actualiza el grafico del 
                    len(data_dopp)), data_dopp)         #audio
        L2.figure.canvas.draw()
      
    line_ani.resume()
    line1_ani.resume()



#graficación
if args.interactivo == True:
    plt.ion                 #gráficos interactivos
    
    Ngraf = 100               #número de puntos a los efectos de la graficación
    tgraf = np.arange(0, 2*np.pi, 2*np.pi/Ngraf)/abs(w) #tiempos para graficar
    x, y = r*np.cos(w*tgraf), r*np.sin(w*tgraf)      #posiciones para graficar
    
    puntos = np.vstack([x.reshape(Ngraf,), y.reshape(Ngraf,)]) #trayectoria
    
    #figura

    fig = plt.figure(figsize=(16, 9))           #figura
    gs = plt.GridSpec(nrows=2, ncols=2)         #subplots
    scal = 1.1                                  #escala para acomodar los ejes
                   
    dgraf = np.linalg.norm(puntos.T - p, axis=1)   #distancias fuente-observador
    distancias = np.vstack([tgraf, dgraf.reshape(Ngraf,)]) #matriz distancias vs
                                                           #tiempos
    
     
    #subplot vehículo
    ax0 = fig.add_subplot(gs[:, 0])
    circle0 = plt.Circle((0,0),r-1, fill=False, color='grey')
    circle1 = plt.Circle((0,0),r+1, fill=False, color='grey')
    ax0.add_artist(circle0)
    ax0.add_artist(circle1)
    punto, = ax0.plot(p[0], p[1] , 'o', color='red')
    L, = plt.plot([], [], 'o',color = 'orange',markersize=15, alpha=.7)
    ax0.set_aspect('equal')
    ax0.set_xlabel('x [m]')
    ax0.set_ylabel('y [m]')
    ax0.set_title('Vehículo en movimiento circular')
    ax0.set_xlim(-r*scal,r*scal)
    ax0.set_ylim(-r*scal,r*scal)
    line_ani = animation.FuncAnimation(fig, update_line0, Ngraf, 
            fargs=(puntos, L, punto), interval=int((abs(tgraf[1]-tgraf[0]))*1000),
            blit=True)

            
    #subplot distancias
    i = 0
    ax1 = fig.add_subplot(gs[0, 1])
    L1, = plt.plot([], [], '-g')
    ax1.set_xlabel('t [s]')
    ax1.set_ylabel('distancia [m]')
    ax1.set_title('Distancia fuente-observador')
    ax1.set_xlim(tgraf[0],tgraf[-1])
    ax1.set_ylim(0,2.7*r)
    line1_ani = animation.FuncAnimation(fig, update_line1, Ngraf, 
            fargs=(L1, distancias), interval=int((abs(tgraf[1]-tgraf[0]))*1000),
            blit=True)
              
    #subplot audio
    ax2 = fig.add_subplot(gs[1, 1])
    L2, = ax2.plot(np.linspace(0, len(data_dopp)/sr, len(data_dopp)), data_dopp, 
            color = 'grey', lw=0.1)
    ax2.set_xlabel('t [s]')

   
    cid = fig.canvas.mpl_connect('button_press_event', onclick)#llamada al clic  


    plt.show()

    
else:
    wavfile.write(args.output, sr, np.int16(data_dopp))
    print('Se generó el archivo: '+str(args.output))
#############################################################################

