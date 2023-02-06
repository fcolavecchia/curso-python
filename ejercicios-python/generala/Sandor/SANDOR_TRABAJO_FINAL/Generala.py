#Importo las librerias necesarias
import numpy as np
import matplotlib.pyplot as plt
import argparse
import random
from PIL import Image

class Jugador:
    def __init__(self,nombre,sim=False):
        self.nombre = nombre
        self.tabla = {'Nombre': self.nombre , 'Juegos': {'n° 1': {'Estado': 'Abierto', 'Puntuación': 0},
                                            'n° 2': {'Estado': 'Abierto', 'Puntuación': 0},
                                            'n° 3': {'Estado': 'Abierto', 'Puntuación': 0},
                                            'n° 4': {'Estado': 'Abierto', 'Puntuación': 0},
                                            'n° 5': {'Estado': 'Abierto', 'Puntuación': 0},
                                            'n° 6': {'Estado': 'Abierto', 'Puntuación': 0},
                                            'Doble': {'Estado': 'Abierto', 'Puntuación': 0},
                                            'Escalera': {'Estado': 'Abierto', 'Puntuación': 0},
                                            'Full': {'Estado': 'Abierto', 'Puntuación': 0},
                                            'Poker': {'Estado': 'Abierto', 'Puntuación': 0},
                                            'Generala': {'Estado': 'Abierto', 'Puntuación': 0},
                                            'Doble Generala': {'Estado': 'Abierto', 'Puntuación': 0}}}
        self.sim=sim
        self.puntaje_total = 0
    def tirar_dados(self,num_dados=5):
        '''

        Funcion que recibe el numero de dados que se quiere arrojar (1<int<5) y devuelve una lista de num_dados
        numeros del 1 al 5 de forma aleatorea (list).

        '''
        dados = np.random.randint(1, 7, size=num_dados)
        return dados

    def mostrar_dados(self,dados):

        '''
        Función que toma la lista de dados obtenidos aleatoriamente (list) y devuelve su imagen.
        '''
        caras = []
        for cara in dados:
            imagen = plt.imread("./dice-{}.png".format(cara))
            caras.append(imagen)
        fig = plt.figure(figsize=(4, 4))
        plt.title('Cerrar imagen para continuar\nLos dados apareceran en consola')
        plt.axis('off')
        for i, num in enumerate(caras):
            ax = fig.add_subplot(1, len(caras), i + 1)
            plt.axis('off')
            plt.imshow(num)
        plt.show()
        return
    def seleccionar_dados(self,dados):
        '''
        Funcion que recibe la lista de dados obtenidos y devuelve la lista de dados seleccionados (list) y el numero
        de dados que no se seleccionaron (int).
        '''
        dados_seleccionados = []
        flag= True
        d = input(
            '\n\nSeleccione los dados, escribiendo las posiciones de los dados que elija separados por un espacio, '
            'si quiere volver a tirar todos los dados escriba 0:\n')

        caras = d.split()
        if len(caras)==1 and caras[0] == '0':
            flag = False
        while flag == True:# Atajo los casos en los cuales se seleccionan los dados incorrectamente.
            flag_list = []
            msg = 'Error en los numeros ingresados, ingrese la posicion de los dados nuevamente:\n'
            if len(caras) > 5:
                flag_list.append(True)
                msg = 'Seleccionó mas de 5 dados, vuelva a seleccionarlos:\n'
            else:
                for i in caras:
                    if i !='1' and i != '2' and i != '3' and i!='4' and i !='5':
                        flag_list.append(True)
                    else: flag_list.append(False)
                if len(set(caras))!=len(caras):
                    flag_list.append(True)
                    msg = 'Seleccionó el mismo dado más de una vez, vuelva a seleccionar dados:\n'
            if True in flag_list:
                d = input(msg)
                caras = d.split()
                flag = True
            else: flag = False

        if d == 0: #Caso en el cual se quiera tirar todos los dados de nuevo.
            dados_seleccionados = []
            n_dados_no_seleccionados = 5
        else:
            for i in caras:
                dado = dados[int(i) - 1]
                dados_seleccionados.append(dado)
            n_dados_no_seleccionados = len(dados) - len(dados_seleccionados)
        return dados_seleccionados, n_dados_no_seleccionados

    @property
    def seleccionar_juego(self):
        '''
        Funcion que devuelve el juego seleccionado (str)
        '''

        flag_juego = True #Atajo la posibilidad de que se ingrese mal el juego seleccionado.
        while flag_juego:
            j = input(
                '\n\nSeleccione el juego:\n n° 1:escribir 1\n n° 2: escribir 2\n n° 3: escribir 3\n n° 4: escribir 4\n n° 5: '
                'escribir 5\n n° 6: escribir 6\n Doble: escribir D\n Escalera: escribir E\n Full: escribir F\n Poker: escribir P'
                '\n Generala: escribir G\n Doble Generala: escribir DG \n')

            juegos = ['n° 1', 'n° 2', 'n° 3', 'n° 4', 'n° 5', 'n° 6', 'Doble', 'Escalera', 'Full', 'Poker', 'Generala',
                      'Doble Generala']

            if j == '1':
                juego = juegos[0]
                flag_juego = False
            elif j == '2':
                juego = juegos[1]
                flag_juego = False
            elif j == '3':
                juego = juegos[2]
                flag_juego = False
            elif j == '4':
                juego = juegos[3]
                flag_juego = False
            elif j == '5':
                juego = juegos[4]
                flag_juego = False
            elif j == '6':
                juego = juegos[5]
                flag_juego = False
            elif j == 'D':
                juego = juegos[6]
                flag_juego = False
            elif j == 'E':
                juego = juegos[7]
                flag_juego = False
            elif j == 'F':
                juego = juegos[8]
                flag_juego = False
            elif j == 'P':
                juego = juegos[9]
                flag_juego = False
            elif j == 'G':
                juego = juegos[10]
                flag_juego = False
            elif j == 'DG':
                juego = juegos[11]
                flag_juego = False

            elif j !='1' and j!='2' and j!= '3' and j != '4' and j !='5' and j != '6' and j!= 'D' and j != 'E' and j != 'F' and j != 'P' and j != 'G' and j != 'DG':
                print('No eligió ningun juego, vuelva a intentarlo')
                flag_juego = True
        return juego

    def contar_puntos(self,dados, juego,n=3):
        '''
        Funcion que recibe una lista de dados (list), el juego seleccionado (str) y el numero n de veces que se
        arrojaron los dados (1<int<3) y devuelve el puntaje que se obtuvo en el juego seleccionado (int).
        -------

        '''

        if juego == 'n° 1' or juego == 'n° 2' or juego == 'n° 3' or juego == 'n° 4' or juego == 'n° 5' or juego == 'n° 6':
            indices = np.where(np.array(dados) == (int('{}'.format(juego[3:4]))))
            puntaje = np.sum(np.array(dados)[list(indices[0])])
        elif juego == 'Doble':
            if n==1: # En caso de ser juego servido se le suman 5 puntos.
                puntaje = 15
            else:
                puntaje =10
        elif juego == 'Escalera':
            if n == 1:
                puntaje = 25
            else:
                puntaje = 20

        elif juego == 'Full':
            if n == 1:
                puntaje = 35
            else:
                puntaje = 30
        elif juego == 'Poker':
            if n == 1:
                puntaje = 45
            else:
                puntaje =  40
        elif juego == 'Generala':
            if n == 1:
                puntaje = 55
            else:
                puntaje =  50
        else:
            if n == 1:
                puntaje = 105
            else:
                puntaje =  100

        self.puntaje_total += puntaje
        return puntaje

    def verificar_juego(self,dados, juego):
        '''
        Funcion que recibe una lista dados (list) y el juego (str) y verifica si el juego es correcto, devolviendo
        True o False.

        '''
        u, rep = np.unique(dados, return_counts=True)
        unicos = list(u)
        repetidos = list(rep)

        if juego == 'Doble':
            if len(repetidos) == 3:
                if repetidos == [1, 2, 2] or repetidos == [2, 1, 2] or repetidos == [2, 2, 1]:
                    valor = True
                else:
                    valor = False
            else:
                valor = False

        elif juego == 'Escalera':
            if len(repetidos) == 5:
                if 1 in unicos and 2 in unicos and 3 in unicos and 4 in unicos and 5 in unicos:
                    valor = True
                elif 2 in unicos and 3 in unicos and 4 in unicos and 5 in unicos and 6 in unicos:
                    valor = True
                elif 3 in unicos and 4 in unicos and 5 in unicos and 6 in unicos and 1 in unicos:
                    valor = True
                else:
                    valor = False
            else:
                valor = False

        elif juego == 'Full':
            if len(repetidos) == 2:
                if repetidos == [3, 2] or repetidos == [2, 3]:
                    valor = True
                else:
                    valor = False
            else:
                valor = False

        elif juego == 'Poker':
            if len(repetidos) == 2:
                if repetidos == [4, 1] or repetidos == [1, 4]:
                    valor = True
                else:
                    False
            else:
                valor = False

        elif juego == 'Generala':
            if len(repetidos) == 1:
                valor = True
            else:
                valor = False

        elif juego == 'Doble Generala':
            if len(repetidos) == 1:
                valor = True
            else:
                valor = False

        return valor

    def jugar(self):
        '''
        Funcion que ejecuta la jugada correspondiente segun sea un jugador o la pc
        '''

        if self.sim:
            self.jugar_pc()
        else:
            self.jugar_persona()
        return

    def jugar_pc(self):
        '''
        Función que ejecuta la jugada de la PC.
        '''

        juegos = ['n° 1', 'n° 2', 'n° 3', 'n° 4', 'n° 5', 'n° 6', 'Doble', 'Escalera', 'Full', 'Poker', 'Generala',
                  'Doble Generala']
        n = 0
        flag = True
        flag_2 = True
        while flag==True and n<3:
            dados = self.tirar_dados(5)
            print('\n\n DADOS : '+ str(dados))
            n += 1
            for i in range(6,len(juegos)): # Para cada tirada verifica si se obtuvo alguno de los juegos principales.
                if self.verificar_juego(dados,juegos[i]):
                    if self.tabla['Juegos'][juegos[i]]['Estado'] == 'Abierto':
                        self.tabla['Juegos'][juegos[i]]['Estado'] = 'Cerrado'
                        self.tabla['Juegos'][juegos[i]]['Puntuación'] = self.contar_puntos(dados, juegos[i],n=n)
                        print('\nEl jugador PC eligió: {}\n'.format(juegos[i]))
                        flag = False # En caso de que no se haya obtenido sale del while
                        flag_2 = False # En caso de que no se haya obtenido va al proximo for
                        break
        if flag_2:
            for i,juego in enumerate(juegos): # Va sumando puntos o tachando juegos en forma ordenada.
                if self.tabla['Juegos'][juego]['Estado'] == 'Abierto': # chequea que el juego este abierto
                    self.tabla['Juegos'][juego]['Estado'] = 'Cerrado'
                    print('\nEl jugador PC eligió: {}\n'.format(juego))
                    if i<=5:
                        self.tabla['Juegos'][juego]['Puntuación'] = self.contar_puntos(dados, juego,n=n)
                    else: self.tabla['Juegos'][juego]['Puntuación']=0
                    break
        self.mostrar_tabla()

    def jugar_persona(self):
        '''
        Funcion que ejecuta la jugada de los jugadores.
        '''
        n = 0
        flag_2 = True
        dados_guardados = []
        n_dados = 5
        while flag_2 == True and n < 3 and n_dados != 0: # Sale del while en caso de haber arrojado 3 veces los dados
            self.mostrar_tabla()                          # o en caso de elegir juego.
            dados = self.tirar_dados(n_dados)
            n += 1
            dados_totales = dados_guardados + list(dados)
            self.mostrar_dados(dados_totales)
            print('\n\n DADOS : '+ str(dados_totales))
            if n<3:
                dados_selec, n_dados = self.seleccionar_dados(dados_totales)
                if len(dados_selec) == 5:
                    dados_guardados = dados_selec
                    flag_2 = False
                else:
                    dados_guardados = []
                    for i in dados_selec:
                        dados_guardados.append(i)
        self.mostrar_tabla()

        # Parte en la cual se selecciona el juego, se verifica que no esté abierto, se verifica que el juego
        # seleccionado sea correcto y en caso de serlo se le asgina el puntaje y se cierra el juego.
        flag = True
        while flag == True:
            juego = self.seleccionar_juego
            if self.tabla['Juegos'][juego]['Estado'] == 'Abierto':
                if juego != 'n° 1' and juego != 'n° 2' and juego != 'n° 3' and juego != 'n° 4' and juego != 'n° 5' and juego != 'n° 6':
                    valor = self.verificar_juego(dados_totales, juego)
                    if valor == True:
                        if juego == 'Doble Generala':
                            if self.tabla['Juegos']['Generala']['Estado'] == 'Abierto':
                                print('Como no has cerrado la Generala aún, el puntaje se le asignará a la Generala ')
                                self.tabla['Juegos']['Generala']['Estado'] = 'Cerrado'
                                self.tabla['Juegos']['Generala']['Puntuación'] = self.contar_puntos(dados_totales, 'Generala', n=n)
                                flag = False
                            else:
                                self.tabla['Juegos'][juego]['Estado'] = 'Cerrado'
                                self.tabla['Juegos'][juego]['Puntuación'] = self.contar_puntos(dados_totales, juego, n=n)
                                flag = False
                        else:
                            self.tabla['Juegos'][juego]['Estado'] = 'Cerrado'
                            self.tabla['Juegos'][juego]['Puntuación'] = self.contar_puntos(dados_totales, juego,n=n)
                            flag = False
                    else:
                        respuesta = input('\nNo tienes juego, desea tacharlo: si/no\n')
                        if respuesta == 'si':
                            if juego == 'Generala':
                                if self.tabla['Juegos']['Doble Generala']['Estado'] == 'Abierto':
                                    print('\nAVISO: Aún no has tachado la doble generala, por lo tanto se tachará primero')
                                    self.tabla['Juegos']['Doble Generala']['Estado'] = 'Cerrado'
                                    self.tabla['Juegos']['Doble Generala']['Puntuación'] = 0
                                    flag = False
                                else:
                                    self.tabla['Juegos'][juego]['Estado'] = 'Cerrado'
                                    self.tabla['Juegos'][juego]['Puntuación'] = 0
                                    flag = False
                            else:
                                self.tabla['Juegos'][juego]['Estado'] = 'Cerrado'
                                self.tabla['Juegos'][juego]['Puntuación'] = 0
                                flag = False
                else:
                    self.tabla['Juegos'][juego]['Estado'] = 'Cerrado'
                    self.tabla['Juegos'][juego]['Puntuación'] = self.contar_puntos(dados_totales, juego)
                    flag = False
            else:
                print('El juego que desea seleccionar se encuentra cerrado, elija otro juego')

    def mostrar_tabla(self):
        '''
        Funcion que muestra la tabla del jugador.
        '''
        E1 = self.tabla['Juegos']['n° 1']['Estado']
        P1 = self.tabla['Juegos']['n° 1']['Puntuación']

        E2 = self.tabla['Juegos']['n° 2']['Estado']
        P2 = self.tabla['Juegos']['n° 2']['Puntuación']

        E3 = self.tabla['Juegos']['n° 3']['Estado']
        P3 = self.tabla['Juegos']['n° 3']['Puntuación']

        E4 = self.tabla['Juegos']['n° 4']['Estado']
        P4 = self.tabla['Juegos']['n° 4']['Puntuación']

        E5 = self.tabla['Juegos']['n° 5']['Estado']
        P5 = self.tabla['Juegos']['n° 5']['Puntuación']

        E6 = self.tabla['Juegos']['n° 6']['Estado']
        P6 = self.tabla['Juegos']['n° 6']['Puntuación']

        ED = self.tabla['Juegos']['Doble']['Estado']
        PD = self.tabla['Juegos']['Doble']['Puntuación']

        EE = self.tabla['Juegos']['Escalera']['Estado']
        PE = self.tabla['Juegos']['Escalera']['Puntuación']

        EF = self.tabla['Juegos']['Full']['Estado']
        PF = self.tabla['Juegos']['Full']['Puntuación']

        EP = self.tabla['Juegos']['Poker']['Estado']
        PP = self.tabla['Juegos']['Poker']['Puntuación']

        EG = self.tabla['Juegos']['Generala']['Estado']
        PG = self.tabla['Juegos']['Generala']['Puntuación']

        EDG = self.tabla['Juegos']['Doble Generala']['Estado']
        PDG = self.tabla['Juegos']['Doble Generala']['Puntuación']

        print('\n'+ 52*' '+'TABLA DEL JUGADOR: {} \n\n'.format(self.tabla['Nombre']))
        print(
            'juegos ' + ':    1    .    2    .    3    .    4    .    5    .    6    .    D    .    E    .    F    .    P    .    G    .    DG   ')
        print(127 * '-')

        print('Estado :' + ' {}'.format(E1) + ' .' + ' {}'.format(E2) + ' .' + ' {}'.format(E3) + ' .' + ' {}'.format(
            E4) + ' .' + ' {}'.format(E5)
              + ' .' + ' {}'.format(E6) + ' .' + ' {}'.format(ED) + ' .' + ' {}'.format(EE) + ' .' + ' {}'.format(
            EF) + ' .' + ' {}'.format(EP) + ' .'
              + ' {}'.format(EG) + ' .' + ' {}'.format(EDG))

        print(127 * '-')

        print('Puntos :' + 4 * ' ' + '{}'.format(P1) + (5 - len(str(P1))) * ' ' 
                         + '.    ' + '{}'.format(P2) + (5 - len(str(P2))) * ' ' 
                         + '.    ' + '{}'.format(P3) + (5 - len(str(P3))) * ' ' 
                         + '.    ' + '{}'.format(P4) + (5 - len(str(P4))) * ' ' + '.    ' + '{}'.format(P5) +
              (5 - len(str(P5))) * ' ' + '.    ' + '{}'.format(P6) + (5 - len(str(P6))) * ' ' + '.    ' + '{}'.format(
            PD) + (5 - len(str(PD))) * ' '
              + '.    ' + '{}'.format(PE) + (5 - len(str(PE))) * ' ' + '.    ' + '{}'.format(PF) + (
                          5 - len(str(PF))) * ' ' + '.    ' + '{}'.format(PP)
              + (5 - len(str(PP))) * ' ' + '.    ' + '{}'.format(PG) + (5 - len(str(PG))) * ' ' + '.    ' + '{}'.format(
            PDG) + (5 - len(str(PDG))) * ' ')

        print(127 * '-')
        return

class Generala:
    '''
    Clase que recibe una lista de jugadores y ejecuta el juego completo de la generala, pudiendo incluir a
    la PC como jugador.
    '''
    def __init__(self,jugadores,simulacion=False):

        self.jugadores = jugadores
        self.num_jugadas = 12
        if simulacion:
            self.jugadores.append(Jugador('PC', sim=True))

    def mostrar_tabla_final(self):
        '''
        Funcion que muestra la tabla con puntajes de todos los jugadores y el puntaje total.
        '''
        print('\n\n Nombre | 1 | 2 | 3 | 4 | 5 | 6 | D | E | F | P | G | DG| Puntos totales')
        print(72 * '-')
        for jugador in self.jugadores:
            P1 = jugador.tabla['Juegos']['n° 1']['Puntuación']
            P2 = jugador.tabla['Juegos']['n° 2']['Puntuación']
            P3 = jugador.tabla['Juegos']['n° 3']['Puntuación']
            P4 = jugador.tabla['Juegos']['n° 4']['Puntuación']
            P5 = jugador.tabla['Juegos']['n° 5']['Puntuación']
            P6 = jugador.tabla['Juegos']['n° 6']['Puntuación']
            PD = jugador.tabla['Juegos']['Doble']['Puntuación']
            PE = jugador.tabla['Juegos']['Escalera']['Puntuación']
            PF = jugador.tabla['Juegos']['Full']['Puntuación']
            PP = jugador.tabla['Juegos']['Poker']['Puntuación']
            PG = jugador.tabla['Juegos']['Generala']['Puntuación']
            PDG = jugador.tabla['Juegos']['Doble Generala']['Puntuación']
            total = str(jugador.puntaje_total)

            print(int((8-len(jugador.nombre))/2) *' ' + jugador.nombre + int((9-len(jugador.nombre))/2) *' ' + '|' + int((3 - len(str(P1)))/2) *' ' +'{}'.format(P1) + int((3-len(str(P1)))/2) * ' ' + '| ' + '{}'.format(P2) + int((3 - len(str(P2)))/2) *' ' + '| '
                  + '{}'.format(P3) + int((3 - len(str(P3)))/2) *' ' + '| ' + '{}'.format(P4) + int(
            (3 - len(str(P4)))/2) *' ' + '| ' + "{}".format(P5) +
                  int((3 - len(str(P5)))/2) *' ' + '| ' + '{}'.format(P6) + int((3 - len(str(P6)))/2) *' ' + '| ' + '{}'.format(
            PD) + int((3 - len(str(PD)))/2)*' '
            + '| ' + '{}'.format(PE) + int((3 - len(str(PE)))/2) * ' ' + '| ' + '{}'.format(PF) + int((
             3 - len(str(PF)))/2) * ' ' + '| ' + '{}'.format(PP)
            + int((3 - len(str(PP)))/2) * ' ' + '| ' + '{}'.format(PG) + int((3 - len(str(PG)))/2) * ' ' + '| ' + '{}'.format(
            PDG) + int((3 - len(str(PDG)))/2) * ' ' + '| ' +int((16-len(str(total)))/2)*' '+ total)




    def ejecutar_juego(self):
        '''
        Funcion que ejecuta la generala completa.
        '''
        for num_jugada in range(self.num_jugadas):
            for jugador in self.jugadores:
                print('\n\nTurno de ------> {}\n'.format(jugador.nombre))
                jugador.jugar()
                self.mostrar_tabla_final()
        lista_puntaje=sorted(self.jugadores,key=lambda x:x.puntaje_total)
        print('\n' + 127*'-')
        print(44*' '+ '¡¡¡El ganador es {0} con {1} puntos!!!'.format(lista_puntaje[-1].nombre,lista_puntaje[-1].puntaje_total))
        print(127*'-')


# --------------------------------------MAIN ----------------------------------------------------------------------------

parser = argparse.ArgumentParser(description='Ingresa Jugadores.')
parser.add_argument('--jugadores','-n', metavar='n', type=str, nargs='+',
                    help='Jugadores que van a jugar a la generala')

lista_jugadores = parser.parse_args().jugadores

# Sorteamos el orden de los jugadores
random.shuffle(lista_jugadores)
jugadores = []

# Creamos los objetos jugadores
for cada_jugador in lista_jugadores:
    jugadores.append(Jugador(cada_jugador))
sim = input('¿Desea agregar a la computadora como un jugador mas? si/no\n')
if sim == 'si':
    sim_flag = True
else:
    sim_flag = False
generala = Generala(jugadores,simulacion=sim_flag)
generala.ejecutar_juego()
