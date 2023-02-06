import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import argparse

class Analisis3D:
    def __init__(self, file):
        self.file = file
        try: x, y, z = np.loadtxt(file, unpack = True)
        except IOError: print('El archivo no existe')
        self.x = x
        self.y = y
        self.z = z
        
    def todos(self, definicion = 100, figsize = (12,12)):
        
        #Defino el tamaño de la figura, sus subgráficos y su relacion de aspecto
        fig = plt.figure(figsize = figsize)
        gs = GridSpec(nrows=2, ncols=2, width_ratios=[5, 1], height_ratios=[1, 5])
        fig.subplots_adjust(wspace=0, hspace=0)
        fig.suptitle('Todos los datos en el plano x-y', fontsize=25)
        
        #Mapa de colores
        ax0 = fig.add_subplot(gs[1, 0])
        ax0.hist2d(self.x, self.y, bins = definicion)
        ax0.set_xlabel('Dirección X', fontsize=20)
        ax0.set_ylabel('Dirección Y', fontsize=20)

        #Histograma superior
        ax1 = fig.add_subplot(gs[0, 0])
        n, bins, patches = ax1.hist(self.x, bins = definicion, facecolor='#2ab0ff', edgecolor='#e0e0e0',
                                    linewidth=0.5, alpha=0.9)
        ax1.axis('off')
        #Color acorde al mapa de colores
        for i in range(len(patches)):
            patches[i].set_facecolor(plt.cm.viridis(n[i]/max(n)))
        
        #Histograma derecho
        ax2 = fig.add_subplot(gs[1, 1])
        n, bins, patches = ax2.hist(self.y, bins = definicion, facecolor='#2ab0ff', edgecolor='#e0e0e0',
                                    linewidth=0.5, alpha=0.9, orientation=u'horizontal')
        ax2.axis('off')
        #Color acorde al mapa de colores
        for i in range(len(patches)):
            patches[i].set_facecolor(plt.cm.viridis(n[i]/max(n)))
        plt.show()
            
    def corte(self, Z, rot = False, definicion = 100, figsize = (12,12)):
           for z in Z:
            #Acumulo la data en un solo array de np para tener mas claridad en el corte
            data = np.array([self.x, self.y, self.z]).T
            #Corto la data y la filtro
            cortes = data[:, 2]; cuchillos = (cortes >= z - 0.5) & (cortes <= z + 0.5); data_cortada = data[cuchillos]
            #Vuelvo a separar la data para generar el histograma
            x, y = data_cortada[:, 0], data_cortada[:, 1]

            #Calculo el centro de la distribucion
            xc, yc = sum(x) / len(x), sum(y) / len(y)

            if rot == True:
                #Centro la data en base al centro de la distribucion
                x, y = x - xc, y - yc; xc = 0; yc = 0
                #Calculo la recta centrada 
                A = np.array([x, np.ones(len(x))])
                a, b = np.linalg.lstsq(A.T, y, rcond=None)[0]
                #Calculo el angulo en radianes entre la recta y la horizontal
                theta = np.arctan(a)

                while abs(theta) > 1e-10:
                    #Procedo a rotar la data usando una matriz de rotacion hasta que theta sea 0
                    rotdat = np.zeros((len(x), 2)) 
                    rotdat[:,0] = x; rotdat[:,1] = y
                    #Lo rotamos con la matriz rotación
                    rotdat = rotdat.dot(np.array([[np.cos(theta), -np.sin(theta)],
                                                  [np.sin(theta), np.cos(theta)]])) 
                    x = rotdat[:, 0]; y = rotdat[:, 1]

                    #Recalculo la recta centrada 
                    A = np.array([x, np.ones(len(x))])
                    a, b = np.linalg.lstsq(A.T, y, rcond=None)[0]
                    #Recalculo el angulo en radianes entre la recta y la horizontal
                    theta = np.arctan(a)

            else:       
                #Calculo la recta 
                A = np.array([x, np.ones(len(x))])
                a, b = np.linalg.lstsq(A.T, y, rcond=None)[0]

                #Calculo el angulo en radianes entre la recta y la horizontal
                theta = np.arctan(a)
        
            #Mismo codigo que para todos pero adaptado a x e y, modificado para incluir el centro y la recta
            fig = plt.figure(figsize = figsize)
            gs = GridSpec(nrows=2, ncols=2, width_ratios=[5, 1], height_ratios=[1, 5])
            fig.subplots_adjust(wspace=0, hspace=0)
            fig.suptitle(f'z0 = {z}', fontsize=25)

            #Mapa de colores
            ax0 = fig.add_subplot(gs[1, 0])
            ax0.hist2d(x, y, bins = definicion)
            #Incluyo el centro y la recta acorde al estilo del mapa de color
            for n in range(15, 0, -1):
                ax0.plot(x, a*x + b, 'g', linewidth = 3 + 0.2*n, alpha =  0 + 1/n)
                ax0.plot(xc, yc, marker = 'o', color = 'g', markersize = 10 + 1*n, alpha = 0 + 1/n)
            ax0.plot(x, a*x + b, 'w', linewidth = 2, alpha=0.9)
            ax0.plot(xc, yc, marker = 'o', color = 'w', markersize = 10, alpha = 0.9)
            ax0.set_xlabel('Dirección X', fontsize=20)
            ax0.set_ylabel('Dirección Y', fontsize=20)

            #Histograma superior
            ax1 = fig.add_subplot(gs[0, 0])
            n, bins, patches = ax1.hist(x, bins = definicion, facecolor='#2ab0ff', edgecolor='#e0e0e0',
                                        linewidth=0.5, alpha=0.9)
            ax1.axis('off')
            #Color acorde al mapa de colores
            for i in range(len(patches)):
                patches[i].set_facecolor(plt.cm.viridis(n[i]/max(n)))

            #Histograma derecho
            ax2 = fig.add_subplot(gs[1, 1])
            n, bins, patches = ax2.hist(y, bins = definicion, facecolor='#2ab0ff', edgecolor='#e0e0e0',
                                        linewidth=0.5, alpha=0.9, orientation=u'horizontal')
            ax2.axis('off')
            #Color acorde al mapa de colores
            for i in range(len(patches)):
                patches[i].set_facecolor(plt.cm.viridis(n[i]/max(n)))
            
            plt.show()
            
    def interactivo(self, N = 10, definicion = 100, figsize = (15,12)):
        #Defino la cantidad de puntos de corte
        zs = np.linspace(self.z.min(), self.z.max(), N)
        z0 = int(zs[-1])
    
        #Acumulo la data en un solo array de np para tener mas claridad en el corte
        data = np.array([self.x, self.y, self.z]).T

        #Listas de valores medios, pendiente y ordenada al origen de la recta y angulo
        cx = []; cy = []; pend = []; oo = []; ang = []

        for z in zs:
            #Corto la data y la filtro
            cortes = data[:, 2]; cuchillos = (cortes >= z - 0.5) & (cortes <= z + 0.5); data_cortada = data[cuchillos]
            #Vuelvo a separar la data para generar el histograma
            x, y, z = data_cortada[:, 0], data_cortada[:, 1], z

            #Calculo el centro de la distribucion para cada coordenada y las agrego a un array
            xc, yc = sum(x) / len(x), sum(y) / len(y)
            cx.append(xc); cxa = np.asarray(cx); cy.append(yc); cya = np.asarray(cy)

            #Calculo las rectas de cada corte y las agrego a un array
            A = np.array([x, np.ones(len(x))])
            a, b = np.linalg.lstsq(A.T, y, rcond=None)[0]
            pend.append(a); penda = np.asarray(pend); oo.append(b); ooa = np.asarray(oo)

            #Calculo el angulo en radianes entre la recta y la horizontal para cada recta y la agrego a un array
            theta = np.arctan(a)
            ang.append(theta); anga = np.asarray(ang); angad = np.degrees(anga)
            
        #Mismo codigo que para todos pero adaptado a x e y, modificado para incluir el centro y la recta
        data = np.array([self.x, self.y, self.z]).T
        #Corto la data y la filtro
        cortes = data[:, 2]; cuchillos = (cortes >= zs[z0-1] - 0.5) & (cortes <= zs[z0-1] + 0.5); data_cortada = data[cuchillos]
        #Vuelvo a separar la data para generar el histograma
        x, y = data_cortada[:, 0], data_cortada[:, 1]
        
        fig = plt.figure(figsize = figsize)
        gs = GridSpec(nrows=3, ncols=3, width_ratios=[2, 4, 1], height_ratios=[1, 2, 2])
        fig.subplots_adjust(wspace=0, hspace=0)
        #fig.suptitle(f'z0 = {z}', fontsize=25)

        #Mapa de colores
        ax0 = fig.add_subplot(gs[1: , 1])
        ax0.hist2d(x, y, bins = definicion)
        #Incluyo el centro y la recta acorde al estilo del mapa de color
        for n in range(15, 0, -1):
            ax0.plot(x, penda[z0-1]*x + ooa[z0-1], 'g', linewidth = 3 + 0.2*n, alpha =  0 + 1/n)
            ax0.plot(cxa[z0-1], cya[z0-1], marker = 'o', color = 'g', markersize = 10 + 1*n, alpha = 0 + 1/n)
        ax0.plot(x, penda[z0-1]*x + ooa[z0-1], 'w', linewidth = 2, alpha=0.9)
        ax0.plot(cxa[z0-1], cya[z0-1], marker = 'o', color = 'w', markersize = 10, alpha = 0.9)
        ax0.set_xlabel('Dirección X', fontsize=20)

        #Histograma superior
        ax1 = fig.add_subplot(gs[0, 1])
        n, bins, patches = ax1.hist(x, bins = definicion, facecolor='#2ab0ff', edgecolor='#e0e0e0',
                                    linewidth=0.5, alpha=0.9)
        ax1.axis('off')
        #Color acorde al mapa de colores
        for i in range(len(patches)):
            patches[i].set_facecolor(plt.cm.viridis(n[i]/max(n)))

        #Histograma derecho
        ax2 = fig.add_subplot(gs[1:, 2])
        n, bins, patches = ax2.hist(y, bins = definicion, facecolor='#2ab0ff', edgecolor='#e0e0e0',
                                    linewidth=0.5, alpha=0.9, orientation=u'horizontal')
        #ax2.axis('off')
        # Turn off tick labels
        ax2.set_yticklabels([]); ax2.set_xticklabels([]); ax2.set_xticks([]); ax2.set_yticks([])
        ax2.spines['top'].set_visible(False); ax2.spines['right'].set_visible(False)
        ax2.spines['left'].set_visible(False); ax2.spines['bottom'].set_visible(False)
        ax2.set_ylabel('Dirección Y', fontsize = 20)
        ax2.yaxis.set_label_position("right")

        #Color acorde al mapa de colores
        for i in range(len(patches)):
            patches[i].set_facecolor(plt.cm.viridis(n[i]/max(n)))
        
        #Graficos de la posicion y angulo respecto al corte           
        #Angulo vs corte
        ax3 = fig.add_subplot(gs[1, 0])
        ax3.grid(); ax3.spines['bottom'].set_visible(False)
        for n in range(15, 0, -1):
            ax3.plot(zs, angad, 'y', linewidth = 3 + 0.2*n, alpha =  0 + 1/n, marker='o', markersize = 5 + 1*n)
        ax3.plot(zs, angad, color = 'white', lw = 2, marker='o')
        ax3.plot(zs[z0-1], angad[z0-1], color = 'navy', marker='o', markersize = 3)
        ax3.set_ylabel('Ángulo (grados)', fontsize = 20)

        #Posicion del centro vs corte
        ax4 = fig.add_subplot(gs[2, 0])
        ax4.grid(); ax4.spines['top'].set_visible(False)
        for n in range(15, 0, -1):
            ax4.plot(zs, cxa, color = 'limegreen', linewidth = 3 + 0.2*n, alpha =  0 + 1/n, marker='o', markersize = 5 + 1*n)
        ax4.plot(zs, cxa, color = 'limegreen', lw = 2, marker='o', label = 'x', alpha = 0.5)
        ax4.plot(zs, cxa, color = 'white', lw = 2, marker='o')
        for n in range(15, 0, -1):
            ax4.plot(zs, cya, color = 'teal', linewidth = 3 + 0.2*n, alpha =  0 + 1/n, marker='o', markersize = 5 + 1*n)
        ax4.plot(zs, cya, color = 'teal', lw = 2, marker='o', label = 'y', alpha = 0.5)
        ax4.plot(zs, cya, color = 'white', lw = 2, marker='o')
        ax4.set_ylabel('coord. centro', fontsize = 20); ax4.set_xlabel('$Z_0$', fontsize = 20); ax4.legend()
        ax4.plot(zs[z0-1], cxa[z0-1], color = 'navy', marker='o', markersize = 3)
        ax4.plot(zs[z0-1], cya[z0-1], color = 'navy', marker='o', markersize = 3)

        def onclick(event):#Acción al hacer click
            zp = event.xdata #extraemos el z
            zp = np.argmin(np.abs(zs - zp))
            
            #Mismo codigo que para todos pero adaptado a x e y, modificado para incluir el centro y la recta
            data = np.array([self.x, self.y, self.z]).T
            #Corto la data y la filtro
            cortes = data[:, 2]; cuchillos = (cortes >= zs[zp] - 0.5) & (cortes <= zs[zp] + 0.5); data_cortada = data[cuchillos]
            #Vuelvo a separar la data para generar el histograma
            x, y = data_cortada[:, 0], data_cortada[:, 1]

            fig = plt.figure(1, figsize = figsize)
            gs = GridSpec(nrows=3, ncols=3, width_ratios=[2, 4, 1], height_ratios=[1, 2, 2])
            fig.subplots_adjust(wspace=0, hspace=0)
            #fig.suptitle(f'z0 = {z}', fontsize=25)

            #Mapa de colores
            ax0 = fig.add_subplot(gs[1: , 1])
            ax0.hist2d(x, y, bins = definicion)
            #Incluyo el centro y la recta acorde al estilo del mapa de color
            for n in range(15, 0, -1):
                ax0.plot(x, penda[zp]*x + ooa[zp], 'g', linewidth = 3 + 0.2*n, alpha =  0 + 1/n)
                ax0.plot(cxa[zp], cya[zp], marker = 'o', color = 'g', markersize = 10 + 1*n, alpha = 0 + 1/n)
            ax0.plot(x, penda[zp]*x + ooa[zp], 'w', linewidth = 2, alpha=0.9)
            ax0.plot(cxa[zp], cya[zp], marker = 'o', color = 'w', markersize = 10, alpha = 0.9)
            ax0.set_xlabel('Dirección X', fontsize=20)

            #Histograma superior
            ax1 = fig.add_subplot(gs[0, 1])
            n, bins, patches = ax1.hist(x, bins = definicion, facecolor='#2ab0ff', edgecolor='#e0e0e0',
                                        linewidth=0.5, alpha=0.9)
            
            #Color acorde al mapa de colores
            for i in range(len(patches)):
                patches[i].set_facecolor(plt.cm.viridis(n[i]/max(n)))
                
            # Turn off tick labels
            ax1.set_yticklabels([]); ax1.set_xticklabels([]); ax1.set_xticks([]); ax1.set_yticks([])
            ax1.spines['top'].set_visible(False); ax1.spines['right'].set_visible(False)
            ax1.spines['left'].set_visible(False); ax1.spines['bottom'].set_visible(False)


            #Histograma derecho
            ax2 = fig.add_subplot(gs[1:, 2])
            n, bins, patches = ax2.hist(y, bins = definicion, facecolor='#2ab0ff', edgecolor='#e0e0e0',
                                        linewidth=0.5, alpha=0.9, orientation=u'horizontal')
            
            # Turn off tick labels
            ax2.set_yticklabels([]); ax2.set_xticklabels([]); ax2.set_xticks([]); ax2.set_yticks([])
            ax2.spines['top'].set_visible(False); ax2.spines['right'].set_visible(False)
            ax2.spines['left'].set_visible(False); ax2.spines['bottom'].set_visible(False)
            ax2.set_ylabel('Dirección Y', fontsize = 20)
            ax2.yaxis.set_label_position("right")

            #Color acorde al mapa de colores
            for i in range(len(patches)):
                patches[i].set_facecolor(plt.cm.viridis(n[i]/max(n)))

            #Graficos de la posicion y angulo respecto al corte           
            #Angulo vs corte
            ax3 = fig.add_subplot(gs[1, 0])
            ax3.grid(); ax3.spines['bottom'].set_visible(False)
            for n in range(15, 0, -1):
                ax3.plot(zs, angad, 'y', linewidth = 3 + 0.2*n, alpha =  0 + 1/n, marker='o', markersize = 5 + 1*n)
            ax3.plot(zs, angad, color = 'white', lw = 2, marker='o')
            ax3.plot(zs[zp], angad[zp], color = 'navy', marker='o', markersize = 3)
            ax3.set_ylabel('Ángulo (grados)', fontsize = 20)

            #Posicion del centro vs corte
            ax4 = fig.add_subplot(gs[2, 0])
            ax4.grid(); ax4.spines['top'].set_visible(False)
            for n in range(15, 0, -1):
                ax4.plot(zs, cxa, color = 'limegreen', linewidth = 3 + 0.2*n, alpha =  0 + 1/n, marker='o', markersize = 5 + 1*n)
            ax4.plot(zs, cxa, color = 'limegreen', lw = 2, marker='o', label = 'x', alpha = 0.5)
            ax4.plot(zs, cxa, color = 'white', lw = 2, marker='o')
            for n in range(15, 0, -1):
                ax4.plot(zs, cya, color = 'teal', linewidth = 3 + 0.2*n, alpha =  0 + 1/n, marker='o', markersize = 5 + 1*n)
            ax4.plot(zs, cya, color = 'teal', lw = 2, marker='o', label = 'y', alpha = 0.5)
            ax4.plot(zs, cya, color = 'white', lw = 2, marker='o')
            ax4.set_ylabel('coord. centro', fontsize = 20); ax4.set_xlabel('$Z_0$', fontsize = 20); ax4.legend()
            ax4.plot(zs[zp], cxa[zp], color = 'navy', marker='o', markersize = 3)
            ax4.plot(zs[zp], cya[zp], color = 'navy', marker='o', markersize = 3)
            
            ax0.figure.canvas.draw()
            ax1.figure.canvas.draw()
            ax2.figure.canvas.draw()

        fig.canvas.mpl_connect('button_press_event', onclick)# se vincula la función onclick con el click
        plt.pause(1000)
        plt.show(1)




parser = argparse.ArgumentParser()


parser.add_argument("-f", "--file", type=str, required = True) 
parser.add_argument("-t", "--todos", action='store_true') 
parser.add_argument("-z", "--corte", nargs = '+', type=float)
parser.add_argument("-i", "--interactivo",action='store_true')
parser.add_argument("-r", "--transform", action='store_true')
parser.add_argument("-d", "--definicion", action = 'store', dest = 'definicion', type = int, default = 100)
parser.add_argument('-N', '--Ndatos', type=int, action = 'store', dest = 'N', default = 10)
args = parser.parse_args()
if args.todos:
    Analisis3D(args.file).todos(args.definicion)
if args.corte != None:
    Analisis3D(args.file).corte(args.corte, args.transform, args.definicion)
if args.interactivo:
    Analisis3D(args.file).interactivo(args.N, args.definicion)
