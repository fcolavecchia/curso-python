# -*- coding: utf-8 -*-
"""
Created on Thu Apr 14 15:28:18 2022

@author: KelvinJ
"""


import sys
import argparse
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from scipy.constants import m_e, pi, eV
from tkinter import _flatten
import matplotlib.animation as animation
plt.ioff()
VERSION = 1.0

# =============================================================================
# Etapa 1
# =============================================================================

# -----------------------------------------------------------------------------

""" 1. Escribir un programa que simule el decaimiento espontáneo
       de N partículas en una caja y permita obtener el número
       partículas como función del tiempo"""

##-----------------------------------------------------------------------------
#### El numero de particulas como función del tiempo
# se puede pensar como una distribución de Poisson

parser=argparse.ArgumentParser( 
    description='Decaimiento')

parser.add_argument('-N0','--N0', dest='N0', default=1000)
#parser.add_argument('-output','--output', dest='output', default=sys.stdout)
args = parser.parse_args()

#output=args.output
N0=int(args.N0) 


def particulas(N,P):
    
    dt=0.13/P
    time=[] # registrar el tiempo
    part=[] # para agregar el numero de particulas
    t=0
    
    while N>0: # mintras haya particulas
        
        part.append(N)
        time.append(t)
        mu=N*P*dt   #muestras
        k=np.random.poisson(lam=mu, size=None)  # lam: eventos-decay que ocurren en un intervalo dt
        N+=-k # actualizo el numero de particulas
        t+=dt
    
    
    return np.array(time), part

t, x=particulas(1000,0.13)
plt.plot(t,x,'o')
plt.ylabel('N(t)')
plt.xlabel('t')
plt.show()

sup='Decaimiento de particulas'
sup +='\n \n tiempo (s)'
sup +=' Numero de Particulas'

np.savetxt('output',list(zip(t,x)), header = sup, fmt='%12.3f')
np.loadtxt('output')

##--------------------------------------------------------------------

""" 2. Graficar el número de partículas N(t) y de la diferencia ΔN 
como función del tiempo t para distintos valores del número inicial
 de partículas N0=10,100,…,100000 (logarítmicamente espaciado)."""
 
##-------------------------------------------------------------------

# la diferencia ΔN son las particulas que se emiten en cada intervalo de tiempo

##---------------------------------------------------------

def delta_part(N,P):
    
    dt=0.13/P
    time=[] # registrar el tiempo
    dif=[] # para agregar el numero de particulas
    t=0
    
    while N>0: # mintras haya particulas
        
        
        mu=N*P*dt   #muestras
        k=np.random.poisson(lam=mu, size=None)  # lam: eventos que ocurren en un intervalo dt
        dif.append(k)
        N+=-k # actualizo el numero de particulas
        t+=dt
        time.append(t)
    
    
    return np.array(time), dif
##---------------------------------------------------------

##### Graficos

fig, (ax1,ax2)=plt.subplots(2, 1, sharex=True, figsize=(6,6))
valores_N=np.logspace(1,5,5)
ax1.semilogy()
#ax1.set_txt(10,10,r'10',ha='right',va='top')
ax2.semilogy()
tau=1/0.13
for xx in valores_N:
    t1, f=particulas(xx,0.13)
    t2, g=delta_part(xx, 0.13)
    ax1.plot(t1/tau, f,'-o',ms=3, label='{}'.format(int(xx)) )
    ax2.plot(t2/tau, g,'-o',ms=2, label='{}'.format(xx) )
    ax1.set_ylabel('$N(t)$')
    ax2.set_xlabel(r'$t/\tau\quad\rm$')
    ax2.set_ylabel('$\Delta N(t)$')
    ax1.legend(loc=1)
plt.subplots_adjust(wspace=0, hspace=0)
plt.show()


#------------------------------------------------------------------------------

"""3. Ajuste los valores de N(t) suponiendo que tiene un comportamiento del tipo"""

#------------------------------------------------------------------------------

######### ajuste exponencial 

def fit_funcion(t, B, lamda):
  y = B*np.exp(-lamda*t)
  return y

def ajuste(x):
    #### generación de datos
    xdata, ydata=particulas(x,0.13)
    tt=xdata
    yy=ydata
    rng= np.random.default_rng()
    ruido = rng.normal(size=len(yy))
    y=np.array(yy)+0.1*ruido
    ### condiciones iniciales u ajuste
    initial_guess= [x+10, 0.3]
    params, p_covarianza = curve_fit(fit_funcion, tt, y, 
                                     bounds=([x-10,0.1],initial_guess))
    yfit=fit_funcion(tt,*params)
    
    return tt, y, yfit, params   
sfuncion= r'${:0.2f}\, \exp(-{:.2f} t)$'

fig, axs = plt.subplots(2, 2, figsize=(10,10))
t1,y1,y1_fit, params1=ajuste(10)
axs[0,0].plot(t1,y1,'o', label='datos' )
label1=sfuncion.format(*params1)
axs[0,0].plot(t1,y1_fit,'--', label=label1 )
axs[0,0].legend(loc='best')

t2,y2,y2_fit, params2=ajuste(100)
axs[0,1].plot(t2,y2,'o', label='datos' )
label2=sfuncion.format(*params2)
axs[0,1].plot(t2,y2_fit,'--', label=label2 )
axs[0,1].legend(loc='best')

t3,y3,y3_fit,params3=ajuste(1000)
axs[1,0].plot(t3,y3,'o', label='datos' )
label3=sfuncion.format(*params3)
axs[1,0].plot(t3,y3_fit,'--', label=label3 )
axs[1,0].legend(loc='best')

t4,y4,y4_fit,params4=ajuste(10000)
axs[1,1].plot(t4,y4,'o', label='datos' )
label4=sfuncion.format(*params4)
axs[1,1].plot(t4,y4_fit,'--', label=label4 )
axs[1,1].legend(loc='best')

plt.subplots_adjust(wspace=0.5, hspace=0.3)
plt.show()


####-------------------------------------------------------------------------


####--------------------------------------------------------------------------

###### ajuste con y=A*t^alpha

def fit_function(tt, A, alfa):
  y2 = A*tt**(alfa)
  return y2

def fiteo(x):
    #### generación de datos
    xdata, ydata=particulas(x,0.13)
    tt=xdata[1:] # evitar la division por  cero (t=0)
    yy=ydata[1:] 
    rng= np.random.default_rng()
    ruido = rng.normal(size=len(yy))
    y=np.array(yy)+0.1*ruido
    ### condiciones iniciales u ajuste
    initial_guess= [0.1*x, -0.5]
    params, p_covarianza = curve_fit(fit_function, tt, y, initial_guess)
    yfit=fit_function(tt,*params)
    
    return tt, y, yfit, params   

gfuncion= r'${:0.2f}\, t**({:.2f})$'

fig, ays = plt.subplots(2, 2, figsize=(10,10))
tt1,yy1,yy1_fit, parametros1=fiteo(10)
ays[0,0].plot(tt1,yy1,'o', label='datos' )
lab1=gfuncion.format(*parametros1)
ays[0,0].plot(tt1,yy1_fit,'--', label=lab1 )
ays[0,0].legend(loc='best')

tt2,yy2,yy2_fit, parametros2=fiteo(100)
ays[0,1].plot(tt2,yy2,'o', label='datos' )
lab2=gfuncion.format(*parametros2)
ays[0,1].plot(tt2,yy2_fit,'--', label=lab2 )
ays[0,1].legend(loc='best')

tt3,yy3,yy3_fit, parametros3=fiteo(1000)
ays[1,0].plot(tt3, yy3,'o', label='datos' )
lab3=gfuncion.format(*parametros3)
ays[1,0].plot(tt3, yy3_fit,'--', label=lab3 )
ays[1,0].legend(loc='best')

tt4, yy4, yy4_fit, parametros4=fiteo(10000)
ays[1,1].plot(tt4, yy4,'o', label='datos' )
lab4=gfuncion.format(*parametros4)
ays[1,1].plot(tt4, yy4_fit,'--', label=lab4 )
ays[1,1].legend(loc='best')

plt.subplots_adjust(wspace=0.5, hspace=0.3)
plt.show()




# =============================================================================
# Etapa 2
# =============================================================================



""" 4. El detector tiene un área dada y es del tipo centellador.
 Cada vez que detecta un electrón se ilumina la posición a la que
 el electrón llega. Simule cómo se vería el detector en estas condiciones, 
 donde en función del tiempo se van detectando nuevas partículas."""

### numero de particulas
NN=int(1e5)
#---------------------------------------------------------------------------
###### considerando que la energia de los elecrones emitidos tiene una
##### distribucion gaussiana


####### calculo de la energia
def energia(x):
  dis=np.random.normal(loc=10*eV, scale=1.0*eV, size=x)
  return dis

##calculo de la velocidad del elec

def velocidad(x):
  a=energia(x)
  aa=[]
  for e in a:
    velocidad=np.sqrt(2*e/m_e)
    aa.append(velocidad)
  return aa 

##calculo del tiempo de viaje del electron

def tiempo(x):
  d=1 #distancia al detector
  b=velocidad(x)
  bb=[]
  for v in b:
    time=d/v
    bb.append(time)
  return bb
#---------------------------------------------------------------------------
 
 #-------------------------------------------------------------------------
""" 5. Simular el número de electrones detectados por unidad de tiempo 
 en estas condiciones. La probabilidad por unidad de tiempo es P=3.2×106.
 Grafique el número de electrones detectados y emitidos 
 como función del tiempo """
 #------------------------------------------------------------------------
 

## numero de electrones emitidos

P=3.2e6
dt=0.13/P

def emitidos(N,P):
    
    dt=0.13/P
    time=[] # registrar el tiempo
    electrones=[] # para agregar el numero de particulas
    t=0
    
    while N>0: # mintras haya particulas
        
        
        mu=N*P*dt   #muestras
        k=np.random.poisson(lam=mu, size=None)  # electrones emitidos
        electrones.append(k)
        N+=-k # actualizo el numero de particulas
        t+=dt
        time.append(t)
    
    return np.array(time), electrones

#---------------------------------------------------------------------------


## numero de electrones que llegan y se detectan 

def deteccion(N,P):
    
    llegada=[] ## creo una lista con todos los tiempos de llegada del e
        
    for xx in emitidos(N,P)[1]: #para cada uno de los electrones emitidos
        
        tt=tiempo(xx) ## calculo su tiempo de llegada con la distribución gaussiana
        num=np.random.random()  #creo un numero aleatorio
        radio=np.random.random() #radio del detector
        l=1 #radio del cascaron
        aread=4*pi*radio**2 #area del detector
        areac=4*pi*l**2     #area del cascaron
        
        if (aread/areac)>num: # condición para ser detectados
            
            llegada.append(tt)
    
    return  list(_flatten(llegada))

#------------------------------------------------------------------------------
#y=deteccion(NN)
#plt.plot(y,'--')

#----------------------------------------------------------------------------
##### un histograma con los tiempos de llegada de los electrones detectadas

tt,yy=emitidos(NN,P) # electrones emitidos
plt.plot(tt/tau, yy,'--',label='electrones emitidos')
dt=0.13/P

z=deteccion(NN,P)
z.sort()
x=np.linspace(z[0], tt[-1],20)
h,bins = np.histogram(z,bins=len(x))
plt.plot(x/tau, h, '-', lw=2, label='electrones detectados')


plt.legend(loc='best')
plt.xlabel(r'$t/\tau\quad\rm$')
plt.ylabel('$\Delta N(t)$')
plt.show()

############### animacion

Npts= 30

data = np.vstack([x, h])

def update_line(num, data, line):
  line.set_data(data[:, :num])
  return line,

# Creamos la figura e inicializamos
# Graficamos una línea sin ningún punto
# Fijamos las condiciones de graficación
fig1, ax = plt.subplots(figsize=(12,8))
L, = plt.plot(x, h, '-o') # equivalente a la siguiente
# L = plt.plot([],[] , '-o')[0]
ax.set_xlim(0,tt[-1])
ax.set_ylim(0, 10000)
ax.set_xlabel('x')
ax.set_title('Animación de una oscilación')


#
line_ani = animation.FuncAnimation(fig1, update_line, Npts, fargs=(data, L), interval=100, blit=True)

plt.show()






