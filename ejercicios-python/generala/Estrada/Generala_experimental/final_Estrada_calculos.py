from tkinter import *
from pandastable import Table, TableModel
import numpy as np
import argparse
import random
import pandas as pd
from itertools import product
import copy

tabla_de_puntos=dict({'1':1,'2':2,'3':3,'4':4,'5':5,'6':6,'D':10,'E':20,'F':30,'P':40,'G':50,'GD':100})
juegos=list(tabla_de_puntos.keys())
puntos=list(tabla_de_puntos.values())

class nuevos_dados:
    def __init__(self,guardar=True):
        self.valores=np.random.randint(1,high=7,size=5)
        self.guardar=np.ones(5)*guardar
        self.servida=True

    def cambiar(self,n):
        if self.guardar[n]==True:
            self.guardar[n]=False
        else:
            self.guardar[n]=True

    def re_roll(self):
        for i in range(5):
            if self.guardar[i]==False:
                self.servida=False
                self.valores[i]=np.random.randint(1,high=7)
                self.guardar[i]=True      
class jugador: #Es una clase que tiene nombre y una tabla de juegos con funciones para cobrarlos o tacharlos y devolver la suma total de puntos.
    def __init__(self,nombre='Jugador',humano=True,dificultad=None):
        self.nombre=nombre
        self.humano=humano
        self.dificultad=dificultad #esto se usa para los bots, por defecto es None
        self.tabla={}
        for juego in juegos:
            self.tabla[juego]=None #crea una con una entrada para cada juego '1','2','3','4','5','6','D','E','F','P','G','GD'

    def calcular_puntos(self): #este método simplemente retorna los puntos de ese jugador
        suma=0
        for i in juegos:
            try: 
                suma=suma+self.tabla[i]
            except:
                pass
        return(suma)

    def tachar_juego(self,juego): #si un juego no fue tachado ni cobrado, este método lo asigna como tachado (False)
        if (juego=='G') and (self.tabla['GD']!=False):
            raise Exception("Debe tachar 'generala doble' antes que 'generala'") 
        if self.tabla[juego]==None:
            self.tabla[juego]=False
        else:
            raise Exception("¡Este juego ya fue usado!")

    def reclamar_juego(self,juego,servida=False,n=0): #si un juego no fue tachado ni cobrado, este método lo asigna como cobrado (un valor entero de puntos)
        if self.tabla[juego]==None:
            if n!=0:
                self.tabla[juego]=tabla_de_puntos[juego]*n + servida*5
            else:
                self.tabla[juego]=tabla_de_puntos[juego] + servida*5
        else:
            raise Exception("¡Este juego ya fue usado!")
class DataFrameTable(Frame): #crea un Frame conteniendo una tabla pd
    def __init__(self, parent, df):
        super().__init__()
        self.parent = parent
        self.pack(fill='x', expand=False)
        self.table = Table(
            self, dataframe=df, showtoolbar=False, showstatusbar=False, editable=False, height=100)
        self.table.autoResizeColumns()
        self.table.show()

def ruta_dado(i):
    text='data/dice-'+str(i)+'.png'
    return(text)

def ruta_avatar(i):
    if i==None: return('data/player.png')
    elif i==1: return('data/easy.png')
    elif i==2: return('data/hard.png')
    elif i==3: return('data/very_difficult.png')

def nuevopartido(nombres,bot1,bot2,bot3): #Guarda los jugadores y los ordena al azar
    partido={} #La idea de que fuera un diccionario es que se almecenen condiciones particulares, por ejemplo si se juega con mas de 5 dados o con dados de mas de 6 caras.
    partido['Jugadores']=[] #En la version actual, partido tiene solo el elemento 'Jugadores', asi que funciona mas bien como una lista. 

    if bot1:
        partido['Jugadores'].append(jugador(nombre='Easy Peasy',humano=False,dificultad=1)) #Aca aparece jugador() por primera vez, es una clase que tiene nombre y una tabla de juegos con funciones para cobrarlos o tacharlos.
    if bot2:
        partido['Jugadores'].append(jugador(nombre='Hard',humano=False,dificultad=2))
    if bot3:
        partido['Jugadores'].append(jugador(nombre='Very Difficult',humano=False,dificultad=3))

    if nombres!=None:
        for nombre in nombres:
            partido['Jugadores'].append(jugador(nombre=nombre,humano=True)) #El parser devuelve los nombres de jugadores en un array por lo que hay que hacer un loop sobre el mismo.
 
    n=len(partido['Jugadores'])
    partido['Jugadores']=random.sample(partido['Jugadores'], n)

    return(partido) #la info sobre los jugadores y el orden de juego regresa a la mainapp

def creardf(partido): #esta funcion toma las tablas de puntos de cada jugador y las devuelve como un dataframe de pandas
    ds=[]   
    nombres=[]
    for jugador in partido['Jugadores']:
        ds.append(jugador.tabla)
        nombres.append(jugador.nombre)
    df=pd.DataFrame(ds)
    df.insert(loc=0, column='Nombre', value=nombres)
    df.set_index('Nombre')
    return(df)  

def mejorjugada(reclamables): #devuelve el nombre del juego que mas puntos tiene de entre una lista 
   mejorpuntaje=max([tabla_de_puntos[juego] for juego in reclamables])
   return(juegos[puntos.index(mejorpuntaje)]) 

def simular_tiradas(num,jugador,dados,dados_a_tirar): #dado un set de dados para conservar, devuelve un numero que depende de los juegos posibles al tirar de nuevo los dados 
    puntos=0
    for i in range(num): #se realizan 'num' tiradas de dados. Con un número bajo el bot ya tiene un bien rendimiento.
        dados_sim=copy.copy(dados)
        for d in dados_a_tirar:
            dados_sim.cambiar(d)
            dados.re_roll()
            
        reclamables,tachables=juegos_disponibles(dados_sim,jugador)
        if len(reclamables)>=1:
            mejor=mejorjugada(reclamables)
            try: 
                int(jugada) 
                repetidos=np.sum(np.array(dados.valores)==int(jugada))
                puntos=puntos+int(tabla_de_puntos[mejorjugada(reclamables)])*repetidos #tener en cuenta multiplicar por dados repetidos al considerar las jugadas de 'numeros'
            except:
                puntos=puntos+int(tabla_de_puntos[mejorjugada(reclamables)])
    return(puntos/num)

def juegos_disponibles(dados,jugador): #dado un set de dados y un jugador(del cual se extrae su tabla con juegos) devuelve los juegos disponibles para reclamar o tachar
    reclamables=set()
    tachables=[]
    for j in [1,2,3,4,5,6]:
        if np.sum(dados.valores==j)>0:
            reclamables.add(str(j))
        if np.sum(dados.valores==j)>=2:
            for i in [1,2,3,4,5,6]:
                if (i!=j) and (np.sum(dados.valores==i)>=2):
                    reclamables.add('D')            
        if np.sum(dados.valores==j)==4:
            reclamables.add('P')
            reclamables.add('D')
        if np.sum(dados.valores==j)==5:
            reclamables.add('G')
            reclamables.add('P')
            reclamables.add('D')   
            reclamables.add('F') 
            if isinstance(jugador.tabla['G'], int):
                reclamables.add('GD') 
    if len(set(dados.valores))==5:
        reclamables.add('E')    
    if len(set(dados.valores))==2:
        reclamables.add('F')

    for juego in jugador.tabla:
        if jugador.tabla[juego]!=None:
            reclamables.discard(juego)
        if jugador.tabla[juego]==None:
            if (juego=='G') and (jugador.tabla['GD']==None):
                pass 
            else:
                tachables.append(juego)

    return(reclamables,tachables)

