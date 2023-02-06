# -*- coding: utf-8 -*-
"""
Created on Wed Apr  6 10:38:04 2022

@author: Omar Lopez Cabrera
"""

import numpy as np
from distutils import util #para que el parse me tome tanto False o 0 como False y True o 1 como True
import argparse
import matplotlib.pyplot as plt
from matplotlib.widgets import Cursor

#funciones a utilizar# 
def cortes_z(x,y,z,z_cut):
    """
    Cortes de xy respecto a z (z0=−4.5,−3.5,…,4.5) con un ancho Δz=±0.5.
    Parametros:
        X=vector de datos en x
        Y= Vector de datos en y
        Z=Vector de datos en z
        z_cut= valor de corte
    Returno:
        xx=vector de valores de x dentro de corte
        yy=vector de valores de y dentro de corte
        zz=vector de valores de z dentro de corte
    """
    data = np.column_stack([x, y, z])
    data = data [ data[:,2]   <= (z_cut+0.5)]  # Me quedo con los puntos dentro del corte
    data = data [ (z_cut-0.5) <= data[:,2] ] 
    xx,yy,zz = (data[:,0], data[:,1], data[:,2])
    return xx,yy,zz


def xylimits(x,y):
    """
    valores maximos y minimos de x e y para realizar los graficos
    Parametros:
        X=vector de datos en x
        Y= Vector de datos en y
    Returno:
        inflimitx= limite inferior de x
        suplimitx= limite superior de x
        inflimity= limite inferior de y
        suplimity= limite superior de y
    """
    inflimitx = min(x)
    suplimitx = max(x)
    inflimity = min(y)
    suplimity = max(y)
    return(inflimitx,suplimitx,inflimity,suplimity)

 
def centro(x,y):
    """
    Calculo de las coordenadas del centro de la grafica
    Parametros:
        X=vector de datos en x
        Y= Vector de datos en y
    Returno:
       x0= valor del centro en x
       y0= valor del centro en y
    """
    x0=np.mean(x)
    y0=np.mean(y)
    return x0,y0

def recta_min(x,y):
    """
    Calculo de la recta de minima distancia a puntos
    Parametros:
      X=vector de datos en x
      Y= Vector de datos en y
    Returno:
      m= pendiente de la recta
      c= ordenada al origen
      angle= angulo de la recta
    """
    p = np.polyfit(x,y,1)
    m=p[0]
    c=p[1]
    angle=np.arctan(m)
    
    return(m,c,angle) # y= m*x + c 

def corregir_angle(x,y,angle):
    """
    Corrige el angulo llevandolo a un valor cercano a 0, rotanto toda la distribucion de puntos y centrandola
    Parametros:
      X=vector de datos en x
      Y= Vector de datos en y
      angle= angulo a corregir
    Returno:
      x=vector de valores de x con angulo y centro corregidos
      y=vector de valores de y con angulo y centro corregidos
    """
    x0,y0 = centro(x, y)
    x= x - x0
    y= y- y0
    while( abs(np.rad2deg(angle)) > 0.1 ):    #itero hasta tener una correcion suficiente del angulo, con una sola pasada aveces no basta
        if angle < 0:
            theta = np.deg2rad(360 + np.rad2deg(np.arctan(angle)))
        elif angle > 0:
            theta = np.arctan(angle)   
             
        x0,y0 = centro(x, y)
        x= x - x0
        y= y- y0
        x=  np.cos(theta)*x + np.sin(theta) *y  
        y= - np.sin(theta) *x + np.cos(theta)*y
        c,m,angle=recta_min(x,y)
     
    return(x,y)
 

#argumentos

parser = argparse.ArgumentParser(description='Analisis de datos')

parser.add_argument('-fn', '--filename', action='store',
                      default="medicion3D.dat.gz", type=str, dest=('filename'),
                      help = '-fn el nombre del archivo entre "" ')

parser.add_argument('-t', '--todos', action='store',
                      default=True, type=util.strtobool, dest=('todos'),
                      help = '-t para mostrar todos los puntos del plano x-y por ejemplo -t False, -t 0, -t True -t 1')

parser.add_argument('-z', '--corte', action='store',
                      default="-4.5 -4.0 -3.5 -3.0 -2.5 -2.0 -1.5 -1.0 -.5 0 .5 1.0 1.5 2.0 2.5 3.0 3.5 4.0 4.5",
                      help = '-z y agregar los valores entre ""  separados por espacio por ejemplo -z "1 2 3"',type=str, dest=('z0'))

parser.add_argument('-i', '--interactivo', action='store',
                      default=True, type=util.strtobool, dest=('interac'),
                      help = '- i para activar el grafico interactivo por ejemplo -i False, -i 0, -i True -i 1')

parser.add_argument('-r', '--transform', action='store',
                      default=True, type=util.strtobool, dest=('rot_angle'),
                      help = '-r para rotar el angulo que tiene la distribucion y centrar el centor en 0,0  por ejemplo -r False, -r 0, -r True -r 1')


#carga de parametros
args = parser.parse_args()
filename =  args.filename
todos=args.todos
z_aux=args.z0
z0 = [float(val) for val in z_aux.split(' ')]  #tomo los valores separados por espacio


interac=args.interac
rot_angle=args.rot_angle


#####Punto1-Se pide que el programa lea los datos desde el archivo comprimido original.
#Nombre del archivo a descomprimir
#el archivo debe estar en la misma carpeta que el programa

x,y,z=np.loadtxt(filename,unpack=True) 


#Defino los limites para el grafico
inflimitx,suplimitx,inflimity,suplimity=xylimits(x, y)
ancho_bin = 0.25
xlim=max(inflimitx,suplimitx)
ylim=max(inflimity,suplimity)
xbins=int((xlim*2/ancho_bin))
ybins=int((ylim*2/ancho_bin))
bins=max(xbins,ybins)

cant_cortes = len(z0)
angle_vec= np.zeros(cant_cortes)
x0_vec=np.zeros(cant_cortes)
y0_vec=np.zeros(cant_cortes)
#reviso si hay cortes a realizar
check_z =  not (z0 is None) #si z no esta vacio



################ Punto 2 Grafica de todos los datos, Plano X-Y 
#Figura 1: gráfico con histograma 2D, 1D en x e y

if (todos):

    fig1 = plt.figure(0,figsize=(10,10))
    #Formato gridspect
    gs1 = fig1.add_gridspec(4, 4,wspace=0.01, hspace=0.01) #una grilla de 4x4 y poco espacio entre graficos
    
    #Histograma 2D
    ax1 = fig1.add_subplot(gs1[1:3, 1:3])
    ax1.hist2d(x, y, bins=bins,range=([inflimitx,suplimitx],[inflimity,suplimity])) 
    #Histograma 1D en x
    ax_histx1 = fig1.add_subplot(gs1[0,1:3], sharex=ax1)
    ax_histx1.hist(x, bins=bins,color='blue')
    ax_histx1.axis('off')    
    #Histograma 1D en y
    ax_histy1 = fig1.add_subplot(gs1[1:3,3], sharey=ax1)
    ax_histy1.axis('off')  
    ax_histy1.hist(y, bins=bins, orientation='horizontal',color='blue')
    #Propiedades del plot del histograma 2D
    ax1.set_xlim(inflimitx,suplimitx)
    ax1.set_ylim(inflimity,suplimity)
    ax1.set_xlabel('Dirección x')
    ax1.set_ylabel('Dirección y')
    #Propiedades del plot del histograma 1D 
    ax_histx1.set_title('Todos los datos en plano x-y', loc='center')
    
################ Punto 4 Rotacion angulo ###############  
    
if(rot_angle):
    
    if((not check_z) ): #caso en donde no hay cortes solicitados se hace la tranformacion sobre el todo
        fig2 = plt.figure(figsize=(15,15))
        gs1 = fig2.add_gridspec(4, 17,wspace=0.01, hspace=0.01)
        #Histograma 2D sin rotacion
        
        inflimitx,suplimitx,inflimity,suplimity=xylimits(x, y)
        xlim=max(inflimitx,suplimitx)
        ylim=max(inflimity,suplimity)
        xbins=int((xlim*2/ancho_bin))
        ybins=int((ylim*2/ancho_bin))
        bins=max(xbins,ybins)
        
        
        ax2 = fig2.add_subplot(gs1[1:3, 3:8])
        ax2.hist2d(x, y, bins=bins,range=([inflimitx,suplimitx],[inflimity,suplimity])) 
        #caluclo la recta
        m,c,angle=recta_min(x, y)
        x0,y0=centro(x, y)
        ax2.scatter(x0,y0,color='red')
        ax2.plot(x,x*m + c, color='red',linestyle='--',dashes=(5, 6), linewidth=1)
        
        #Histograma 1D en x
        ax_histx1 = fig2.add_subplot(gs1[0,3:8], sharex=ax1)
        ax_histx1.hist(x, bins=bins,color='blue')
        ax_histx1.axis('off')    
        #Histograma 1D en y
        ax_histy1 = fig2.add_subplot(gs1[1:3,8], sharey=ax1)
        ax_histy1.axis('off')  
        ax_histy1.hist(y, bins=bins, orientation='horizontal',color='blue')
        #Propiedades del plot del histograma 2D
        ax2.set_xlim(inflimitx,suplimitx)
        ax2.set_ylim(inflimity,suplimity)
        ax2.set_xlabel('Dirección x')
        ax2.set_ylabel('Dirección y')
        #Propiedades del plot del histograma 1D 
        ax_histx1.set_title('Todos los datos sin rotacion,  angulo %(b)s°  ' % {'b': round(np.rad2deg(angle),3)}, loc='center') 
                      
        
        #Histograma 2D con rotacion 
        
        ax3 = fig2.add_subplot(gs1[1:3, 11:16])
        xx,yy=corregir_angle(x, y, angle)
        
        inflimitx,suplimitx,inflimity,suplimity=xylimits(xx,yy)
        xlim=max(inflimitx,suplimitx)
        ylim=max(inflimity,suplimity)
        xbins=int((xlim*2/ancho_bin))
        ybins=int((ylim*2/ancho_bin))
        bins=max(xbins,ybins)
        
        
        
        m,c,angle=recta_min(xx, yy)
        x0,y0=centro(xx, yy)
        
        ax3.hist2d(xx, yy, bins=bins,range=([inflimitx,suplimitx],[inflimity,suplimity])) 
        ax3.scatter(x0,y0,color='red')
        ax3.plot(xx,xx*m + c, color='red',linestyle='--',dashes=(5, 6), linewidth=1)
        
        
        #Histograma 1D en x
        ax_histx2 = fig2.add_subplot(gs1[0,11:16], sharex=ax1)
        ax_histx2.hist(xx, bins=bins,color='blue')
        ax_histx2.axis('off')    
        #Histograma 1D en y
        ax_histy2 = fig2.add_subplot(gs1[1:3,16], sharey=ax1)
        ax_histy2.axis('off')  
        ax_histy2.hist(yy, bins=bins, orientation='horizontal',color='blue')
        #Propiedades del plot del histograma 2D
        ax3.set_xlim(inflimitx,suplimitx)
        ax3.set_ylim(inflimity,suplimity)
        ax3.set_xlabel('Dirección x')
        ax3.set_ylabel('Dirección y')
        #Propiedades del plot del histograma 1D 
        ax_histx2.set_title('Todos los datos con rotacion,  angulo %(b)s°   ' % {'b': round(np.rad2deg(angle),3)}, loc='center')              
                      
    if(check_z):                 
         length = len(z0)
         for i in range(length):
             
             fig3 = plt.figure(figsize=(15,15))
             gs1 = fig3.add_gridspec(4, 17,wspace=0.01, hspace=0.01) #una grilla de 4x4 y poco espacio entre graficos
             #Histograma 2D sin rotacion
             xx,yy,zz=cortes_z(x,y,z,z0[i])
             x0,y0 = centro(xx,yy)
        
             inflimitx,suplimitx,inflimity,suplimity=xylimits(xx, yy)
             xlim=max(inflimitx,suplimitx)
             ylim=max(inflimity,suplimity)
             xbins=int((xlim*2/ancho_bin))
             ybins=int((ylim*2/ancho_bin))
             bins=max(xbins,ybins)
             
             
             ax2 = fig3.add_subplot(gs1[1:3, 3:8])
             ax2.hist2d(xx, yy, bins=bins,range=([inflimitx,suplimitx],[inflimity,suplimity])) 
             #caluclo la recta
             m,c,angle=recta_min(xx, yy)
             x0,y0=centro(xx, yy)
             ax2.scatter(x0,y0,color='red')
             ax2.plot(xx,xx*m + c, color='red',linestyle='--',dashes=(5, 6), linewidth=1)
             
             #Histograma 1D en x
             ax_histx1 = fig3.add_subplot(gs1[0,3:8], sharex=ax1)
             ax_histx1.hist(xx, bins=bins,color='blue')
             ax_histx1.axis('off')    
             #Histograma 1D en y
             ax_histy1 = fig3.add_subplot(gs1[1:3,8], sharey=ax1)
             ax_histy1.axis('off')  
             ax_histy1.hist(yy, bins=bins, orientation='horizontal',color='blue')
             #Propiedades del plot del histograma 2D
             ax2.set_xlim(inflimitx,suplimitx)
             ax2.set_ylim(inflimity,suplimity)
             ax2.set_xlabel('Dirección x')
             ax2.set_ylabel('Dirección y')
             #Propiedades del plot del histograma 1D 
             ax_histx1.set_title('Sin rotacion  Zo= %(n)s angulo %(b)s° ' % {'n': z0[i], 'b': round(np.rad2deg(angle),3)}, loc='center') 
                           
             
             #Histograma 2D con rotacion 
             
             ax3 = fig3.add_subplot(gs1[1:3, 11:16])
             xx2,yy2=corregir_angle(xx, yy, angle)
             
             inflimitx,suplimitx,inflimity,suplimity=xylimits(xx,yy)
             xlim=max(inflimitx,suplimitx)
             ylim=max(inflimity,suplimity)
             xbins=int((xlim*2/ancho_bin))
             ybins=int((ylim*2/ancho_bin))
             bins=max(xbins,ybins)
             
             
             
             m,c,angle=recta_min(xx2, yy2)
             x0,y0=centro(xx2, yy2)
             
             ax3.hist2d(xx2, yy2, bins=bins,range=([inflimitx,suplimitx],[inflimity,suplimity])) 
             ax3.scatter(x0,y0,color='red')
             ax3.plot(xx2,xx2*m + c, color='red',linestyle='--',dashes=(5, 6), linewidth=1)
             
             
             #Histograma 1D en x
             ax_histx2 = fig3.add_subplot(gs1[0,11:16], sharex=ax1)
             ax_histx2.hist(xx2, bins=bins,color='blue')
             ax_histx2.axis('off')    
             #Histograma 1D en y
             ax_histy2 = fig3.add_subplot(gs1[1:3,16], sharey=ax1)
             ax_histy2.axis('off')  
             ax_histy2.hist(yy2, bins=bins, orientation='horizontal',color='blue')
             #Propiedades del plot del histograma 2D
             ax3.set_xlim(inflimitx,suplimitx)
             ax3.set_ylim(inflimity,suplimity)
             ax3.set_xlabel('Dirección x')
             ax3.set_ylabel('Dirección y')
             #Propiedades del plot del histograma 1D 
             
             ax_histx2.set_title('Con rotacion  Zo= %(n)s angulo %(b)s° ' % {'n': z0[i], 'b': round(np.rad2deg(angle),3)}, loc='center') 

        
        
    
################ Punto 3 Cortes en z0  #################

if (check_z ):
    
    length = len(z0)
    for i in range(length):
            
        fig4 = plt.figure(figsize=(10,10))
        #Formato gridspect
        gs2 = fig4.add_gridspec(4, 4,wspace=0.01, hspace=0.01) #una grilla de 4x4 y poco espacio entre graficos
        
        #corte y centro
        
        xx,yy,zz=cortes_z(x,y,z,z0[i])
        x0,y0 = centro(xx,yy)
        x0_vec[i]=x0
        y0_vec[i]=y0
        #Defino los limites para el grafico
        inflimitx,suplimitx,inflimity,suplimity=xylimits(xx, yy)
        xlim=max(inflimitx,suplimitx)
        ylim=max(inflimity,suplimity)
        xbins=int((xlim*2/ancho_bin))
        ybins=int((ylim*2/ancho_bin))
        bins=max(xbins,ybins)
        
        #Histograma 2D
        ax2 = fig4.add_subplot(gs2[1:3, 1:3])
        ax2.hist2d(xx, yy, bins=bins,range=([inflimitx,suplimitx],[inflimity,suplimity])) 
        #Histograma 1D en x
        ax_histx2 = fig4.add_subplot(gs2[0,1:3], sharex=ax2)
        ax_histx2.hist(xx, bins=bins,color='blue')
        ax_histx2.axis('off')   
        #Histograma 1D en y
        ax_histy2 = fig4.add_subplot(gs2[1:3,3], sharey=ax2)
        ax_histy2.axis('off')  
        ax_histy2.hist(yy, bins=bins, orientation='horizontal',color='blue')
        #Propiedades del plot del histograma 2D
        ax2.set_xlim(inflimitx,suplimitx)
        ax2.set_ylim(inflimity,suplimity)
        ax2.set_xlabel('Dirección x')
        ax2.set_ylabel('Dirección y')    
        ax2.scatter(x0,y0,color='tab:red')
          
     
        m,c,angulo = recta_min(xx, yy) 
        angle_vec[i] = angulo
        ax_histx2.set_title('Corte para Zo= %(n)s angulo %(b)s° ' % {'n': z0[i], 'b': round(np.rad2deg(angulo),2)}, loc='center')   
        maximo_x=max(xx);
        minimo_x=min(xx)
        cant= len(xx)
        xx_new=np.linspace(minimo_x,maximo_x,cant)
        ax2.plot(xx_new,xx_new*m + c, color='red',linestyle='--',dashes=(5, 6), linewidth=1)
        
 ################ Punto 5 y 6 Interactivo    
        
def click(event):
    
    z0 = event.xdata
    z0c=z_interact[np.argmin(np.abs(z_interact-z0))] #z más cercano al punto marcado
    z0cidx=np.argmin(np.abs(z_interact-z0)) #índice del z más cercano al punto marcado      
    x3,y3,z3 = cortes_z(x, y, z, z_interact[z0cidx])
    
    inflimitx,suplimitx,inflimity,suplimity=xylimits(x3, y3)
    xlim=max(inflimitx,suplimitx)
    ylim=max(inflimity,suplimity)
    xbins=int((xlim*2/ancho_bin))
    ybins=int((ylim*2/ancho_bin))
    bins=max(xbins,ybins)
    
    ax3.cla() #limpio la figura
    ax3.hist2d(x3, y3, bins=bins,range=([inflimitx,suplimitx],[inflimity,suplimity])) 
    ax3.set_xlabel('Dirección x')
    #Histograma 1D en x
    ax_histx1.cla()#limpio la figura
    ax_histx1.hist(x3, bins=bins,color='blue')
    ax_histx1.axis('off')  
    #Histograma 1D en y
    ax_histy1.cla()#limpio la figura
    ax_histy1.hist(y3, bins=bins, orientation='horizontal',color='blue')
    ax_histy1.set_ylabel('Dirección y')
    ax_histy1.yaxis.set_label_position('right')  
    ax_histy1.grid(linestyle='--')
    ax_histy1.tick_params(axis="y", labelleft=False)
    ax_histy1.tick_params(axis="y", labelright=True)
  
    #Para graficar el punto del angulo
    ax_z0_angle.cla()
    ax_z0_angle.plot(z_interact,angle_vec2,color='blue')
    ax_z0_angle.scatter(z_interact,angle_vec2,s=10, color='blue',zorder=1)  
    ax_z0_angle.scatter(z0c,angle_vec2[z0cidx],s=50, color='green',label='Z0=%(n)s'% {'n': z_interact[z0cidx]},zorder=2)  
    ax_z0_angle.set_ylabel(' angulo(grados)')
    ax_z0_angle.grid(linestyle='--')
    ax_z0_angle.legend()
    # Para graficar el punto del centro
    ax_z0_centro.cla()
    ax_z0_centro.plot(z_interact,x0_vec2,color='red',label='X')
    ax_z0_centro.scatter(z_interact,x0_vec2,color='red',zorder=1,s=10)
    ax_z0_centro.scatter(z0c,x0_vec2[z0cidx],color='green',zorder=2,s=50)
    ax_z0_centro.plot(z_interact,y0_vec2,color='blue',label='Y')
    ax_z0_centro.scatter(z_interact,y0_vec2,color='blue',zorder=1,s=10)
    ax_z0_centro.scatter(z0c,y0_vec2[z0cidx],color='green',s=50,zorder=2)
    ax_z0_centro.grid(linestyle='--')
    ax_z0_centro.set_ylabel('coord. centro')
    plt.legend()
    

    #Agrego centro y recta al histo2d
    x0,y0=centro(x3, y3)
    ax3.scatter(x0,y0,color='tab:red')
  
    m,c,angulo = recta_min(x3, y3) 
    ax_histx1.set_title('Corte para Zo= %(n)s angulo %(b)s° ' % {'n': z_interact[z0cidx], 'b': round(np.rad2deg(angulo),2)}, loc='center')   
    ax3.plot(x3,x3*m + c, color='red',linestyle='--',dashes=(5, 6), linewidth=1)    

    print("se hizo click") #para verificar que funciona cada click
    #aveces tarda unos segundos en actulizar la grafica o hay que mover el mouse
    #posibles mejoras pre-cargar todos los cortes o usar las matrices mas chicas.
    
    return
  
        
        

if interac:
    #Todos los posibles cortes
    z_interact=[-4.5,-4,-3.5,-3,-2.5,-2,-1.5,-1,-0.5,0,0.5,1,1.5,2,2.5,3,3.5,4,4.5];
   
    length = len(z_interact)
    x0_vec2=np.zeros(length)
    y0_vec2=np.zeros(length)
    angle_vec2=np.zeros(length)
    for i in range(length): #obtengo los centros y angulos para el grafico
            
        #corte y centro
        
        xx2,yy2,zz2=cortes_z(x,y,z,z_interact[i])
        x0,y0 = centro(xx2,yy2)
        x0_vec2[i]=x0
        y0_vec2[i]=y0
        m,c,angulo = recta_min(xx2, yy2) 
        angle_vec2[i] = angulo
   
   
    #grafico inicial para corte en z0=0
    x3,y3,z3=cortes_z(x,y,z,0)
    
    inflimitx,suplimitx,inflimity,suplimity=xylimits(x3, y3)
    xlim=max(inflimitx,suplimitx)
    ylim=max(inflimity,suplimity)
    xbins=int((xlim*2/ancho_bin))
    ybins=int((ylim*2/ancho_bin))
    bins=max(xbins,ybins)
    
    
    fig5  = plt.figure(figsize=(15,20))
    #Formato gridspect
    gs3 = fig5.add_gridspec(6, 12,wspace=0.01, hspace=0.01) #una grilla de 4x6 y poco espacio entre graficos
    #Histograma 2D
    ax3 = fig5.add_subplot(gs3[1:5, 5:11])
    ax3.hist2d(x3, y3, bins=bins,range=([inflimitx,suplimitx],[inflimity,suplimity])) 
    ax3.set_xlabel('Dirección x')
    
    
    #Histograma 1D en x
    ax_histx1 = fig5.add_subplot(gs3[0,5:11], sharex=ax3)
    ax_histx1.hist(x3, bins=bins,color='blue')
    ax_histx1.axis('off')    
    ax_histx1.set_title('Corte Zo= %(n)s indice %(b)s  ' % {'n': z_interact[9], 'b': 9}, loc='center')
    #Histograma 1D en y
    ax_histy1 = fig5.add_subplot(gs3[1:5,11], sharey=ax3)
    #ax_histy1.axis('off')  
    ax_histy1.hist(y, bins=bins, orientation='horizontal',color='blue')
    ax_histy1.set_ylabel('Dirección y')
    ax_histy1.yaxis.set_label_position('right')  
    ax_histy1.grid(linestyle='--')
    ax_histy1.tick_params(axis="y", labelleft=False)
    ax_histy1.tick_params(axis="y", labelright=True)
    
    #Agrego centro y recta al histo2d
    x0,y0=centro(x3, y3)
    ax3.scatter(x0,y0,color='tab:red')
    
    
    m,c,angulo = recta_min(x3, y3) 
    ax_histx1.set_title('Corte para Zo= %(n)s angulo %(b)s° ' % {'n': z_interact[9], 'b': round(np.rad2deg(angulo),2)}, loc='center')   
    ax3.plot(x3,x3*m + c, color='red',linestyle='--',dashes=(5, 6), linewidth=1)
    
    #Grafico Corte vs angulo
    ax_z0_angle = fig5.add_subplot(gs3[1:3,0:4])
    ax_z0_angle.plot(z_interact,np.rad2deg(angle_vec2),color='blue')
    ax_z0_angle.scatter(z_interact,np.rad2deg(angle_vec2),s=10,color='blue',zorder=1)  
    ax_z0_angle.scatter(z_interact[9],np.rad2deg(angle_vec2[9]),s=50,label='Z0=%(n)s'% {'n': z_interact[9]},color='green',zorder=2)
    ax_z0_angle.set_ylabel(' angulo(grados)')
    ax_z0_angle.grid(linestyle='--')
    plt.legend()
    
    #Grafico corte vs centro en x e y
    ax_z0_centro = fig5.add_subplot(gs3[3:5,0:4],sharex=ax_z0_angle)
    ax_z0_centro.plot(z_interact,x0_vec2,color='red',label='X')
    ax_z0_centro.scatter(z_interact,x0_vec2,color='red',zorder=1,s=10)
    ax_z0_centro.scatter(z_interact[9],x0_vec2[9],color='green',zorder=2,s=50)
    ax_z0_centro.plot(z_interact,y0_vec2,color='blue',label='Y')
    ax_z0_centro.scatter(z_interact,y0_vec2,color='blue',zorder=1,s=10)
    ax_z0_centro.scatter(z_interact[9],y0_vec2[9],color='green',s=50,zorder=2)
    ax_z0_centro.grid(linestyle='--')
    ax_z0_centro.set_ylabel('coord. centro')
    plt.legend()
    ax_z0_angle.get_shared_x_axes().join(ax_z0_angle, ax_z0_centro)
    #Propiedades del plot del histograma 
    ax1.set_xlim(inflimitx,suplimitx)
    ax1.set_ylim(inflimity,suplimity)

    # Agrego el cursor y conecto la accion de presionar a la funcion click
    cursor1 = Cursor(ax_z0_angle, horizOn=True, vertOn=True, useblit=True,
                    color='g', linewidth=1)
    cursor2 = Cursor(ax_z0_centro, horizOn=True, vertOn=True, useblit=True,
                    color='g', linewidth=1)
    fig5.canvas.mpl_connect('button_press_event', click)  
    
plt.show() #para mostrar cuando se corra por consola



