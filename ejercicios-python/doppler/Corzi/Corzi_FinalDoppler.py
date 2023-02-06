#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simulación del Efecto Doppler

El siguiente script permite simular el efecto Doppler acústico sobre una pista
de audio almacenado en un archivo de formato WAV de varios canales, el cual es percibido
por un receptor ubicado en un punto fijo del espacio y generado por un emisor
que se desplaza en movimiento circular uniforme de radio y velocidad tangencial
constantes.

Física del problema:
El algoritmo principal de la simulación esta basado en la variacion temporal que experimenta
la onda sonoda al ser percibida por el receptor cuando el emisor se encuentra en movimiento.
Esta variacion temporal puede interpretarse como un cambio en el muestreo realizado por el
receptor de la señal.

    Muestreo_del_receptor = (1 + velocidad_relativa/velocidad_del_sonido) * Muestreo_del_emisor

A partir del vector de tiempos de muestreo del receptor, se procede a encontrar mediante
interpolation el valor de la señal percibida.

Nota: La simulación solo tienen en cuenta el Efecto Doppler experimentado
por la señal y no la variacion de la amplitud debido al inverso del cuadrado.

Utilización:
Este script genera una imagen donde puede apreciarse la simulación del experimento para
parametros determinados por el usuario mediante linea de comandos: 
-n --nombre:      Nombre de archivo de audio.
-r --radio:       Radio de la circunferencia descripta por el emisor.
-v --velocidad:   Velocidad tangencial del emisor.
-x --puntoenX:    Posición del receptor en el eje X.
-y --puntoenY:    Posición del receptor en el eje Y.
-g --guardaren:   Nombre de archivo de audio de salida.
-i --interactivo: Trabajar en modo interactivo.

Requerimientos:
Para correr este script se requiere que los siguientes módulos estén instalados:
- numpy.
- scipy.
- matplotlib.
- argparse.
- datetime.

Extras:
Este archivo también puede ser importado como un modulo que contiene a la clase
"EfectoDoppler". Ademas, la misma incorpora algunos metodos estáticos que pueden
ser utilizados como funciones:
- Leer_Archivo.
- Escribir_Archivo.
- Velocidad_Relativa.
- Variacion_Temporal.
- Interpolacion.

@Author: Leo Corzi
@Email: damian.corzi@ib.edu.ar
@Date: Mon Apr 18 08:55:41 2022
@Credit: Juan Fiol
@Links: https://fiolj.github.io/final-python-22/ej_doppler_circ.html
"""

#Procesamiento
import numpy as np
from scipy.io import wavfile
from scipy.interpolate import interp1d

#Graficacion
import matplotlib.pyplot as plt
import matplotlib.animation as animation

#Otros
import argparse
from datetime import datetime

# In[0]: Configuracion del parser
parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)

#Lista de argumentos esperados, tipo y valores por defecto
parser.add_argument('-n', '--nombre',     type=str,   action="store",      dest='n', required=True, help='Nombre de archivo de audio')
parser.add_argument('-r', '--radio',      type=float, action="store",      dest='r', default=10,    help='Radio de la circunferencia descripta por el emisor')
parser.add_argument('-v', '--velocidad',  type=float, action="store",      dest='v', default=10,    help='Velocidad tangencial del emisor')
parser.add_argument('-x', '--puntoenX',   type=float, action="store",      dest='x', default=0,     help='Posicion del receptor en el eje X')
parser.add_argument('-y', '--puntoenY',   type=float, action="store",      dest='y', default=0,     help='Posicion del receptor en el eje Y')
parser.add_argument('-g', '--guardaren',  type=str,   action="store",      dest='g', default=None,  help='Nombre de archivo de audio de salida')
parser.add_argument('-i', '--interactivo',            action="store_true", dest='i',                help='Trabajar en modo interactivo')

#Variable que almacena los parametros
args = parser.parse_args()

# In[1]: Definicion de la clase principal

class EfectoDoppler :
    """
    Clase que permite realizar la simulacion del efecto doppler sobre el sonido
    almacenado en un archivo de audio.

    Attributes
    ----------
    n : str
        Nombre del archivo de audio.
    r : float
        Radio de la circunferencia descripta por el emisor. The default is 10.
    v : float
        Velocidad tangencial del emisor. The default is 10.
    s : float
        Velocidad del sonido en el medio. The default is 343.0.
    w : float
        Velocidad angular del emisor.
    x : float
        Ubicación del receptor respecto al eje X. The default is 0.
    y : float
        Ubicación del receptor respecto al eje Y. The default is 0.
    
    se_sample : int
        Frecuencia de muestro de la se;al original.
    se_signal : numpy array
        Se'al de audio original.
    se_type : numpy dtype
        Formato de la señal de audio original.
    se_length : float
        Duración de la se;al de audio original.
    se_time : numpy array
        Vector de tiempos donde la señal original fue muestreada.
    sr_signal : numpy array
        Se'al de audio modificada por el Efecto Doppler en el receptor.
    sr_time : numpy array
        Vector de tiempos asociado a la se;al recibida por el receptor.
    
    f_an : int
        Duracion de cada frame. The default is 500.
    t_an : numpy array
        Array de tiempos secundario.
    x_an : numpy array
        Puntos X de la circunferencia animada.
    y_an : numpy array
        Puntos Y de la circunferencia animada.
    d_an : numpy array
        Puntos de la distancia animada.
    
    fig : matplotlib.figure.Figure
        Figura principal.
    axd : matplotlib.axes._subplots.AxesSubplot
        Axis del subplot.
    pls : matplotlib.lines.Line2D
        Curvas a graficar.
    an : matplotlib.animation.FuncAnimation
        Animaciones de la figura.
    
    cid : int
        Idenficador del capturador de eventos utilizado.

    Methods
    -------
    Editar (audio_in, radio=10, velocidad=10, puntoenx=0, puntoeny=0, velsonido=343.0)
        Funcion que permite editar los parametros del objeto.
    Graficar ()
        Funcion que genera la grafica y configura la animacion.
    Interactivar ()
        Funcion que configura la interactividad de la grafica.
    Almacenar (nombre = None)
        Metodo que permite almacenar el audio obtenido en un nuevo archivo.
    Animar_Grafica(i)
        Funcion generadora de la animacion de la grafica.
    Onclick(event)
        Metodo que actualiza los parametros durante el evento click.
        
    Leer_Archivo (nombre)
        Metodo estatico que permite leer el archivo de audio especificado.
    Escribir_Archivo (nombre, sample, signal)
        Metodo estatico que permite escribir el archivo de audio especificado.
    Velocidad_Relativa (t, r, w, x, y)
        Metodo estatico que determina la velocidad relativa entre el emisor y el receptor
        para cada uno de los instantes de tiempo especificados por el array t.
    Variacion_Temporal (v, s, samplerate)
        Metodo estatico que determina un vector de tiempos modificado debido
        al efecto doppler.
    Interpolacion (e_sig, te, tr)
        Metodo estatico que calcula mediante interpolacion la señal de audio
        escuchada por el receptor debida al efecto doppler.
        
    """
    
    def __init__(self, audio_in, radio=10, velocidad=10, puntoenx=0, puntoeny=0, velsonido=343.0):
        """
        
        Parameters
        ----------
        audio_in : str
            Nombre del archivo de audio.
        radio : float, optional
            Radio de la circunferencia descripta por el emisor. The default is 10.
        velocidad : float, optional
            Velocidad tangencial del emisor. The default is 10.
        puntoenx : float, optional
            Ubicación del receptor respecto al eje X. The default is 0.
        puntoeny : float, optional
            Ubicación del receptor respecto al eje Y. The default is 0.
        velsonido : float, optional
            Velocidad del sonido en el medio. The default is 343.0.

        Returns
        -------
        None.

        """
        #Parametros principales
        self.n = audio_in
        self.r = radio
        self.v = velocidad
        self.s = velsonido
        self.w = velocidad/radio
        self.x = puntoenx
        self.y = puntoeny
        
        #Lectura del archivo de audio
        self.se_sample, self.se_signal, self.se_type = self.Leer_Archivo(audio_in)

        #Duracion del audio
        self.se_length = len(self.se_signal) / self.se_sample

        #Vector de tiempos donde la señal original fue muestreada
        self.se_time = np.linspace(0, self.se_length, len(self.se_signal))
        
        #Señal de audio captada por el receptor debido al efecto doppler
        aux_vel                      = self.Velocidad_Relativa (self.se_time, self.r, self.w, self.x, self.y)
        aux_time                     = self.Variacion_Temporal (aux_vel, self.s, self.se_sample)
        self.sr_time, self.sr_signal = self.Interpolacion (self.se_signal, self.se_sample, aux_time)
        
        #Parametros para graficas y animaciones
        self.f_an = 40                                                         #Duracion de cada frame en ms
        self.t_an = np.arange(0, self.se_length, self.f_an/1000)               #Array de tiempos secundario
        self.x_an = self.r*np.cos(self.w*self.t_an)                            #Puntos de la circunferencia animada
        self.y_an = self.r*np.sin(self.w*self.t_an)                            #Puntos de la circunferencia animada
        self.d_an = ( (self.x - self.x_an)**2 + (self.y - self.y_an)**2 )**0.5 #Puntos de la distancia animada
        
        #Grafica general
        self.fig = None
        self.axd = None
        self.pls = None
        
        #Animacion de la grafica
        self.an  = None
        
        #Interactividad
        self.cid = None 
        
    def Editar (self, audio_in, radio=10, velocidad=10, puntoenx=0, puntoeny=0, velsonido=343.0):
        """
        Metodo que permite editar los parametros del objeto.

        Parameters
        ----------
        audio_in : str
            Nombre del archivo de audio.
        radio : float, optional
            Radio de la circunferencia descripta por el emisor. The default is 10.
        velocidad : float, optional
            Velocidad tangencial del emisor. The default is 10.
        puntoenx : float, optional
            Ubicación del receptor respecto al eje X. The default is 0.
        puntoeny : float, optional
            Ubicación del receptor respecto al eje Y. The default is 0.
        velsonido : float, optional
            Velocidad del sonido en el medio. The default is 343.0.

        Returns
        -------
        Method

        """
        
        if self.cid != None:
            self.fig.canvas.mpl_disconnect(self.cid)
            self.cid = None
    
        return self.__init__(audio_in, radio, velocidad, puntoenx, puntoeny, velsonido)
    
    def Graficar (self):
        """
        Metodo que genera la gráfica y configura la animacion.

        Returns
        -------
        None

        """
        #Configuracion de la imagen y su layout
        self.fig, self.axd = plt.subplot_mosaic(
            [['mov', 'dis'],
             ['mov', 'sig']],
            gridspec_kw=dict(width_ratios=[1, 1], height_ratios=[1, 1]),
            figsize=(10, 5), constrained_layout=True
        )
        
        #Parametros auxiliares para la graficacion
        pha   = np.linspace(0,2*np.pi,1000)
        rmin  = 0.9*self.r
        rmax  = 1.1*self.r
        xylim = 1.2*max(abs(self.r), abs(self.x), abs(self.y))
        
        #Grafica de la ubicacion del receptor y edl desplazamiento del emisor
        self.axd["mov"].set_title('Tren en movimiento circular')
        self.axd["mov"].plot(rmin*np.cos(pha),rmin*np.sin(pha))
        self.axd["mov"].plot(rmax*np.cos(pha),rmax*np.sin(pha))
        self.axd["mov"].set_xlim(-xylim, xylim)
        self.axd["mov"].set_ylim(-xylim, xylim)
        
        #Grafica de la distancia entre el emisor y el receptor
        self.axd["dis"].set_title('Distancia al observador')
        self.axd["dis"].set_xlim(0   , self.se_length)
        self.axd["dis"].set_ylim(0.9*min(self.d_an), 1.1*max(self.d_an))
        self.axd["dis"].set_xlabel("Tiempo (s)")
        self.axd["dis"].set_ylabel("Distancia (m)")
        
        #Grafica de la señal de audio
        self.axd["sig"].set_xlabel("Tiempo (s)")
        self.axd["sig"].set_xlim(0   , self.se_length)
        self.axd["sig"].set_ylim(1.1*min(self.se_signal), 1.1*max(self.se_signal))
        
        #Diccionario de curvas 
        self.pls = {
            "rec" : self.axd["mov"].plot([self.x],[self.y],"*r")[0],
            "emi" : self.axd["mov"].plot([self.x_an[0]],[self.y_an[0]],"*b")[0],
            "dis" : self.axd["dis"].plot([0],[0])[0],
            "sig" : self.axd["sig"].plot(self.sr_time, self.sr_signal)[0]
        }
        
        self.an = animation.FuncAnimation(self.fig, self.Animar_Grafica, frames = len(self.t_an), interval = self.f_an, blit = True)
        
        return None
    
    def Interactivar (self):
        """
        Metodo que configura la interactividad de la grafica.

        Returns
        -------
        None.

        """

        self.cid = self.fig.canvas.mpl_connect('button_press_event', self.Onclick)
        
        return None
    
    def Almacenar (self, nombre = None):
        """
        Metodo que permite almacenar el audio obtenido en un nuevo archivo.

        Parameters
        ----------
        nombre : TYPE, optional
            Nombre del archivo. The default is None.

        Returns
        -------
        None.

        """
        if type(nombre) is str:
            aux = nombre
        else:
            aux = self.n[:-4] + "_EfectoDopler_" + datetime.now().strftime('%Y-%m-%d_%H.%M.%S') + ".wav"
        
        self.Escribir_Archivo(aux, self.se_sample, self.sr_signal.astype(self.se_type))
        
        return None
    
    def Animar_Grafica(self, i):
        """
        Metodo generador de la animacion de la grafica.
        Si bien el punto que representa la ubicacion del receptor no cambia,
        debemos enviar su valor si queremos utilizar la opcion blit = True.

        Parameters
        ----------
        i : int
            Secuencia de la animacion.

        Returns
        -------
        matplotlib.lines.Line2D
            Curva que grafica la posicion del emisor.
        matplotlib.lines.Line2D
            Curva que grafica la posicion del receptor.
        matplotlib.lines.Line2D
            Curva que grafica la distancia entre emisor y receptor.

        """
        
        self.pls["emi"].set_data(self.x_an[i], self.y_an[i])
        self.pls["dis"].set_data(self.t_an[:i],self.d_an[:i])

        return self.pls["emi"], self.pls["rec"], self.pls["dis"]

    def Onclick(self, event):
        """
        Metodo que actualiza los parametros durante el evento click.

        Parameters
        ----------
        event : matplotlib.backend_bases.MouseEvent
            Evento generado por el mouse al hacer click.

        Returns
        -------
        None.

        """
        
        if event.inaxes is self.axd["mov"]:
        
            #Detiene y reinicia la animacion
            self.an.event_source.stop()
            self.an.frame_seq = self.an.new_frame_seq() 
        
            #Determina ubicacion del click
            ix, iy = event.xdata, event.ydata
        
            #Calcula la señal de audio en el receptor
            aux_vel                      = self.Velocidad_Relativa (self.se_time, self.r, self.w, ix, iy)
            aux_time                     = self.Variacion_Temporal (aux_vel, self.s, self.se_sample)
            self.sr_time, self.sr_signal = self.Interpolacion (self.se_signal, self.se_sample, aux_time)
        
            #Grafica la posicion del receptor
            self.pls["rec"].set_data([ix],[iy])
        
            #Grafica la nueva señal
            self.pls["sig"].set_data(self.sr_time,self.sr_signal)
            
            #Calcula las nuevas distancias
            self.d_an = ( (ix - self.x_an)**2 + (iy - self.y_an)**2 )**0.5
            self.axd["dis"].set_ylim(0.9*min(self.d_an), 1.1*max(self.d_an))
            
            #Reinicia la animacion
            self.an.event_source.start()
        
            #Redibuja las graficas
            self.fig.figure.canvas.draw()
            
        return None
    
    @staticmethod
    def Leer_Archivo (nombre):
        """
        Metodo estatico que permite leer el archivo de audio especificado.

        Parameters
        ----------
        nombre : str
            Archivo de audio a leer.

        Returns
        -------
        sample : int
            Frecuentia de muestreo.
        signal : numpy array
            Señal de audio contenida en el archivo.
        stype : numpy dtype
            Formato de la se;al de audio.

        """
        
        try:
            sample, signal = wavfile.read(nombre)
        except IOError:
            print("Error al leer el archivo de audio especificado.")
            exit(1)
            
        stype = signal.dtype
        if type(signal[0]) is np.ndarray:
            signal = signal.mean(axis=1)
            
        return sample, signal, stype
    
    @staticmethod
    def Escribir_Archivo (nombre, sample, signal):
        """
        Metodo estatico que permite escribir el archivo de audio especificado.

        Parameters
        ----------
        nombre : str
            Nombre del nuevo archivo de audio.
        sample : int
            Frecuencia de muestreo del audio.
        signal : numpy array
            Señal de audio a almacenar.

        Returns
        -------
        None.

        """
        
        try:
            wavfile.write(nombre, sample, signal)
        except IOError:
            print("Error al escribir el archivo de audio especificado.")
        
        return None
    
    @staticmethod
    def Velocidad_Relativa (t, r, w, x, y):
        """
        Metodo estatico que determina la velocidad relativa entre el emisor y el receptor
        para cada uno de los instantes de tiempo especificados por el array t.

        Parameters
        ----------
        t : numpy array
            Array de tiempos.
        r : float
            Radio de la circunferencia.
        w : float
            Velocidad angular del emisor.
        x : float
            Posicion en el eje x del receptor.
        y : float
            Posicion en el eje y del receptor.

        Returns
        -------
        v : numpy array or float
            Velocidad en los instantes t.

        """
        #Calculo de divisores
        num = r*w*(x*np.sin(t*w)-y*np.cos(t*w))
        den = ( (x-r*np.cos(w*t))**2 + (y-r*np.sin(w*t))**2 )**0.5
        
        #Division condicionada por el deneminador
        v   = np.divide(num, den, out=np.full( len(num), np.nan ), where=( den!=0 ) )
        
        #Retorna el siguiente valor cuando el denominador era cero
        return np.where(np.isnan(v), np.roll(v,-1), v)
    
    @staticmethod
    def Variacion_Temporal (v, s, samplerate):
        """
        Metodo estatico que determina un vector de tiempos modificado debido
        al efecto doppler.

        Parameters
        ----------
        v : numpy array
            Vector de velocidades en funcion del tiempo original de muestreo.
        s : float
            Velocidad del sonido en aire.
        samplerate : int
            Frecuencia de muestreo de la señal original.

        Returns
        -------
        tr : numpy array
            Vector de tiempos modificados.

        """
        
        #Vector de periodos de muestreo
        tr = (1 + v/s)/samplerate

        #Retorna el vector de tiempos de muestreo
        return tr.cumsum() - tr[0]
    
    @staticmethod
    def Interpolacion (e_sig, e_sample, r_time):
        """
        Metodo estatico que calcula mediante interpolacion la señal de audio
        escuchada por el receptor debida al efecto doppler.

        Parameters
        ----------
        e_sig : numpy array
            Señal original emitida.
        e_sample : int
            Frecuencia de muestreo de la señal orginal.
        r_time : numpy array
            Vector de tiempos del receptor.

        Returns
        -------
        n_time : numpy array
            Vector de tiempos generado cuando el receptor resamplea la señal.
        r_sig : numpy array
            Señal modificada por el efecto doppler.

        """
        
        #Funcion de interpolacion
        inter  = interp1d(r_time, e_sig, kind='cubic')

        #Vector de tiempos en el receptor al tener en cuenta al sample original
        n_time = np.arange(0,r_time[-1],1/e_sample)

        #Señal muestreada en los tiempos correctos
        r_sig  = inter(n_time)
        
        return n_time, r_sig

    def __str__ (self):
        return "EfectoDoppler:\n"\
        "- archivo de audio = {:}\n"\
        "- radio de la circunferencia = {:}\n"\
        "- velocidad tangencial del tren = {:}\n"\
        "- velocidad del sonido = {:}\n"\
        "- posicion en x del receptor = {:}\n"\
        "- posicion en y del receptor = {:}"\
        .format(self.n, self.r, self.v, self.s, self.x, self.y)

    def __repr__(self):
        return self.__str__()
    
# In[2]: Desarrollo del programa solicitado

#Creacion del objeto
ED = EfectoDoppler(args.n, args.r, args.v, args.x, args.y, 343.0)

#Verificacion de los parametros
print(ED)

#Inicializar las graficas
ED.Graficar()

#Agregar Interactividad en caso este especificada por linea de comando
if args.i:
    ED.Interactivar()

#Caso contrario, almacenar los resultados en un nuevo archivo de audio
else:
    ED.Almacenar(args.g)

plt.show()
exit()