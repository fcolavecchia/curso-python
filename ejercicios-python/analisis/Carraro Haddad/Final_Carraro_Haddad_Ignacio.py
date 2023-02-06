#!/usr/bin/env python
# coding: utf-8

# In[82]:


import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Cursor
from scipy import stats
import argparse



# In[74]:

#Pasamos los argumentos por consola
parser = argparse.ArgumentParser()

parser.add_argument("-f", "--filename", type=str, required = True) #Nombre del archivo
parser.add_argument("-t", "--todos", action='store_true') #Opción para graficar todos los datos
parser.add_argument("-z", "--corte",nargs = '+', type=float) #Para realizar los cortes deseados
parser.add_argument("-i", "--interactivo",action='store_true')#Opción para hacer el gráfico interactivo
parser.add_argument("-r", "--transform", action='store_true')#Opción para rotar el eje principal y hacerlo horizontal

#Cambiamos nombres
args = parser.parse_args()
fname = args.filename
all_ = args.todos
zo = args.corte
interactive = args.interactivo
rotate = args.transform


# # 1.

# In[77]:

#importamos los datos 
data = np.loadtxt(fname+'.dat.gz')
x = data[:,0]
y = data[:,1]
z = data[:,2]


# In[78]:


def rot(x_,y_,xo,yo,theta): 
    
    """Función que rota los datos x_,y_ en el plano x-y en un ángulo theta y centrado en (xo,yo), además traslada el centro al origen"""
    #Ponemos los datos en una grilla 2D
    data_c = np.zeros((x_.shape[0],2)) 
    data_c[:,0] = x_-xo #Trasladamos al origen
    data_c[:,1] = y_-yo
    #Lo rotamos con la matriz rotación
    data_c = data_c.dot(np.array([[np.cos(theta), -np.sin(theta)],
                                  [np.sin(theta), np.cos(theta)]])) 
    #Volvemos a separar la data en columnas
    xr = data_c[:,0]
    yr = data_c[:,1]
    return xr,yr

def all_data(rotate): 
    """
    Función que ajusta el eje principal de todos los datos con cuadrados mínimos y orienta (rotate == True), o no (rotate == False), dicho eje horizontalmente con su centro en el origen. Retorna los datos rotados (o no) x_, y_, su centro xo,yo y la pendiente (slope) y ordenada (inter) del ajuste del eje
    """
    x_,y_ = x,y
    #Calculamos el centro de los datos en x-y
    xo = np.mean(x_)
    yo = np.mean(y_)
    #ajustamos el eje
    lr = stats.linregress(x_, y_)
    slope, inter = lr[0], lr[1]

    theta = np.arctan(slope) #ángulo horizontal del ajuste

    if rotate:#Aplicamos la rotación hasta que el eje principal quede horizontal

        for i in range(100): #iteramos la rotación, rotando en el ángulo del ajuste de la recta
            x_,y_ = rot(x_,y_,xo,yo,theta)
            
            xo,yo = 0.,0. 

            lr = stats.linregress(x_, y_)
            slope, inter = lr[0], lr[1]
            theta = np.arctan(slope)
            if(np.abs(theta)<0.0001): return x_,y_,xo,yo,slope,inter
            
    return x_,y_,xo,yo,slope,inter


def cut_zo(zp, rotate): 
    """
    Función que ajusta el eje principal de los datos x-y en el intervalo [zp-0.5, zp+0.5] con cuadrados mínimos y orienta (rotate == True), o no (rotate == False), dicho eje horizontalmente con su centro en el origen. Retorna los datos rotados (o no) x_, y_, su centro xo,yo y la pendiente (slope) y ordenada (inter) del ajuste del eje
    """
    
    xc = x[(z<=(zp+0.5)) * (z>=(zp-0.5))] #Se fija en los datos x que están en el intervalo
    yc = y[(z<=(zp+0.5)) * (z>=(zp-0.5))] #Se fija en los datos y que están en el intervalo


    xo = np.mean(xc) #Sacamos el centro de los datos
    yo = np.mean(yc)

    lr = stats.linregress(xc, yc) #Ajustamos el eje
    slope, inter = lr[0], lr[1]

    theta = np.arctan(slope)

    if rotate:
        for i in range(100): #mismo protocolo que en all_data
            xc,yc = rot(xc,yc,xo,yo,theta)

            xo,yo = 0.,0.

            lr = stats.linregress(xc, yc)
            slope, inter = lr[0], lr[1]
            theta = np.arctan(slope)
            if(np.abs(theta)<0.0001): return xc,yc,xo,yo,slope,inter
            
    return xc,yc,xo,yo,slope,inter


# # 2.

# In[96]:


if all_: #En caso de graficar todos los datos
    x_,y_,xo,yo,slope,inter = all_data(rotate) #Extraemos los datos

    #Graficamos los datos y los histogramas
    fig, ax = plt.subplots(2, 2, gridspec_kw={'width_ratios': [3, 1], 'height_ratios':[1,3]}, figsize=(10,10))
    fig.subplots_adjust(hspace=0.02, wspace = 0.02)

    ax[1,0].hist2d(x_, y_, bins=100) #Graficamos los histogramas en 2D
#     xl = np.linspace(-25,25,1000)
#     ax[1,0].plot(xl, inter+xl*slope, 'r--')
#     ax[1,0].scatter(xo, yo, color = 'red')
    ax[1,0].set_xlabel("$x$")
    ax[1,0].set_ylabel("$y$")
    #Graficamos los histogramas para los datos x e y por separado
    ax[0,0].hist(x_, bins = 100, density = True) 
    ax[1,1].hist(y_, bins = 100,orientation='horizontal', density = True)
    #Algunos detalles de la gráfica
    ax[0,0].spines['top'].set_visible(False)
    ax[0,0].spines['right'].set_visible(False)
    ax[0,0].spines['bottom'].set_visible(False)
    ax[0,0].spines['left'].set_visible(False)
    ax[0,0].get_xaxis().set_ticks([])
    ax[0,0].get_yaxis().set_ticks([])
    ax[1,1].spines['top'].set_visible(False)
    ax[1,1].spines['right'].set_visible(False)
    ax[1,1].spines['bottom'].set_visible(False)
    ax[1,1].spines['left'].set_visible(False)
    ax[1,1].get_xaxis().set_ticks([])
    ax[1,1].get_yaxis().set_ticks([])
    ax[0,1].spines['top'].set_visible(False)
    ax[0,1].spines['right'].set_visible(False)
    ax[0,1].spines['bottom'].set_visible(False)
    ax[0,1].spines['left'].set_visible(False)
    ax[0,1].get_xaxis().set_ticks([])
    ax[0,1].get_yaxis().set_ticks([])
    ax[0,0].set_xlim(ax[1,0].get_xlim())
    ax[1,1].set_ylim(ax[1,0].get_ylim())
    ax[0,0].set_title('Todos los datos en el plano x-y', loc = 'center')


# # 3.

# In[94]:


if zo != None: #En caso de graficar cortes
    for zop in zo: #Iteramos en todos los cortes
        xc,yc,xo,yo,slope,inter = cut_zo(zop,rotate) #Extraemos el corte 
        #Graficamos similarmente al caso anterior

        fig, ax = plt.subplots(2, 2,gridspec_kw={'width_ratios': [3, 1], 'height_ratios':[1,3]})
        fig.subplots_adjust(hspace=0.02, wspace = 0.02)

        ax[1,0].hist2d(xc, yc, bins=100)
        #ax[1,0].scatter(xc, yc)
        ax[1,0].scatter(xo, yo, color = 'red', linewidth = 1)
        xl = np.linspace(-25.,25.,1000)
        ax[1,0].plot(xl, inter + slope*xl, 'r--')#Graficamos el ajuste del eje principal

        # ax[1,0].set_xlim(-25,25)
        # ax[1,0].set_ylim(-25,25)
        # ax[0,0].set_xlim(-25,25)
        # ax[1,1].set_ylim(-25,25)

        ax[1,0].set_xlabel("$x$")
        ax[1,0].set_ylabel("$y$")



        ax[0,0].hist(xc, bins = 100, density = True)
        ax[1,1].hist(yc, bins = 100,orientation='horizontal', density = True)
        ax[0,0].spines['top'].set_visible(False)
        ax[0,0].spines['right'].set_visible(False)
        ax[0,0].spines['bottom'].set_visible(False)
        ax[0,0].spines['left'].set_visible(False)
        ax[0,0].get_xaxis().set_ticks([])
        ax[0,0].get_yaxis().set_ticks([])
        ax[1,1].spines['top'].set_visible(False)
        ax[1,1].spines['right'].set_visible(False)
        ax[1,1].spines['bottom'].set_visible(False)
        ax[1,1].spines['left'].set_visible(False)
        ax[1,1].get_xaxis().set_ticks([])
        ax[1,1].get_yaxis().set_ticks([])
        ax[0,1].spines['top'].set_visible(False)
        ax[0,1].spines['right'].set_visible(False)
        ax[0,1].spines['bottom'].set_visible(False)
        ax[0,1].spines['left'].set_visible(False)
        ax[0,1].get_xaxis().set_ticks([])
        ax[0,1].get_yaxis().set_ticks([])
        ax[0,0].set_xlim(ax[1,0].get_xlim())
        ax[1,1].set_ylim(ax[1,0].get_ylim())
        plt.title("$z_o = $"+str(zop))


# # 5.

# In[68]:


if interactive: #En caso de hacer un gráfico interactivo
    T_o = []#Lista de ángulos a distintos cortes
    #Listas de valores medios xo y yo
    X_o = []
    Y_o = []

    Z = np.linspace(z.min(),z.max(),50) #Barrido sobre valores de z
    for zp in Z:
        #Valores de x,y que caen en el intervalor z+-0.5
        xc = x[(z<=(zp+0.5)) * (z>=(zp-0.5))]
        yc = y[(z<=(zp+0.5)) * (z>=(zp-0.5))]
        #Valores medios del centro
        xo = np.mean(xc)
        yo = np.mean(yc)
        #Ajuste lineal del eje principal
        lr = stats.linregress(xc, yc)
        slope, inter = lr[0], lr[1]

        T_o.append(np.arctan(slope))
        X_o.append(xo)
        Y_o.append(yo)

    #Graficamos
    fig = plt.figure(figsize=(10, 10))
    fig.subplots_adjust(hspace=0., wspace = 0.)
    gs = fig.add_gridspec(5, 5)#Armamos una grilla de grafs
    #Elejimos las proporciones deseadas de cada graf
    ax1 = fig.add_subplot(gs[1:3,0:2])
    ax2 = fig.add_subplot(gs[3:,0:2])
    ax3 = fig.add_subplot(gs[1:,2:4])
    ax4 = fig.add_subplot(gs[1:,4])
    ax5 = fig.add_subplot(gs[0,2:4])

    ax = [ax1, ax2, ax3, ax4, ax5]

    zp = 0.
    xl = np.linspace(-25.,25.,1000)#Rango del ajuste del eje
    xc,yc,xo,yo,slope,inter = cut_zo(zp,rotate) #grafico inicial
    #grafs de la izquierda
    ax[0].plot(Z,np.array(T_o)*180./np.pi,'k.-')
    ax[1].plot(Z,X_o, 'b.-', label = '$x_o$')
    ax[1].plot(Z,Y_o, 'g.-', label = '$y_o$')
    #grafico de x,y con su ajuste
    ax[2].hist2d(xc, yc, bins=100)
    ax[2].plot(xl, inter + slope*xl, 'r--')
    ax[2].scatter(xo, yo, color = 'red', linewidth = 1)
    #distribuciones en x e y por separado
    ax[3].hist(yc, bins = 100,orientation='horizontal', density = True)
    ax[4].hist(xc, bins = 100, density = True)

    #fijamos los rangos de ax3 y ax4 al de ax2
    ax[3].set_ylim(ax[2].get_ylim())
    ax[4].set_xlim(ax[2].get_xlim())
    ax[3].get_xaxis().set_ticks([])
    ax[4].get_xaxis().set_ticks([])
    ax[4].get_yaxis().set_ticks([])

    #Etiquetas de los axis
    ax[0].set_ylabel("ángulo (grados)")
    ax[1].set_xlabel("$z_o$")
    ax[1].set_ylabel("coord. centro")
    ax[3].text(1.1, .5, '$y$',ha='right', va='center',transform=ax[3].transAxes, rotation = 90.)

    #algunos detalles...
    ax[0].grid();ax[1].grid()
    ax[0].spines['bottom'].set_visible(False)
    ax[1].spines['right'].set_visible(False)

    def onclick(event):#Acción al hacer click
        zp = event.xdata #extraemos el z
        xc,yc,xo,yo,slope,inter = cut_zo(zp,rotate)
        #Actualizamos los grafs con cada click
        ax[2].cla()
        ax[3].cla()
        ax[4].cla()
        #Graficamos
        ax[2].hist2d(xc, yc, bins=100)
        ax[2].plot(xl, inter + slope*xl, 'r--')
        ax[2].scatter(xo, yo, color = 'red', linewidth = 1)
        ax[3].hist(yc, bins = 100,orientation='horizontal', density = True)
        ax[4].hist(xc, bins = 100, density = True)
        #Actualizamos los rangos de los histogramas, ticks (removidos) y textos
        ax[3].set_ylim(ax[2].get_ylim())
        ax[4].set_xlim(ax[2].get_xlim())
        ax[3].get_xaxis().set_ticks([])
        ax[4].get_xaxis().set_ticks([])
        ax[4].get_yaxis().set_ticks([])
        ax[3].text(1.1, .5, '$y$',ha='right', va='center',transform=ax[3].transAxes, rotation = 90.)
        ax[2].set_xlabel('$x$')

        #Actualizamos el indicador del zo seleccionado y su leyenda
        s0.set_offsets([Z[np.argmin(np.abs(Z-zp))],T_o[np.argmin(np.abs(Z-zp))]*180./np.pi])
        leg0.texts[0].set_text('$z_o = $ {:.1f}'.format(zp))
        s10.set_offsets([Z[np.argmin(np.abs(Z-zp))],X_o[np.argmin(np.abs(Z-zp))]])
        s11.set_offsets([Z[np.argmin(np.abs(Z-zp))],Y_o[np.argmin(np.abs(Z-zp))]])
        
        ax[2].figure.canvas.draw()
        ax[3].figure.canvas.draw()
        ax[4].figure.canvas.draw()
        s0.figure.canvas.draw()
        leg0.figure.canvas.draw()
        s10.figure.canvas.draw()
        s11.figure.canvas.draw()

    #Graficamos el indicador de zo y definimos sus propiedades
    s0 = ax[0].scatter(Z[np.argmin(np.abs(Z-zp))],T_o[np.argmin(np.abs(Z))]*180./np.pi, color = 'red', label='$z_o = $ {:.1f}'.format(zp))
    s10 = ax[1].scatter(Z[np.argmin(np.abs(Z-zp))],X_o[np.argmin(np.abs(Z))], color = 'red')
    s11 = ax[1].scatter(Z[np.argmin(np.abs(Z-zp))],Y_o[np.argmin(np.abs(Z))], color = 'red')
    leg0 = ax[0].legend(loc = 'upper left')
    ax[1].legend()

    #Quitamos marcos de los histogramas
    ax[3].spines['top'].set_visible(False)
    ax[3].spines['right'].set_visible(False)
    ax[3].spines['bottom'].set_visible(False)
    ax[3].spines['left'].set_visible(False)

    ax[4].spines['top'].set_visible(False)
    ax[4].spines['right'].set_visible(False)
    ax[4].spines['bottom'].set_visible(False)
    ax[4].spines['left'].set_visible(False)

    #Metemos los ticks dentro del graf
    ax[0].tick_params(axis='both', which='major')
    ax[0].tick_params(which = 'both',bottom=True, top=True, left=True, right=True)
    ax[0].tick_params(direction='in', length=6, width=1, color='k')

    ax[1].tick_params(axis='both', which='major')
    ax[1].tick_params(which = 'both',bottom=True, top=True, left=True, right=True)
    ax[2].tick_params(direction='in', length=6, width=1, color='k')

    ax[2].tick_params(axis='both', which='major')
    ax[2].tick_params(which = 'both',bottom=True, top=True, left=True, right=True, labelleft=False) #Quitamos los ticks labels que interfieren
    ax[2].tick_params(direction='in', length=6, width=1, color='w', labelcolor = 'k')
    ax[2].set_xlabel('$x$')

    ax[3].tick_params(color='w', labelcolor = 'w')#Usamos los ticks del histograma derecho

    #Definimos los cursores en los grafs de la izquierda
    cursor0 = Cursor(ax[0], useblit=True, color='red', linewidth=2)
    cursor1 = Cursor(ax[1], useblit=True, color='red', linewidth=2)

    cid = fig.canvas.mpl_connect('button_press_event', onclick)# se vincula la función onclick con el click


plt.show()

# In[ ]:




