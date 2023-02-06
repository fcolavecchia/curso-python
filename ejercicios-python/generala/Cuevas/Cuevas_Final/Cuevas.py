# -*- coding: utf-8 -*-
"""
Created on Sat Apr  9 18:23:32 2022

@author: santi cuevas

Juega random!!

"""

import numpy as np
import pygame
import argparse



#Parseamos argumentos
parser = argparse.ArgumentParser(description='Jugadores...')

parser.add_argument('-n','--nombres',action='append', type=str, help='Nombre del jugador')

args=parser.parse_args()




pygame.init()
pygame.display.set_caption('Generala')
##CC: Ojo con las barras de directorios, pueden cambiar entre S.Os, con
## lo cual el código no corre.
programIcon = pygame.image.load('Dices/dice-6.png')
pygame.display.set_icon(programIcon)


class Jugador:
    def __init__(self,name,cpu=False):
        self.name=name
        self.J=dict(zip(Combos,[' ']*12))
        self.score=0
        self.cpu=cpu
        

#Variables globales a usar
Combos=['1','2','3','4','5','6','D','E','F','P','G','GD']
CombosActivos=dict(zip(Combos,[False]*12))

Nombres=args.nombres

if Nombres==None:
    Jugadores=[Jugador('Jugador')]
else:
    Jugadores=[Jugador(n) for n in Nombres]
NJ=len(Jugadores)    
    

if NJ==1:    
    #Jugadores=[Jugador('Tu Compu',cpu=True)]+Jugadores
    Jugadores.append(Jugador('Tu Compu',cpu=True))
    NJ+=1

#Jugadores=[Jugador('Tu Compu',cpu=True)]
#NJ=len(Jugadores)  

Rondas=1
ended= False



#Variables de dibujo
copete=100+40*NJ
sangria=230
tabfont = pygame.font.SysFont(None, 40)
font = pygame.font.SysFont(None, 60)
delay=False
longdelay=False

#Fondo de juego (canvas)
screen = pygame.display.set_mode([900, 450+NJ*40])

#cargamos imagenes de dados
##CC: Ojo con las barras de directorios, pueden cambiar entre S.Os, con
## lo cual el código no corre.
Ds={}
for i in range(6):
    i=i+1
    Di = pygame.image.load('Dices/dice-'+str(i)+'.png')
    Di = pygame.transform.scale(Di, (100, 100)).convert_alpha()
    Ds[i]=Di
     
#Creamos dados
Dados=np.random.randint(6,size=5)+1
#Dados=[1,2,3,4,5]
#print(Dados)
Rolleables=[False]*5



#Preparamos primera p-ronda
Turno=1
Ji=0
Scoring=False


#Chekeador de combos 
def combo_checker():
    'Actualiza variable CombosActivos según el valor de los Dados'
    #Diccionario con todos los combos en false
   
    
    for n in np.arange(0,6):
        if n+1 in Dados:
            CombosActivos[str(n+1)]=True
        else:
            CombosActivos[str(n+1)]=False
            
    CombosActivos['D']=sum(np.bincount(Dados)==2)==2
    CombosActivos['E']=(sum(np.bincount(Dados)==1)==5)and(6 not in Dados or 2 not in Dados or 1 not in Dados)
    CombosActivos['F']=(sum(np.bincount(Dados)==2)==1)and(sum(np.bincount(Dados)==3)==1)
    CombosActivos['P']=sum(np.bincount(Dados)==4)==1
    CombosActivos['G']=sum(np.bincount(Dados)==5)==1
    CombosActivos['GD']=CombosActivos['G'] and not(Jugadores[Ji].J['G']==' ' or Jugadores[Ji].J['G']=='x')
    
    
#la llamamos para tener los combos activos ya cargados 
combo_checker()
#print(CombosActivos)

#obtener puntaje
def get_score(combo):
    'Recibe el combo a anotar y devuelve el puntaje'
    if combo=='GD':
        score=100 + (Turno==1)*5
        return score
    
    if combo=='G':
        score=50 + (Turno==1)*5
        return score
    
    if combo=='P':
        score=40 + (Turno==1)*5
        return score
    
    if combo=='F':
        score=30 + (Turno==1)*5
        return score
    
    if combo=='E':
        score=20 + (Turno==1)*5
        return score
    
    if combo=='D':
        score=10 + (Turno==1)*5
        return score
    
    score=int(combo)*sum(np.array(Dados)==int(combo))
    return score
        

#clase para botones de dado
class but():
    def __init__(self,x,y):
        self.rect=pygame.Rect((x, y) ,(20,20))
        self.push=False
    
    def draw(self):
        pygame.draw.rect(screen, (0, self.push*240, 0), self.rect)
        
        pos=pygame.mouse.get_pos()
        
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0]==1:
                self.push= not self.push
                global delay
                delay=True
                #pygame.time.delay(100)
        
#Botones de acción      
class Abut():
    def __init__(self,x,y,text=' ',width=80,color=(0,0,200),shift=0):
        self.rect=pygame.Rect((x, y) ,(width,40))
        self.pushed=False
        self.text=font.render(text, True,(255, 255, 255))
        self.x=x
        self.y=y
        self.availiable=True
        self.color=color
        self.shift=shift
        self.name=text
    
    def draw(self):
        action=False
    
        if self.availiable:
            pygame.draw.rect(screen, self.color, self.rect)
        else:
            pygame.draw.rect(screen, (150,150,150), self.rect)
        screen.blit(self.text, (self.x+2+self.shift,self.y+2))
        
        pos=pygame.mouse.get_pos()
        
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0]==1 and self.pushed==False:
                self.pushed == True
                action=True
                
            #if pygame.mouse.get_pressed()[0]==0 :
                #self.pushed == False
        
        return action*self.availiable

#Rerollear dados
def roll_dices():
    for j in range(5):
        if Rolleables[j]:
            Dados[j]=np.random.randint(5)+1
    for B in Bs:
        B.push=False
    #print(Dados)
    combo_checker()
    #print(CombosActivos)
        
#Mostrar tabla
def cargar_tabla():
    #Dibujo combos
    xname=150
    for i in range(12):
        pygame.draw.rect(screen, (255, 255, 255), pygame.Rect(xname+55*i, 0, 55, 40))
        pygame.draw.rect(screen, (0, 0, 0), pygame.Rect(xname+55*i, 0, 55, 40),width=1)
        img = tabfont.render(Combos[i], True,(0,0,0))
        screen.blit(img, (xname+5+55*i, 6))
        
    pygame.draw.rect(screen, (255, 255, 255), pygame.Rect(xname+55*12, 0, 80, 40))
    pygame.draw.rect(screen, (0, 0, 0), pygame.Rect(xname+55*12, 0, 80, 40),width=1)
    img = tabfont.render('Total', True,(0,0,0))
    screen.blit(img, (xname+5+55*12, 6))
        
    for j in range(len(Jugadores)):
        
        pygame.draw.rect(screen, (255, 255, 255), pygame.Rect(0, (j+1)*40, xname, 40))
        pygame.draw.rect(screen, (0, 0, 0), pygame.Rect(0, (j+1)*40,xname, 40),width=1)
        img = tabfont.render(Jugadores[j].name, True,(0,0,0))
        screen.blit(img, (5, (j+1)*40+6))
        
        for i in range(12):
            pygame.draw.rect(screen, (255, 255, 255), pygame.Rect(xname+55*i, (j+1)*40, 55, 40))
            pygame.draw.rect(screen, (0, 0, 0), pygame.Rect(xname+55*i, (j+1)*40, 55, 40),width=1)
            img = tabfont.render(str(Jugadores[j].J[Combos[i]]), True,(0,0,0))
            screen.blit(img, (xname+5+55*i, (j+1)*40+6))
            
        pygame.draw.rect(screen, (255, 255, 255), pygame.Rect(xname+55*12, (j+1)*40, 80, 40))
        pygame.draw.rect(screen, (0, 0, 0), pygame.Rect(xname+55*12, (j+1)*40, 80, 40),width=1)
        img = tabfont.render(str(Jugadores[j].score), True,(0,0,0))
        screen.blit(img, (xname+5+55*12,(j+1)*40+6))
        
#Botones
Bs=[]
for i in range (5):
    Bs.append(but(sangria+46+i*100,copete+110))

rollBut=Abut(sangria+530,copete+30,'Tirar',100)    
scoreBut=Abut(20,copete+180,'Anotar',145,(0,0,0))
crossBut=Abut(20,copete+250,'Tachar',145,(0,0,0))

#Botones de puntaje
toscoreBs=[]
tocrossBs=[]

for i in range(6):
    toscoreBs.append(Abut(sangria+20+100*i,copete+180,Combos[i],70,(0,150,0),22))
    toscoreBs.append(Abut(sangria+20+100*i,copete+250,Combos[i+6],70,(0,150,0),20))
    tocrossBs.append(Abut(sangria+20+100*i,copete+180,Combos[i],70,(150,0,0),22))
    tocrossBs.append(Abut(sangria+20+100*i,copete+250,Combos[i+6],70,(150,0,0),20))    
toscoreBs[-1].shift=1
tocrossBs[-1].shift=1
        
#pasar ronda
def next_round():
    global Turno,Scoring,Dados,scoreBut,crossBut
    Turno=1
    Scoring=False
    Dados=np.random.randint(6,size=5)+1
    combo_checker()      
    scoreBut.pushed=False
    crossBut.pushed=False
    scoreBut.availiable=True
    crossBut.availiable=True
    
    for B in Bs:
        B.push=False
    
    global Ji
    if Ji==NJ-1:
        Ji=0
    else:
        Ji=Ji+1
        
    global Rondas,Rolleables
    Rondas=Rondas+1
    Rolleables=[False]*5
    
        
    #print('Turn change..')
    #print(Dados)
    #print(CombosActivos)

#Disponer los tachables
def set_tachables():
    for B in tocrossBs:
        if Jugadores[Ji].J[B.name]==' ':
            B.availiable=True
        else:
            B.availiable=False
    if Jugadores[Ji].J['G']==' ':
        tocrossBs[-1].availiable=False
            
            
#Disponer Scoreables
def set_scoreables():
    for B in toscoreBs:
        if Jugadores[Ji].J[B.name]==' ':
            if CombosActivos[str(B.name)]:
                B.availiable=True
            else:
                B.availiable=False
                
        else:
            B.availiable=False
            
    if not(Jugadores[Ji].J['G']==' ' or Jugadores[Ji].J['G']=='x') and  CombosActivos['G']:
        toscoreBs[-1].availiable=True
  

#Jugador de turno
NombreDisplays=[]
for J in Jugadores:
    NombreDisplays.append(Abut(20,copete+30,J.name,width=140,color=(78, 98, 84),shift=0))

#Winner
def set_winner():
     
    screen.fill((78, 98, 84))
    cargar_tabla()
    pygame.draw.rect(screen, (155, 155, 150), pygame.Rect(sangria/2+18, copete/2+75, 600, 240))
    pygame.draw.rect(screen, (0, 0, 0), pygame.Rect(sangria/2+18, copete/2+75, 600, 240),width=1)
    img = font.render('El Ganador es:', True,(0,0,0))
    screen.blit(img, (sangria/2+30, copete))
    
    maxScore=0
    #####ELEGIR GANADOR
    for J in Jugadores:
        if J.score>=maxScore:
            winner=J
            maxScore=J.score
            
    
    
    img = pygame.font.SysFont(None, 80).render(winner.name, True,(0,0,0))
    screen.blit(img, (sangria/2+180, copete+90))
    
    
###########################################################
#HORA DE LA CPU BRO
def AutoRoll():
    
    keepgoing=True
    
    C=np.bincount(Dados)
    for i in range(5):   
        
        #Random
        #Bs[i].push=bool(np.random.choice([True, False]))
        #Rolleables[i]=Bs[i].push
        
        if C[Dados[i]]==1:
            Bs[i].push=True
            Rolleables[i]=Bs[i].push
        else:
            Bs[i].push=False
            Rolleables[i]=Bs[i].push
            
            
    global longdelay
    if sum(Rolleables)==0:
        AutoScore()
        next_round()
        longdelay=True
        keepgoing=False
        
    if CombosActivos['E'] and Jugadores[Ji].J['E']==' ':
        AutoScore()
        next_round()
        longdelay=True
        keepgoing=False
        
            
            
    if keepgoing:
        roll_dices()
        global Turno
        Turno=Turno+1
        #print('PC turn',Turno)
     
def AutoScore():
    anoted=False
    
    for combo in reversed(Combos[5:]):
        if CombosActivos[combo]:
            if Jugadores[Ji].J[combo]==' ':
            
                round_score=get_score(combo)
                Jugadores[Ji].J[combo]=round_score
                Jugadores[Ji].score+=round_score
                
                anoted=True
            
      
                break
            
            
    if not anoted:
        maxCount=0
        maxCombo=''
        Counts=np.bincount(Dados)
        Counts=list(Counts)+(8-len(Counts))*[0]
        for i in range(1,7):
            if Counts[i]>maxCount and Jugadores[Ji].J[str(i)]==' ' :
                maxCombo=str(i)
                maxCount=Counts[i]
                
        if maxCombo != '':
            
            round_score=get_score(maxCombo)
            Jugadores[Ji].J[maxCombo]=round_score
            Jugadores[Ji].score+=round_score
                
            anoted=True
            
        
    if not anoted:
        for combo in Combos:
            if Jugadores[Ji].J[combo]==' ':
                Jugadores[Ji].J[combo]='x'
                break
            
        
#########################################################################            
    
    





# Run until the user asks to quit
running = True
while running:
    
 
    
    
    
    
    
    
    # Fill the background 
    screen.fill((78, 98, 84))
    
    #Dibujar tabla
    cargar_tabla()
    
    
   
    
   
    # Did the user click the window close button?
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
  
    if not ended:    
        
        #Nombre de jugador de turno
        NombreDisplays[Ji].draw()
        
        
        
        #Mostrar dados
        for j in range(5):
            screen.blit(Ds[Dados[j]],(sangria+j*100+10,copete))
            
       
        #Dibujar Botones
        if Turno<3 and not Scoring and not Jugadores[Ji].cpu:
            for i in range(5):
                Bs[i].draw()
                    
                Rolleables[i]=Bs[i].push
                
                
            if rollBut.draw():
                #print('Roll dices...'+str(Turno))
                if sum(Rolleables):
                    Turno=Turno+1
                    #print('Turno:',Turno)
                    roll_dices()
                    delay=True
               
               
        #Si no es posible anotar anulamos el "scoreBut"
        set_scoreables()
        
        if sum([B.availiable for B in toscoreBs])==0:
            scoreBut.availiable=False
        #Si no lo mostramos disponible (excepto que estemos tachando o ya se haya presionado el de tachar)
        else:
            if not crossBut.pushed:
                scoreBut.availiable=True
                
                
                
                
        #############################        
        #TURNO DE LA CPU
        if Jugadores[Ji].cpu:
            if Turno>=3:
                AutoScore()
                next_round()
                longdelay=True
            
            else:
                AutoRoll()
                longdelay=True
        ##############################  
            
                
             
        
        
        if scoreBut.draw():
            Scoring=True
            crossBut.availiable=False
            
        
        if crossBut.draw():
            Scoring=True
            scoreBut.availiable=False
            crossBut.pushed=True
            set_tachables()
            
    
            
        if Scoring and scoreBut.availiable:
            for B in toscoreBs:
                if B.draw():
                    round_score=get_score(B.name)
                    Jugadores[Ji].J[B.name]=round_score
                    Jugadores[Ji].score+=round_score
                    next_round()
        
        if Scoring and crossBut.availiable:
            for B in tocrossBs:
                if B.draw():
                    Jugadores[Ji].J[B.name]='x'
                    next_round()
                
        
    
    
    #pygame.time.delay(100)
    if(Rondas==12*NJ+1):
        set_winner()
        ended=True
    
    #set_winner()
    
    # Flip the display
    pygame.display.flip()
    
    
    if delay:
        pygame.time.delay(250)
        delay=False
        
    if longdelay:
        pygame.time.delay(800)
        longdelay=False
        
    

# Done! Time to quit.
pygame.quit()