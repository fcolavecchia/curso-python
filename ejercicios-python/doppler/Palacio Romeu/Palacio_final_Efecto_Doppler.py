from matplotlib.pyplot import *
import scipy.io.wavfile as wf
import argparse
import sys
import os
import numpy as np
import scipy.interpolate as ip
from matplotlib.animation import FuncAnimation

c = 343 # velocidad del sonido en el aire en [m/s]
norm = lambda x: x/max(abs(x))

class Movimiento:
    def __init__(self, p, N=100):
        self.r = p.r
        self.v = p.v
        self.pos = p.pos
        self.N = N
        self.T = 2*np.pi*p.r/p.v
        self.t_e = np.linspace(0, 2*np.pi, N)*p.r/p.v # vector de tiempo del emisor
        self.dt_e = np.diff(self.t_e)[0] # diferencial de tiempo en segundos
        self.phi = np.linspace(0, 2*np.pi, N)  # ángulo de rotación del emisor
        self.x = p.r*np.cos(self.phi)  # posición x,y del emisor
        self.y = p.r*np.sin(self.phi)
        self.d = ((self.x - p.pos[0])**2 + (self.y - p.pos[1])**2)**0.5  # distancia del emisor al observador
        self.R = (p.pos[0]**2 + p.pos[1]**2)**0.5  # distancia del observador al origen
        self.vr = np.diff(self.d)/self.dt_e; self.vr = np.insert(self.vr,0,self.vr[0])  # velocidad relativa entre el emisor y el observador (en la dirección que une a ambos)
        self.df = self.vr/c*1000  # desviación de frecuencia para un tono de 1 kHz

def read_audio(filename):
    fs, audio = wf.read(filename)
    if len(audio.shape)-1: audio = np.mean(audio, axis=0)  # Si el audio tiene dos canales tomo el promedio de ambos
    t_a = np.arange(len(audio))/fs  # vector de tiempo del audio original
    return t_a, audio, fs

def aplicar_dopler_algoritm(audio, fs, p):
    M = len(audio)

    N = int((2*np.pi*p.r/p.v)*fs) 
    m = Movimiento(p, N = N)
    
    if M/fs > m.T:
        audio = audio[:N] # El audio es más largo que el recorrido del tren, se tomará el audio hasta el final de la primera vuelta
    audio = audio/(1 + (m.d[:M]/m.r)**2)
    
    t_dopler = m.d[:M]/c - min(m.d[:M])/c + m.t_e[:M]  # tiempo no uniforme
    t_dopler = t_dopler - t_dopler[0]  

    t_u = np.arange(int(t_dopler[-1]*fs))/fs  # vector de tiempo uniforme para el audio
    return t_u, ip.interp1d(t_dopler, audio, kind='linear')(t_u) # interpolación del audio en el tiempo uniforme

############################################################################### 
#                               PARÁMETROS                                    #
###############################################################################
parser = argparse.ArgumentParser(description='Efecto Doppler')
# parser.add_argument('--audiofile', action="store", default = None, dest = 'audiofile', help = 'Nombre del archivo de audio', type = str)
# parser.add_argument('--audiofile', action="store", default = 'sirena_ambulanza.wav', dest = 'audiofile', help = 'Nombre del archivo de audio', type = str)
parser.add_argument('--audiofile', action="store", default = 'data_train-whistle.wav', dest = 'audiofile', help = 'Nombre del archivo de audio', type = str)
parser.add_argument('-r','--radio', action="store", default = 20, dest = 'r', help = 'Radio del círculo en [m]', type = float)
parser.add_argument('-v','--velocidad', action="store", default = 20, dest = 'v', help = 'Velocidad del emisor en [m/s]', type = float)
parser.add_argument('-p','--pos', action="store", default = [0,0], dest = 'pos', help = 'Posición de la persona (x,y)', type = float, nargs = 2)
parser.add_argument('-i','--interct', action="store_true", dest = 'interact', help = 'Modo interactivo, Default False')
parser.add_argument('-o','--outputfile', action="store", default = 'audio_doppler.wav', dest = 'name', help = 'Nombre del archivo de salida, si el modo interactivo está desactivado', type = str)
p = parser.parse_args()

if not p.audiofile: 
    print('No se especificó archivo de audio')
    sys.exit()

if not os.path.exists(p.audiofile):
    print('El archivo de audio no existe')
    sys.exit()

############################################################################### 
#                               Lectura del Audio                             #
###############################################################################

t_a, audio, fs = read_audio(p.audiofile)
# audio = np.iinfo(np.int16).max*np.sin(2*np.pi*1000*t_a) # tono sinusoidal de prueba

############################################################################### 
#                       Parámetros de simulación del tren                     #
###############################################################################

m = Movimiento(p)  # objeto con parámetros importantes para la simulación

############################################################################### 
#                       Efecto Doppler aplicado al audio                      #
###############################################################################

t_u, audio_dopler = aplicar_dopler_algoritm(audio, fs, p)

############################################################################### 
#                                   Gráficos                                  #
###############################################################################

if not p.interact:
    name = p.name
    if not name.endswith('.wav'):
        name = name + '.wav'
    wf.write(name, fs, (audio_dopler).astype(np.int16))  # escritura del audio con efecto doppler
    sys.exit()

fig = gcf()
fig.set_constrained_layout(True)
fig.figure.set_size_inches(12,6)

ax1 = subplot2grid((2,4),(0,0), rowspan = 2, colspan = 2)
ax2 = subplot2grid((2,4),(0,2), colspan = 2)
ax3 = subplot2grid((2,4),(1,2), colspan = 2)

l1, = ax1.plot([],[],'or', markersize = 10)
l2, = ax1.plot([],[],'og', markersize = 10)
l3, = ax2.plot([],[],'--k')
l4, = ax3.plot([],[],'g')

vr_template = r'$v_r = %.2f$ m/s'
vr_text = ax2.text(0.1, 0.1, '', transform=ax2.transAxes, fontsize=10)

def init():
    l1.set_data([], [])
    l2.set_data(p.pos[0], p.pos[1])
    ax1.plot(1.1*m.x, 1.1*m.y, color='#8188F7')
    ax1.plot(0.9*m.x, 0.9*m.y, color='#8188F7')
    ax1.autoscale(enable=True, axis='both', tight=True)
    ax1.set_aspect('equal')
    ax1.margins(0.1)
    ax1.set_xticks([])
    ax1.set_yticks([])
    ax1.set_title('Tren en movimiento')

    l3.set_data([], [])
    ax2.set_xlim(0, m.T)
    ax2.set_ylim(0, 3*m.r)
    ax2.set_title('Efecto Doppler')
    ax2.set_xlabel('Tiempo [s]')
    ax2.set_ylabel('Distancia [m]')

    l4.set_data(t_u[::10], audio_dopler[::10])
    a = np.iinfo(audio.dtype).max
    ax3.set_xlim(-t_u[-1]*0.1, t_u[-1]*1.1)
    ax3.set_ylim(-a, a)
    ax3.set_title('Audio de salida')
    ax3.set_xlabel('Tiempo [s]')


    return l1, l2, l3, l4, vr_text

def animate(i):
    l1.set_data(m.x[i], m.y[i])
    l3.set_data(m.t_e[:i], m.d[:i])
    vr_text.set_text(vr_template % m.vr[i])
    return l1, l2, l3, l4, vr_text

anim = FuncAnimation(fig, animate, init_func=init, frames=m.N, interval=m.dt_e*1000, blit=True)

def click(event):
    global m, t_u, audio_dopler, _pause_
    x,y = (event.xdata, event.ydata)
    if event.button == 1 and x and y: # click izquierdo, actualiza posición del observador, distancias y audio de salida
        p.pos = (x,y)
        m = Movimiento(p)
        t_u, audio_dopler = aplicar_dopler_algoritm(audio, fs, p)
        l2.set_data(p.pos[0], p.pos[1])
        l4.set_data(t_u[::10], audio_dopler[::10])
    
    elif event.button == 3: # click derecho, pausa o reanuda la animación
        _pause_ = not _pause_
        if _pause_:
            anim.pause()
        else:
            anim.resume()

fig.canvas.mpl_connect('button_press_event', click)
_pause_ = False
show()
