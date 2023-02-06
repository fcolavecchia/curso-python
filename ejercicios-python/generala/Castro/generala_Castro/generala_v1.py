# Programa que implementa el juego de generala tradicional.
# Pueden jugar un número arbitrario de jugadores (siempre y cuando
# la tabla con todos los nombres siga siendo legible). También 
# puede jugar la compu. Si no se especifica el nombre de algún 
# jugador y se invita a la compu, juega sola.

# Programa realizado como examen final de la materia 
# Introducción a Python para Ciencias e Ingenieria
# dictada por Juan Fiol y Flavio Colavecchia.

# Abril de 2022, Facundo Castro

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.widgets import Button, CheckButtons
import argparse
import numpy as np
from func_generala import actualiza_fig, actualiza_tabla, reset_img_dados, reset_checkboxes, calcular_puntajes, mensaje

##########################################
##########################################

#  Inicialización general

#--------------
#   Parsing 
#--------------

parser = argparse.ArgumentParser(description='Programa para jugar a la generala. N jugadores. Se puede jugar también contra la computadora.')

parser.add_argument('-n', action='append', dest='nombres', help='Nombre de los jugadores (repetir esta opción para cada jugador). ')

parser.add_argument('--compu', action='store_true', help='Si se especifica esta opción también juega la computadora.')

par = parser.parse_args()

#-------------------------------------
#   Configuración de los jugadores
#-------------------------------------

if par.nombres is None:
    if par.compu == True: # Juega la compu sola
        nombres = ['Compu']

else: # Hay algún humano
    if par.compu:
        nombres = par.nombres + ['Compu']
    else:
        nombres = par.nombres

# Sorteo del orden de juego
aux=[]
for elem in nombres:
    aux.append([elem, np.random.uniform(0, 1, 1)[0]])

nombre_jugadores = []
for elem in sorted(aux, key=lambda x: x[1]):
    nombre_jugadores.append(elem[0])

nro_jugadores = len(nombre_jugadores)

index_jugador = 0  # Índice que identifica a cada jugador.

#----------------------------------
#   Inicialización de variables
#----------------------------------

int_v = np.vectorize(int)

# array con los puntos de los jugadores (en columnas). La última fila tiene la suma de los puntos.
puntos = np.array(nro_jugadores*13*[None]).reshape((13,nro_jugadores)) 

# array con unos en los juegos disponibles. Cada fila es un jugador.
juegos_disp = np.array(nro_jugadores*12*[1]).reshape((nro_jugadores,12)) 

# array con las caras que salieron en los dados
dados = np.array(5*[None])       

# array booleano con los dados seleccionados
dados_selec = np.array(5*[True]) 

# array con las imágenes de las caras de los dados
dados_img = []                   
for i in range(7):
    dados_img.append(plt.imread('dice-'+str(i)+'.png'))

# cantidad de tiradas del jugador
ntiradas = 0

# ronda del juego (total = 12)
ronda = 1

##########################################
##########################################

#  Construcción de la GUI  

mpl.rcParams['toolbar'] = 'None'

# Figura
fig = plt.figure(figsize=(6.4, 7.0))
fig.canvas.manager.set_window_title('Generala')


# -------------------------
#    Axes para los dados
# -------------------------

dados_axes = np.array(5*[None])  # array con los axes para los dados
dados_left = 0.07
dados_bottom = 0.8
dados_gap = 0.14
dados_size = 0.11
for i in range(5):
    dados_axes[i] = fig.add_axes([dados_left, dados_bottom - dados_gap*i, dados_size, dados_size])
    dados_axes[i].imshow(dados_img[0],alpha=0.5)
    dados_axes[i].axis('off')


# -----------------------------------------------------
#    Checkbuttons para seleccionar los dados a tirar
# -----------------------------------------------------

def check_func(i, dados_selec, check):
    ''' Función conectada al evento click en un checkbutton.
        Guarda en el array dados_selec los dados seleccionados (booleano).'''
    
    def clicked(event):
        dados_selec[i] = check[i].get_status()[0]
    return clicked

# Armado de los checkbuttons
check = np.array(5*[None])       # array con los checkButtons
check_axes = 5*[None]            # array con los axes para los checkButtons
check_left = dados_left + 0.12   # parámetros de tamaño y ubicación
check_bottom = 0.78
check_gap = dados_gap
check_size = 0.16
for i in range(5):
    check_axes[i] = fig.add_axes([check_left, check_bottom - check_gap*i, check_size, check_size])
    check_axes[i].axis('off')
    check[i] = CheckButtons(check_axes[i],[' '],[True])
    check[i].on_clicked(check_func(i, dados_selec, check))


# --------------------------------
#    Botón para tirar los dados  
# --------------------------------

def tirar_dados(compu, lances_min = 3, lances_max = 8, period = 0.05):

# No se puede poner en el archivo aparte con las funciones porque usa variables globales.

# Es necesario usar variables globales porque esta función se llama dentro de on_clicked 
# y no puede devolver valores.

    ''' Función conectada al evento click en el botón tirar.
        Simula tirar los dados usando números al azar.
        Cada vez que se la ejecuta realiza un número de tiradas 
        elegidas al azar entre lances_min y lances_max.
        
        Parámetros
        compu:         booleano que indica si la compu está tirando los dados
        index_jugador: índice que identifica al jugador
        lances_min:    cantidad mínima de veces que "ruedan" los dados antes de definir su valor.
        lances_max:    cantidad máxima de veces que "ruedan" los dados antes de definir su valor.
        period:        tiempo en segundos durante el cual se muestran los estados intermedios de los dados.
        '''

    def single_run(alfa):
        ''' 1 lanzamiento de los dados. Se actualizan las imágenes en la figura.'''
        
        cara_azar = int_v(np.random.uniform(1,7,5))
        for i in range (5):
            if dados_selec[i]:
                dados_axes[i].clear()
                dados_axes[i].axis('off')
                dados_axes[i].imshow(dados_img[cara_azar[i]], alpha = alfa)
                dados[i] = cara_azar[i]

    def multi_run():
        ''' Simulación del rodado de los dados. Se realizan 
            n lanzamientos al azar (lances_min <= n <= lances_max)'''            

        lances = int(np.random.uniform(lances_min, lances_max, 1)[0])
        for i in range(lances):
            plt.pause(period)
            single_run(alfa = 0.5 + 0.5*i/(lances - 1))
            actualiza_fig(fig)
        reset_checkboxes(False, check, dados_selec) # al finalizar la tirada se resetean los checkboxes

    def lanzamiento():
        '''Lanzamiento de los dados.'''

        global ntiradas, dados_tirados

        dados_tirados = sum(dados_selec)

        # Control de posibles errores
        if dados_tirados == 0: # No se tiró ningún dado
            texto = 'Es necesario seleccionar al menos un dado para tirar. \n("esc" para ocultar)'
            mensaje(fig, mensajes_axes, texto, color = 'red')
            return None

        if ntiradas == 0 and dados_tirados < 5: # No todos los dados fueron seleccionados.
            texto = 'Todos los dados deben lanzarse al menos una vez. \n("esc" para ocultar)'
            mensaje(fig, mensajes_axes, texto, color = 'red')
            return None

        # Lanzamiento
        if ntiradas < 3 and ronda <= 12:
            ntiradas += 1
            bot_tirar.label.set_text('Tirar (' + str(3-ntiradas) + ')')
            multi_run()
            
            if len(set(dados)) == 1 and dados_tirados == 5: # Generala servida!
                texto = '  ¡¡¡Generala servida!!! ¡' + nombre_jugadores[index_jugador] + ' ganó el partido!'
                mensaje(fig, mensajes_axes, texto, tamaño_texto = 14)

    def clicked(event): # Humano tira los dados, hace click en el botón.
        
        lanzamiento()

    if compu: # Juega la compu.

        lanzamiento()
    
    
    return clicked

# Armado del botón
bot_tirar_axes = fig.add_axes([0.075, 0.11, 0.1, 0.1])
bot_tirar = Button(bot_tirar_axes, 'Tirar (3)', color="orange")
bot_tirar.on_clicked(tirar_dados(compu=False))


# -----------------------
#    Tabla de puntajes 
# -----------------------

tabla_axes = fig.add_axes([0.25, 0.09, 0.93, 0.91])
tabla = tabla_axes.table(cellText=puntos, loc='center', colLabels=nombre_jugadores)
actualiza_tabla(puntos, nombre_jugadores, tabla, index_jugador, tabla_axes, fig)


# ---------------------------------
#   Botones para anotar puntajes 
# ---------------------------------

def anotar_puntaje(index, compu):
    '''Función conectada al evento hacer click en un botón para anotar un puntaje.
       Anota el puntaje elegido en la tabla de puntajes.
       Para que funcione la conexión entre los clicks en los botones y esta función hace
       falta generar esta estructura extraña en la que se agrega la función clicked y se
       retorna esa función.
       (https://stackoverflow.com/questions/70047193/python-add-optional-argument-into-matplotlib-button-on-clicked-function)
       También hace falta poner por separado la condición sobre la variable compu para que se ejecute 
       la función cuando se la llama desde el código.'''

    def anota():
        '''Esta es la función que efectivamente anota los puntajes. Puede ser llamada por
           un click en un botón de anotar juego, o por la compu.'''

        global puntos, ntiradas, index_jugador, ronda

        if puntos[index, index_jugador] is None:

            # Intento de anotar la doble sin la generala
            if index == 11 and puntos[10, index_jugador] != 50 and calcular_puntajes(dados_tirados, dados)[11] == 100: 
                texto = 'No se puede anotar la doble generala sin la generala. \n("esc" para ocultar)'
                mensaje(fig, mensajes_axes, texto, color = 'red')
                return None

            # Intento de tachar la generala sin haber tachado la doble
            if index == 10 and calcular_puntajes(dados_tirados, dados)[10] == 0 and puntos[11, index_jugador] != 0:
                texto = 'No se puede tachar la generala sin haber tachado la doble generala antes. \n("esc" para ocultar)'
                mensaje(fig, mensajes_axes, texto, color = 'red')
                return None
            
            # Anota el puntaje
            puntos[index, index_jugador] = calcular_puntajes(dados_tirados, dados)[index]
            juegos_disp[index_jugador, index] = 0 # Este juego ya no está disponible.
            # Sumo el puntaje hasta el momento
            puntos_juegos = puntos[0:12, index_jugador] # Excluyo la última fila con el total.
            puntos[12, index_jugador] = np.sum(puntos_juegos[puntos_juegos != None])
            
            # Reset del número de tiradas
            ntiradas = 0
            bot_tirar.label.set_text('Tirar (' + str(3-ntiradas) + ')')
            
            # Pasaje de jugador y eventualmente de ronda
            if index_jugador + 1 < nro_jugadores: # Ronda no concluida, pasa al siguiente jugador
                index_jugador += 1
            
            elif index_jugador + 1 == nro_jugadores: # Ronda finalizada, pasa a la siguiente
                index_jugador = 0
                ronda += 1
            
                if ronda == 13: # El juego terminó
                    actualiza_tabla(puntos, nombre_jugadores, tabla, index_jugador, tabla_axes, fig)
                    reset_img_dados(dados_axes,dados_img)
                    reset_checkboxes(True, check, dados_selec)
                    actualiza_fig(fig) 

                    # Identificación del ganador y publicación en pantalla
                    ganador = nombre_jugadores[np.where(puntos[12]==np.max(puntos[12]))[0][0]]
                    if np.size(np.where(puntos[12]==np.max(puntos[12]))[0]) > 1: # empate
                        for i in range(1, np.size(np.where(puntos[12]==np.max(puntos[12]))[0])):
                            ganador += ' y ' + nombre_jugadores[np.where(puntos[12]==np.max(puntos[12]))[0][i]]
                            texto = '  El juego terminó. ¡' + ganador + ' empataron!'
                    else:
                        texto = '  El juego terminó. ¡El ganador es ' + ganador + '!'
                        mensaje(fig, mensajes_axes, texto, tamaño_texto = 13)
                    return None

            # Actualización de figuras        
            actualiza_tabla(puntos, nombre_jugadores, tabla, index_jugador, tabla_axes, fig)
            reset_img_dados(dados_axes,dados_img)
            reset_checkboxes(True, check, dados_selec)
            actualiza_fig(fig) 

            # Si el próximo jugador es la compu la hace jugar.
            if nombre_jugadores[index_jugador] == 'Compu':
                juega_compu()

    if compu:      # Compu anota su resultado
        anota()

    def clicked(event): # Humano hace click en el botón
        anota()

    return clicked

# Creación de los botones para anotar los juegos
boton = 12*[None]      # array con los botones
bot_axes = 12*[None]   # array con los axes
bot_left = 0.283       # parámetros de tamaño y ubicación de los botones  
bot_bottom = 0.835 
bot_gap = 0.058
bot_width = 0.2
bot_height = bot_gap
bot_labels=['1','2','3','4','5','6','Doble','Escalera','Full','Poker','Generala','Doble generala']

for i in range(12):
    bot_axes[i] = fig.add_axes([bot_left, bot_bottom - bot_gap*i, bot_width, bot_height])
    boton[i] = Button(bot_axes[i], bot_labels[i], color="lightgrey")
    boton[i].on_clicked(anotar_puntaje(i, compu = False))


# -------------------------
#    Figura para mensajes
# -------------------------

mensajes_axes = fig.add_axes([0.02,0.02,0.96,0.09])
mensajes_axes.axis('off')
texto = 'Ayuda: apretar tecla "h"'
mensaje(fig, mensajes_axes, texto)


# ----------------------------------------------------------
#    Algunas funcionalidades que se activan con el teclado
# ----------------------------------------------------------

def on_press(event):
    if event.key == 'h': # muestra la ayuda
        texto = 'Generala 1.0: generala tradicional para n jugadores (opcionalmente, la computadora juega). \
El orden de juego se sortea al inicio. Con el botón "Tirar" se lanzan los dados elegidos. Con los botones grises se anotan los juegos. \
Si el juego no salió, se anotan 0 puntos (juego "tachado").\n\
("esc" para ocultar)'
        mensaje(fig, mensajes_axes, texto)
    if event.key == 'escape': # resetea los mensajes
        texto = 'Ayuda: apretar tecla "h"'
        mensaje(fig, mensajes_axes, texto)
    if event.key == 't': # tira los dados (compu=True es la forma de hacerlo por código)
        tirar_dados(compu=True)
    if event.key == 's': # se seleccionan todos los checkboxes.
        reset_checkboxes(True, check, dados_selec)
        actualiza_fig(fig)

fig.canvas.mpl_connect('key_press_event', on_press)


##########################################
##########################################

#  Funciones para que juegue la compu 

# Estas funciones se incluyen aquí y no en el módulo aparte porque utilizan las funciones
# tirar_dados y anotar_puntaje. Tal vez se podría intentar armar copias de esas funciones
# que en lugar de usar variables globales devuelvan valores. Si bien eso podría dejar más
# separada la parte gráfica del resto del programa, tal vez sería desventajoso porque habría
# dos versiones de tirar_dados y anotar_puntaje. Tal vez llamando una función común dentro de
# estas se podría resolver. Para verlo eventualmente en el futuro.

#---------------------
#  Función principal
#---------------------

def juega_compu():    
    ''' Función que implementa el método de juego de la computadora.'''
    
    if ntiradas < 3:
        tirar_dados(compu=True)
        jugada = compu_busca_jugada()
        if np.array_equal(jugada,[0,0,0,0,0]): # la compu decide no jugar más
            compu_elige_puntaje()
        else: # una tirada más
            for i, elem in enumerate(jugada):
                if elem == 1:
                    check[i].set_active(0)
            actualiza_fig(fig)
            juega_compu()

    elif ntiradas == 3:
        compu_elige_puntaje()


#-----------------------
#  Búsqueda de jugadas
#-----------------------

def compu_busca_jugada(n = 500):
    
    """Función que define la próxima jugada de la computadora en el juego de generala.
    La idea básica es simular n veces todas las jugadas posibles, calificar cada jugada
    con un puntaje (valor del juego máximo de la jugada), y elegir la de puntaje más alto.
    Se incluye la posibilidad de no hacer una nueva tirada o de tirar todos los dados.
    Se toman en cuenta los juegos disponibles (no anotados).
    
    Parámetros:
    n: cantidad de veces que se simula cada jugada posible (default 500)
    
    Devuelve:
    ----------
    jugada: np.array con 1 en los dados que deben tirarse y 0 en los que no."""
            
    # Los 1 representan los dados que se arrojan nuevamente, los 0 los que quedan fijos.
    # Esta lista contiene todas las posibles jugadas a partir de una tirada de dados.
    posibles = np.array([[1,0,0,0,0],[0,1,0,0,0],[0,0,1,0,0],[0,0,0,1,0],[0,0,0,0,1],
                         [1,1,0,0,0],[1,0,1,0,0],[1,0,0,1,0],[1,0,0,0,1],[0,1,1,0,0],
                        [0,1,0,1,0],[0,1,0,0,1],[0,0,1,1,0],[0,0,1,0,1],[0,0,0,1,1],
                        [1,1,1,0,0],[1,1,0,1,0],[1,0,1,1,0],[0,1,1,1,0],[1,1,0,0,1],
                        [1,0,1,0,1],[0,1,1,0,1],[1,0,0,1,1],[0,1,0,1,1],[0,0,1,1,1],
                        [1,1,1,1,0],[1,1,1,0,1],[1,1,0,1,1],[1,0,1,1,1],[0,1,1,1,1],
                        [1,1,1,1,1]])
    
    max = 0
    unos = np.ones(5).astype(int)

    if np.array_equal(juegos_disp[0:10],np.zeros(10)): # sólo le queda buscar las generalas
        # tratamiento especial sin simulaciones, armando una jugada dejando fijos los dados repetidos, si los hubiera. 
        jugada = unos
        vals, counts = np.unique(dados, return_counts=True)
        dado_rep = vals[np.where(np.max(counts)==counts)[0][0]] # Identifico los dados repetidos
        for elem in np.where(dados==dado_rep)[0]:
            jugada[elem]=0
        return jugada
    
    # Caso general: simulación de jugadas    
    for elem in posibles: # loop sobre todas las posibles jugadas
        puntaje = 0
        fijos = dados*(unos - elem) # dados que quedan fijos
        for i in range(n): # loop con n repeticiones de una misma jugada, se acumula el puntaje
            lanzados = elem*int_v(np.random.uniform(1,7,5)) # los dados que se tiran (los 0 de elem matan los valores al azar de los fijos)
            puntaje += np.max(juegos_disp[index_jugador]*calcular_puntajes(dados_tirados, fijos + lanzados))
        if puntaje > max: # si la jugada tiene un puntaje mayor se registra.
            jugada = elem
            max = puntaje
    
    # inclusión del caso en el que no se tira ningún dado
    puntaje = n*np.max(juegos_disp[index_jugador]*calcular_puntajes(dados_tirados, dados))  
    if puntaje > max:
        jugada = np.array([0,0,0,0,0])
        max = puntaje
    
    return jugada #, max/n


# ---------------------------------
#   Elección del puntaje a anotar
# ---------------------------------

def compu_elige_puntaje():

    '''Función mediante la cual la compu define qué puntaje anotarse.
       Básicamente, si obtiene un puntaje >= 15 lo anota. Si no,
       considera diferentes opciones según los juegos que va sacando.'''
    
    puntos_posibles = juegos_disp[index_jugador]*calcular_puntajes(dados_tirados,dados)
    puntos_max = np.sort(puntos_posibles)[-1]
    index_top = np.where(puntos_posibles == puntos_max)[0][-1] # máximo puntaje empezando de los puntajes más altos
    index_bot = np.where(puntos_posibles == puntos_max)[0][0] # máximo puntaje empezando de los puntajes más bajos

    if puntos_max >= 15:  # puntaje de juegos o puntaje alto para números: anoto
        if index_top == 11 and juegos_disp[index_jugador, 10] == 1: # el máximo ocurre para la doble, pero todavía no se anoto la generala
            anotar_puntaje(10, compu = True)
        else:
            anotar_puntaje(index_top, compu = True)

    else:
        if puntos_max == 12 and index_bot == 5: # 12 al 6, puede esconder otro puntaje anotable. 
                                                # Para evitarlo se toma el segundo puntaje más alto.
            puntos_max = np.sort(puntos_posibles)[-2]
            index_top = np.where(puntos_posibles == puntos_max)[0][-1]
            index_bot = np.where(puntos_posibles == puntos_max)[0][0]

        if set([index_bot]).issubset(set([0,1,2])) and juegos_disp[index_jugador,index_bot] == 1: # puntaje del 1, 2 o 3: anoto
        # agrego que controle que el juego esté disponible porque si no saca ningún puntaje el máximo es 0 y index_bot=0, pero puede tener anotado el 1.    
            anotar_puntaje(index_bot, compu = True)
        elif index_bot == 3 and puntos_max >= 8: # 8 o 12 al cuatro, anoto.
            anotar_puntaje(index_bot, compu = True)
        elif index_top == 6: # doble, también anoto
            anotar_puntaje(index_top, compu = True)
        else: # tacho (o anoto, si de casualidad hay algún dado con el número correspondiente)
            lista_tachar = [0, 1, 11, 2, 10, 7, 3, 6, 4, 8, 9, 5]
            # lista con los índices de los juegos a tachar: 1, 2, GD, 3, G, E, 4, D, 5, F, P, 6
            for elem in lista_tachar: # Se tacha el primero disponible
                if juegos_disp[index_jugador, elem] == 1:
                    anotar_puntaje(elem, compu = True)
                    return None

##########################################
##########################################

#  Main!

# Si juega la compu y es el primer jugador, lanza los dados!
if par.compu and nombre_jugadores[0] == 'Compu':
    juega_compu()

plt.show()