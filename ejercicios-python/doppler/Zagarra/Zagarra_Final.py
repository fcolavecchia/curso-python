import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.widgets import Button
import argparse as ap
from scipy.io import wavfile
import simpleaudio as sa #Es posible que no tenga esta librería instalada, se necesita para reproducir audio interactivamente,
# si la instala es probable que tenga que reiniciar la compu para que ande bien. Yo tuve que reiniciarla.


parser = ap.ArgumentParser(
    description="Efecto Doppler: Transforma un archivo de audio .wav en otro utilizando el efecto doppler"
)
parser.add_argument(
    "-i", "--input", type=str, help="Nombre del archivo de entrada", default=""
)
parser.add_argument(
    "-o", "--output", type=str, help="Nombre del archivo de salida", default="Doppler",
)
parser.add_argument(
    "-c", "--c", type=float, help="Velocidad del sonido (m/s)", default=20
)
parser.add_argument(
    "-xr", "--xr", type=float, help="Posición del receptor en el eje x (m)", default=0
)
parser.add_argument(
    "-yr", "--yr", type=float, help="Posición del receptor en el eje y (m)", default=0
)
parser.add_argument(
    "--elipse", action="store_true", help="Usar elipse para la trayectoria del emisor"
)
parser.add_argument(
    "--recta", action="store_true", help="Usar recta para la trayectoria del emisor"
)

# Para hacer círculo
parser.add_argument(
    "-r", "--r", type=float, help="Radio del círculo para la trayectoria del emisor (m)", default=1,
)

# Para hacer elipse
parser.add_argument( 
    "-a", "--a", type=float, help="Eje x de la elipse para la trayectoria del emisor (m)", default=1,
)
parser.add_argument(
    "-b", "--b", type=float, help="Eje y de la elipse para la trayectoria del emisor (m)", default=1,
)

# Para hacer recta
parser.add_argument(
    "-xei", "--xei", type=float, help="Posición inicial del emisor en el eje x (m)", default=-1,
)
parser.add_argument(
    "-yei", "--yei", type=float, help="Posición inicial del emisor en el eje y (m)", default=1,
)
parser.add_argument(
    "-xef", "--xef", type=float, help="Posición final del emisor en el eje x (m)", default=1,
)
parser.add_argument(
    "-yef", "--yef", type=float, help="Posición final del emisor en el eje y (m)", default=1,
)
# Para hacerlo interactivo
parser.add_argument("--interactive", action="store_true", help="Modo interactivo")
parser.add_argument('--s', action='store_true', help='Guardar el archivo de salida') # Para guardar la animación en un archivo

args = parser.parse_args()

# Manejo de errores

try:
    fs, data = wavfile.read(args.input)
except:
    print("Error: No se pudo abrir el archivo de entrada")
    exit()
if args.elipse and args.recta:
    print("Error: No se puede usar ambas opciones: --elipse y --recta")
    exit()
if args.r <= 0 or args.a <= 0 or args.b <= 0:
    print("Error: Los valores de r, a, y b deben ser positivos")
    exit()

# Promedio si el archivo es stereo
if len(data.shape) > 1:
    data = data.mean(axis=1)

# Construyo la trayectoria del emisor solicitada
# Mapeo el tiempo del audio con el tiempo del recorrido completo del emisor,
# por ejemplo, el emisor da una vuelta completa al círculo en lo que dura el audio.
n = len(data)
T = n / fs
if args.elipse:
    phi = np.linspace(0, 2 * np.pi, n)
    x = args.a * np.cos(phi)
    y = args.b * np.sin(phi)
elif args.recta:
    x = np.linspace(args.xei, args.xef, n)
    y = np.linspace(args.yei, args.yef, n)
else:
    phi = np.linspace(0, 2 * np.pi, n)
    x = args.r * np.cos(phi)
    y = args.r * np.sin(phi)

# Genero el audio con Doppler
d = np.sqrt((x - args.xr) ** 2 + (y - args.yr) ** 2)
t = np.linspace(0, T, n) # Tiempo del audio
t_d = t + d / args.c # Tiempo del audio con el efecto doppler
t_d = t_d - t_d.min() # Normalizo el tiempo
# Ordeno los datos por tiempo de llegada al receptor, esto es para considerar velocidades del emisor mayor a la del sonido
data_d = data[np.argsort(t_d)] 
t_d = np.sort(t_d)
# Interpolo los datos para que coincidan con el tiempo del audio
data_d = np.interp(t, t_d, data_d).astype(np.int16) 

if args.interactive:
    fig = plt.figure(figsize=(10, 10))
    gs = fig.add_gridspec(2, 4)
    ax1 = fig.add_subplot(gs[:, 0:2]) # Recorrido del emisor y posición del recptor
    ax2 = fig.add_subplot(gs[0, 2:]) # Distancias entre el emisor y el receptor en función del tiempo
    ax3 = fig.add_subplot(gs[1, 2:]) # Audio en función del tiempo
    ax1.set_xlabel("x (m)")
    ax1.set_ylabel("y (m)")
    ax2.set_title("Distancia entre emisor y receptor")
    ax2.set_xlabel("Tiempo (s)")
    ax2.set_ylabel("Distancia (m)")
    ax3.set_title("Audio con Efecto Doppler")
    ax3.set_xlabel("Tiempo (s)")
    ax3.set_ylabel("Amplitud")
    
    emisor, = ax1.plot([], [],'o', color="red", label="Emisor")
    receptor, = ax1.plot(args.xr,args.yr,'D' , color="green", label="Receptor")
    distancia, = ax2.plot([], [], color="black")
    ax2.set_ylim(0, d.max()*1.1)
    ax2.set_xlim(t.min(), t.max())
    audio, = ax3.plot(t, data_d, color="blue")
    ax3.set_xlim(t.min(), t.max())

    if args.elipse:
        if args.a==args.b:
            ax1.set_title("Emisor en Círculo")
        else:
            ax1.set_title("Emisor en Elipse")
        ax1.set_aspect('equal')
        ax1.set_xlim(-args.a*1.2 , args.a * 1.2)
        ax1.set_ylim(-args.b*1.2 , args.b * 1.2)
        x1,y1 = args.a*1.1*np.cos(phi), args.b*1.1*np.sin(phi)
        x2,y2 = args.a*0.9*np.cos(phi), args.b*0.9*np.sin(phi)
        calle1, = ax1.plot(x1,y1, color="black")
        calle2, = ax1.plot(x2,y2, color="black")
    elif args.recta:
        ax1.set_title("Emisor en Recta")
        miny = min(args.yei, args.yef,args.yr)
        maxy = max(args.yei, args.yef,args.yr)
        minx = min(args.xei, args.xef,args.xr)
        maxx = max(args.xei, args.xef,args.xr)
        dy = maxy - miny
        dx = maxx - minx
        ax1.set_ylim(miny - dy*.2 , maxy + dy*.2)
        ax1.set_xlim(minx - dx*.2 , maxx + dx*.2)
        calle1, = ax1.plot(x,y+.05, color="black")
        calle2, = ax1.plot(x,y-.05, color="black")
    else:
        ax1.set_title("Emisor en Círculo")
        ax1.set_aspect('equal')
        ax1.set_xlim(-args.r*1.2 , args.r*1.2)
        ax1.set_ylim(-args.r*1.2 , args.r*1.2)
        x1,y1 = args.r*1.1*np.cos(phi), args.r*1.1*np.sin(phi)
        x2,y2 = args.r*0.9*np.cos(phi), args.r*0.9*np.sin(phi)
        calle1, = ax1.plot(x1,y1, color="black")
        calle2, = ax1.plot(x2,y2, color="black")


    def click(event):
        if event.button == 1 and event.inaxes == ax1:
            xr = event.xdata
            yr = event.ydata
            global d
            global data_d

            # Genero el audio con doppler
            d = np.sqrt((x - xr) ** 2 + (y - yr) ** 2)
            t_d = t + d / args.c 
            t_d = t_d - t_d.min() 
            data_d = data[np.argsort(t_d)] 
            t_d = np.sort(t_d)
            data_d = np.interp(t, t_d, data_d).astype(np.int16)

            # Actualizo los datos
            ax2.set_ylim(0, d.max()*1.1)
            receptor.set_data(xr, yr)
            audio.set_ydata(data_d)
            audio.figure.canvas.draw()
    
    def play_audio(event):
        sa.play_buffer(data_d, 1, 2, fs)
    
    def update(i):
        emisor.set_data(x[i], y[i])
        distancia.set_data(t[:i], d[:i])        
        return emisor, distancia, receptor

    #play button
    plt.subplots_adjust(right=.9,hspace=.3,wspace=1) 
    play_ax = plt.axes([0.92, .25, 0.05, 0.075])
    play = Button(play_ax, 'Play')
    play.on_clicked(play_audio)
    
    fig.canvas.mpl_connect('button_press_event', click)
    frames = np.arange(0, n, int(.002*n))
    ani = animation.FuncAnimation(fig, update, frames=frames, interval=1, blit=True)
    plt.show()

    if args.s:
        ani.save('Doppler_animation.gif', writer='pillow')

else:
    wavfile.write(args.output+'.wav', fs, data_d)


