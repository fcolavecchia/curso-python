import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Cursor
import gzip
import math
import argparse
import sys
path=sys.path[0]
#Lectura de argumentos
parser = argparse.ArgumentParser(description='"Graficación de datos Este programa grafica un conjunto de datos x,y,z. El programa puede probarse con el archivo medicion3D.dat.gz"')
parser.add_argument('filename',action="store",type=str,help="Nombre del archivo ubicado en la carpeta del .py", default='')
parser.add_argument('-t', '--todos=', action="store_true", dest='todos',help="Muestra los histogramas de todos los valores",default=False)
parser.add_argument('-z', '--corte', action="store",nargs='+',type=float, dest='cortes',help="Valores de corte: muestra los histogramas entre corte+-0.5. Acepta los siguientes valores -4.5,-3.5,...,3.5,4.5. Acepta multiples valores",default=[-44])
parser.add_argument('-i', '--interactivo', action="store_true", dest='interactividad',help="Gráfico interactivo",default=False)
parser.add_argument('-r', '--transform', action="store_true", dest='transformar',help="Muestra el histograma en el sistema rotado al eje principal.",default=False)
args = parser.parse_args()

filename=args.filename
cortes=args.cortes
todos=args.todos
transformacion=args.transformar
interactividad=args.interactividad

#Modo por defecto: muestra todos los valores
if(cortes==[-44]):
    todos=True

#Lectura de archivos
file=path+"\\"+filename
try:
    fi= gzip.open(file)
    a = fi.read().decode("utf-8")
    l=a.splitlines()
    def DecStr(x):
        """Decodifica una linea del archivo"""
        a=x.split()
        return float(a[0]),float(a[1]),float(a[2])
    def Read(s):
        """Lee el archivo"""
        x=np.zeros(len(s))
        y=np.zeros(len(s))
        z=np.zeros(len(s))
        for i,string in enumerate(s):
            x[i],y[i],z[i]=DecStr(string)
        return x,y,z
    x,y,z=Read(l)
except:
    raise Exception("El archivo {} no existe".format(file))

#Funciones utiles
def RotateAndCentrate(x_,y_):
    """Centra el conjunto de datos x_,y_ en su punto medio y luego lo rota hasta un sistema en que la curva de ajuste lineal tenga pendiente 0
    return: 2-tuple
        Conjunto rotado de datos
    """
    xsol=x_-np.mean(x_)
    ysol=y_-np.mean(y_)
    def Rotate(s,b):
        angle=np.arctan(np.polyfit(s,b,1)[0])
        x2=s*np.cos(angle)+b*np.sin(angle)
        y2=b*np.cos(angle)-s*np.sin(angle)
        return x2,y2
    tol=1e-10
    while(abs(np.polyfit(xsol,ysol,1)[0])>tol):
    	xsol,ysol=Rotate(xsol,ysol)
    return xsol,ysol
def FormatHist(ax,data,v,lims):
    """Actualiza y formatea los histogramas 1D"""
    ax.cla()
    if(v==True):
        ax.hist(data,bins=binsy,density=True,orientation=u'horizontal',color='tab:blue')
        ax.set_ylim(lims)
    else:
        ax.hist(data,bins=binsx,density=True,color='tab:blue')
        ax.set_xlim(lims)
    ax.axis("off")
def FormatHist2D(ax,x1,y1,xlim,ylim):
    """Actualiza y formatea el histograma 2D"""
    ax.cla()
    ax.hist2d(x1,y1,bins=[binsx,binsy])
    ax.set_ylabel("Dirección y",fontsize=fs)
    ax.set_xlabel("Dirección x",fontsize=fs)
    ax.set_xlim(xlim)
    ax.set_ylim(ylim)
    ax.tick_params(axis='x',labelsize=fs)
    ax.tick_params(axis='y',labelsize=fs)
    ax.tick_params(bottom=False,left=False)
def Centro(ax,xt,yt):
    """Dibujar centro de la distribucion de puntos"""
    ax.scatter(np.mean(xt),np.mean(yt),s=ms)
    return None
def EjePrincipal(ax,xt,yt,xlims,ylims):
    """Dibujar eje principal"""
    ax.plot(np.linspace(xlims[0],xlims[1],1000),np.polyval(np.polyfit(xt,yt,1),np.linspace(xlims[0],xlims[1],1000)),'--',lw=fs/3)
    return None


#Graficación de datos
if(interactividad==True):
    #Datos
    if(transformacion==True):
        x1,y1=RotateAndCentrate(x,y)
    else:
        x1=x
        y1=y
    xlims=[np.min(x1),np.max(x1)]
    ylims=[np.min(y1),np.max(y1)]

    #Parametros generales de la figura
    figsize=(10,10)
    fig = plt.figure(figsize=figsize,constrained_layout=True)
    plt.style.use('ggplot')
    binsx=100
    binsy=100
    fs=figsize[0]*1.5
    ms=figsize[0]*15
    titlesize=figsize[0]*2
    
    #Grilla
    gs = fig.add_gridspec(nrows=5, ncols=7, left=0.05, right=0.75,
                      hspace=0.1, wspace=0.05)    
    axxyz = fig.add_subplot(gs[3:5,0:2])
    axangulo = fig.add_subplot(gs[1:3,0:2],sharex=axxyz)
    axx = fig.add_subplot(gs[0, 2:-1])
    ax2d = fig.add_subplot(gs[1:, 2:-1])
    axy = fig.add_subplot(gs[1:, -1])
    ax2d.yaxis.set_label_position("right")
    ax2d.yaxis.tick_right()

    #Angulo vs Z, x vs Z, y vs Z
    zposibles=np.arange(-4.5,5.5,1)
    angulos=[]
    xcent=[]
    ycent=[]
    for i in zposibles:
        conds=np.logical_and(z>=i-0.5,z<=i+0.5)
        angulos.append(np.rad2deg(np.arctan(np.polyfit(x[conds],y[conds],1)[0])))
        xcent.append(np.mean(x[conds]))
        ycent.append(np.mean(y[conds]))
    axangulo.plot(zposibles,angulos,'-o')
    axangulo.set_ylabel("ángulo (grados)")
    axxyz.plot(zposibles,xcent,'-o',label='x')
    axxyz.plot(zposibles,ycent,'-o',label='y')
    axxyz.legend(loc='upper right')
    axxyz.set_xticks([-2.5,0,2.5])
    axxyz.set_ylabel("coord. centro")
    axxyz.set_xlabel(r"$z_0$")
    axangulo.tick_params(bottom=False)
    plt.setp(axangulo.get_xticklabels(), visible=False)
    #l1 y l2 son los puntos verdes que indican el corte
    l2=axxyz.plot([],[],'o',color='tab:green')
    l1=axangulo.plot([],[],'o',color='tab:green')
    cursor = Cursor(axxyz, useblit=True,horizOn=False, vertOn=False)  

    def onclick(event):
            if (event.inaxes == axangulo or event.inaxes==axxyz):
                #Actualizar los puntos verdes
                z0=np.ceil(event.xdata)-0.5
                l1[0].set_data(z0,np.array(angulos)[np.array(zposibles)==z0])
                l1[0].set_label(r'$z_0={}$'.format(z0))
                axangulo.legend()
                l2[0].set_data([z0,z0],[np.array(xcent)[np.array(zposibles)==z0],np.array(ycent)[np.array(zposibles)==z0]])

                #Actualizar los histogramas
                condition=np.logical_and(z>=z0-0.5,z<=z0+0.5)
                if(transformacion==True):
                    x1,y1=RotateAndCentrate(x[condition],y[condition])
                else:
                    x1=x[condition]
                    y1=y[condition]
                xlims=[np.min(x1),np.max(x1)]
                ylims=[np.min(y1),np.max(y1)]

                FormatHist(axx,x1,False,xlims)
                FormatHist(axy,y1,True,ylims)
                FormatHist2D(ax2d,x1,y1,xlims,ylims)
                Centro(ax2d,x1,y1)
                EjePrincipal(ax2d,x1,y1,xlims,ylims)

                #Dibujarlos
                l1[0].figure.canvas.draw()
                l2[0].figure.canvas.draw()
                axx.figure.canvas.draw()
                ax2d.figure.canvas.draw()
                axy.figure.canvas.draw()
            else:
                return None
    cid = fig.canvas.mpl_connect('button_press_event', onclick)
    FormatHist(axx,x1,False,xlims)
    FormatHist(axy,y1,True,ylims)
    FormatHist2D(ax2d,x1,y1,xlims,ylims)
    Centro(ax2d,x1,y1)
    EjePrincipal(ax2d,x1,y1,xlims,ylims)
    plt.show()
else:
    for corte in cortes:
        if(todos==True):
            cond=np.ones(len(x),dtype=bool)
        else:
            cond=np.logical_and(z>=corte-0.5,z<=corte+0.5)
        if(transformacion==True):
            x1,y1=RotateAndCentrate(x[cond],y[cond])
        else:
            x1=x[cond]
            y1=y[cond]
        xlims=[np.min(x1),np.max(x1)]
        ylims=[np.min(y1),np.max(y1)]
        figsize=(10,10)
        fig = plt.figure(figsize=figsize,constrained_layout=True)
        plt.style.use('ggplot')
        binsx=100
        binsy=100
        fs=figsize[0]*1.5
        ms=figsize[0]*15
        titlesize=figsize[0]*2

        gs = fig.add_gridspec(nrows=5, ncols=5, left=0.05, right=0.75,
                          hspace=0.1, wspace=0.05)
        move=0
        axx = fig.add_subplot(gs[0, move:-1])
        ax2d = fig.add_subplot(gs[1:, move:-1])
        axy = fig.add_subplot(gs[1:, -1])
        if(todos==True):
            plt.suptitle("Todos los datos en el plano x-y",fontsize=titlesize)
        else:
            plt.suptitle(r"$z_0$={}".format(corte),fontsize=titlesize)
        FormatHist(axx,x1,False,xlims)
        FormatHist(axy,y1,True,ylims)
        FormatHist2D(ax2d,x1,y1,xlims,ylims)
        Centro(ax2d,x1,y1)
        EjePrincipal(ax2d,x1,y1,xlims,ylims)
        if(todos==True):
            plt.show()
            break
    plt.show()