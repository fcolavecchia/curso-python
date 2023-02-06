from turtle import title
import numpy as np
import argparse
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import parser
import gzip
from scipy.odr import *
from matplotlib.backend_bases import MouseButton

zs=[-4.5,-4.0,-3.5,-3.0,-2.5,-2.0,-1.5,-1.0,-0.5,0.0,0.5,1.0,1.5,2.0,2.5,3.0,3.5,4.0,4.5]
thetas=[]
bs=[]
centros=[]

parser = argparse.ArgumentParser(description='"Análisis de datos interactivo"')
groupInter = parser.add_mutually_exclusive_group(required=True)
#groupCortes = groupInter.add_mutually_exclusive_group()
parser.add_argument('-f', '-file=', action="store", dest='f_name',type=str,help='Nombre del archivo de datos (requerido)',required=True)
groupInter.add_argument('-t','-todos=', action='store_true',dest='graf_todo',help='Graficar el conjunto total de puntos',default=False)
groupInter.add_argument('-z', '-corte', action="append",metavar="[-4.5 - 4.5]" ,choices={-4.5,-4.0,-3.5,-3.0,-2.5,-2.0,-1.5,-1.0,-0.5,0.0,0.5,1.0,1.5,2.0,2.5,3.0,3.5,4.0,4.5},dest='cortes',type=float,help='Cortes a graficar (-z <corte1> -z <corte2> ...)',default=[])
groupInter.add_argument('-i','-interactivo', action='store_true',dest='interactivo',help='Hacer graficos interactivos',default=False)
parser.add_argument('-r','-transform', action='store_true',dest='transform',help='Graficar datos rotados y centrados',default=False)

args=parser.parse_args()

file = gzip.open(args.f_name, "rb")
datos=np.genfromtxt(file).transpose()
file.close()

def linear_func(p, x): #Para la regresion lineal ortogonal
   m, c = p
   return m*x + c

def plotCorte(xdata,ydata,cortes=[]): #Funcion para plotear
    if len(cortes)==0:
        datosx=np.array(xdata)
        datosy=np.array(ydata)
        fig=plt.figure("Proyección en plano x-y",figsize=(8,8))
        gs=fig.add_gridspec(2,2,  width_ratios=(7, 2), height_ratios=(2, 7), left=0.1, right=0.9, bottom=0.1, top=0.9, wspace=0.01, hspace=0.01)
        ax=fig.add_subplot(gs[1,0])
        histx=fig.add_subplot(gs[0,0],sharex=ax)
        histy=fig.add_subplot(gs[1,1],sharey=ax)

        if args.transform:
            linear_model = Model(linear_func)
            data=RealData(datosx,datosy)
            odr = ODR(data, linear_model, beta0=[1., 0.])
            out=odr.run() #Ajusto la recta que minimiza la distancia ortogonal a los puntos
            theta=np.arctan(out.beta[0]) #Angulo de la recta
            for i in range(len(datosy)): #Rotacion
                datosx[i], datosy[i]=datosx[i]*np.cos(-theta)-datosy[i]*np.sin(-theta), datosx[i]*np.sin(-theta)+datosy[i]*np.cos(-theta)
            datosx-=np.median(datosx) #Traslacion en x
            datosy-=np.median(datosy) #Traslacion en y
            datosx=np.append(datosx,int(min(datos[0]))) #Puntos auxilares para que todos los cortes tengan el mismo tamaño
            datosx=np.append(datosx,int(min(datos[0]))) #
            datosx=np.append(datosx,int(max(datos[0]))) #
            datosx=np.append(datosx,int(max(datos[0]))) #
            datosy=np.append(datosy,int(min(datos[1]))) #
            datosy=np.append(datosy,int(max(datos[1]))) #
            datosy=np.append(datosy,int(min(datos[1]))) #
            datosy=np.append(datosy,int(max(datos[1]))) #
            ax.scatter(0,0,s=50,color='red',zorder=3) #Centro de la distribucion 2D
            ax.plot(np.linspace(-30,30,100),np.zeros(100),color='red',ls="--") #Eje principal de la distribucion 2D

        histx.set_title('Proyección en el plano $x$-$y$ (todos los planos)',fontsize=14)
        ax.hist2d(datosx,datosy,bins=100)
        ax.set_xlabel('Dirección $x$',fontsize=14)
        ax.set_ylabel('Dirección $y$',fontsize=14)
        ax.tick_params(axis='x', labelsize= 12)
        ax.tick_params(axis='y', labelsize= 12)
        ax.set_xticks(np.linspace(-30,30,13))
        ax.set_yticks(np.linspace(-30,30,13))
        ax.set_xlim(int(min(xdata)),int(max(xdata)))
        ax.set_ylim(int(min(ydata)),int(max(ydata)))
        histx.hist(datosx,bins=100) #Histograma en x
        for i in ax.get_xticks():
            histx.axvline(x=i,color='grey',linestyle='dotted',zorder=0)
        histx.axis('off')
        histy.hist(datosy,bins=100,orientation='horizontal') #Histograma en y
        for i in ax.get_yticks():
            histy.axhline(y=i,color='grey',linestyle='dotted',zorder=0)
        histy.axis('off')
        
    else:
        for z in cortes:
            datosx=np.array([xdata[i] for i in range(len(xdata)) if datos[2][i]>=(z-0.5) and datos[2][i]<=(z+0.5)])
            datosy=np.array([ydata[i] for i in range(len(ydata)) if datos[2][i]>=(z-0.5) and datos[2][i]<=(z+0.5)])
            datosx=np.append(datosx,int(min(datos[0]))) #Puntos auxilares para que todos los cortes tengan el mismo tamaño
            datosx=np.append(datosx,int(min(datos[0]))) #
            datosx=np.append(datosx,int(max(datos[0]))) #
            datosx=np.append(datosx,int(max(datos[0]))) #
            datosy=np.append(datosy,int(min(datos[1]))) #
            datosy=np.append(datosy,int(max(datos[1]))) #
            datosy=np.append(datosy,int(min(datos[1]))) #
            datosy=np.append(datosy,int(max(datos[1]))) #
            if args.transform:
                linear_model = Model(linear_func)
                data=RealData(datosx,datosy)
                odr = ODR(data, linear_model, beta0=[1., 0.])
                out=odr.run() #Ajusto la recta que minimiza la distancia ortogonal a los puntos
                theta=np.arctan(out.beta[0]) #Angulo de la recta
                for i in range(len(datosx)): #Rotacion
                    datosx[i], datosy[i]=datosx[i]*np.cos(-theta)-datosy[i]*np.sin(-theta), datosx[i]*np.sin(-theta)+datosy[i]*np.cos(-theta)
                datosx-=np.median(datosx) #Traslacion en x
                datosy-=np.median(datosy) #Traslacion en y
            fig=plt.figure("Corte "+str(z),figsize=(8,8))
            gs=fig.add_gridspec(2,2,  width_ratios=(7, 2), height_ratios=(2, 7), left=0.1, right=0.9, bottom=0.1, top=0.9, wspace=0.01, hspace=0.01)
            ax=fig.add_subplot(gs[1,0])
            histx=fig.add_subplot(gs[0,0],sharex=ax)
            histy=fig.add_subplot(gs[1,1],sharey=ax)

            histx.set_title('$z_0=$'+str(z),fontsize=14)
            ax.hist2d(datosx,datosy,bins=100)
            ax.set_xlabel('Dirección $x$',fontsize=14)
            ax.set_ylabel('Dirección $y$',fontsize=14)
            ax.tick_params(axis='x', labelsize= 12)
            ax.tick_params(axis='y', labelsize= 12)
            ax.set_xticks(np.linspace(-30,30,13))
            ax.set_yticks(np.linspace(-30,30,13))
            ax.set_xlim(int(min(datos[0])),int(max(datos[0])))
            ax.set_ylim(int(min(datos[1])),int(max(datos[1])))
            linear_model = Model(linear_func)
            data=RealData(datosx,datosy)
            odr = ODR(data, linear_model, beta0=[1., 0.])
            out=odr.run() #Ajusto la recta que minimiza la distancia ortogonal a los puntos
            ax.scatter(np.median(datosx),np.median(datosy),s=50,color='red') #Centro de la distribucion 2D
            ax.plot(np.linspace(-30,30,100),np.linspace(-30,30,100)*out.beta[0]+out.beta[1],color='red',ls="--") #Eje principal de la distribucion 2D
            histx.hist(datosx,bins=100) #Histograma en x
            for i in ax.get_xticks():
                histx.axvline(x=i,color='grey',linestyle='dotted',zorder=0)
            histx.axis('off')
            histy.hist(datosy,bins=100,orientation='horizontal') #Histograma en y
            for i in ax.get_yticks():
                histy.axhline(y=i,color='grey',linestyle='dotted',zorder=0)
            histy.axis('off')
    plt.show()

def plotInter(xdata,ydata,z):
    datosx=np.array([xdata[i] for i in range(len(xdata)) if datos[2][i]>=(z-0.5) and datos[2][i]<=(z+0.5)])
    datosy=np.array([ydata[i] for i in range(len(ydata)) if datos[2][i]>=(z-0.5) and datos[2][i]<=(z+0.5)])
    if args.transform:
        for i in range(len(datosx)): #Rotacion
            datosx[i], datosy[i]=datosx[i]*np.cos(-thetas[zs.index(z)])-datosy[i]*np.sin(-thetas[zs.index(z)]), datosx[i]*np.sin(-thetas[zs.index(z)])+datosy[i]*np.cos(-thetas[zs.index(z)])
        datosx-=np.median(datosx) #Traslacion en x
        datosy-=np.median(datosy) #Traslacion en y

    datosx=np.append(datosx,int(min(datos[0]))) #Puntos auxilares para que todos los cortes tengan el mismo tamaño
    datosx=np.append(datosx,int(min(datos[0]))) #
    datosx=np.append(datosx,int(max(datos[0]))) #
    datosx=np.append(datosx,int(max(datos[0]))) #
    datosy=np.append(datosy,int(min(datos[1]))) #
    datosy=np.append(datosy,int(max(datos[1]))) #
    datosy=np.append(datosy,int(min(datos[1]))) #
    datosy=np.append(datosy,int(max(datos[1]))) #
    histx.set_title('$z_0=$'+str(z),fontsize=14)
    ax.hist2d(datosx,datosy,bins=100)
    ax.set_xlabel('Dirección $x$',fontsize=14)
    ax.set_xticks(np.linspace(-30,30,13))
    ax.set_yticks(np.linspace(-30,30,13))
    ax.set_xlim(int(min(datos[0])),int(max(datos[0])))
    ax.set_ylim(int(min(datos[1])),int(max(datos[1])))
    ax.tick_params(top=False,bottom=True,left=False,right=False,labelright=False,labelbottom=True,labelleft=False)
    if not args.transform:
        ax.scatter(centros[zs.index(z)][0],centros[zs.index(z)][1],s=50,color='red') #Centro de la distribucion 2D
        ax.plot(np.linspace(-30,30,100),np.linspace(-30,30,100)*np.tan(thetas[zs.index(z)])+bs[zs.index(z)],color='red',ls="--") #Eje principal de la distribucion 2D
    else:
        ax.scatter(0,0,s=50,color='red') #Centro de la distribucion 2D
        ax.plot(np.linspace(-30,30,100),np.zeros(100),color='red',ls="--") #Eje principal de la distribucion 2D
    
    histx.hist(datosx,bins=100) #Histograma en x
    histx.axis('off')
    for i in ax.get_xticks():
        histx.axvline(x=i,color='grey',linestyle='dotted',zorder=0)
    histy.hist(datosy,bins=100,orientation='horizontal') #Histograma en y
    histy.yaxis.tick_right()
    histy.tick_params(top=False,bottom=False,left=False,right=False,labelright=True,labelbottom=False)
    histy.spines['top'].set_visible(False)
    histy.spines['right'].set_visible(False)
    histy.spines['bottom'].set_visible(False)
    histy.spines['left'].set_visible(False)
    histy.set_ylabel('Dirección $y$',fontsize=14)
    histy.yaxis.set_label_position("right")
    for i in ax.get_yticks():
        histy.axhline(y=i,color='grey',linestyle='dotted',zorder=0)

    theta_vs_z.get_xaxis().set_visible(False)
    theta_vs_z.plot(zs,np.array(thetas)*180/np.pi,zorder=3)
    theta_vs_z.scatter(zs,np.array(thetas)*180/np.pi,zorder=4)
    theta_vs_z.scatter(zs[zs.index(z)],thetas[zs.index(z)]*180/np.pi,color='red',label="$z_0=$"+str(z),s=50,zorder=5)
    theta_vs_z.legend(fontsize=12)
    theta_vs_z.set_ylabel("Ángulo [°]",fontsize=12)
    theta_vs_z.grid(zorder=0,axis='x')
    theta_vs_z.grid(zorder=0,axis='y')
    for i in range(-4,5): #Esto está porque por alguna razon no me toma la grid en el eje y
        theta_vs_z.axvline(x=i,color='0.8',lw=1,zorder=0)
    xcent=[i[0] for i in centros]
    ycent=[i[1] for i in centros]
    centro_vs_z.plot(zs,xcent,zorder=3)
    centro_vs_z.scatter(zs,xcent,label="$x$",zorder=4)
    centro_vs_z.scatter(zs[zs.index(z)],xcent[zs.index(z)],color='red',s=50,zorder=5)
    centro_vs_z.plot(zs,ycent,zorder=3)
    centro_vs_z.scatter(zs,ycent,label="$y$",zorder=4)
    centro_vs_z.scatter(zs[zs.index(z)],ycent[zs.index(z)],color='red',s=50,zorder=5)
    centro_vs_z.set_ylabel("Coord. centro",fontsize=14)
    centro_vs_z.set_xticks([-4,-3,-2,-1,0,1,2,3,4])
    centro_vs_z.legend(fontsize=12)
    centro_vs_z.grid(axis='x',zorder=0)
    centro_vs_z.grid(axis='y',zorder=0)
    centro_vs_z.set_xlabel('$z_0$',fontsize=14)

if not args.interactivo: #Si no se pide gráfico interactivo
    if args.graf_todo: #Si se pide graficar todos el eje z
        plotCorte(datos[0],datos[1])

    else: #Si se pide graficar dados cortes
        plotCorte(datos[0],datos[1],args.cortes)

else: #Si se pide gráfico interactivo
    for z in zs:
        datosx=np.array([datos[0][i] for i in range(len(datos[0])) if datos[2][i]>=(z-0.5) and datos[2][i]<=(z+0.5)])
        datosy=np.array([datos[1][i] for i in range(len(datos[1])) if datos[2][i]>=(z-0.5) and datos[2][i]<=(z+0.5)])
        linear_model = Model(linear_func)
        data=RealData(datosx,datosy)
        odr = ODR(data, linear_model, beta0=[1., 0.])
        out=odr.run() #Ajusto la recta que minimiza la distancia ortogonal a los puntos
        theta=np.arctan(out.beta[0]) #Angulo de la recta
        b=out.beta[1]
        thetas.append(theta)
        bs.append(b)
        centros.append((np.median(datosx),np.median(datosy)))
    
    fig=plt.figure("Visualización interactiva",figsize=(8,8))
    gs=fig.add_gridspec(3,3,width_ratios=(3,5, 1.428), height_ratios=(1.428, 4,4), left=0.1, right=0.9, bottom=0.1, top=0.9, wspace=0.00, hspace=0.00)
    ax=fig.add_subplot(gs[1:,1])
    histx=fig.add_subplot(gs[0,1],sharex=ax)
    histy=fig.add_subplot(gs[1:,2],sharey=ax)
    centro_vs_z=fig.add_subplot(gs[2,0])
    theta_vs_z=fig.add_subplot(gs[1,0],sharex=centro_vs_z)
    plotInter(datos[0],datos[1],0.0)

    def on_click(event):
        if event.button is MouseButton.LEFT:
            if event.inaxes==centro_vs_z:
                for c in centros:
                    if event.xdata<=zs[centros.index(c)]+0.25 and event.xdata>=zs[centros.index(c)]-0.25:
                        if event.ydata<=c[0]+0.1 and event.ydata>=c[0]-0.1:
                            ax.clear()
                            histx.clear()
                            histy.clear()
                            centro_vs_z.clear()
                            theta_vs_z.clear()
                            plotInter(datos[0],datos[1],zs[centros.index(c)])
                            plt.draw()
                            break
                        elif event.ydata<=c[1]+0.1 and event.ydata>=c[1]-0.1:
                            ax.clear()
                            histx.clear()
                            histy.clear()
                            centro_vs_z.clear()
                            theta_vs_z.clear()
                            plotInter(datos[0],datos[1],zs[centros.index(c)])
                            plt.draw()
                            break
                        else:
                            print("Seleccione un punto valido")
                        
            elif event.inaxes==theta_vs_z:
                for t in thetas:
                    if event.xdata<=zs[thetas.index(t)]+0.25 and event.xdata>=zs[thetas.index(t)]-0.25:
                        if event.ydata<=t*180/np.pi +5 and event.ydata>=t*180/np.pi -5:
                            ax.clear()
                            histx.clear()
                            histy.clear()
                            centro_vs_z.clear()
                            theta_vs_z.clear()
                            plotInter(datos[0],datos[1],zs[thetas.index(t)])
                            plt.draw()   
                            break
                        else:
                            print("Seleccione un punto valido")
            else:
                print("Seleccione un punto valido")

    plt.connect('button_press_event', on_click)

    plt.show()


    
