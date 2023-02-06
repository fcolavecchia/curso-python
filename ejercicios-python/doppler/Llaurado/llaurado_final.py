from scipy.io import wavfile
import matplotlib.pyplot as plt
import numpy as np
import math
from matplotlib.animation import FuncAnimation
import argparse

parser = argparse.ArgumentParser(description='Efecto Doppler con animación!')
parser.add_argument('-xo', dest='x_observador', action='store', default = 0)
parser.add_argument('-yo', dest='y_observador', action='store', default = 0)
parser.add_argument('-R', dest='radio', action='store', default = 1)
parser.add_argument('-w', dest='velocidad', action='store', default = 1)
parser.add_argument('--animacion', dest='animacion', action='store_true', default = False)
parser.add_argument('--filename', dest='filename', action='store', default = 'train.wav')

args = vars(parser.parse_args())
vars = [args[arg] for arg in args]

#Leemos el archivo
filename = vars[-1]
samplerate, data = wavfile.read(filename)
data = data.tolist()
if len(data) == 2:
    data = [sum(x) for x in zip(data[1][:], data[0][:])]

#Parámetros
R = float(vars[2]) #Radio del circulo
w = float(vars[3]) #Velocidad angular del emisor (constante)
c = 334 #Velocidad del sonido.
phi = np.random.random()*2*math.pi #Fase inicial del tren
xo, yo = float(vars[0]), float(vars[1]) #Posición observador en cuadrado 2Rx2R
animar = vars[-2]

T = 2*math.pi/w #Período vuelta

def doppler(samplerate, data):
    ts = np.arange(0, len(data))/samplerate #Tiempo total del audio dividido en 1/f intervalos.
    xs = np.cos(w*ts + phi)*R #Posicion del tren para cada intervalo de tiempo.
    ys = np.sin(w*ts + phi)*R
    ds = np.array([((xe-xo)**2 + (ye - yo)**2)**(1/2) for xe, ye in zip(xs, ys)]) #Distancia del tren al observador.
    tps = ts + ds/c #Tiempo de llegada de los frentes de onda.
    if w*R > c: #Cuanvo v > c, hay frentes que pueden llegar antes que sus predecesores.
        data_ = [x for _, x in sorted(zip(tps, data))] 
        tps = sorted(tps)
    else:
        data_ = data
    #La mayoría de los valores ahora no caen en los intervalos equidistantes -> vamos a interpolar a primer orden.
    data_ = np.interp(ts, tps, data_)
    return data_, tps

data_, tps = doppler(samplerate, data)

dt = 0.01 #dt para el update del tren.
max_it = int(tps[-1]/dt) #Cantidad de iteraciones de la animación.
if animar:
    fig = plt.figure(figsize = (16,8))
    ax1 = plt.subplot(1,2,1)
    ax2 = plt.subplot(2,2,2)
    ax3 = plt.subplot(2,2,4)
    xdata, ydata = [], []
    train, = ax1.plot([], [], 'bo')
    observer, = ax1.plot([], [], 'kx')
    distance, = ax2.plot([], [], 'r-')
    audio, = ax3.plot(tps, data_, 'b-', alpha = .5)
    i = 0
    def onclick(event):
        if event.inaxes == ax1 and event.button == 1:
            global i
            global xo
            global yo
            global data_
            global tps
            global xdata, ydata  
            xdata = []
            ydata = []
            xo = event.xdata
            yo = event.ydata 
            data_, tps = doppler(samplerate, data) 
            observer.set_data(xo,yo)
            observer.figure.canvas.draw()
            audio.set_data(tps, data_)
            audio.figure.canvas.draw()
            ax2.set_xlim(0, 2*math.pi/w)
            i = 0

    def init():
        ax1.set_title('Tren en MCU')
        ax1.set_xlim(-1.2*R, 1.2*R)
        ax1.set_ylim(-1.2*R, 1.2*R)
        ax2.set_xlim(0, 2*math.pi/w)
        ax2.set_ylim(-2.2*R, 2.2*R)
        ax3.set_xlim(0, tps[-1])
        ax1.set_xlabel('y [m]')
        ax1.set_ylabel('x [m]')
        ax2.set_xlabel('Tiempo [s]')
        ax2.set_ylabel('Distancia [m]')
        ax3.set_ylabel('Frente de onda')
        ax3.set_xlabel('Tiempo [s]')
        ax3.ticklabel_format(style='sci', axis='y', scilimits=(0,0))
        observer.set_data(xo,yo)
        audio.set_data(tps,data_)
        return train, distance, observer, audio,

    def update(j):
        global i
        i = i + 1
        x = np.cos(w*j*dt + phi)*R
        y = np.sin(w*j*dt + phi)*R
        d = ((x-xo)**2 + (y-yo)**2)**(1/2)
        xdata.append(i*dt)
        ydata.append(d)
        train.set_data(x, y)
        distance.set_data(xdata, ydata)
        if i*dt > 2*math.pi/w:
            ax2.set_xlim(i*dt - 2*math.pi/w, i*dt)

        return train, distance, observer, audio,

    ani = FuncAnimation(fig, update, interval = 50, frames = range(max_it), init_func=init, repeat = True)
    cid = fig.canvas.mpl_connect('button_press_event', onclick)
    plt.show()
else:
    oname = 'awesome_doppler.wav'
    wavfile.write(oname, samplerate, data_)