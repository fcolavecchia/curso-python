from tkinter import *
# from pandastable import Table, TableModel
# import pandas as pd
import numpy as np
import time
import argparse
import final_Estrada_calculos as calc
import final_Estrada_bot as bot
import sys
from datetime import datetime

def destroy_all_widgets(lista): #se le entrega una lista de secciones de la interfaz gráfica y remueve sus componentes.
    for frame in lista:
        for widgets in frame.winfo_children():
            widgets.destroy()

def mainapp(partido):
    
    def salir(): #es la manera mas prolija para salir de la interfaz. Si el usuario usa la X de la ventana o usa el botón salir, tkinter sale de la pausa y cierra mainapp (ver funcion 'pausar')
        exitVar.set(True)
        pauseVar.set(True)
        sys.exit()

    def pausar(pauseVar,exitVar):
        mainwindow.wait_variable(pauseVar) #Importantisimo. Esto hace al programa esperar a que el usuario realice alguan acción que cambie el estado de 'pauseVar'
        if exitVar.get()==True: #si se presiona la X de la ventana o se presiona 'Salir' la variable exitVar pasa a ser True
            quit()
        pauseVar.set(False) #Al salir de la pausa (wait_variable) se setea pauseVar como False para que el programa se pase cuando vuelva a llamarse a 'wait_variable'

    def iniciar_partido(): #esta función controla principalmente la interacción con la interfaz gráfica.
        global t 
        global tabla_pandas

        def cambiar_dado(n): #esta función es llamada cuando se clickea sobre el dado n-esimo 
            dados.cambiar(n) #marca el dado n-esimo para ser sorteado cuando se llame a la funcion 're-roll'
            if dados.guardar[n]==True:
                d[n]['relief']=RAISED #cambia el relieve del boton del dado
            else:
                d[n]['relief']=SUNKEN

            boton_tirar["state"] = "normal" #habilita presionar el boton para re lanzar los dados

        def accion_conservar_dados(): #esta funcion se activa cuando el usuario decide no volver a lanzar ningun dado
            global conservar_dados
            conservar_dados=True
            pauseVar.set(True) #sale de la pausa y la interfaz continua a la proxima ventana

        def reclamar_tachar(partido,jugador,dados,reclamables,tachables): #esta funcion controla la interaccion del usuario para cobrar o tachar los juegos que quedaron luego de arrojar 3 veces los dados.
            global reclamar
            global tachar

            def reclamar_juego(r): #devuelve en 'reclamar' el nombre del juego seleccionado y quita la pausa
                global reclamar
                reclamar=r
                pauseVar.set(True)
            def tachar_juego(t): #devuelve en 'tachar' el nombre del juego seleccionado y quita la pausa
                global tachar
                tachar=t
                pauseVar.set(True)

            def boton_reclamar(parent,juego): #definicion del boton para reclamar un juego disponible
                button=Button(parent,text=juego,command=lambda *args: reclamar_juego(juego),height = 1,width = 1)
                button.pack(side=LEFT)

            def boton_tachar(parent,juego): #definicion del boton para tachar un juego disponible
                button=Button(parent,text=juego,command=lambda *args: tachar_juego(juego),height = 1,width = 1)
                button.pack(side=LEFT)

            #-------------GRÁFICOS-------------
            destroy_all_widgets([bottom_frame1,bottom_frame2]) #elimina los dados y botones usados en el paso anterior

            dado_img={} #a partir de aqui se re definen imagenes para nuevos dados y sus ubicaciones
            for d in range(5):
                dado_img[d]=PhotoImage(file=calc.ruta_dado(dados.valores[d])) #dados.valores devuelve el valor del dado y ruta_dado devuelve una imagen para ese valor de dado   
                dado_img[d] = dado_img[d].subsample(12,12)
            d=[]
            d.append(Label(center_frame,image=dado_img[0],height = 100,width = 100))
            d[0].pack(side=LEFT)
            d.append(Label(center_frame,image=dado_img[1],height = 100,width = 100))
            d[1].pack(side=LEFT)
            d.append(Label(center_frame,image=dado_img[2],height = 100,width = 100))
            d[2].pack(side=LEFT)
            d.append(Label(center_frame,image=dado_img[3],height = 100,width = 100))
            d[3].pack(side=LEFT)
            d.append(Label(center_frame,image=dado_img[4],height = 100,width = 100))
            d[4].pack(side=LEFT)

            text=Label(bottom_frame1,text='Juegos que puede reclamar') #caja de texto
            text.config(font=('Neutra Display Titling',15))
            text.pack(expand=False,side=LEFT)
            
            reclamar=None
            boton1={}
            for juego in reclamables:
                boton1[juego]=boton_reclamar(bottom_frame1,juego) #crea un boton para cada juego reclamable

            text=Label(bottom_frame2,text='Juegos que puede tachar') #caja de texto
            text.config(font=('Neutra Display Titling',15))
            text.pack(expand=False,side=LEFT)

            tachar=None
            boton2={}
            for juego in tachables:
                boton2[juego]=boton_tachar(bottom_frame2,juego) #crea un boton para cada juego tachable

            pausar(pauseVar,exitVar)

            destroy_all_widgets([top_frame,center_frame,bottom_frame1,bottom_frame2])
            #-------------FIN-GRÁFICOS-------------

            if reclamar in ['1','2','3','4','5','6']: #esta parte es requerida para que al cobrar un juego de 'numeros repetidos' el puntaje varia segun la cantidad de dados iguales
                repetidos=np.sum(dados.valores==int(reclamar))
                return(reclamar,tachar,repetidos)
            else:
                return(reclamar,tachar,0)

        #Aqui comienzan j rondas donde se repite un turno para cada jugador=================
        for j in range(t):
            for jugador in partido['Jugadores']: #la interfaz gráfica para humano o bot es muy parecida, por lo que solo se cambian algunos detalles segun si el metodo jugador.humano es True o False

                #-------------GRÁFICOS-------------
                destroy_all_widgets([top_frame,center_frame,bottom_frame1,bottom_frame2])
                tabla_pandas.destroy()
                tabla_pandas = calc.DataFrameTable(parent=top_frame, df=calc.creardf(partido)) #se refresca la tabla de puntajes al comienzo de cada turno

                imagen=PhotoImage(file=calc.ruta_avatar(jugador.dificultad))  #imagen que representa al jugador
                imagen = imagen.subsample(5,5)   
                avatar=Label(center_frame,image=imagen)
                avatar.pack(expand=False,side=LEFT)

                text=Label(center_frame,text='Juega:\n%s'%jugador.nombre) #caja de texto con nombre
                text.config(font=('Neutra Display Titling',20))
                text.pack(expand=False,side=LEFT)

                text=Label(center_frame,text='Puntos: %s'%jugador.calcular_puntos()) #caja de texto con puntos
                text.config(font=('Neutra Display Titling',20))
                text.pack(expand=False,side=RIGHT)
                #-------------FIN-GRÁFICOS-------------

                if jugador.humano==True: #Si el jugador es humano los dados van a ser botones y se agrergan los botones con comandos 'volver a tirar' y 'conservar todos'
                    for i in range(2): #el jugador puede re-lanzar los dados hasta 2 veces, si decide conservar los dados este for es cortado con un break
                        #-------------GRÁFICOS-------------
                        if i==0:
                            dados=calc.nuevos_dados() #en la primera tirada los dados deben ser creados nuevos (la clase nuevos_dados ya se inicia con dados al azar)

                            info=Label(bottom_frame1,text='Seleccione dados y luego presione "Volver a tirar" para descartarlos o "Conservar todos" para continuar.',height = 1,width = 100)
                            info.config(font=('Neutra Display',15)) #caja de texto con instrucciones
                            info.pack(side=LEFT)

                            boton_tirar=Button(bottom_frame2,text='Volver a tirar',state=DISABLED,command=lambda *args: pauseVar.set(True),height = 2,width = 15)
                            boton_tirar.pack(side=LEFT) #El boton de volver a tirar simplemente quita la pausa para pasar al siguiente paso

                            global conservar_dados
                            conservar_dados=False
                            boton_notirar=Button(bottom_frame2,text='Conservar todos',command=accion_conservar_dados,height = 2,width = 15)
                            boton_notirar.pack(side=LEFT) #el boton conservar todos cambia la variable 'conservar_todos' lo que luego hace frenar el loop for

                        else:
                            boton_tirar["state"] = "disabled"
                            for n in [0,1,2,3,4]:
                                d[n].destroy() #si no es la primera tirada de dados, se remueven los dados viejos y se desactiva el boton 'tirar de nuevo' hasta que vuelva a elegirse al menos un dado

                        dado_img={} #a partir de aqui se re definen botones para nuevos dados y sus ubicaciones
                        for d in range(5):
                            dado_img[d]=PhotoImage(file=calc.ruta_dado(dados.valores[d]))    
                            dado_img[d] = dado_img[d].subsample(12,12)
                        d=[]
                        d.append(Button(center_frame,relief=RAISED,image=dado_img[0],command=lambda *args: cambiar_dado(0),height = 100,width = 100))
                        d[0].pack(side=LEFT)
                        d.append(Button(center_frame,relief=RAISED,image=dado_img[1],command=lambda *args: cambiar_dado(1),height = 100,width = 100))
                        d[1].pack(side=LEFT)
                        d.append(Button(center_frame,relief=RAISED,image=dado_img[2],command=lambda *args: cambiar_dado(2),height = 100,width = 100))
                        d[2].pack(side=LEFT)
                        d.append(Button(center_frame,relief=RAISED,image=dado_img[3],command=lambda *args: cambiar_dado(3),height = 100,width = 100))
                        d[3].pack(side=LEFT)
                        d.append(Button(center_frame,relief=RAISED,image=dado_img[4],command=lambda *args: cambiar_dado(4),height = 100,width = 100))
                        d[4].pack(side=LEFT)
                
                        pausar(pauseVar,exitVar)
                        
                        for n in [0,1,2,3,4]:
                            d[n].destroy()
                        #-------------FIN-GRÁFICOS-------------

                        if conservar_dados: #si el usuario presiona el boton 'conservar todos' el loop se rompe, sino se re-rollean los dados.
                            break
                        else:
                            dados.re_roll()

                    (reclamables,tachables)=calc.juegos_disponibles(dados,jugador)  #esta funcion devuelve los juegos disponibles en funcion de los dados y de los juegos tachados o reclamados de jugador.tabla     

                    reclamar,tachar,repetidos=reclamar_tachar(partido,jugador,dados,reclamables,tachables) #esta funcion llama a la interfaz gráfica donde el usario indicara que juego tachar o reclamar

                    #las funciones reclamar_juego y tachar_juego modifican los valores de jugador.tabla según lo que haya elegido el jugador
                    if reclamar!=None: 
                        jugador.reclamar_juego(reclamar,dados.servida,repetidos)
                    if tachar!=None:
                        jugador.tachar_juego(tachar)

                elif jugador.humano==False: #si el jugador es bot, solo estan disponibles los botones 'Ok' y 'Salir'
                    dados=calc.nuevos_dados()

                    #-------------GRÁFICOS-------------
                    if fastplay==False: #si esta puesto el modo rapido, el programa se ahorra cargar las imagenes
                        dado_img={}
                        for i in range(5):
                            dado_img[i]=PhotoImage(file=calc.ruta_dado(dados.valores[i]))    
                            dado_img[i] = dado_img[i].subsample(12,12)
                        d=[]
                        d.append(Label(center_frame,image=dado_img[0],height = 100,width = 100)) #Los dados aquí no son botones sino solo imagenes
                        d[0].pack(side=LEFT)
                        d.append(Label(center_frame,image=dado_img[1],height = 100,width = 100))
                        d[1].pack(side=LEFT)
                        d.append(Label(center_frame,image=dado_img[2],height = 100,width = 100))
                        d[2].pack(side=LEFT)
                        d.append(Label(center_frame,image=dado_img[3],height = 100,width = 100))
                        d[3].pack(side=LEFT)
                        d.append(Label(center_frame,image=dado_img[4],height = 100,width = 100))
                        d[4].pack(side=LEFT)
                        
                        text=Label(bottom_frame1,text='Estoy pensando...') #caja con texto simpático
                        text.config(font=('Neutra Display Titling',15))
                        text.pack(expand=False,side=LEFT)

                    mainwindow.after(1000,lambda *args: pauseVar.set(True))
                    #-------------FIN-GRÁFICOS-------------
                    
                    (jugada,reclamar,dados)=bot.bot(jugador,dados) #toma de decisiones del bot en otro programa
                    #bot.bot puede llevar un argumento opcional (nsimulaciones=10). De ese numero depende la cantidad de predicciones para cada decision.
                    
                    if fastplay==False:
                        pausar(pauseVar,exitVar)

                    #-------------GRÁFICOS-------------
                    if fastplay==False: #si esta puesto el modo rapido, el programa se ahorra cargar las imagenes y botones
                        for i in range(5):
                            d[i].destroy()
                            if jugador.dificultad==3: #el bot que hace trampa no va a motrar sus dados
                                dado_img[i]=PhotoImage(file=calc.ruta_dado('x')) #ruta_dado('x') lleva siempre a una imagen de un dado con '?'
                            else:
                                dado_img[i]=PhotoImage(file=calc.ruta_dado(dados.valores[i])) #si es el bot1 o bot2 muestra sus dados   
                            dado_img[i] = dado_img[i].subsample(12,12)
                        d=[]
                        d.append(Label(center_frame,image=dado_img[0],height = 100,width = 100))
                        d[0].pack(side=LEFT)
                        d.append(Label(center_frame,image=dado_img[1],height = 100,width = 100))
                        d[1].pack(side=LEFT)
                        d.append(Label(center_frame,image=dado_img[2],height = 100,width = 100))
                        d[2].pack(side=LEFT)
                        d.append(Label(center_frame,image=dado_img[3],height = 100,width = 100))
                        d[3].pack(side=LEFT)
                        d.append(Label(center_frame,image=dado_img[4],height = 100,width = 100))
                        d[4].pack(side=LEFT)

                        if reclamar:
                            text['text']='Juego reclamado: %s'%jugada #texto que avisa la eleccion del bot
                        else:
                            text=Label(bottom_frame1,text='Juego tachado: %s'%jugada) #texto que avisa la eleccion del bot
                        text.config(font=('Neutra Display Titling',15))
                        text.pack(expand=False,side=LEFT)

                        boton_saltear=Button(bottom_frame2,text='Ok',command=lambda *args: pauseVar.set(True),height = 1,width = 10) #boton para que el usario confirme
                        boton_saltear.pack(side=LEFT)

                    #-------------FIN-GRÁFICOS-------------

                    if fastplay==False: #si no esta puesto el modo rapido, la interfaz espera a que el usuario presione 'Ok'
                        pausar(pauseVar,exitVar)
        #Aqui terminan las j rondas=========================================================

        #Mensaje final
        destroy_all_widgets([center_frame,bottom_frame1,bottom_frame2])
        center_frame.destroy() #remover la caja de texto y dados de la ultima jugada
        bottom_frame2.destroy()
        tabla_pandas.destroy()
        tabla_pandas = calc.DataFrameTable(parent=top_frame, df=calc.creardf(partido))
        linea=[]
        for jugador in partido['Jugadores']: 
            linea.append(jugador.nombre)
            linea.append(str(jugador.calcular_puntos()))  #crear un string con los nombres y puntos
        text=Label(bottom_frame1,text='Juego terminado:\n %s'%linea) #caja de texto con puntos
        text.config(font=('Neutra Display Titling',20))
        text.pack(expand=False,side=RIGHT)

        #----------Output-----------
        if args.output:
            salida = ",".join(linea) #formato tipo CSV
            with open('partidos_generala.txt', 'a') as f:
                f.write(salida) #cada partido jugado sera una linea del archivo txt
                f.write('\n')

    
    #-------------GRÁFICOS-------------
    mainwindow= Tk()
    mainwindow.title("Generala")
    mainwindow.geometry('1200x400')
    mainwindow.protocol("WM_DELETE_WINDOW",salir)
    #-------------Variables de control de flujo de la interfaz-------------
    pauseVar = BooleanVar()
    pauseVar.set(False)
    exitVar=BooleanVar()
    exitVar.set(False)
    
    top_frame = Frame(mainwindow, relief='raised', borderwidth=2) #tercio superior de la ventana
    top_frame.place(relx=0.5, rely=0.1, anchor=N)

    global tabla_pandas
    tabla_pandas = calc.DataFrameTable(parent=top_frame, df=calc.creardf(partido)) #tabla con puntos de cada jugador

    center_frame = Frame(mainwindow, relief='raised', borderwidth=2)  #tercio medio de la ventana
    center_frame.place(relx=0.5, rely=0.6, anchor=CENTER)

    bottom_frame1 = Frame(mainwindow, relief='raised', borderwidth=2) #tercio inferior de la ventana para botones superiores
    bottom_frame1.place(relx=0.5, rely=0.8, anchor=CENTER)

    text=[]
    text.append(Label(center_frame,text='Orden de juego:\n')) #caja de texto inicial
    text[-1].config(font=('Neutra Display Titling',20))
    text[-1].pack(expand=False,side=LEFT)
    i=0
    for jugador in partido['Jugadores']:
        i=i+1
        text.append(Label(center_frame,text=' %i) '%i+str(jugador.nombre))) #se escriben los nombres de los jugadores en orden de la ronda
        text[-1].config(font=('Neutra Display Titling',20))
        text[-1].pack(expand=False,side=LEFT)

    bottom_frame2 = Frame(mainwindow, relief='raised', borderwidth=2) #tercio inferior de la ventana para botones inferiores
    bottom_frame2.place(relx=0.5, rely=0.9, anchor=CENTER)

    boton_comenzar=Button(bottom_frame2,text='Comenzar',command=iniciar_partido,height = 2,width = 15)  #boton comenzar, solo en la primera ventana
    boton_comenzar.pack(side=LEFT)

    salir_frame = Frame(mainwindow, relief='raised', borderwidth=2) 
    salir_frame.place(relx=0.9, rely=0.9, anchor=CENTER)
    boton_salir=Button(salir_frame,text='Salir',command=salir,height = 2,width = 15) #este boton se mantiene todo el tiempo en la interfaz
    boton_salir.pack(side=RIGHT)

    if fastplay==False: #si esta activado el fastplay se salteara parte de la interfaz grafica (util para bots)
        pausar(pauseVar,exitVar)

    mainwindow.mainloop()

#MAIN
parser = argparse.ArgumentParser(description='Juego de Generala. Puede ingresarse mas de un jugador. Pueden activarse mas de un bot en simulteneo.')
exclusivos = parser.add_mutually_exclusive_group()
exclusivos.add_argument('-n','--nombre',action='append',default=None,help='Ingresar nombre del jugador (humano)')
parser.add_argument('-b1','--bot1',action='store_true',default=False,help='Activar jugador simulado (easy peasy lemon squeezy)')
parser.add_argument('-b2','--bot2',action='store_true',default=False,help='Activar jugador simulado (hard)')
parser.add_argument('-b3','--bot3',action='store_true',default=False,help="Activar jugador simulado (it's very difficult)")
exclusivos.add_argument('-r','--rapido',action='store_true',default=False,help="Modo rapido para probar bots")
parser.add_argument('-o','--output',action='store_true',default=False,help='Al concluir el partido se guardan los puntajes en un txt')
args = parser.parse_args()

fastplay=args.rapido #cuando sea True se saltea el comando que le pide a Tkinter esperar.
partido=calc.nuevopartido(args.nombre,args.bot1,args.bot2,args.bot3) #inicia un diccionario con datos recolectados de parser y crea un elemento jugador() para cada nombre y bot.

t=len(calc.juegos) #la cantidad de turnos (t) depende de la tabla de juegos, por si en algun momento se agregan o quitan juegos de dados.

mainapp(partido) #programa principal del juego

sys.exit()