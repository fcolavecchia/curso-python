import time
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from PIL import Image, ImageTk
import random
import math
from matplotlib.pyplot import text
import numpy as np
import re
import argparse
import sys
import os

parser = argparse.ArgumentParser(description='Juego de dados: La Generala')
parser.add_argument('-n', action='append', nargs='+',
    help='Agrega un jugador -n Nombre')
parser.add_argument('-ai',action='store_true',
    help='Agrega Un jugador controlado por la computadora')
parser.add_argument('-noGUI',action ='store_true',
    help='''Jugar la versión de texto del juego. 
    Para seleccionar los dados que se desean guardar tipear su posición.
    EJ: tirada  2 2 4 5 6
    si quiere guardar los 2 debe escribir 12.''')
parser.add_argument('-test', action ='store_true',
help='Modo automático, juega solo la maquina')

args = parser.parse_args()
nombres= []
if args.n:
    for name in args.n:
        nombres.append(name)
else:
    nombres=['Player']

def close_window():
        global running, win,juego
        running = False 
        win.destroy()
        del juego
        sys.exit(0)

class Dado:
    """Clase que define un dado. Para otros juegos se puede
    cambiar la cantidad de caras. El default es 6"""
    def __init__(self,caras=6,noGUI=False):
        
        self.value = None
        self.caras = caras
        self.fijo = False
##        self.image_path = {'1':"img/dice-1.png",'2':"img/dice-2.png",'3':"img/dice-3.png",
##                            '4':"img/dice-4.png",'5':"img/dice-5.png",'6':"img/dice-6.png",
##                            '1f':"img/dice-1f.png",'2f':"img/dice-2f.png",'3f':"img/dice-3f.png",
##                            '4f':"img/dice-4f.png",'5f':"img/dice-5f.png",'6f':"img/dice-6f.png"}
        self.image_path = {'1':os.path.join("img","dice-1.png"),'2':os.path.join("img","dice-2.png"),'3':os.path.join("img","dice-3.png"),
                            '4':os.path.join("img","dice-4.png"),'5':os.path.join("img","dice-5.png"),'6':os.path.join("img","dice-6.png"),
                            '1f':os.path.join("img","dice-1f.png"),'2f':os.path.join("img","dice-2f.png"),'3f':os.path.join("img","dice-3f.png"),
                            '4f':os.path.join("img","dice-4f.png"),'5f':os.path.join("img","dice-5f.png"),'6f':os.path.join("img","dice-6f.png")}
        
        if not noGUI:
            self.image ={'1': self.update_image('1',(150,150)),
                        '2': self.update_image('2',(150,150)),
                        '3': self.update_image('3',(150,150)),
                        '4': self.update_image('4',(150,150)),
                        '5': self.update_image('5',(150,150)),
                        '6': self.update_image('6',(150,150)),
                        '1f': self.update_image('1f',(150,150)),
                        '2f': self.update_image('2f',(150,150)),
                        '3f': self.update_image('3f',(150,150)),
                        '4f': self.update_image('4f',(150,150)),
                        '5f': self.update_image('5f',(150,150)),
                        '6f': self.update_image('6f',(150,150)),}
        self.image_container = None

    def tirar(self):
        self.value = random.randint(1,self.caras)

    def liberar(self):
        self.fijo = False

    def fijar(self):
        self.fijo = True
    
    def fijar2(self,jugador = None):
        """Funcion para cambiar el estado de los dados mediante clicks. la llama el metodo
        fijar de Cubilete"""
        if jugador:
            if jugador.restantes ==3:
                pass
            else:
                if self.fijo:
                    self.fijo = False
                else:
                    self.fijo = True
        else:
            if self.fijo:
                self.fijo = False
            else:
                self.fijo = True

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return f'{self.value}'
    
    def update_image(self,n,size):
        path = self.image_path[n]
        return ImageTk.PhotoImage(Image.open(path).resize(size, Image.ANTIALIAS))

class Cubilete:
    """Clase que define un Cubilete, en la función __init__ puede elegirse
    la cantidad de dados que tiene el cubilete para poder jugar distintos juegos.
    Por defecto son 5 dados."""
    def __init__(self,N=5,noGUI=False):
        self.noGUI = noGUI
        self.dados = []
        self.jugada = []
        self.numeros =[]
        self.nDados = N
        self.separados = []
        for i in range(N):
            self.dados.append(Dado(noGUI=self.noGUI))

    def tirar(self):
        """Método de Cubilete para simular una tirada de cubilete"""
        self.jugada = []
        self.numeros = []
        for dado in self.dados:
            if not dado.fijo :
                dado.tirar()
            self.jugada.append(dado.value)
        self.cuenta() # crea el array self.numeros cant de veces qeu salio el dado
        self.nPuntos() #calcula el puntaje de los numeros los guarda self.puntosN
        return self.jugada 
    
    def reset(self):
        self.dados = []
        self.separados = []
        for i in range(self.nDados):
            self.dados.append(Dado())

    def liberar(self):
        for dado in self.dados:
            dado.liberar()       

    def cuenta(self):
        """Método de Cubilete que recuenta el resultado de la tirada y lo
        guerda en self.numeros.
        EJ:[2,2,3,6,5] --> [0,2,1,0,1,1]"""
        for i in range(1,7):
            self.numeros.append(self.jugada.count(i))
  
    def nPuntos(self):
        """Método de Cubilete calcula la cantidad de puntos que se podría anotar en 
        cada número"""
        self.puntosN = np.array(self.numeros)*np.array(range(1,7))

    def analizar(self,jugador):
        """Método que analiza los juegos hechos en la tirada."""
        self.objetivos = []
        #print(f'1: {self.numeros[0]}, 2: {self.numeros[1]}, 3: {self.numeros[2]}, 4: {self.numeros[3]}, 5: {self.numeros[4]}, 6: {self.numeros[5]}')
        j1 = self.numeros
        if j1.count(0) < 2 and 0 not in j1[2:5]:
            self.objetivos.append('escalera')
        elif max(j1) == 4:
            """Si se saca 5 dados iguales no se puede anotar como Poker."""
            self.objetivos.append('poker')
        elif max(j1) == 5:
            if 'generala' in jugador.falta:
                self.objetivos.append('generala')
            else:
                self.objetivos.append('generala doble')
        elif 3 in j1 and 2 in j1:
            """Si se hace Full no vale anotarse par."""
            self.objetivos.append('full')
        elif j1.count(2) == 2 :
            self.objetivos.append('par')
        self.objetivos.append(self.puntosN)

    def fijar(self,dado,root,juego):
        
        jugador = juego.jugadores[juego.leToca]
        dado.fijar2(jugador)
        
        if  dado.fijo:
            
            root.itemconfig(dado.image_container,image=dado.image.get(str(dado.value)+'f'))
        else:
            root.itemconfig(dado.image_container,image=dado.image.get(str(dado.value)))
    
    def limpiar(self,juego):
        for dado in self.dados:
            if running:
                juego.canvas.itemconfig(dado.image_container,image=dado.image.get(str(dado.value)))
            
            

class Jugador:
    def __init__(self,name='Player',N=3,ai=False):
        """EL jugador se llama Player por defecto y tiene 3 tiradas por turno"""
        self.juegos = {'par': 10,'escalera': 20, 'full': 30, 'poker': 40, 'generala': 50, 'generala doble':100}
        if type(name)==list:
            name = name[0]
        self.name = name
        self.nTiradas = N
        self.restantes = N
        self.tabla ={'1': None, '2': None, '3': None,
                    '4': None, '5': None, '6': None,
                    'par': None,'escalera': None,
                    'full': None, 'poker': None,
                    'generala': None, 'generala doble':None,}
        self.falta = []
        self.enJuego = True
        self.puntos = 0
        self.entryNombre = ""
        self.tablaGUI = {}
        self.ai = ai

    def resetTabla(self):
        self.tabla ={'1': None, '2': None, '3': None,
                    '4': None, '5': None, '6': None,
                    'par': None,'escalera': None,
                    'full': None, 'poker': None,
                    'generala': None, 'generala doble':None,}

    def resetTurnos(self):
        "Vuelve a 3 el numero de tiradas, se llama después de finalizar un turno"
        self.restantes = self.nTiradas
    
    def pendientes(self):
        """Función que verifica que juegos le faltan al jugador y los guarda en
        la lista self.falta"""
        self.falta = []
        for key in self.tabla:
            if self.tabla[key] is None:
                self.falta.append(key)
        if len(self.falta) == 0:
            self.enJuego = False
        
        return self.falta

    def tachar(self):
        self.pendientes()
        if 'generala doble' in self.falta and 'generala' in self.falta:
            self.falta.remove('generala')

        print(f'Te podés tachar {self.falta}')
        while True:
            rta = input('¿Que tachas?')
            try:
                self.tabla[rta]
                self.tabla[rta] = 0
                print(f'Te tachaste {rta}') 
                break
            except:
                print('Escribí el juego que quieras tachar')


    def desanotar(self):
        self.posibles = {}

    def anotar(self,objetivos):
        """actualiza jugador.posibles, un diccionario con los juegos que faltan y
        el puntaje correspondiente, teniendo en cuenta que si se logra el juego en 
        el primer tiro vale 5 puntos más"""
        self.posibles = {}
        if self.restantes == self.nTiradas:
            servido = 5
        else:
            servido = 0
        # Si objetivos tiene más de un elemento el primero si o si es un juego
        # el segundo es la lista de los puntajes para cada numero 
        if len(objetivos)>1:
            #Me fijo que no se haya anotado ese juego antes
            #print(f'Hay juego: {objetivos[0]}')

            if self.tabla[objetivos[0]] is None:
                self.posibles[objetivos[0]]= self.juegos[objetivos[0]] + servido

        for i,pts in enumerate(objetivos[-1]):
            if self.tabla[str(i+1)] is None:
                self.posibles[str(i+1)] = objetivos[-1][i]
    

           
    

class Juego:
    def __init__(self,root=None,N=2, nombres = None, noGUI = False):
        if not nombres:
            nombres = [f"Jugador {i}" for i in range(1,N+1)]
        self.nombres = nombres
        if args.ai:
            self.nombres.append('Terminator')
        self.njugadores = N
        self.jugadores = []
        self.positivos = ('si','y','yes','sí')
        self.negativos = ('no','n')
        self.cubi = Cubilete(noGUI=noGUI)
        self.noGUI = noGUI
        self.root = root
        self.esperando = True
        for i in range(self.njugadores):
            if args.test:
                self.jugadores.append(Jugador(name=nombres[i],ai=True))
            else:
                self.jugadores.append(Jugador(name=nombres[i]))
        if args.ai:
            self.jugadores.append(Jugador(name='Terminator',ai=True))
    
    def anotar_puntajes(self,jugador):
        "muestra los valores de jugador.tabla en la tabal del canvas"
        total = 0
        for key in jugador.tabla:
            if jugador.tabla[key] and running:
                jugador.tablaGUI[key].config(text =jugador.tabla[key])
                total += jugador.tabla[key]
            if jugador.tabla[key] == 0 and running:
                jugador.tablaGUI[key].config(text ="X")
        jugador.labelTotal.config(text= total)
        
    def resetTablaGUI(self):
        """Borra las jugadas de la partida de la tabla GUI"""
        for jugador in self.jugadores:
            for key in jugador.tablaGUI:
                jugador.tablaGUI[key].config(text ="")

    def anotar_tachar(self):
        """Muestra una ventana emergente para seleccionar que anotarse"""
        global x,y,button
        cartel = Toplevel(win,takefocus=True)
        button.config(state=DISABLED)
        cartel.overrideredirect(True)
        cartel.geometry(f'300x400+{int(x)+325}+{int(y)+125}')
        cartel.transient()
        win.update_idletasks()
        jugador = self.jugadores[self.leToca]
        jugador.pendientes()
        if 'generala doble' in jugador.falta and 'generala' in jugador.falta:
            jugador.falta.remove('generala')
        A = StringVar()    
        T = StringVar()
        self.tachButt = ttk.Button(cartel,text='Tachar',
        command=lambda :self.tacharGUI(cartel,T),state=DISABLED )
        self.tachButt.grid(column=7,row= 1,columnspan= 3,)
        if len(jugador.posibles)>0:
            self.anoButt= ttk.Button(cartel,text='Anotar',
                       command=lambda:self.anotarGUI(cartel,A),state=DISABLED)
            self.anoButt.grid(column=4,row= 1,columnspan= 3)  
            print(f'posibles {jugador.posibles}')
            for (i,juego) in enumerate(jugador.posibles):
                cartel.rb = Radiobutton(cartel, text = juego, variable = A,value = juego,
                command=self.activarAnotar,tristatevalue='x')
                cartel.rb.deselect()
                cartel.rb.grid(column=5,row=i+3)
                puntos = Label(cartel,text=jugador.posibles[juego])
                puntos.grid(column=6,row=i+3)
        
        for i,juego in enumerate(jugador.falta):
            cartel.rb = Radiobutton(cartel, text = juego, variable = T,
            value = juego,command=self.activarTachar,tristatevalue='x' )
            cartel.rb.grid(column=7,row=i+3)
            cartel.rb.deselect()
   
    def activarAnotar(self):
        self.anoButt.config(state=NORMAL)
        
    
    def activarTachar(self):
        self.tachButt.config(state=NORMAL)
  
    def anotarGUI(self,ventana,A):
        juego = A.get()
        jugador = self.jugadores[self.leToca]
        print(f'Te vas a anotar {juego}')
        jugador.tabla[juego] = jugador.posibles[juego]
        self.anotar_puntajes(jugador)
        ventana.destroy()
        self.esperando = False
        button.config(state=NORMAL)
    
    def tacharGUI(self,ventana,T):
        juego = T.get()
        jugador =self.jugadores[self.leToca] 
        print(f'Te vas a tachar {juego}')
        jugador.tabla[juego] = 0
        self.anotar_puntajes(jugador)
        ventana.destroy()
        self.esperando = False
        button.config(state=NORMAL)
                     
    def jugar(self):
        """El main loop del juego"""
        global running
        self.ronda = 1
        while  self.jugadores[-1].enJuego and running:
            print(f'Ronda número: {self.ronda}')
            for i, jugador in enumerate(self.jugadores):
                self.leToca = i
                if not self.noGUI:
                    if jugador.ai:
                        self.turnoAI(jugador)
                    else:
                        self.turnoGUI(jugador)
                else:
                    self.turno(jugador)
            self.ronda += 1
            if self.ronda >12:
                jugador.enJuego = False
        ##      Fin de juego      ##    
        if running:
            clasificacion = self.puntaje()
            gana = [key for key,value in clasificacion.items() if value ==max(clasificacion.values())]
            ganador = gana[0]
            if not self.noGUI:
                if len(gana) == 1:
                    messagebox.showinfo(title='Final del juego',message=f'Ganó {ganador} con {clasificacion[ganador]} puntos.')
                else:
                    messagebox.showinfo(title='Final del juego',message=f'Hubo empate entre {gana}')
                rta = messagebox.askyesno(title='Fin',message='¿Desea jugar de nuevo?')
                if rta:
                    for jugador in self.jugadores:
                        jugador.resetTabla()
                        jugador.enJuego = True
                        self.anotar_puntajes(jugador)
                    self.resetTablaGUI()
                    self.jugar()
                else:
                    close_window()
            else:
                print('Juego Terminado')
                print(clasificacion)
                if len(gana) == 1:
                    print(f'Ganó {ganador}')
                else:
                    print(f'Hubo empate entre {gana}')
            
    def puntaje(self):
        resultados = {}
        for jugador in self.jugadores:
            total = 0
            for key in jugador.tabla:
                if jugador.tabla[key]:
                    total += jugador.tabla[key]
            jugador.puntos = total
            resultados[jugador.name] = total
        posiciones = {k: v for k, v in sorted(resultados.items(), key=lambda item: item[1])}
        return posiciones
    
    def seleccion(self):
        while True:
            rta = re.sub(r"\D" ,"" ,input('¿Que dados queres guardar? : \n'))
            if re.search("[1-5]", rta) and len(rta) <5:
                return rta
            elif rta == '':
                return ''
            else:
                print('escribi numeros del 1 al 5 sin repeticiones')
  
    def printabla(self):
        """Tabla de puntos texto."""
        jugador = self.jugadores[0]
        juegos = [juego[0].upper() for juego in jugador.tabla.keys()]
        juegos[-1] = 'GD'
        puntos = []
        for jugador in self.jugadores:
            valores_crudo = jugador.tabla.values()
            valores = []
            for valor in valores_crudo:
                if valor is None:
                    valor = 0
                valores.append(valor)
            puntos.append(valores) 
        
        fila = "{:>5}" * (len(juegos) + 1)
        print(fila.format("", *juegos))
        for player, row in zip(self.nombres, puntos):
            print(fila.format(player[0], *row))

    def turnoAINoGUI(self,jugador):
        print(f'Turno de {jugador.name}')
        jugador.resetTurnos()
        self.cubi.liberar()
        while jugador.restantes >0 and running:
            self.cubi.tirar()
            print(*self.cubi.dados)
            jugador.pendientes()
            self.cubi.analizar(jugador) 
            jugador.anotar(self.cubi.objetivos)

            if len(self.cubi.objetivos) == 2: 
                # Si hay juego y lo puede anotar lo anota
                if jugador.restantes ==2 and self.cubi.objetivos[0]=='poker':
                    #Si sale poker en el segundo tiro se la juega por la generala
                    pass
                elif self.cubi.objetivos[0] in jugador.falta and running:
                        jugador.restantes = 0
                        jugador.tabla[self.cubi.objetivos[0]] = jugador.posibles[self.cubi.objetivos[0]]
                        print(f'{jugador.name} se anotó {self.cubi.objetivos[0]} por {jugador.posibles[self.cubi.objetivos[0]]}')

            self.fijarAI(jugador)
            if jugador.restantes == 1:
                maxrep = 0
                keymax = 0
                for key in jugador.posibles:
                    n_rep = jugador.posibles[key]/int(key)
                    
                    if n_rep > maxrep:
                        maxrep = n_rep
                        keymax = key
                        
                if maxrep > 0:
                    jugador.tabla[keymax] = jugador.posibles[keymax]
                    print(f'{jugador.name} se anota {jugador.posibles[keymax]} al {keymax}')
                else:
                    if 'generala doble' in jugador.falta and 'generala' in jugador.falta:
                        jugador.falta.remove('generala')
                    tacho = '0'
                    n_intentos = 0
                    while len(tacho)<2 and n_intentos<5:
                        #No se tachan números s menos que no quede otra opción
                        tacho = random.choice(jugador.falta)
                        n_intentos +=1
                    jugador.tabla[tacho] = 0
                    print(f'{jugador.name} se tachó {tacho}')
            jugador.restantes -=1
            #self.cubi.liberar()
            

        

    def turnoAI(self,jugador):
        global canvas
        self.printabla()
        print(f'Turno de {jugador.name}')
        jugador.resetTurnos()
        leToca = False
        while jugador.restantes >0 and running:
            
            if not self.noGUI:
                if running:
                    self.root.update()
                    if not leToca:
                        jugador.entryNombre.config(fg='red')
                        leToca = True
                else:
                    break
                self.animacion(canvas)
                print(*self.cubi.dados)
                self.aiChoise(jugador)
        if running:        
            messagebox.showinfo(title=f'Fin de turno  ', message=f'El turno de {jugador.name} ha finalizado')    
            self.cubi.liberar()
            self.cubi.limpiar(self)
            jugador.resetTurnos()
            jugador.entryNombre.config(fg = 'blue')

    def aiChoise(self,jugador):
        """Estrategia de ai con GUI"""
        for dado in self.cubi.dados:
            if not dado.fijo and running:
                canvas.itemconfig(dado.image_container,image=dado.image.get(str(dado.value)))
        if running:
            canvas.update_idletasks()
        now = time.time()
        jugador.pendientes()
        self.cubi.analizar(jugador) # Analizo si hay juegos
        jugador.anotar(self.cubi.objetivos)
        while time.time()-now <1.5 and running:
            self.root.update()
        
        if len(self.cubi.objetivos) == 2: 
            
            if jugador.restantes ==2 and self.cubi.objetivos[0]=='poker':
                #Si sale poker en el segundo tiro se la juega por la generala
                pass
            elif self.cubi.objetivos[0] in jugador.falta and running:# Si hay juego y lo puede anotar lo anota
                    jugador.restantes = 0
                    jugador.tabla[self.cubi.objetivos[0]] = jugador.posibles[self.cubi.objetivos[0]]
                    self.anotar_puntajes(jugador)
                    messagebox.showinfo(title='Resultados',message=f'{jugador.name} se anota {self.cubi.objetivos[0]}')
        self.fijarAI(jugador)
        while time.time()-now <2:
            pass
        #Fin de turno anotar o tachar
        if jugador.restantes == 1:
            maxrep = 0
            keymax = 0
            for key in jugador.posibles:
                n_rep = jugador.posibles[key]/int(key)
                
                if n_rep > maxrep:
                    maxrep = n_rep
                    keymax = key
                    
            if maxrep > 0:
                jugador.tabla[keymax] = jugador.posibles[keymax]
                self.anotar_puntajes(jugador)
                messagebox.showinfo(title='Resultados',message=f'{jugador.name} se anota {jugador.posibles[keymax]} al {keymax}')
            else:
                if 'generala doble' in jugador.falta and 'generala' in jugador.falta:
                    jugador.falta.remove('generala')
                tacho = '0'
                n_intentos = 0
                while len(tacho)<2 and n_intentos<5:
                    #No se tachan números s menos que no quede otra opción
                    tacho = random.choice(jugador.falta)
                    n_intentos +=1

                jugador.tabla[tacho] = 0
                messagebox.showinfo(title='Resultados',message=f'{jugador.name} se tachó {tacho}.')
                self.anotar_puntajes(jugador)
        jugador.restantes -=1
                    
    def fijarAI(self,jugador):
        """Estrategia de AI, se fija cuales son los dados repetidos y los fija,
         si hay más de uno guarda los dados del valor que no haya anotado todavia"""
        global args
        self.cubi.liberar()
        if not args.noGUI:
            self.cubi.limpiar(self)
        N_fijar = max(self.cubi.numeros) # numero de dados repetidos
        num = None
        num2 = None
        if N_fijar > 1:
            num = self.cubi.numeros.index(N_fijar) + 1 # valor del dado más repetido
            
            if self.cubi.numeros.count(N_fijar) > 1:
                #Si hay 2 pares num2 es el segundo numero que se repite
                num2 = 6 - self.cubi.numeros[::-1].index(N_fijar)
                
                if num2 in jugador.falta and num not in jugador.falta:
                    """Si hay 2 numeros repetidos distintos y uno de ellos no lo tiene 
                    anotado lo elige para fijar"""
                    num = num2
                    
            if str(num) in jugador.falta or 'generala' in jugador.falta or 'generala doble' in jugador.falta or 'poker' in jugador.falta:
                for dado in self.cubi.dados:
                    if dado.value == num:
                        dado.fijar()
                        
                        if not args.noGUI and running:
                            canvas.itemconfig(dado.image_container,image=dado.image.get(str(dado.value)+'f'))
                            self.root.update()
            # elif num2 in jugador.falta:
            #     for dado in self.cubi.dados:
            #         if dado.value == num2:
            #             dado.fijar()
            #             if not args.noGUI and running:
            #                 canvas.itemconfig(dado.image_container,image=dado.image.get(str(dado.value)+'f'))
            #                 self.root.update()
        else:
            for dado in self.cubi.dados:
                if str(dado.value) in jugador.falta:
                    dado.fijar()
                    if not args.noGUI and running:
                            canvas.itemconfig(dado.image_container,image=dado.image.get(str(dado.value)+'f'))
                            self.root.update()
                break
    
    def turnoHumano(self,jugador):
        while jugador.restantes >0:
                print('Resultado de la tirada:')
                print(*self.cubi.tirar()) # realizo la tirada (Cubilete)
                self.cubi.liberar() # Libero los dados guardados
                self.cubi.analizar(jugador) # Analizo si hay juegos
                jugador.anotar(self.cubi.objetivos)
                if len(self.cubi.objetivos) == 2: 
                    #Solo si hay juego
                    if self.cubi.objetivos[0] in jugador.falta:
                        #Si no lo anotó o tachó
                        rta =input(f'¿Te anotas? {self.cubi.objetivos[0]} por {jugador.posibles[self.cubi.objetivos[0]]} puntos ... ')
                        if rta.lower() in self.positivos:
                            jugador.restantes = 0
                            jugador.tabla[self.cubi.objetivos[0]] = jugador.posibles[self.cubi.objetivos[0]]
                            print(f'Anotaste {self.cubi.objetivos[0]} por {jugador.posibles[self.cubi.objetivos[0]]}')
                            print('-'*30)
                            break
                    else:
                        print(f'Lamentable no te sirve.')
                if jugador.restantes == 3:
                    print('Te quedan 2 tiros')
                elif jugador.restantes == 1:
                    print('Te quedaste sin tiros')
                    if len(jugador.posibles)>0:
                        while True:
                            if len(jugador.posibles):
                                print('Los juegos que podes anotar son')
                                print('Juegos :',*jugador.posibles,'\n'
                                ,'Puntos :', *jugador.posibles.values())
                            rta = input('Anotar [a] / Tachar [t]')
                            if rta.lower() in ['a']:
                                print('Elegiste anotar')
                                while True:
                                    try:
                                        rta = input('¿Qué anotas? \n')
                                        jugador.tabla[rta] = jugador.posibles[rta]
                                        self.cubi.liberar()
                                        print(f'Anotaste {rta} por {jugador.posibles[rta]} puntos.')
                                        print('-'*30)
                                        break
                                    except:
                                        print('El juego ingresado es inválido')
                            elif rta.lower() in ['t']:
                                print('Elegiste tachar')
                                jugador.tachar()
                                print('-'*30)
                                break
                            else:
                                print('No entendí')
                                continue
                            break
                        break
                    else:
                        print('No podes anotarte ningún juego.')
                        jugador.tachar()
                        print('-'*30)
                        break

                elif jugador.restantes ==2:
                    print('Te queda un tiro')    
                seleccion = self.seleccion()
                separados = [self.cubi.dados[int(num)-1] for num in seleccion]

                for dado in separados:
                    dado.fijar()
                else:
                    print(f'Guardaste ',*separados)
                jugador.restantes -=1

    def turno(self,jugador):
        self.printabla()
        print(f'Turno de {jugador.name}')
        jugador.resetTurnos()
        print(f'{jugador.name} te falta ',*jugador.pendientes())
        if not jugador.ai:
            self.turnoHumano(jugador)
        else:
            self.turnoAINoGUI(jugador) 
            


    def turnoGUI(self,jugador):
        """Función de turno si está activada la interfaz gráfica"""
        global running
        jugador.resetTurnos()
        jugador.pendientes()
        messagebox.showinfo(title=f'Ronda : {self.ronda}', message=f'Turno de {jugador.name}')
        leToca = False
        
        while jugador.restantes >0 :
            if running:
                self.root.update()
                if not leToca:
                    jugador.entryNombre.config(fg='red')
                    leToca = True
            if not running:
                break
                    
        if running:        
            messagebox.showinfo(title=f'Fin de turno  ', message=f'El turno de {jugador.name} ha finalizado')    
            self.cubi.liberar()
            self.cubi.limpiar(self)
            jugador.resetTurnos()
            jugador.entryNombre.config(fg = 'blue')

    def mesa(self,root):
        """Crea los elementos de la interfaz gráfica"""
        x0 = 100
        y0 = 60
        lado = 150
        gapH = 15
        gapV = 15
        x1 = x0 + lado/2
        y1 = y0 + gapV + lado

        posiciones = ((x0,y0),(x0+lado+gapH,y0),(x0+2*(lado+gapH),y0),(x1,y1),(x1+lado+gapH,y1))
        self.canvas = root
        for i,dado in enumerate(self.cubi.dados):
            dado.image_container = root.create_image(posiciones[i][0],posiciones[i][1], anchor="nw",image=dado.image.get(str(i+1)))
            root.tag_bind(dado.image_container, '<Button-1>',lambda event, dado=dado, root = root: self.cubi.fijar(dado,root,self))
    
    def Table(self,root):
        """Crea la tabla de la interfaz gráfica."""     
        for i,jugador in enumerate(self.jugadores):
            self.e = Label(root, width=8, fg='blue',
                        font=('Arial',14,'bold'))
            self.e.grid(row=i+2, column=0)
            self.e.config(text=jugador.name)
            jugador.entryNombre =self.e
            jugador.labelTotal = Label(root,width=3, fg='black',font=('Arial',16,'bold'))
            jugador.labelTotal.grid(row=i+2,column=14)
        
        for j,juego in enumerate(jugador.tabla.keys()):
            self.e = Label(root, width=3, fg='blue',
                        font=('Arial',16,'bold'))
            self.e.grid(row=1, column=j+1)
            if juego == 'generala doble':
                texto = 'GD'
            else:
                texto = juego[0].upper()
            self.e.config(text = texto)
            for i,jugador in enumerate(self.jugadores):
                self.pts = Label(root, width=3, fg='black',
                        font=('Arial',16,'bold'))
                self.pts.grid(row=i+2, column=j+1)
                jugador.tablaGUI[juego] = self.pts
        self.ltot = Label(root,width=4, fg='black',font=('Arial',16,'bold'),text='Tot')
        self.ltot.grid(column=14,row=1)
        root.pack()

    def animacion(self,root):
        "Animación de la tirada de dados + tirada"
        now = time.time()
        while time.time()-now < 1:
            if running:
                root.update_idletasks()
                root.update()

            if math.ceil(time.time()*330)%3 ==0:
                n = [random.randint(0,6) for _ in range(6)]
                for i,dado in enumerate(self.cubi.dados):
                    if not dado.fijo and running:
                        root.itemconfig(dado.image_container,image=dado.image.get(str(n[i])))
        self.cubi.tirar()

    def roll(self,root):
        """tirada de dados. """
        global running
        jugador = self.jugadores[self.leToca]
        self.animacion(root)
        self.cubi.analizar(jugador) # Analizo si hay juegos
        jugador.anotar(self.cubi.objetivos)

        for dado in self.cubi.dados:
            if not dado.fijo:
                root.itemconfig(dado.image_container,image=dado.image.get(str(dado.value)))
        if running:
            root.update_idletasks()

        if len(self.cubi.objetivos) == 2:
            if self.cubi.objetivos[0] in jugador.falta:
                    if messagebox.askyesno(title='Salió juego',message=f'¿Te anotas {self.cubi.objetivos[0]} por {jugador.posibles[self.cubi.objetivos[0]]}  puntos?'):
                        jugador.restantes = 0
                        jugador.tabla[self.cubi.objetivos[0]] = jugador.posibles[self.cubi.objetivos[0]]
                        self.anotar_puntajes(jugador)
                        print('-'*30)
                        return
        
        if self.jugadores[self.leToca].restantes ==1:
            messagebox.showinfo(title='Fin del Turno', message='Te quedaste sin tiros.')
            self.anotar_tachar()
            while self.esperando:
                if running:
                    root.update()
                else:
                    break
                
            self.esperando = True
        
        self.jugadores[self.leToca].restantes -=1


if __name__ == "__main__":
    noGUI = args.noGUI
    if not noGUI:
        win= Tk()
        
        # Tamaño de la pantalla
        ancho_pantalla = win.winfo_screenwidth() 
        alto_pantalla = win.winfo_screenheight() 
        #Tamaño de la ventana
        ancho = 900
        alto = 650
        # Para que la ventana abra en el medio de la pantalla
        x = (ancho_pantalla/2) - (ancho/2)
        y = (alto_pantalla/2) - (alto/2)
        win.geometry(f"{ancho}x{alto}+{int(x)}+{int(y)}")
        
        win.title('Generala')
        icono = PhotoImage(file="img/icono.png")
        win.iconphoto(True,icono)


        canvas= Canvas(win, width=650, height= 450,bg = 'green')
        button= ttk.Button(win, text="Tirar",
        command=lambda:juego.roll(canvas))
        button.pack()


        #Add image to the canvas
        juego = Juego(root=win,N=len(nombres),nombres=nombres,)
        juego.mesa(canvas)
        canvas.pack()
        frame = Frame(win)
        tabla_puntajes = juego.Table(frame)
        running = True
        win.protocol("WM_DELETE_WINDOW", close_window)
        juego.jugar()
        win.mainloop()
            
        
    else:
        running = True
        juego = Juego(noGUI=True,N=len(nombres),nombres=nombres)
        juego.jugar()







