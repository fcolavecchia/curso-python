import numpy as np 
import matplotlib.pyplot as plt
from matplotlib.widgets import Cursor 
from scipy import stats
import gzip 
import argparse

def gzip_to_lista(iname):
    '''Función que lee los datos comprimidos 
    y los devuelve en un array'''
    
    datos_comp = gzip.open(iname, mode='rt')   #mode para abrirlo en formato texto y no binario 
    datos_leidos = datos_comp.read()
    datos_comp.close()
    datos = datos_leidos.splitlines()
    lista = []
    for l in datos:
        lista.append(list(filter(None, l.split(' '))))
    return np.array(lista, dtype = np.float32)

def plot_datos(data, z=None, todos=None, ya=[]):
    ''' Función que grafica los datos. 
    
    -z: grafica los datos de los cortes indicados, su media y eje principal de distribución.
    
    -t: grafica todos los datos. '''

    fig = plt.figure(figsize=(10,10))
    gs = fig.add_gridspec(5, 5)

    ax1 = fig.add_subplot(gs[0, 0:4])     #distribucion en x arriba
    ax2 = fig.add_subplot(gs[1:, 4])      #distribucion en y derecha
    ax3 = fig.add_subplot(gs[1:, 0:4])     #histrograma 2D

    if todos!=None:
        fig.suptitle("Todos los datos en plano x-y", size=25)

    if z!=None:
        fig.suptitle("$Z_0 = $"+str(z), size=25)

    ax1.set_xticks([])
    ax1.set_yticks([])
    ax1.hist(data[:,0],bins=51)

    ax2.set_xticks([])
    ax2.set_yticks([])
    ax2.hist(data[:,1],bins=51, orientation="horizontal")

    ax3.hist2d(data[:,0],data[:,1].T, bins=101)
    ax3.set_xlabel("Dirección x", size=20)
    ax3.set_ylabel("Dirección y", size=20)
    if z!=None:
        ax3.scatter(data[:,0].mean(), data[:,1].mean(), color="orange", s=75)
        ax3.plot(data[:,0],ya, '--', color="orange", linewidth=2 , label = 'Eje principal de distribución'  )
        ax3.legend()
    return plt.show()

def rotacion(data):
    '''Función que rota los datos.'''
    result = stats.linregress(data[:,0],data[:,1])
    Xmean, Ymean = data[:,0].mean(), data[:,1].mean()
    data[:,0] = data[:,0]- Xmean
    data[:,1] = data[:,1]- Ymean
    ang = np.arctan(result.slope)
    x1 = data[:,0]
    y1 = data[:,1]
    def opt(x,y):
        x1 = x*np.cos(ang) + y * np.sin(ang) 
        y1 = -x*np.sin(ang) + y* np.cos(ang)  
        return x1,y1
    while(np.abs(ang)>0.001):
        x1, y1 = opt(x1,y1)
        result = stats.linregress(x1,y1)
        ang = np.arctan(result.slope)
    data[:,0] = x1
    data[:,1] = y1
    result = stats.linregress(data[:,0],data[:,1])
    return data

def recorta(data,z0):
    '''Función que recorta datos de a un z0 por vez.'''
    nuevos_datos = data[data[:,2]>z0-0.5]
    nuevos_datos = nuevos_datos[nuevos_datos[:,2]<z0+0.5]    
    return nuevos_datos

def angulos(data,z0):
    '''Función que devuelve el angulo corresponiente 
    al eje de distribución de los datos. 
    '''
    ang = []
    for i in z0:
        datos = recorta(data,i)
        result = stats.linregress(datos[:,0],datos[:,1])
        ang = ang + [np.rad2deg(np.arctan(result.slope))]
    return np.array(ang)

def XYmean(data,z0):
    '''Función que devuelve la media de la distribución de los datos. 
    '''
    X = []
    Y = []
    for i in z0:
        datos = recorta(data,i)
        X = X + [datos[:,0].mean()]
        Y = Y + [datos[:,1].mean()]
    return np.array(X), np.array(Y) 

def plot_interactivo(data, z=None, todos=None, ya=[]):
    ''' Función que grafica los datos. 
    
    -i: inicialmente grafica todos los datos.
    
    Si hace clic en alguna de las figuras de la izquierda puede obtener 
    la distribución de los cortes correspondientes a ese z seleccionado. '''

    def onclick(event):
        ''' Función que actualiza los datos cuando se hace un clic en ax4 o ax5. 
        '''
        print('En proceso...')
        z0 = event.xdata 
        if round(z0,0)>z0:
            z0 = round(z0,0) - 0.5
        else:
            z0 = round(z0,0) + 0.5
        x0, y0 = XYmean(data,np.array([z0]))
        ang = angulos(data, np.array([z0]))
        datos_recortados = recorta(data,z0)
        result = stats.linregress(datos_recortados[:,0],datos_recortados[:,1])
        ya = datos_recortados[:,0]*result.slope + result.intercept
        s1.set_data(np.array([z0,ang]))
        s2.set_data(np.array([z0,x0])) 
        s3.set_data(np.array([z0,y0])) 
        x0 = np.around(x0,2)
        y0 = np.around(y0,2)
        leg1.get_texts()[0].set_text(f'z = {z0}')
        leg2.get_texts()[0].set_text(f'x = {x0}')
        leg2.get_texts()[1].set_text(f'y = {y0}')
        ax3.cla()
        ax3.hist2d(datos_recortados[:,0],datos_recortados[:,1], bins=101)
        ax3.set_xlabel("Dirección x", size=20)
        ax3.plot(datos_recortados[:,0].mean(), datos_recortados[:,1].mean(),'o', color="orange", ms=12)
        ax3.plot(datos_recortados[:,0],ya, '--', color="orange", linewidth=2  )
        ax3.set_yticks([])
        print('Listo!')

    fig = plt.figure(figsize=(20,10))
    gs = fig.add_gridspec(7, 7)

    ax1 = fig.add_subplot(gs[0, 2:6])     #distribucion en x arriba
    ax2 = fig.add_subplot(gs[1:, 6])      #distribucion en y derecha
    ax3 = fig.add_subplot(gs[1:, 2:6])    #histrograma 2D
    ax4 = fig.add_subplot(gs[1:4, 0:2])    #angulos 
    ax5 = fig.add_subplot(gs[4:, 0:2])    #coordenada centro 

    fig.suptitle("Gráfico interactivo", size=25)

    for pos in ['right', 'top', 'bottom', 'left']:
        ax1.spines[pos].set_visible(False)
        ax2.spines[pos].set_visible(False)


    ax1.set_xticks([])
    ax1.set_yticks([])
    ax1.hist(data[:,0],bins=51)


    ax2.set_xticks([])
    #ax2.set_yticks([])
    ax2.hist(data[:,1],bins=51, orientation="horizontal",zorder=3)
    ax2.yaxis.set_label_position("right")
    ax2.yaxis.tick_right()
    ax2.set_ylabel("Dirección y", size=20)
    ax2.grid(zorder=0)

    #ax3.imshow(h)
    ax3.hist2d(data[:,0],data[:,1], bins=101)
    ax3.set_xlabel("Dirección x", size=20)
    ax3.plot(data[:,0].mean(), data[:,1].mean(),'o', color="orange", ms=12)
    ax3.plot(data[:,0],ya, '--', color="orange", linewidth=2 , label = 'Eje principal de distribución' )
    ax3.set_yticks([])
    ax3.legend()

    z0 = np.linspace(-4.5,4.5,10)

    ang = angulos(data,z0)

    s1, = ax4.plot([], [],'o', color='green', ms=12)
    ax4.plot(z0, ang,'-o' ,color="blue", label='z0 = todos')
    ax4.set_ylabel("ángulo (grados)")
    ax4.set_xticks([])
    ax4.grid()
    leg1 = ax4.legend(loc = 'best')
    cursor = Cursor(ax4, horizOn=False, vertOn=False, useblit=True)

    x0, y0 = XYmean(data,z0)
   
    s2, = ax5.plot([],[],'o', color="green", ms=12)
    s3, = ax5.plot([],[],'o', color="green", ms=12)   
    ax5.plot(z0,x0 ,'-o', label="x", color="red")
    ax5.plot(z0,y0 ,'-o', label="y", color="blue")
    ax5.set_ylabel("coord. centro")
    ax5.set_xlabel("$z_0$")
    ax5.grid()
    leg2 = ax5.legend(loc='best')
    cursor5 = Cursor(ax5, horizOn=False, vertOn=False, useblit=True)

    fig.canvas.mpl_connect('button_press_event', onclick)
    
    return plt.show()

parser = argparse.ArgumentParser(
    description='Argumentos para análisis de datos',
)
parser.add_argument('--input','-inp',dest='iname', action="store", default='medicion3D.dat.gz' , help='Nombre del archivo input .gz')
parser.add_argument('--todos=','-t',dest='todos', action="store_true", default=None, help='Graficar el conjunto total de puntos')
parser.add_argument('--corte','-z',dest='z',nargs='*', action="store", default=None, help='Valor de corte en z: [-4.5,...,4.5]')
parser.add_argument('--interactivo','-i',dest='interactivo', action="store_true", default=False , help='Gráfico interactivo')
parser.add_argument('--transform','-r',dest='r', action="store_true" ,default=None, help='Rotación y traslación de los datos')

args = parser.parse_args()
iname = args.iname
todos = args.todos
z = args.z
interactivo = args.interactivo
r = args.r

data = gzip_to_lista(iname)  #leo y organizo los datos

if todos!=None:
    if r!=None:
        datos = rotacion(data)
    grafico = plot_datos(datos, todos=todos)

if z!=None:
    z = [float(i) for i in z]
    nuevos_datos = {}
    for z0 in z:
        nuevos_datos[z0] = recorta(data,z0)
        if r!=None:
            nuevos_datos[z0] = rotacion(nuevos_datos[z0])
        result = stats.linregress(nuevos_datos[z0][:,0],nuevos_datos[z0][:,1])
        ya = nuevos_datos[z0][:,0]*result.slope + result.intercept
        grafico = plot_datos(nuevos_datos[z0],z0, ya=ya)

if interactivo != False:
    result = stats.linregress(data[:,0],data[:,1])
    ya = data[:,0]*result.slope + result.intercept
    grafico = plot_interactivo(data, ya=ya)