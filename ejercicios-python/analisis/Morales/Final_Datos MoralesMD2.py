# -*- coding: utf-8 -*-
"""
El siguiente programa fue realizado por la alumna Morales María Dolores en el marco de 
examen final de la materia "Introducción al lenguaje Python para Ciencias e Ingenierías"
Seguidamente, se detalla la documentacion del programa realizado para la resolución 
del ejercicio titulado "Análisis de Datos" 
El script que se presenta a continuación permite analizar, procesar y graficar datos 
correspondientes a puntos del espacio tridimensional (coordenadas en x, y, z).
Los módulos empleados para su ejecución son argparse, numpy y matplotlib
Además, el mismo puede ser ejecutado por líneas de comandos reconociendo los parámetros:
'-n', '--nombre': ejecuta el nombre del archivo de datos
'-t', '--todos=': grafica el conjunto total de puntos
'-z', '--corte': grafica los cortes seleccionados considerando valores de z entre -4.5 y 4.5
'-i', '--interactivo': realiza un gráfico interactivo
'-r', '--transform': es independiente de los tres últimos y grafica los datos centrados y rotados respecto al original
"""

import argparse
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import MultiCursor


#Posibles valores de puntos que puede adquirir z0 expresados en una lista

z0s = np.arange(-4.5, 5.5, 1).tolist()

#Configuración del parser

parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)

#Argumentos aceptados: tipo y valores por defecto

parser.add_argument('-n', '--nombre',   type=str,   action="store",      dest='n', required=True,            help='Nombre de archivo')
parser.add_argument('-t', '--todos=',               action="store_true", dest='t',                           help='Trabajar con todos los puntos')
parser.add_argument('-z', '--corte',    type=float, action="store",      dest='z', default=0.5, choices=z0s, help='Cota')
parser.add_argument('-i', '--interactivo',          action="store_true", dest='i',                           help='Modo interactivo')
parser.add_argument('-r', '--transform',            action="store_true", dest='r',                           help='Activar la transformacion de ejes')

#Almacenamiento de los resultados

args = parser.parse_args()

#Lectura del archivo de datos

datos = np.loadtxt(args.n,dtype=np.float32).transpose()

#Definición de las funciones utilizadas

def Cortes (datos,z0):
    """
    La función "Cortes" realiza cortes al conjunto de datos basados en z teniendo en cuenta un ancho Δz=±0.5
    """
    S = np.logical_and((z0-0.5)<=datos[2], datos[2]<=(z0+0.5))
    return datos[:,S]

def Centroide (datos):
    """
    Mediante la función "Centroide" se obtiene el punto promedio del arreglo de puntos del plano x-y
    """
    return datos[0].mean(), datos[1].mean()

def Recta (datos):
    """
    La función "Recta" realiza una regresión lineal del tipo y = ax+b
    mediante una función polinómica de grado 1 y devuelve los valores de pendiente y ordenada al origen 
    """
    modelo = np.polyfit(datos[0], datos[1], 1)
    return (modelo[0], modelo[1]), np.arctan(modelo[0])

def Transformar(datos,x0,y0,angulo):
    """
    La función "Transformar" grafica los datos rotados respecto a los originales teniendo en cuenta
    que los nuevos puntos queden centrados en el origen y el eje principal (recta) se alinee con el horizontal
    """
    x = datos[0] - x0
    y = datos[1] - y0
    
    xp = x*np.cos(angulo) + y*np.sin(angulo)
    yp = -x*np.sin(angulo) + y*np.cos(angulo)
    
    return [xp,yp,datos[2]]

def Grafica_Histogramas(ax_hx, ax_hy, ax_h2, datos, recta = None, punto = None):
    """
    En esta función se definen las herramientas usadas para realizar
    una figura central que muestre el conjunto total de puntos (histograma 2D) y anexado a este, 
    otras dos figuras que muestren la distribución (histogramas XY) de puntos x e y respectivamente
    """
    #Datos a graficar
    X,Y = datos[0],datos[1]

    #Definición de los bins para los histogramas
    binwidth = 0.5
    xymax = max(np.max(np.abs(X)), np.max(np.abs(Y)))
    lim   = (int(xymax/binwidth) + 1) * binwidth
    bins  = np.arange(-lim, lim + binwidth, binwidth)

    #Borrado de las curvas actuales
    ax_hx.cla()
    ax_hy.cla()
    ax_h2.cla()

    #Curvas de los histogramas XY
    ax_hx.tick_params(axis="x", labelbottom=False)
    ax_hx.tick_params(axis="y", labelleft=False, labelright=True)
    ax_hy.tick_params(axis="y", labelleft=False, labelright=True)
    ax_hy.set_ylabel("Direccion Y")
    ax_hy.yaxis.set_label_position("right")
    ax_hy.grid(axis="y")
    ax_hx.hist(X, bins=bins)
    ax_hy.hist(Y, bins=bins, orientation='horizontal')

    #Figura central (histograma 2D)
    ax_h2.tick_params(axis="y", labelleft=False)
    ax_h2.set_xlabel("Direccion X")
    ax_h2.hist2d(X, Y, bins=bins, cmap="viridis")

    #Recta de la figura central
    if recta != None:
        x = np.linspace(-lim, lim, 1000)
        y = recta[0]*x + recta[1]
        ax_h2.plot(x,y, "r--")
    
    #Punto centroide de la Figura central
    if punto != None:
        ax_h2.plot(punto[0],punto[1], "r*")

def Grafica_NoInteractivo():
    """
    La presente función define la configuración de los histogramas descriptos en la función "Grafica_Histogramas",
    su distribución y tamaño
    """
    #Configuración de la figura final no interactiva
    fig = plt.figure(figsize=(8, 8))
    gs = fig.add_gridspec(2, 2,  width_ratios=(7, 2), height_ratios=(2, 7),
                          left=0.1, right=0.9, bottom=0.1, top=0.9,
                          wspace=0.05, hspace=0.05)

    #Definición de los ejes
    ax_h2 = fig.add_subplot(gs[1, 0])
    ax_hx = fig.add_subplot(gs[0, 0], sharex=ax_h2)
    ax_hy = fig.add_subplot(gs[1, 1], sharey=ax_h2)
    
    #Definición de diccionario con los ejes
    axs = {
        "histX"   : ax_hx,
        "histY"   : ax_hy,
        "hist2D"  : ax_h2
    }

    return fig, axs

def Grafica_Interactivo(angulos, posicionesX, posicionesY):
    """
    En esta función se define la configuración de los histogramas descriptos en la función "Grafica_Histogramas"
    junto con la de las figuras ángulo vs. zo y coord. centro vs. z0, su distribución y tamaño
    """
    #Configuración de la figura final interactiva
    fig = plt.figure(figsize=(12.5,10))
    gs = fig.add_gridspec(3, 3,  width_ratios=(5, 7, 2), height_ratios=(2, 3.5, 3.5),
                          left=0.1, right=0.9, bottom=0.1, top=0.9,
                          wspace=0.05, hspace=0.05)
    #Definición de los ejes
    ax_h2 = fig.add_subplot(gs[1:3, 1])
    ax_hx = fig.add_subplot(gs[0, 1],   sharex=ax_h2)
    ax_hy = fig.add_subplot(gs[1:3, 2], sharey=ax_h2)
    ax_an = fig.add_subplot(gs[1,0])
    ax_xy = fig.add_subplot(gs[2,0],    sharex=ax_an)
    
    #Definición de diccionario con los ejes
    axs = {
        "angulo"  : ax_an,
        "posicion": ax_xy,
        "histX"   : ax_hx,
        "histY"   : ax_hy,
        "hist2D"  : ax_h2
    }
    
    #Gráfica ángulo vs. z0
    ax_an.plot(angulos[0],angulos[1], label="Z0 = 0.5")
    ax_an.set_ylabel("angulo (grados)")
    ax_an.grid()
    ang = {
        "punto" : ax_an.plot([0.5],angulos[1][5], "*")[0],
        "label" : ax_an.legend()
    }

    #Gráfica coord. centro vs. z0
    ax_xy.plot(posicionesX[0],posicionesX[1], label="X")
    ax_xy.plot(posicionesY[0],posicionesY[1], label="Y")
    ax_xy.set_xlabel("Z0")
    ax_xy.set_ylabel("coord. centro")
    ax_xy.grid()
    ax_xy.legend()
    pos = {
    "puntox" : ax_xy.plot([0.5],posicionesX[1][5], "*")[0],
    "puntoy" : ax_xy.plot([0.5],posicionesY[1][5], "*")[0]
    }

    return fig, axs, ang, pos

def onclick(event, axs, ang, pos, datos_c, recta_t, angulos180, centrox, centroy):
    """
    La función "onclick" permite obtener una nueva gráfica tal como la descripta en "Grafica_Interactivo"
    dependiendo del z0 seleccionado con el mouse. 
    Se precargaron posibles valores de z0 del rango permitido. La función trabaja considerando el valor más cercano 
    entre el seleccionado manualmente y el precargado
    """
    if (event.inaxes is axs["angulo"]) or (event.inaxes is axs["posicion"]):
        #Posición en x del click
        x0 = event.xdata
        
        #Array auxiliar de valores posibles de z0
        a  = np.array(z0s)
        
        #Valor de z0 más cercano al z0 indicado por el usuario
        z0 = a.flat[np.abs(a - x0).argmin()]
        
        #Indice donde se encuentra el elemento z0 solicitado
        i  = z0s.index(z0)
        
        #Edición de curvas
        ang["label"].get_texts()[0].set_text("z0 = {:}".format(str(z0)))
        ang["punto"].set_data([z0],[angulos180[i]])
        pos["puntox"].set_data([z0],[centrox[i]])
        pos["puntoy"].set_data([z0],[centroy[i]])
        
        #Edición de ejes
        Grafica_Histogramas(axs["histX"], axs["histY"], axs["hist2D"], datos_c[i], recta_t[i], [centrox[i],centroy[i]])
        
        #Actualización de la imagen
        axs["angulo"].figure.canvas.draw()
        axs["posicion"].figure.canvas.draw()
        axs["histY"].figure.canvas.draw()
        axs["hist2D"].figure.canvas.draw()

#Funcionamiento del programa según los parámetros definidos

#Si la opción interactiva está indicada:
    
if args.i :
    
    #Procesamiento de datos
    #Lista de variables donde se almacenan los datos
    datos_c = [0] * len(z0s)
    recta_t = [0] * len(z0s)
    angulos = [0] * len(z0s)
    centrox = [0] * len(z0s)
    centroy = [0] * len(z0s)

    #Resultados encontrados para cada valor posible de z0
    for i, z in enumerate(z0s):
        datos_c[i] = Cortes(datos,z)
        centrox[i], centroy[i] = Centroide(datos_c[i])
        recta_t[i], angulos[i] = Recta(datos_c[i])

    #Si está indicada la opción de rotación:
    if args.r :
        for i, z in enumerate(z0s):
            datos_c[i] = Transformar(datos_c[i],centrox[i],centroy[i],angulos[i])
            centrox[i], centroy[i] = Centroide(datos_c[i])
            recta_t[i], angulos[i] = Recta(datos_c[i])
    
    #Gráfica
    #Angulos expresados en forma hexadecimales
    angulos180 = [ i * 180/np.pi for i in angulos]

    #Creación de la gráfica
    fig, axs, ang, pos = Grafica_Interactivo([z0s,angulos180], [z0s,centrox], [z0s,centroy])

    #Gráfica de los histogramas
    Grafica_Histogramas(axs["histX"], axs["histY"], axs["hist2D"], datos_c[5], recta_t[5], [centrox[5],centroy[5]])
    
    #Adición de interactividad
    multi = MultiCursor(fig.canvas, (axs["angulo"], axs["posicion"]), color='r', lw=1)
    fig.canvas.mpl_connect('button_press_event', lambda event: onclick(event, axs, ang, pos, datos_c, recta_t, angulos180, centrox, centroy))


#Si la opción "todos" está indicada:
    
elif args.t:
    
    #Procesamiento de datos
    centrox, centroy = Centroide(datos)
    recta_t, angulos = Recta(datos)
    
    if args.r :
        datos = Transformar(datos,centrox,centroy,angulos)
        centrox, centroy = Centroide(datos)
        recta_t, angulos = Recta(datos)
    
    #Gráfica
    fig, axs = Grafica_NoInteractivo()
    Grafica_Histogramas(axs["histX"], axs["histY"], axs["hist2D"], datos, recta_t, [[centrox],[centroy]])

#Si la opción "todos" no está indicada, tener en cuenta a z0

else:
    
    #Procesamiento de datos
    datos = Cortes(datos,args.z)
    centrox, centroy = Centroide(datos)
    recta_t, angulos = Recta(datos)
    
    if args.r :
        datos = Transformar(datos,centrox,centroy,angulos)
        centrox, centroy = Centroide(datos)
        recta_t, angulos = Recta(datos)
    
    #Gráfica
    fig, axs = Grafica_NoInteractivo()
    Grafica_Histogramas(axs["histX"], axs["histY"], axs["hist2D"], datos, recta_t, [[centrox],[centroy]])

plt.show()
