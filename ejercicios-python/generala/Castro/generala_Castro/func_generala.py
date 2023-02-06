# -----------------------------------------------
#   Funciones generales del programa generala 
# -----------------------------------------------

def actualiza_fig(fig):
    '''Actualiza la figura completa.'''
    fig.canvas.draw()
    fig.canvas.flush_events()

# -----------------------------------------------

def actualiza_tabla(puntos, nombre_jugadores, tabla, index_jugador, tabla_axes, fig):
    '''Actualiza la tabla de puntajes.'''
    
    from func_generala import actualiza_fig

    tabla_axes.clear()
    tabla = tabla_axes.table(cellText=puntos, loc='center', colLabels=nombre_jugadores)
    tabla.set_fontsize(10)
    tabla.scale(0.5,2.44)
    celda = tabla[0, index_jugador]
    celda.set_facecolor('orange')
    tabla_axes.axis('off')
    actualiza_fig(fig)

# -----------------------------------------------

def reset_img_dados(dados_axes,dados_img):
    '''Pone todos los dados en blanco.'''
    for elem in dados_axes:
        elem.clear()
        elem.axis('off')
        elem.imshow(dados_img[0])

# -----------------------------------------------
    
def reset_checkboxes(index, check, dados_selec):
    '''Pone todos los checkboxes iguales con el valor de index.'''

    import numpy as np

    if index:    
        for elem in check[np.logical_not(dados_selec)]:
            elem.set_active(0)
    else:
        for elem in check[dados_selec]:
            elem.set_active(0)

# -----------------------------------------------

def mensaje(fig, axes, texto, tamaño_texto = 9., color = 'black'):
    '''Función para poner mensajes en la ventana del juego. Anota texto en axes.'''

    axes.clear()
    axes.axis('off')
    axes.annotate(texto, xy=(0.,0.), xytext=(0.,0.), textcoords="axes fraction", wrap=True, fontsize = tamaño_texto, color = color)
    fig.canvas.draw()
    
# -----------------------------------------------

def calcular_puntajes(dados_tirados, dados):
    """Función que devuelve TODOS los posibles puntajes asociados a una tirada.
    
    Parámetros:
    -----------
    dados_tirados: número de dados que fueron tirados.

    dados:  np.array
            Valores obtenidos en cada dado
    
    Devuelve:
    ----------
    puntos: np.array
            Puntaje de cada categoría en el orden 
            1,2,3,4,5,6,D,E,F,P,G,DG."""

    # Inicialización y cálculos comunes
    import numpy as np

    puntos = np.zeros(12)
    dados_set = set(dados)

    if dados_tirados == 5: # juego servido
        servido = 1
    else:
        servido = 0
    vals, counts = np.unique(dados, return_counts=True)
    
    # -----------------------
    # Puntajes de los números
    for i in range(np.size(vals)):
        puntos[vals[i] - 1] = vals[i]*counts[i]
    
    # -----------------------
    # Puntajes de los Juegos
    
    # Doble
    if len(dados_set) == 3 and np.max(counts) == 2: # doble
        puntos[6] = 10 + 5*servido

    # Full o poker
    elif len(dados_set) == 2:
        if np.max(counts) == 3: # full
            puntos[8] = 30 + 5*servido
        else: # np.max(counts) == 4, poker
            puntos[9] = 40 + 5*servido
        
    # Escalera
    elif len(dados_set) == 5 and set([3,4,5]).issubset(dados_set):
        puntos[7] = 20 + 5*servido
    
    # Generalas
    elif len(dados_set) == 1:
        puntos[10] = 50 # Generala
        puntos[11] = 100 # Generala doble
        # Cuando se llama a esta función se controla no anotar la doble sin la generala!
        
    return np.int_(puntos) 