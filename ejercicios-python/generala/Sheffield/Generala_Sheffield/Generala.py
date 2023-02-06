"""
Juego de Generala
Facundo Sheffield 2022
Introducción a Python
Juego sin generala servida, en algún momento hay que elegir las reglas cuando cada quién tiene la suya.

Nota del código: El control de flujo se realiza mediante la varible CONDITION, donde cada valor de CONDITION representa
un estado de juego diferente. De esta manera, se tiene:
CONDITION = 0 -> Pantalla inicial, selección de juego
CONDITION = 1 -> Single PLayer Mode - Set Player Values; avanza automáticamente a la siguiente condición
CONDITION = 2 -> Single Player Mode - Modo single player, se juega contra un bot (full) random
CONDITION = 3 -> Multiplayer Mode - Choose Names, se elige el número de jugadores y sus nombres
CONDITION = 4 -> Multiplayer Mode - Modo Multiplayer
CONDITION = 5 -> Game Over - Pantalla de fin de juego, se determina el ganador y se pregunta por un nuevo juego.
CONDITION = 6 -> About - Pantalla About, información adicional del programa, reglas, notas y créditos.
"""

import numpy as np
from time import sleep
import pygame
from pygame import mixer  # sound effects

clock = pygame.time.Clock()
tirada = np.random.randint(1, 7, 5)  # tirada de dados inicial
isPressed = [-1] * 5  # Determina si el dado fue seleccionado para mantenerlo en la tirada
Num_tir = 1  # número de tiros realizados
p_name = ""  # player name (variable auxiliar)
Player_Names = []  # list of player names
Players = []  # list of player objects
P_turn = 0  # turn of the player
names = [["1", '-'], ["2", '-'], ["3", '-'], ["4", '-'], ["5", '-'], ["6", '-'], ["D", '-'], ["E", '-'], ["F", '-'],
         ["P", '-'], ["G", '-'], ["GD", '-']]  # Nombres y puntajes de los juegos. Esta variable es en realidad muda,
# ya que su funcionalidad quedó implementada en la inicialización de las clases Player. Sin embargo, la mantuve porque
# tenerla al principio hace más fácil de leer el código (en mi opinión)
pygame.init()  # initialize pygame

# Tamaño de ventana
ancho = 840
alto = 600
# create screen
screen = pygame.display.set_mode((ancho, alto))  # (x.y), desde esquina sup izq
CONDITION = 0  # Estado de juego, diferentes valores indican diferentes estados de juego (single player, multiplayer,
# multiplayer choosing name phase, end of game, etc)
Puntaje = 0  # Puntaje inicial
IsRunning = True
Turn_Over = False

# Title and icon (png-32px)
pygame.display.set_caption("Generala")
icon = pygame.image.load('dice_6.png')
pygame.display.set_icon(icon)

# Dice Figures
DiceFigs = [pygame.image.load('dice_1.png'), pygame.image.load('dice_2.png'),
            pygame.image.load('dice_3.png'), pygame.image.load('dice_4.png'),
            pygame.image.load('dice_5.png'), pygame.image.load('dice_6.png')]
DiceFigsb = [pygame.image.load('dice_1b.png'), pygame.image.load('dice_2b.png'),
             pygame.image.load('dice_3b.png'), pygame.image.load('dice_4b.png'),
             pygame.image.load('dice_5b.png'), pygame.image.load('dice_6b.png')]

# sound
diceroll = mixer.Sound("dermotte_diceroll.wav")


class Player:
    """
    Clase jugador, cada jugador tiene su set de juegos y su puntaje.
    """

    def __init__(self, Pname, Names, Juego_Cerrado=None, Punt=0):
        if Juego_Cerrado is None:
            Juego_Cerrado = [False] * 12
        self.Pname = Pname
        self.Names = Names
        self.Juego_Cerrado = Juego_Cerrado
        self.Punt = Punt

    def Puntaje_Tot(self):
        """
        Calcula el puntaje total (Punt) sumando el de cada juego
        :return puntaje total del jugador
        """
        u = 0
        for n in range(len(self.Names)):
            if self.Names[n][1] != '-':
                u += self.Names[n][1]
        self.Punt = u
        return u

    def Calcula_puntos(self, tiro, tirnum, ind):
        """
        Calcula los puntos de una tirada de generala
        :param tiro: tirada de 5 dados (list)
        :param tirnum: número de tirada. Determina si es servida o no. (int)
        :param ind: indice que indica para qué juego se calculan los puntos (int)
        :return: -
        """

        servida = 0
        if tirnum == 1:
            servida = 5
        if ind == 0:
            self.Names[ind][1] = np.where(tiro == 1, tiro, 0).sum()
            self.Juego_Cerrado[ind] = True
        elif ind == 1:
            self.Names[ind][1] = np.where(tiro == 2, tiro, 0).sum()
            self.Juego_Cerrado[ind] = True
        elif ind == 2:
            self.Names[ind][1] = np.where(tiro == 3, tiro, 0).sum()
            self.Juego_Cerrado[ind] = True
        elif ind == 3:
            self.Names[ind][1] = np.where(tiro == 4, tiro, 0).sum()
            self.Juego_Cerrado[ind] = True
        elif ind == 4:
            self.Names[ind][1] = np.where(tiro == 5, tiro, 0).sum()
            self.Juego_Cerrado[ind] = True
        elif ind == 5:
            self.Names[ind][1] = np.where(tiro == 6, tiro, 0).sum()
            self.Juego_Cerrado[ind] = True
        elif ind == 6:  # doble
            seen = set()
            dupes = set([X for X in tiro if X in seen or seen.add(X)])
            if len(dupes) > 1:  # chequeo el doble
                self.Names[ind][1] = 10 + servida
            else:
                self.Names[ind][1] = 0
            self.Juego_Cerrado[ind] = True
        elif ind == 7:  # escalera
            u = set(tiro)
            if len(u) == len(tiro):
                self.Names[ind][1] = 20 + servida
            else:
                self.Names[ind][1] = 0
            self.Juego_Cerrado[ind] = True
        elif ind == 8:  # full
            u = set(tiro)
            if len(u) == 2:
                self.Names[ind][1] = 30 + servida
            else:
                self.Names[ind][1] = 0
            self.Juego_Cerrado[ind] = True
        elif ind == 9:  # poker
            u = set(tiro)
            seen = set()
            dupes = set([X for X in tiro if X in seen or seen.add(X)])
            if len(u) <= 2 and len(dupes) == 1:
                self.Names[ind][1] = 40 + servida
            else:
                self.Names[ind][1] = 0
            self.Juego_Cerrado[ind] = True
        elif ind == 10:  # generala
            u = set(tiro)
            if len(u) == 1:
                self.Names[ind][1] = 50 + servida
                self.Juego_Cerrado[ind] = True
            elif self.Names[11][1] == 0:  # if generala doble tachada
                self.Names[ind][1] = 0
                self.Juego_Cerrado[ind] = True
        elif ind == 11:  # generala doble
            u = set(tiro)
            if len(u) == 1 and self.Names[10][1] != 0:
                self.Names[ind][1] = 100 + servida
            else:
                self.Names[ind][1] = 0
            self.Juego_Cerrado[ind] = True


def text_print(xpos, ypos, text="", size=10):
    """
    Imprime texto en la ventana de pygame
    :param xpos: Posición en x del texto (int)
    :param ypos: Posición en y del texto (int)
    :param text: Texto (string)
    :param size: Tamaño de letra (int)
    :return: -
    """
    normal_font = pygame.font.Font('freesansbold.ttf', size)
    palabras = normal_font.render(text, True, (255, 255, 255))
    text_rect = palabras.get_rect(center=(int(xpos), int(ypos)))
    screen.blit(palabras, text_rect)


# Main game loop
while IsRunning:
    screen.fill((0, 102, 0))  # background color
    if CONDITION == 0:
        # loopea por todos los eventos que estan pasando en la ventana
        for event in pygame.event.get():
            # si toco el boton de cerrar, el ciclo para
            if event.type == pygame.QUIT:
                IsRunning = False

            x, y = pygame.mouse.get_pos()
            # hover over button
            if (int(ancho / 2) - 200 < int(x) < int(ancho / 2) + 200) and (250 - 50 < int(y) < 250 + 50):
                pygame.draw.rect(screen, (30, 102, 30), [int(ancho / 2) - 200, 250 - 50, 400, 100])
            elif (int(ancho / 2) - 200 < int(x) < int(ancho / 2) + 200) and (350 - 50 < int(y) < 350 + 50):
                pygame.draw.rect(screen, (30, 102, 30), [int(ancho / 2) - 200, 350 - 50, 400, 100])
            elif (int(ancho / 2) - 200 < int(x) < int(ancho / 2) + 200) and (450 - 50 < int(y) < 450 + 50):
                pygame.draw.rect(screen, (30, 102, 30), [int(ancho / 2) - 200, 450 - 50, 400, 100])

            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                if (int(ancho / 2) - 200 < int(x) < int(ancho / 2) + 200) and (250 - 50 < int(y) < 250 + 50):
                    CONDITION = 1  # singleP
                if (int(ancho / 2) - 200 < int(x) < int(ancho / 2) + 200) and (350 - 50 < int(y) < 350 + 50):
                    CONDITION = 3  # MultiP
                if (int(ancho / 2) - 200 < int(x) < int(ancho / 2) + 200) and (450 - 50 < int(y) < 450 + 50):
                    CONDITION = 6  # About

        text_print(ancho / 2, 60, "¡Bienvenido!", 60)
        text_print(ancho / 2, 250, "Un jugador", 50)
        text_print(ancho / 2, 350, "Multijugador", 50)
        text_print(ancho / 2, 450, "Créditos", 50)
        screen.blit(DiceFigs[0], (100, 150))
        screen.blit(DiceFigs[1], (100, 300))
        screen.blit(DiceFigs[2], (100, 450))
        screen.blit(DiceFigs[3], (700, 150))
        screen.blit(DiceFigs[4], (700, 300))
        screen.blit(DiceFigs[5], (700, 450))

        clock.tick(120)
        pygame.display.update()

    elif CONDITION == 1:  # single player set players, crea las clases Player
        s = Player("Player", [["1", '-'], ["2", '-'], ["3", '-'], ["4", '-'], ["5", '-'], ["6", '-'], ["D", '-'],
                              ["E", '-'], ["F", '-'],
                              ["P", '-'], ["G", '-'], ["GD", '-']])
        Players.append(s)
        b = Player("Bot", [["1", '-'], ["2", '-'], ["3", '-'], ["4", '-'], ["5", '-'], ["6", '-'], ["D", '-'],
                           ["E", '-'], ["F", '-'],
                           ["P", '-'], ["G", '-'], ["GD", '-']])
        Players.append(b)
        CONDITION = 2

    elif CONDITION == 2:  # singleplayer
        sleep(0.1)
        for idx, elem in enumerate(tirada):
            if isPressed[idx] == 1:
                screen.blit(DiceFigsb[elem - 1], (50 + 75 * idx, 50))
            else:
                screen.blit(DiceFigs[elem - 1], (50 + 75 * idx, 50))

        if P_turn == 1:  # Bot turn
            if np.random.rand() < 0.5 and Num_tir < 3:  # Tirar de nuevo
                mixer.Sound.play(diceroll)
                sleep(0.5)
                R = np.random.rand(5)
                for idx, r in enumerate(R):  # simula elegir los dados
                    if r < 0.5:
                        sleep(0.3)
                        isPressed[idx] *= -1
                pygame.draw.rect(screen, (30, 102, 30), [515, 25, 180, 50])
                Num_tir += 1
                for i in range(5):
                    if isPressed[i] == -1:
                        tirada[i] = np.random.randint(1, 7)
            else:  # Plantarse
                sleep(0.5)
                pygame.draw.rect(screen, (30, 102, 30), [515, 75, 180, 50])
                Turn_Over = True
                i = np.random.randint(0, 12)
                while Players[P_turn].Juego_Cerrado[i]:  # busca juego no cerrado
                    i = np.random.randint(0, 12)
                if not Players[P_turn].Juego_Cerrado[i]:
                    sleep(0.5)
                    pygame.draw.rect(screen, (30, 102, 30), [100 + 50 * i - 15, 185, 30, 30])
                    # calcula puntos y cierra el juego
                    Players[P_turn].Calcula_puntos(tirada, Num_tir, i)
                    if Players[P_turn].Juego_Cerrado[i]:
                        P_turn = (P_turn + 1) % len(Players)  # next player
                        Turn_Over = False
                        tirada = np.random.randint(1, 7, 5)
                        for idx, elem in enumerate(tirada):
                            screen.blit(DiceFigs[elem - 1], (50 + 75 * idx, 50))
                        isPressed = [-1] * 5
                        Num_tir = 1
                        mixer.Sound.play(diceroll)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                IsRunning = False
            if P_turn == 0:  # player turn
                if event.type == pygame.MOUSEBUTTONDOWN:
                    x, y = pygame.mouse.get_pos()
                    for i in range(5):
                        if (50 + 75 * i < int(x) < 50 + 75 * i + 64) and (50 < int(y) < 50 + 64):
                            isPressed[i] *= -1

                    if (515 < int(x) < 515 + 180) and (25 < int(y) < 75) and Num_tir < 3:  # Tirar de nuevo
                        mixer.Sound.play(diceroll)
                        pygame.draw.rect(screen, (30, 102, 30), [515, 25, 180, 50])
                        Num_tir += 1
                        for i in range(5):
                            if isPressed[i] == -1:
                                tirada[i] = np.random.randint(1, 7)

                    elif (515 < int(x) < 515 + 180) and (75 < int(y) < 125):  # Plantarse
                        pygame.draw.rect(screen, (30, 102, 30), [515, 75, 180, 50])
                        Turn_Over = True

                    elif Turn_Over:  # Seleccionar juego
                        for i in range(12):
                            if (100 + 50 * i - 15 < int(x) < 100 + 50 * i + 15) and (185 < int(y) < 215) and not \
                                    Players[P_turn].Juego_Cerrado[i]:
                                pygame.draw.rect(screen, (30, 102, 30), [100 + 50 * i - 15, 185, 30, 30])
                                # calcula puntos y cierra el juego
                                Players[P_turn].Calcula_puntos(tirada, Num_tir, i)
                                if Players[P_turn].Juego_Cerrado[i]:
                                    P_turn = (P_turn + 1) % len(Players)  # next player
                                    Turn_Over = False
                                    tirada = np.random.randint(1, 7, 5)
                                    for idx, elem in enumerate(tirada):
                                        screen.blit(DiceFigs[elem - 1], (50 + 75 * idx, 50))
                                    isPressed = [-1] * 5
                                    Num_tir = 1
                                    mixer.Sound.play(diceroll)
        if Num_tir == 3:  # máximo número de tiradas
            Turn_Over = True

        text_print(110, 25, f"Tirada N°: {Num_tir}", 20)
        text_print(600, 50, "Tirar de nuevo", 20)
        text_print(600, 100, "Plantarse", 20)
        text_print(600, 150, f"Juega: {Players[P_turn].Pname}", 20)
        k = 200

        # Print en pantalla
        for i in range(12):
            text_print(100 + 50 * i, k, names[i][0], 20)
        for j, p in enumerate(Players):
            for i in range(12):
                text_print(100 + 50 * i, k + 50 * (j + 1), str(p.Names[i][1]), 20)
            text_print(100 + 50 * 12, k + 50 * (j + 1), str(p.Puntaje_Tot()), 20)
            text_print(50, k + 50 * (j + 1), p.Pname, 20)
        text_print(100 + 50 * 12, k, "Total", 20)

        if np.all(Players[-1].Juego_Cerrado):  # Acaba el juego
            CONDITION = 5
        pygame.display.update()

    elif CONDITION == 3:  # multiplayer choose names
        sleep(0.1)
        if len(Player_Names) == 5:  # 5 players max
            for k in Player_Names:
                s = Player(k, [["1", '-'], ["2", '-'], ["3", '-'], ["4", '-'], ["5", '-'], ["6", '-'], ["D", '-'],
                               ["E", '-'], ["F", '-'],
                               ["P", '-'], ["G", '-'], ["GD", '-']])
                Players.append(s)
                np.random.shuffle(Players)
            CONDITION = 4  # max player num

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                IsRunning = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    Player_Names.append(p_name)
                    Player_Names = list(set(Player_Names))  # nombres diferentes
                    p_name = ""
                elif event.key == pygame.K_BACKSPACE:
                    try:
                        p_name = p_name[:-1]
                    except IndexError:  # ignora el error
                        pass
                elif pygame.key.name(event.key).__len__() > 1:
                    text_print(400, 550, "Solo se aceptan caractéres únicos, inténtelo de nuevo.", 12)
                    Player_Names = []
                    pygame.display.update()
                    sleep(0.3)
                else:
                    p_name += str(pygame.key.name(event.key))
                    # print(Player_Names)
            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                # print(x, y)
                if (625 < int(x) < 775) and (460 < int(y) < 530):  # Listo
                    pygame.draw.rect(screen, (30, 102, 30), [625, 460, 150, 70])
                    for k in Player_Names:
                        # sería más cómodo copiar names, pero para eso necesito un deepcopy y no quería agregar otra lib
                        s = Player(k,
                                   [["1", '-'], ["2", '-'], ["3", '-'], ["4", '-'], ["5", '-'], ["6", '-'], ["D", '-'],
                                    ["E", '-'], ["F", '-'],
                                    ["P", '-'], ["G", '-'], ["GD", '-']])
                        Players.append(s)
                        np.random.shuffle(Players)
                    CONDITION = 4

        text_print(ancho / 2, 60, "¿Quiénes Juegan?", 60)
        text_print(700, 500, "Listo", 60)
        text_print(450, 500, p_name, 45)

        pygame.display.update()

    elif CONDITION == 4:  # multiplayer
        sleep(0.1)
        for idx, elem in enumerate(tirada):
            if isPressed[idx] == 1:
                screen.blit(DiceFigsb[elem - 1], (50 + 75 * idx, 50))
            else:
                screen.blit(DiceFigs[elem - 1], (50 + 75 * idx, 50))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                IsRunning = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                for i in range(5):
                    if (50 + 75 * i < int(x) < 50 + 75 * i + 64) and (50 < int(y) < 50 + 64):
                        isPressed[i] *= -1

                if (515 < int(x) < 515 + 180) and (25 < int(y) < 75) and Num_tir < 3:  # Tirar de nuevo
                    mixer.Sound.play(diceroll)
                    pygame.draw.rect(screen, (30, 102, 30), [515, 25, 180, 50])
                    Num_tir += 1
                    for i in range(5):
                        if isPressed[i] == -1:
                            tirada[i] = np.random.randint(1, 7)

                elif (515 < int(x) < 515 + 180) and (75 < int(y) < 125):  # Plantarse
                    pygame.draw.rect(screen, (30, 102, 30), [515, 75, 180, 50])
                    Turn_Over = True

                elif Turn_Over:  # Seleccionar juego
                    for i in range(12):
                        if (100 + 50 * i - 15 < int(x) < 100 + 50 * i + 15) and (185 < int(y) < 215) and not \
                                Players[P_turn].Juego_Cerrado[i]:
                            pygame.draw.rect(screen, (30, 102, 30), [100 + 50 * i - 15, 185, 30, 30])
                            # calcula puntos y cierra el juego
                            Players[P_turn].Calcula_puntos(tirada, Num_tir, i)
                            if Players[P_turn].Juego_Cerrado[i]:
                                P_turn = (P_turn + 1) % len(Players)  # next player
                                Turn_Over = False
                                tirada = np.random.randint(1, 7, 5)
                                for idx, elem in enumerate(tirada):
                                    screen.blit(DiceFigs[elem - 1], (50 + 75 * idx, 50))
                                isPressed = [-1] * 5
                                Num_tir = 1
                                mixer.Sound.play(diceroll)

        if Num_tir == 3:
            Turn_Over = True

        text_print(110, 25, f"Tirada N°: {Num_tir}", 20)
        text_print(600, 50, "Tirar de nuevo", 20)
        text_print(600, 100, "Plantarse", 20)
        text_print(600, 150, f"Juega: {Players[P_turn].Pname}", 20)
        k = 200

        for i in range(12):
            text_print(100 + 50 * i, k, names[i][0], 20)
        for j, p in enumerate(Players):
            for i in range(12):
                text_print(100 + 50 * i, k + 50 * (j + 1), str(p.Names[i][1]), 20)
            text_print(100 + 50 * 12, k + 50 * (j + 1), str(p.Puntaje_Tot()), 20)
            text_print(50, k + 50 * (j + 1), p.Pname, 20)
        text_print(100 + 50 * 12, k, "Total", 20)

        if np.all(Players[-1].Juego_Cerrado):  # Acaba el juego
            CONDITION = 5
        pygame.display.update()

    elif CONDITION == 5:  # Game Over
        sleep(0.1)
        Tot = {a.Pname: a.Puntaje_Tot() for a in Players}
        winner = max(Tot, key=Tot.get)
        W = [k for k, v in Tot.items() if v == Tot[winner]]
        if len(W) > 1:  # empate
            text_print(410, 340, "Empataron ", 30)
            for idx, w in enumerate(W):
                text_print(400 + 100 * idx, 390, f"{w}", 30)
        else:
            text_print(410, 340, f"El ganador es: {winner} con {Tot[winner]} puntos.", 30)
        text_print(410, 300, "Juego Terminado", 30)
        text_print(460, 440, "Jugar de nuevo? (Y)/(N)", 28)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                IsRunning = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_y:
                    tirada = np.random.randint(1, 7, 5)
                    isPressed = [-1] * 5
                    Num_tir = 1
                    p_name = ""
                    Player_Names = []
                    Players = []
                    P_turn = 0
                    CONDITION = 0
                    Puntaje = 0
                    IsRunning = True
                    Turn_Over = False
                if event.key == pygame.K_n:
                    IsRunning = False

        pygame.display.update()

    elif CONDITION == 6:  # About
        sleep(0.1)
        about = pygame.image.load('About.png')
        screen.blit(about, (-60, 25))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                IsRunning = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                CONDITION = 0

        pygame.display.update()
