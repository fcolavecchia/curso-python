############################## PROBLEMA EFECTO DOPPLER: ##############################
import argparse
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import wave
import struct
import numpy as np
from matplotlib.gridspec import GridSpec # para crear una imagen tipo grilla configurable
from scipy import interpolate
import struct

#%matplotlib qt5
plt.ioff()

#def efecto_doppler(oname,R,vm,x0,y0,inter=0):
parser = argparse.ArgumentParser(description='"Programa para calcular el Efecto Doppler sobre un emisor de sonido en movimiento"')
parser.add_argument('-o', '--output', action='store', dest='oname',default='salida_doppler')
parser.add_argument('-i', '--input', action='store', dest='iname',default='data_train-whistle')
parser.add_argument('-R', '--radio_circ', action='store', dest='R', type=float, default=45)
parser.add_argument('-vm', '--velocidad', action='store', dest='vm', type=float, default=55)
parser.add_argument('-x0', '--coord_x_inic', action='store', dest='x0', type=float, default=0)
parser.add_argument('-y0', '--coord_y_inic', action='store', dest='y0', type=float, default=0)
parser.add_argument('-inter', '--interactivo', action='store_true', dest='int',default=None)
args = parser.parse_args()

iname=args.iname
oname=args.oname
R=args.R
vm=args.vm
x0=args.x0
y0=args.y0
inter=args.int    

'''
o: nombre del archivo de audio de salida *.wav (escriba el nombre sin la extension .wav. Ruta local por default )
i: nombre del archivo de audio de entrada *.wav (escriba el nombre sin la extension .wav, opcionalmente la ruta, ruta default: '../' carpeta actual)
R: radio de circunferencia trayectoria circular de la fuente de sonido
vm: velocidad de la fuente de sonido en km/h
x0: coordenada del observador eje x
y0: coordenada del observador eje y
inter: modo interactivo si se ingresa por teclado; modo No interactivo por defecto

'''
######################## Creacion de datos: ############################
# cargo el archivo *.wav y obtengo los parametros para procesar el audio
filepathin = "" 
#iname='cantoparadoppler'
infile = filepathin+iname+'.wav'
file=wave.open(infile,"rb") #"../EF_DOPPLER/data_train-whistle.wav"
params = file.getparams()
nchannels, sampwidth, framerate, nframes = params[:4]
time = np.arange(0,nframes)*(1.0 / framerate)
strData = file.readframes(nframes) # Leer audio, formato de cadena
#waveData = np.fromstring (strData, dtype = np.int16) #Convertir una cadena en int
#waveData = 20*np.log10(waveData) #* 1.0 / (max (abs (waveData))) # normalización de amplitud de onda
wavedatos = np.fromstring (strData, dtype = np.short) #Convertir una cadena en int
#wavedatos= wavedatos * 1.0 / (max (abs (wavedatos))) # normalización de amplitud de onda
if nchannels == 2:
    wavedatos.shape = -1,2
    # Transponer datos
    waveData = np.mean(wavedatos.T,axis=0)
else:
    waveData = np.fromstring (strData, dtype = np.int16) # Convertir una cadena en int

fs=framerate
file.close() # cierro el archivo 

## DATOS del movimiento de la fuente de sonido (MCU):
tsim=nframes/framerate #tiempo de simulacion en segundos
tpos=np.linspace(0,tsim,100) #tiempo de posiciones len(time)
v=vm/3.6 # [m/s]
omega=v/R # [rad/s]
tita=omega*tpos # [rad] SIST. INERCIAL
vs=1000/3.6 # [m/s] veloc. del sonido c.n.p.t
vx=v*np.sin(tita) # [m/s] SIST. INERCIAL
vy=v*np.cos(tita) # [m/s] SIST. INERCIAL

# calcul las coordenadas del movil en MCU:
x=R*np.cos(np.linspace(0,2*np.pi,100)) # [m] 
y=R*np.sin(np.linspace(0,2*np.pi,100)) # [m] 
# Coordenadas iniciales del observador:
Dx0=abs(x-x0)
Dy0=abs(y-y0)
# Modulo del vector posicion inicial del movil respecto del observador
Dr=np.sqrt(Dx0**2+Dy0**2) 
xmax = np.max(x)
# Numero de muestras de la animacion:
Npts= len(tpos) # esto me da la cantidad de cuadros que se van a animar: si Nptos=len(tpos) entonces se van a animar todos los puntos, si Nptos=1 entonces solo se va a animar el punto 0

# Defino si quiero una animacion del problema o solo una salida de audio:

if inter==True:
    # Creo la figura e inicializo
    # Fijo las condiciones de graficación
    fig = plt.figure(constrained_layout=True,figsize=(10,5))

    gs = GridSpec(2, 2, figure=fig) # creo una grilla de 2x2 imagenes y configuro para 3 imagenes
    ax1 = fig.add_subplot(gs[:, :-1]) # la 1er imagen ocupa los 2 cuadros de la izq
    ax2 = fig.add_subplot(gs[0, 1]) # la 2da imag. ocupa la pos sup der
    ax3 = fig.add_subplot(gs[1, 1]) # la 3ra imag. ocupa la pos inf der
    # Bach de datos iniciales para las graficas:
    data1 = np.vstack([x, y]) # fig animada izq, movil en MCU
    data2 = np.vstack([tpos, Dr]) # fig animada sup. der. dist. relat. movil/observador

    ############################################ FUNCIONES #############################################

    ## Funcion para animar la grafica de MCU del movil soble la via:
    def update_line1(num, data, line):
        line.set_data(data[:,num])
        return line


    ## Funcion para inicializar la curva de inensidad/tiempo del sonido 
    # en func. de la x0,y0 ingresada por el usario (grafica inf. der.)
    def init_wave(x0,y0):
        tita=omega*time # [rad] SIST. INERCIAL
        x=R*np.cos(tita) # [m] 
        y=R*np.sin(tita) # [m] 
        Dx=x-x0
        Dy=y-y0
        r=((abs(Dx)**2+abs(Dy)**2))**.5
        t_p=(r/vs) #distorsion de cada paso temporal creada por el movimiento del movil relativ al observador
        time_p=time[:]+t_p
        print(t_p)
        
        return time_p,waveData
    
    
    ## Funcion para actualizar la Grafica de Intensidad/tpos al hacer click en la nueva pos del observ.
    def actual_sonido(event):
        tita=omega*time # [rad] SIST. INERCIAL
        x=R*np.cos(tita) # [m] 
        y=R*np.sin(tita) # [m] 
        x0 = event.xdata
        y0 = event.ydata
        Dx=abs(x-x0)
        Dy=abs(y-y0)
        r=np.sqrt(Dx**2+Dy**2)
        t_p=(r/vs) #distorsion de cada paso temporal creada por el movimiento del movil relativ al observador
        time_p=time[:]+t_p
        ax3.set_xlim(min(time_p)*1, max(time_p)*1.1)
        L3.set_data([time_p, waveData[:]])
        #L3.figure.canvas.draw()

    # conecto el evento click con la funcion actual_sonido
    cid3=fig.canvas.mpl_connect('button_press_event', actual_sonido) 


    ## Funcion para graficar el pto. selecc. para la pos. del observador:
    def pos_observ(event):
        x0 = event.xdata
        y0 = event.ydata
        L1a.set_data([x0, y0])
        #L1a.figure.canvas.draw()
        
    # conecto la accion de presionar a la funcion pos_observ
    cid1=fig.canvas.mpl_connect('button_press_event', pos_observ)

    ## Funcion para animar la graf. de dist. relat. movil/observador (sup. der.)
    def actual_data(event):
        global Dr, data2 # declaro como globales las variables que se van a usar para actualizar graficas
        x0 = event.xdata
        y0 = event.ydata
        Dx=abs(x-x0)
        Dy=abs(y-y0)
        Dr=np.sqrt(Dx**2+Dy**2)
        
        data2 = np.vstack([tpos, Dr]) # fig animada sup. der. dist. relat. movil/observador
        ax2.set_ylim(min(Dr),max(Dr))
        
      

    # conecto la accion de presionar a la funcion actual_data
    cid=fig.canvas.mpl_connect('button_press_event', actual_data)

    ## Funcion generadora de datos para actualizar curva Dist. relat. vs tpo.:
    def gen_function():
        ''''if cid==0:
        pass #data=data20
        else:'''
        data=data2
        return Npts, data, L2
    
    ## Funcion para inicializar la curva de Dist. relat. vs tiempo (graf. superior derecha):  
    def init():
        ax2.set_xlim(0, max(tpos))
        ax2.set_ylim(min(Dr)*.95, max(Dr)*1.05)
        ax2.set_xlabel('tiempo [s]')
        ax2.set_ylabel('distancia [m]')
        ax2.set_title('Distancia relat. fuente-observador')

        L2, = ax2.plot([], [], '-k',lw=2) # curva de la distancia entre el punto de observacion y el punto representado en el movil (inicializacion)  return line,
        #L2.set_data(data20)
        #return L2

    ## Funcion para animar curva Dist. relat. vs tpo.:  
    def update_line2(num):
        L2.set_data(data2[:,0:num])
        return L2,


    ############################################ GRAFICAS: ########################################

    # Creo las lineas de las graficas y las inicializo:
    L1, = ax1.plot([], [], 'ok',lw=15) # pto representando el movil (tren) en su trayectoria, posicion inicial (SE actrualiza)
    L1a, = ax1.plot(x0,y0,'or',markersize=8) # pto de posicion del observador, posicion inicial (SE actrualiza)
    L1b, = ax1.plot(x*1.05, y*1.05, '-.b', lw=.5) # circulo externo trayectoria circular (NO se actualiza)
    L1c, = ax1.plot(x*.95, y*.95, '-.b', lw=.5)  # circulo interno trayectoria circular (NO se actualiza)
    L2, = ax2.plot([], [], '-k',lw=2) # curva de la distancia entre el punto de observacion y el punto representado en el movil (inicializacion)
    tiempo,intensidad=init_wave(x0,y0)
    L3, = ax3.plot(tiempo,intensidad,'--b') # grafico de la onda sonora (tiempo, intensidad señal)

    # Configuro los titulos y leyendas de las graficas:
    plt.xlabel("Tiempo [s]")
    plt.ylabel("Amplitud")
    plt.title("Amplitud señal audio")
    plt.grid ('encendido') # Escala, encendido: sí, apagado: no.
    file.rewind() # rewinds the file to the beginning (si no no se puede volver a cargar la grafica de onda sonora despues de la primera vez)

    # Configuro la grafica del movimiento de la fuente de sonido (grafica izquierda):
    ax1.set_xlim(min(x)*1.5, max(x)*1.5)
    #ax1.axis('off')
    ax1.set_ylim(min(y)*1.5, max(y)*1.5)
    ax1.set_ylabel('')
    ax1.set_xlabel('[m]')
    ax1.set_title('Animación trayectoria fuente sonido', loc='center')
    
    
    # Funciones de animacion de las graficas:
    line_ani1 = animation.FuncAnimation(fig, update_line1, Npts, fargs=(data1, L1),
                                        repeat=True, interval=0, blit=False)
    line_ani2 = animation.FuncAnimation(fig, update_line2, Npts,init_func=init, repeat=True, interval=0, blit=False) #fargs=(data2, L2), 
    fig.get_tight_layout() 

    plt.show()
    
# MODO NO INTERACTIVO (Solo grabacion de audio c/ efecto Doppler)
else:  
    tita=omega*time # [rad] SIST. INERCIAL
    x=R*np.cos(tita) # [m] 
    y=R*np.sin(tita) # [m] 
    Dx=abs(x-x0)
    Dy=abs(y-y0)
    r=np.sqrt(Dx**2+Dy**2)
    r -= r[0]
    t_p=(r/vs) #distorsion de cada paso temporal creada por el movimiento del movil relativ al observador
    time_p=time[:]+t_p # vector de tiempos distorsionado
       
    # Creo el polinomio interpolador:
    interp= interpolate.interp1d(time_p, waveData[:], kind=3,axis=0,fill_value='extrapolate') #(, )
    wave_dop = interp(time[:]) #[:-1] para que no se repita el ultimo valor
    plt.plot(time,wave_dop)
    filepathin = "../" #Añadir ruta EF_DOPPLER/
    outData = wave_dop #* 1.0 / (max (abs (wave_dop))) # = wavedatos * 1.0 / (max (abs (wavedatos)))Datos que se escribirán en wav, aquí todavía hay datos de waveData
    outfile = filepathin+oname+'.wav'
    outwave = wave.open (outfile, 'wb') # Defina la ruta de almacenamiento y el nombre del archivo
    nchannels 
    sampwidth 
    data_size = len(outData)
    framerate = int(fs)
    nframes = data_size
    comptype = "NONE"
    compname = "not compressed"
    
    outwave.setparams((nchannels, sampwidth, framerate, nframes,
        comptype, compname))
    
    try:
        for v in outData:
            outwave.writeframes (struct.pack ('<h', int (v ))) # * 64000/2 outData: 16 bits, -32767 ~ 32767, cuidado de no desbordar
    except:
        print('sale de rango')
        outData = wave_dop* 1.0 / (max (abs (wave_dop)))
        for v in outData:
            outwave.writeframes (struct.pack ('i', int (v )))
            outwave.close()
    
    outwave.close()



