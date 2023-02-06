import final_Estrada_calculos as calc
from itertools import product
import numpy as np
import random

def bot(jugador,dados,nsimulaciones=50):
    if jugador.dificultad==1: #bot mas simple. Para los dados que recibe cobra el mejor juego, si no hay, tacha uno al azar. Todos sus juegos son servidos (es buen adversario)                 
        (reclamables,tachables)=calc.juegos_disponibles(dados,jugador)
        if len(reclamables)>0:
            jugada=calc.mejorjugada(list(reclamables))
            try:
                int(jugada)
                repetidos=np.sum(np.array(dados.valores)==int(jugada))
            except:
                repetidos=0
            jugador.reclamar_juego(jugada,servida=True,n=repetidos)
            reclamar=True 
        else:
            jugada=random.choice(list(tachables))
            jugador.tachar_juego(jugada)
            reclamar=False 

    if jugador.dificultad==2: #El bot mas complicado. Para los dados que recibe compara los juegos posibles con los de situaciones simuladas al sortear todas las combinaciones de dados. Solo re-lanza dados 1 vez.
        #La capacidad de prediccion de este bot depende de la cantidad de simulaciones (nsimulaciones) Con n=1 toma decisiones decentes.
        combinaciones=list(product([False,True], repeat=5))
        peso=[]
        for combinacion in combinaciones:
            combinacion=np.array(combinacion)
            peso.append(calc.simular_tiradas(nsimulaciones,jugador,dados,np.where(combinacion==False)[0]))
        
        peso=np.array(peso)

        eleccion=(combinaciones[peso.argmax()])

        for i in np.where(eleccion==False):
            dados.cambiar(i)
        dados.re_roll()

        (reclamables,tachables)=calc.juegos_disponibles(dados,jugador)
        if len(reclamables)>0:
            jugada=calc.mejorjugada(list(reclamables))
            try:
                int(jugada)
                repetidos=np.sum(np.array(dados.valores)==int(jugada))
            except:
                repetidos=0
            jugador.reclamar_juego(jugada,servida=dados.servida,n=repetidos)
            reclamar=True
        else:
            jugada=random.choice(list(tachables))
            jugador.tachar_juego(jugada)
            reclamar=False 
 
    if jugador.dificultad==3: #Bot dificl, simplemente hace trampa. De la tabla de juegos posibles elije uno y lo cobraa, pero gana menos puntos y nunca saca servida.
        cut=np.array(list(jugador.tabla.values()))==None
        jugada=random.choice(np.array(list(jugador.tabla))[cut])
        # print(jugada)
        jugador.reclamar_juego(jugada,servida=False,n=0)
        reclamar=True 

    return(jugada,reclamar,dados)