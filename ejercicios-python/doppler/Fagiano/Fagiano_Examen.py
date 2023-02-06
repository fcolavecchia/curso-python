# Examen Final - Introducción al lenguaje Python orientado a Ingenierías y Física
# Florencia Fagiano
# Fecha: 23/04/22


import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.animation as animation
import os.path
from scipy.io import wavfile
from scipy import interpolate
import argparse


plt.ioff()


# Creación del objeto ArgumentParser
parser = argparse.ArgumentParser(description="""Simulación del efecto Doppler. 
Este programa trabaja por línea de comandos y posee un modo interactivo y un 
modo no interactivo, en ambos casos se debe ingresar por línea de comandos el 
nombre del archivo de audio con el cual se quiere trabajar. Para activar el 
modo interactivo, se debe escribir “-i” en la línea de comandos. Al correr el 
programa en el modo interactivo, se lee el archivo de audio y se muestra una 
figura animada interactiva con 3 gráficos que ilustran la situación. En el 
panel de la izquierda (Gráfico 1), se muestra la animación de la posición de la
fuente de sonido siguiendo una trayectoria circular y la posición del oyente. 
En el panel superior derecho (Gráfico 2) se muestra el gráfico animado de la 
distancia relativa entre el oyente y la fuente de sonido en función del tiempo.
En el panel inferior derecho (Gráfico 3) se muestra el gráfico de la intensidad
del sonido en función del tiempo según la percepción del oyente, teniendo en 
cuenta el efecto Doppler. Al trabajar en el modo interactivo, el usuario puede 
seleccionar la posición del oyente al hacer click en cualquier punto del Gráfico 1. 
Al seleccionar una nueva posición, automáticamente se actualizan los Gráficos 2 y 3,
mostrando la distancia relativa entre emisor y oyente, y la intensidad del 
sonido en función del tiempo, respectivamente, para la nueva posición del oyente.  
Si no se activa el modo interactivo, el programa lee el archivo de audio original,
y genera y guarda un nuevo archivo de audio con el sonido modificado según el 
efecto Doppler (el nombre del archivo puede definirlo el usuario, en caso contrario 
se guarda con el nombre “Doppler_Effect.wav” por defecto). En este caso, además 
se imprime por pantalla un mensaje donde se indica el nombre con el cual se guardó 
el sonido y su ubicación (path). Tanto en el modo interactivo como en el no 
interactivo, el programa acepta por línea de comandos valores correspondientes 
a la velocidad del emisor de sonido, radio de la circunferencia (su trayectoria), 
y las coordenadas x e y de la posición del oyente. Si estos valores no son ingresados 
por el usuario, se utilizan los valores por defecto.""")

# Argumentos 
parser.add_argument('-v', '--velocidad', action='store', default=1., type=float, dest='v', help='Velocidad tangencial de la fuente de sonido [m/s]')
parser.add_argument('-R', '--radio', action='store', default=1., type=float, dest='R', help='Radio de la circunferencia que forma la trayectoria de la fuente de sonido [m]')
parser.add_argument('-x', '--coordenadax', action='store', default=1., type=float, dest='x', help='Coordenada x de la posición del oyente [m]')
parser.add_argument('-y', '--coordenaday', action='store', default=1., type=float, dest='y', help='Coordenada y de la posición del oyente [m]')
parser.add_argument('-o', '--output', action='store', dest='o', type=str, default='Doppler_Effect.wav', help='Nombre del archivo de sonido de salida con el efecto Doppler (.wav)')
parser.add_argument('-a', '--abrir', action='store', dest='a', type=str, help='Nombre del archivo de sonido original (.wav)')
parser.add_argument('-i', '--interactivo', action='store_true', dest='i', default = False, help='Activa el modo interactivo')



# Variable que almacena resultados
args = parser.parse_args()

# Definición de variables
v = args.v
R = args.R
x = args.x
y = args.y 
output = args.o
filename = args.a
i = args.i


# Si no se ingresa el nombre del archivo de audio a procesar, imprimir:
if filename == None:
    print("""Es necesario ingresar por línea de comandos el nombre del archivo de audio. 
          Ejemplo: -a sonido.wav""")
    exit()


# Función para realizar la lectura del archivo de audio
# Si el audio posee 2 canales (stereo), calcula el promedio entre ellos
def read_audio(archivo):
    """Función para realizar la lectura del archivo de audio.
    Toma como agumento el archivo de audio (.wav)
    y devuelve la frecuencia de muestreo (samplerate), 
    un array de datos de amplitud de sonido (data),
    la longitud del archivo de audio (length)
    y el array de valores de tiempo (time).
    
    
    La lectura del archivo se realiza con la función 
    scipy.io.wavfile.read() que devuelve la frecuencia de muestreo y 
    un array (1-D o 2-D dependiendo se el archivo WAV posee uno o dos canales)
    Si el audio posee 2 canales (stereo), 
    se calcula el promedio entre ellos"""
    samplerate, data_o = wavfile.read(archivo)
    if data_o.ndim==2:
        data=(data_o[:, 0]+data_o[:, 1])/2
        length = len(data) / samplerate
        time = np.linspace(0., length, len(data))
    else:
        data=data_o
        length = len(data) / samplerate
        time = np.linspace(0., length, len(data))
    return samplerate, data, length, time


# Definición de variables samplerate, data, length y time
samplerate, data, length, time = read_audio(filename)



# Asignación de variables a utilizar en la simulación
Te = time   # Tiempo del emisor de sonido
Vs = 343    # Velocidad de sonido
w = v/R     # Velocidad angular



# Función que determina el tiempo que tarda en llegar el sonido 
# desde la fuente al receptor
def Trec(R,w,x,y,t):
    """Función que determina el tiempo que tarda en llegar 
    el sonido desde el emisor al receptor.
    Parámetros:
        R: Radio de la circunferencia (trayectoria del emisor)
        w: Velocidad angular [1/s]
        x: Coordenada x de la posición del oyente [m] 
        y: Coordenada y de la posición del oyente [m]
        t: Tiempo [s]
    Devuelve el array de tiempo que percibe el receptor"""
    Tr = t + ((x-R*np.cos(w*t))**2+(y-R*np.sin(w*t))**2)**(1/2)*t/Vs
    return Tr


# Definición del tiempo que percibe el receptor (Tr) en función de R, w, x, y, Te 
Tr = Trec(R, w, x, y, Te)



# Función que determina la distancia entre el emisor y el receptor 
# para cada instante de tiempo
def dist(R,w,x,y,t):
    """Función que determina la distancia entre el emisor y
    el receptor para cada instante de tiempo
    Parámetros:
        R: Radio de la circunferencia (trayectoria del emisor)
        w: Velocidad angular [1/s]
        x: Coordenada x de la posición del oyente [m] 
        y: Coordenada y de la posición del oyente [m]
        t: Tiempo [s]
    Devuelve el array de distancia entre el emisor y receptor"""
    d = ((x-R*np.cos(w*t))**2+(y-R*np.sin(w*t))**2)**(1/2)
    return d



# Si se activa el modo interactivo se muestra una figura animada 
# interactiva con 3 gráficos que ilustran la situación :
if i:
    
    print('''Modo interactivo. 
Se generó una interfaz interactiva en donde el usuario puede seleccionar con el click 
la ubicación del oyente y obtener para esa nueva posición el gráfico de la distancia 
relativa entre el oyente y el emisor de sonido y el gráfico de la intensidad del 
sonido en función del tiempo, teniendo en cuenta el efecto Doppler.''')
    
    
    # Definición de figura y grilla donde se ubicará cada subplot
    figura = plt.figure(figsize=(9, 4.5))
    gs = gridspec.GridSpec(2,2, figure=figura)
    
    # Definición de array de tiempos para las simulaciones 
    T = np.linspace(0., time[-1], int(25*time[-1]))
    
    # Definición de la distancia entre el emisor y el receptor en función de R, w, x, y, T
    d = dist(R, w, x, y, T)
       
    
    
    # Función para obtener valores de posición al hacer click
    def onclick(event):
        """Función que toma como argumento el evento (click) y permite 
        obtener valores de la nueva posición del oyente 
        según los valores de x e y del punto seleccionado por el 
        usuario al hacer click en el gráfico de trayactoria circular 
        del emisor y posición del oyente. 
        
        Se actualiza la posición del oyente.
        Se actualiza el gráfico de distancia relativa entre emisor y 
        receptor en función del tiempo.
        Se actualiza el gráfico de intensidad de sonido en función del 
        tiempo según percepción del oyente, con el efecto Doppler."""
        global data_d
        global ymax
        x = event.xdata
        y = event.ydata
        oyente.set_data([x],[y])
        dn = dist(R, w, x, y, T)
        data_d = np.vstack([T, dn])
        tn = Trec(R, w, x, y, Te)
        L2.set_data([tn],[dn])
        ymax=np.max(dn)
        ax2.set_ylim(0, ymax+0.5)
        ax2.figure.canvas.draw()
        L3.set_data([tn],[data])
        ax3.set_xlim(np.min(tn), np.max(tn))
        ax3.figure.canvas.draw()
        plt.draw()
        
                 
    
    
    # Creación del subplot donde se graficará la trayactoria circular, 
    # animación del movimiento del emisor y la posición del oyente (Gráfico 1)
    ax1 = figura.add_subplot(gs[:,0])
        
    # Posición del emisor
    xe = R*np.cos(w*T)
    ye = R*np.sin(w*T)
    data_p = np.vstack([xe, ye])
    
    # Creación de la línea de graficación de la posición del emisor
    L1, = ax1.plot([], [], 'ok', markersize=6)
    
    # Creación de la línea de graficación de la posición del oyente
    oyente, = ax1.plot(x,y, 'og', markersize=6)       
    
    #Trayectoria del emisor (circunferencia)
    tita = np.linspace(0, 2*np.pi, 200)
    x1 = R*np.cos(tita)
    y1 = R*np.sin(tita)
    x2 = (R+(0.1*R))*np.cos(tita)
    y2 = (R+(0.1*R))*np.sin(tita) 
    x3 = (R-(0.1*R))*np.cos(tita)
    y3 = (R-(0.1*R))*np.sin(tita)
    
    # Grafica la trayectoria del emisor
    ax1.plot(x1,y1,'.k', markersize=0.2)
    ax1.plot(x2,y2,'-k', lw=0.4)
    ax1.plot(x3,y3,'-k', lw=0.4)
    
    # Límites de graficación
    ax1.set_xlim(-(R+(0.2*R)), (R+(0.2*R)))
    ax1.set_ylim(-(R+(0.2*R)), (R+(0.2*R)))
    
    # Labels y título del gráfico
    ax1.set_xlabel('Posición x [m]')
    ax1.set_ylabel('Posición y [m]')
    ax1.set_title('Trayectoria del emisor y posición del oyente', fontsize=10)
    
    
    
    # Creación del subplot donde se graficará la distancia relativa entre
    # la fuente de sonido y el oyente en función del tiempo (Gráfico 2)
    ax2 = figura.add_subplot(gs[0,-1])
    
    data_d = np.vstack([T, d])
    
    # Creación de la línea de graficación de la distancia relativa
    L2, = ax2.plot(T, d, '-g', lw=2)  
    
    # Límites de graficación
    ax2.set_xlim(np.min(Te), np.max(Te))
    ymax = np.max(d)
    ax2.set_ylim(0, ymax+0.5)
    
    # Labels y título del gráfico
    ax2.set_xlabel('Tiempo [s]')
    ax2.set_ylabel('Distancia [m]')
    ax2.set_title('Distancia al oyente', fontsize=10)
    
    
    
    # Creación del subplot donde se graficará la intensidad del sonido 
    # en función del tiempo según la percepción del oyente (Gráfico 3)
    ax3 = figura.add_subplot(gs[-1,-1]) 
    
    # Gráfico de intensidad de sonido según percepción del oyente
    L3, = ax3.plot(Tr, data, lw=0.5) 

    # Labels y título del gráfico
    ax3.set_title('Intensidad de sonido según la percepción del oyente', fontsize=10)
    ax3.set_xlabel("Tiempo [s]")
    ax3.set_ylabel("Amplitud")
    
    # Límites de graficación
    ax3.set_xlim(np.min(Tr), np.max(Tr))
    
    
    
    # Función para actualizar las líneas:
    def update_line(num, L1, L2, oyente):
        L1.set_data(data_p[:, num])
        L2.set_data(data_d[:, :num])
        return [L1, L2, oyente]
    
    
    
    # Función que genera la animación:
    line_ani = animation.FuncAnimation(figura, update_line, int(25*time[-1]), fargs=(L1, L2, oyente), interval=(1), blit=True)
    
        
    # Ajusta automáticamente los parámetros de los subplots para lograr 
    # una buena distribución del área de la figura:   
    figura.tight_layout()   
    
    # Conecta el evento (hacer click) con la función onclick:
    cid = figura.canvas.mpl_connect('button_press_event', onclick)
        
    plt.show()
    
    
    
# Si no se activa el modo interactivo, se genera y guarda un nuevo archivo
# de audio con el sonido modificado según el efecto Doppler     
else:
    
    # El array de tiempos según la percepción del oyente (Tr), no se corresponde 
    # con un array equiespaciado, y para generar un archivo de audio se debe
    # proporcionar un array con valores de amplitudes que se correspondan con
    # tiempos equiespaciados. 
    # Por lo tanto, se realiza la interpolación a valores de tiempo equiespaciados.
    
    # Función interpolante basada en los puntos correspondientes a Tr y data:
    interpol = interpolate.interp1d(Tr, data)
    
    # Creación de valores de tiempo equiespaciados donde se quiere evaluar
    # la función mediante la interpolación:
    Tr_eq = np.linspace(Tr[0], Tr[-1], len(data))  
    
    # Obtención de nuevos valores de amplitud correspondientes a tiempos equiespaciados:
    data_new = interpol(Tr_eq)
          
    # Función para guardar el sonido modificado con el efecto Doppler como archivo .wav
    wavfile.write(output, samplerate, data_new.astype(np.int16))
    
    print('''Modo no interactivo. 
Se generó un archivo de audio con el sonido reconstituido teniendo en cuenta el efecto Doppler.
Nombre del archivo: {}
Ubicación: {}'''.format(output, os.path.dirname(os.path.abspath(output))))




  


