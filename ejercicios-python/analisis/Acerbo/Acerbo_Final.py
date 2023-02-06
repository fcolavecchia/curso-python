import numpy as np
import argparse
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from scipy import odr
from matplotlib.widgets import Cursor


#Comandos para setear los graficos
plt.style.use('default')
plt.rc('font', size=23)                   # controls default text sizes
plt.rc('axes', titlesize=17)              # fontsize of the axes title
plt.rc('axes', labelsize=17)              # fontsize of the x and y labels
plt.rc('xtick', labelsize=14)             # fontsize of the tick labels
plt.rc('ytick', labelsize=14)             # fontsize of the tick labels
plt.rc('legend', fontsize=10)             # legend fontsize
plt.rc('figure', titlesize=20)            # fontsize of the figure title

#####################################################################################################

# Variables que se piden por linea de comando

parser = argparse.ArgumentParser(description = 'Especificaciones del gráfico')
parser.add_argument('-t','--todos', type = bool, default = 1, help=' De ser verdad y no pasarse ningún corte en z grafica todos los puntos.')
parser.add_argument('-name ','--nombrearchivo', type = str, default = None , help='Nombre del archivo de datos que se va a graficar.')
parser.add_argument('-z','--corte' ,type = float, nargs= '*', default= [], help=' Lista de valores de z de los cuales se van a graficar los puntos que se encuentren en +- 0.5')
parser.add_argument('-i','--interactivo' ,type = bool, default = 0, help= 'Booleano si se quiere que el grafico sea interactivo.')
parser.add_argument('-r','--transform' ,type = bool  , default = 0, help='Booleano si se quiere que los datos se presenten rotados.')
parser.add_argument('-b','--bineado' ,type = int  , default = 70, help='Número de bines con los que se van a hacer los histogramas.')
args = parser.parse_args()

#####################################################################################################

# Pregunto si pasaron un nombre de archivo, sino se pide
if args.nombrearchivo == None: 
    name = input('Indique que archivo se desea graficar: ')
else:
    name = args.nombrearchivo

# Cargo las columnas de coordenadas para despues utilizarlas o separarlas si se pide
auxx = np.loadtxt(name, usecols=0) #Guardo todos los valores de x
auxy = np.loadtxt(name, usecols=1) #Guardo todos los valores de y
auxz = np.loadtxt(name, usecols=2) #Guardo todos los valores de z

if args.interactivo == 0 : ###################### BLOQUE NO INTERACTIVO ##############################################

    if(args.todos == 1 and len(args.corte) == 0 ): # GRAFICO CON TODOS LOS PUNTOS
        x = auxx
        y = auxy
        z = auxz

        #Calculo el eje principal de la distribucion de los puntos
        data = odr.Data(x,y)
        odr_obj = odr.ODR(data, odr.unilinear, beta0=[0,1.0])
        output = odr_obj.run()
        poli = np.poly1d(output.beta)
        x_fit = np.linspace(np.min(x),np.max(x),500)

        # Guardo los valores del angulo con respecto a la horizontal y trigonometricas de ese angulo
        Theta = np.arctan(output.beta[0])
        cos = np.cos(-Theta)
        sin = np.sin(-Theta)

        #Genero la figura y la grilla que va a separar las figuras
        fig= plt.figure(figsize=(8, 8),constrained_layout=True)
        fig.set_facecolor('gainsboro')
        gs = gridspec.GridSpec(2, 2,  width_ratios=(7, 2), height_ratios=(2, 7),left=0.05, right=0.95, bottom=0.05, top=0.95, wspace=0.02, hspace=0.02)

        #Ubicación de los distintos histogramas y diferentes parametros de cada uno
        graf = plt.subplot(gs[1,0], frameon = True)
        graf.tick_params(bottom = True, left = False, top = False, right = True,labelleft=False,labelright=True, color = 'gray')
        graf.tick_params(axis = 'y', length = 110)
        histx = plt.subplot(gs[0,0], frameon = False, sharex = graf)
        histx.tick_params(bottom = False, left = False, labelleft=False,labelbottom=False)
        histx.axis('off')
        histy = plt.subplot(gs[1,1], frameon = False, sharey = graf)
        histy.tick_params(bottom = False, left = False, labelleft=False, labelbottom=False)
        histy.axis('off')

        if args.transform != 0: # Si se quiere que los datos sean rotados los calculo y se grafican esos
            x_rot = (x-np.mean(x))*cos - (y-np.mean(y))*sin
            y_rot = (y-np.mean(y))*cos + (x-np.mean(x))*sin
            graf.hist2d(x_rot, y_rot, bins = args.bineado, density = False , cmap = 'viridis')
            graf.scatter(np.mean(x_rot),np.mean(y_rot),s = 75, color = 'tomato', marker = '+', label = 'mean (x,y)')
            histx.hist(x_rot, bins = args.bineado ,density = True)
            histx.axvline(np.mean(x_rot), color = 'tomato', linestyle = '--', label = 'mean (x)')
            histy.hist(y_rot, bins = args.bineado ,density = True, orientation='horizontal')
            histy.axhline(np.mean(y_rot), color = 'tomato', linestyle = '--', label = 'mean (y)')
            fig.suptitle('Todos los datos del plano x-y rotados y centrados')

        else: # Si no se quiere que los datos sean rotados los calculo y se grafican los originales con el eje principal
            graf.hist2d(x, y, bins = args.bineado, density = False , cmap = 'viridis')
            graf.scatter(np.mean(x),np.mean(y),s = 75, color = 'tomato', marker = '+', label = 'mean (x,y)')
            graf.plot(x_fit,poli(x_fit), linestyle = ':' , color = 'tomato', label = 'Eje principal, $\Theta$ = '+ str(Theta*180/np.pi)[0:5]+'$^{\circ}$' )
            histx.hist(x, bins = args.bineado ,density = True)
            histx.axvline(np.mean(x), color = 'tomato', linestyle = '--', label = 'mean (x) = ' + str(np.mean(x))[0:5])
            histy.hist(y, bins = args.bineado ,density = True, orientation='horizontal')
            histy.axhline(np.mean(y), color = 'tomato', linestyle = '--', label = 'mean (y) = ' + str(np.mean(y))[0:5])
            fig.suptitle('Todos los datos del plano x-y')

        graf.set_ylabel('Dirección en y')
        graf.set_xlabel('Dirección en x')
        fig.legend(bbox_to_anchor=(0.925,0.925))
        plt.show()

    else:                               # GRAFICO DE LOS CORTES QUE SE PASAN POR PARAMETRO args.corte
        args.corte = [float(args.corte[i]) for i in range(len(args.corte))]
        #Se separan los datos en distintas listas segun el corte que se haya pasado por parametro
        x = [[auxx[i] for i in range(len(auxz)) if(auxz[i]<= j+0.5 and auxz[i]>= j-0.5)] for j in args.corte]
        y = [[auxy[i] for i in range(len(auxz)) if(auxz[i]<= j+0.5 and auxz[i]>= j-0.5)] for j in args.corte]
        z = [[auxz[i] for i in range(len(auxz)) if(auxz[i]<= j+0.5 and auxz[i]>= j-0.5)] for j in args.corte]
            
        for j in range(len(args.corte)): #Generación de un gráfico para cada corte

            #Calculo el eje principal de la distribucion de los puntos para ese corte
            data = odr.Data(x[j][:],y[j][:])
            odr_obj = odr.ODR(data, odr.unilinear, beta0=[0,1.0])
            output = odr_obj.run()
            poli = np.poly1d(output.beta)
            x_fit = np.linspace(np.min(x[j][:]),np.max(x[j][:]),1000)

            # Guardo los valores del angulo con respecto a la horizontal y trigonometricas de ese angulo
            Theta = np.arctan(output.beta[0])
            cos = np.cos(-Theta)
            sin = np.sin(-Theta)

            #Genero la figura y la grilla que va a separar las figuras
            fig= plt.figure( j ,figsize=(8, 8),constrained_layout=True)
            fig.set_facecolor('gainsboro')
            gs = gridspec.GridSpec(2, 2,  width_ratios=(7, 2), height_ratios=(2, 7),left=0.05, right=0.95, bottom=0.05, top=0.95, wspace=0.02, hspace=0.02)

            #Ubicación de los distintos histogramas y diferentes parametros de cada uno
            graf = plt.subplot(gs[1,0], frameon = True)
            graf.tick_params(bottom = True, left = False, top = False, right = True,labelleft=False,labelright=True, color = 'gray')
            graf.tick_params(axis = 'y', length = 110)
            histx = plt.subplot(gs[0,0], frameon = False, sharex = graf)
            histx.tick_params(bottom = False, left = False, labelleft=False,labelbottom=False)
            histx.axis('off')
            histy = plt.subplot(gs[1,1], frameon = False, sharey = graf)
            histy.tick_params(bottom = False, left = False, labelleft=False, labelbottom=False)
            histy.axis('off')

            if args.transform != 0: #Si se piden los datos rotados y centrados se grafican los datos rotados y centrados
                x_rot = (x[j]-np.mean(x[j][:]))*cos - (y[j]-np.mean(y[j][:]))*sin
                y_rot = (y[j]-np.mean(y[j][:]))*cos + (x[j]-np.mean(x[j][:]))*sin
                graf.hist2d(x_rot, y_rot, bins = args.bineado, density = False , cmap = 'viridis')
                fig.suptitle('Puntos con z $\in$ ['+str(args.corte[j]-0.5) + ',' + str(args.corte[j]+0.5) + ']' + ' rotados y centrados')
                graf.scatter(np.mean(x_rot),np.mean(y_rot),s = 75, marker = '+', color = 'tomato', label = 'centro (x,y)')
                histx.hist(x_rot, bins = args.bineado ,density = True)   
                histx.axvline(np.mean(x_rot), color = 'tomato', linestyle = '--', label = 'mean (x)' )
                histy.hist(y_rot, bins = args.bineado ,density = True, orientation='horizontal')
                histy.axhline(np.mean(y_rot), color = 'tomato', linestyle = '--', label = 'mean (y)')

            else: #Si no se piden los datos rotados y centrados se grafican los datos originales y el eje principal
                graf.hist2d(x[j][:], y[j][:], bins = args.bineado, density = False , cmap = 'viridis')
                graf.plot(x_fit,poli(x_fit), linestyle = ':' , color = 'tomato', label = 'Eje principal, $\Theta$ = '+ str(Theta*180/np.pi)[0:5]+'$^{\circ}$')
                graf.scatter(np.mean(x[j][:]),np.mean(y[j][:]),s = 75, marker = '+', color = 'tomato', label = 'centro (x,y)')
                fig.suptitle('Puntos con z $\in$ ['+str(args.corte[j]-0.5) + ',' + str(args.corte[j]+0.5) + ']')
                histx.hist(x[j][:], bins = args.bineado ,density = True)   
                histx.axvline(np.mean(x[j][:]), color = 'tomato', linestyle = '--', label = 'mean (x) = ' + str(np.mean(x[j]))[0:5] )
                histy.hist(y[j][:], bins = args.bineado ,density = True, orientation='horizontal')
                histy.axhline(np.mean(y[j][:]), color = 'tomato', linestyle = '--', label = 'mean (y) = ' + str(np.mean(y[j]))[0:5] )

            graf.set_ylabel('Dirección en y')
            graf.set_xlabel('Dirección en x')
            fig.legend(bbox_to_anchor=(0.925,0.925))

        plt.show(block = True)

########################################################### BLOQUE INTERACTIVO ##########################################################
else:
    import matplotlib
#    matplotlib.use('TkAgg')
    
    z_corte = np.linspace(-4.5,4.5,19)
    x = [ [auxx[i] for i in range(len(auxz)) if(auxz[i]<= j+0.5 and auxz[i]>= j-0.5)] for j in z_corte]
    y = [ [auxy[i] for i in range(len(auxz)) if(auxz[i]<= j+0.5 and auxz[i]>= j-0.5)] for j in z_corte]

    x_medio = np.array([np.mean(x[i][:]) for i in range(len(x))])
    xx_medio = np.array([np.mean(xx) for xx in x])
    y_medio = np.array([np.mean(y[i][:]) for i in range(len(y))])

    Theta = np.zeros(len(z_corte))
    Pendientes = np.zeros(len(z_corte))
    Ordenadas = np.zeros(len(z_corte))

    for j in range(len(z_corte)):
        data = odr.Data(x[j][:],y[j][:])
        odr_obj = odr.ODR(data, odr.unilinear, beta0=[0,1.0])
        output = odr_obj.run()
        Theta[j] = np.arctan(output.beta[0])
        Pendientes[j] = output.beta[0]
        Ordenadas[j] = output.beta[1]


    def seleccionar(event): ################################## FUNCION DE CLICKEO #############################
        x0 = event.xdata #Valor de x que se presionó
        n = int(np.round((x0+4.5)/0.5)) #Indice del vector de zetas
        if n > 18: n = 18 # Por si uno se pasa

        graf.cla() #Cierro los graficos viejos
        histx.cla()
        histy.cla()
        graf_centro.cla()
        graf_Theta.cla()

        x_fit = np.linspace(np.min(x[n][:]),np.max(x[n][:]),500) # Nuevo eje principal de la distribucion
        Recta = Pendientes[n]*x_fit + Ordenadas[n]
        
        #Rehago todos los graficos
        graf.hist2d(x[n][:] , y[n][:], cmap = 'viridis', bins = args.bineado, density = False) 
        graf.scatter(np.mean(x[n][:]),np.mean(y[n][:]),s = 75, color = 'tomato', marker = '+', label = 'mean (x,y)')
        graf.plot( x_fit, Recta, linestyle = ':' , color = 'tomato', label = 'Eje principal, $\Theta$ = '+ str(Theta[n] *180/np.pi)[0:5]+ '$^{\circ}$' )

        histx.hist(x[n][:], bins = args.bineado ,density = True)
        histx.axvline(np.mean(x[n][:]), color = 'tomato', linestyle = '-')
        histy.hist(y[n][:], bins = args.bineado ,density = True, orientation='horizontal')
        histy.axhline(np.mean(y[n][:]), color = 'tomato', linestyle = '-')
        graf_centro.plot(z_corte, x_medio, marker = 'o', linestyle = '-', color = 'blue', label= 'Centro de x = '+ str(x_medio[n])[0:5] , zorder = -1)
        graf_centro.plot(z_corte, y_medio, marker = 'o', linestyle = '-', color = 'r', label= 'Centro de y = '+ str(y_medio[n])[0:5], zorder = -1)
        graf_Theta.plot(z_corte, Theta*180/np.pi, marker = 'o', linestyle = '-', color = 'k', label= 'Angulo del eje principal', zorder = -1)
        graf_centro.tick_params(bottom = True, left = True, top = False, right = False, labelsize = 10)
        graf_centro.set_xlabel('z de corte')
        graf_centro.set_ylabel('Centro (x,y)')
        graf_centro.grid('both')
        graf_centro.set_xticks(z_corte[::3])
        graf_Theta.tick_params(bottom = False, left = True, top = False, right = False, labelbottom=False, labelsize = 10)
        graf_Theta.set_yticks(np.linspace(-90,90,13))
        graf_Theta.grid('both')
        graf_Theta.set_ylabel('$\Theta$'+'[$^{\circ}$]')
        graf_centro.scatter( z_corte[n] ,x_medio[n], color='green', s=50, zorder = 0)
        graf_centro.scatter( z_corte[n] ,y_medio[n], color='green', s=50, zorder = 0)
        graf_Theta.scatter( z_corte[n] , Theta[n]*180/np.pi, color='green', s=50, label = '$z_0$ = '+str(z_corte[n]), zorder = 0)
        fig.legend(bbox_to_anchor=(0.25,0.98), facecolor='white', framealpha=1)
        fig.figure.canvas.draw()

    #Eje inicial
    x_fit = np.linspace(np.min(x[9][:]),np.max(x[9][:]),500)
    Recta = Pendientes[9]*x_fit + Ordenadas[9]

    #Inicializo el grafico con la red de subfiguras
    fig= plt.figure(figsize=(10, 8),constrained_layout=True)
    fig.set_facecolor('gainsboro')
    fig.suptitle('Todos los cortes del plano x-y')
    gs = gridspec.GridSpec(3, 3, height_ratios=[2, 4, 4], width_ratios=[4 ,8, 2],left=0.05, right=0.95, bottom=0.05, top=0.95, wspace=0.02, hspace=0.02)
   
    #Inicializo todas las subfiguras con distintos parámetros
    graf = plt.subplot(gs[1:, 1:2], frameon = True)
    graf.tick_params(bottom = True, left = False, top = False, right = True,labelleft=False,labelright=True, color = 'gray')
    graf.tick_params(axis = 'y', length = 110)
    histx = plt.subplot(gs[0,1], frameon = False, sharex = graf)
    histx.axis('off')
    histx.tick_params(bottom = False, left = False, labelleft=False, labelbottom=False)
    histy = plt.subplot(gs[1:,2], frameon = False, sharey = graf)
    histy.tick_params(bottom = False, left = False, labelleft=False, labelbottom=False)
    histy.axis('off')
    graf_centro = plt.subplot(gs[2,0], frameon = False)
    graf_centro.tick_params(bottom = True, left = True, top = False, right = False, labelsize = 10)
    graf_centro.set_xlabel('z de corte')
    graf_centro.set_ylabel('Centro (x,y)')
    graf_centro.grid('both')
    graf_centro.set_xticks(z_corte[::3])
    graf_Theta = plt.subplot(gs[1,0], frameon = False, sharex = graf_centro)
    graf_Theta.tick_params(bottom = False, left = True, top = False, right = False, labelbottom=False, labelsize = 10)
    graf_Theta.set_yticks(np.linspace(-90,90,13))
    graf_Theta.grid('both')
    graf_Theta.set_ylabel('$\Theta$'+'[$^{\circ}$]')

    # Determino que grafico va en cada subfigura
    graf.hist2d(x[9][:], y[9][:], cmap = 'viridis', bins = args.bineado, density = False)
    graf.scatter(np.mean(x[9][:]),np.mean(y[9][:]),s = 75, color = 'tomato', marker = '+', label = 'mean (x,y)')
    graf.plot(x_fit,Recta , linestyle = ':' , color = 'tomato', label = 'Eje principal, $\Theta$ = '+ str(Theta[9]*180/np.pi)[0:5]+ '$^{\circ}$' )
    histx.hist(x[9][:], bins = args.bineado ,density = True)
    histx.axvline(np.mean(x[9][:]), color = 'tomato', linestyle = '-')
    histy.hist(y[9][:], bins = args.bineado ,density = True, orientation='horizontal')
    histy.axhline(np.mean(y[9][:]), color = 'tomato', linestyle = '-')
    graf_centro.plot(z_corte, x_medio, marker = 'o', linestyle = '-', color = 'blue', label= 'Centro de x = '+ str(x_medio[9])[0:5] , zorder = -1)
    graf_centro.plot(z_corte, y_medio, marker = 'o', linestyle = '-', color = 'r', label= 'Centro de y = '+ str(y_medio[9])[0:5], zorder = -1)
    graf_centro.scatter( [z_corte[9]] ,[x_medio[9]], color='green', zorder = 0)
    graf_centro.scatter( [z_corte[9]] ,[y_medio[9]], color='green', zorder = 0)
    graf_Theta.plot(z_corte, Theta*180/np.pi, marker = 'o', linestyle = '-', color = 'k', label= 'Angulo del eje principal', zorder = -1)
    graf_Theta.scatter([z_corte[9]] ,[Theta[9]], color='green', label = '$z_0$ = '+str(z_corte[9]), zorder = 0)
    
    #Parametros de la figura y leyenda
    graf.set_ylabel('Dirección en y',labelpad=-520)
    graf.set_xlabel('Dirección en x')
    fig.legend(bbox_to_anchor=(0.25,0.98), facecolor='white', framealpha=1)
    #Inicializo el cursor
    angle_cursor = Cursor(graf_Theta, horizOn=False, vertOn=True, useblit=True,color='blue', linewidth=1)
    coord_cursor = Cursor(graf_centro, horizOn=False, vertOn=True, useblit=True,color='blue', linewidth=1)
    fig.canvas.mpl_connect('button_press_event', seleccionar)

    plt.show()

    
