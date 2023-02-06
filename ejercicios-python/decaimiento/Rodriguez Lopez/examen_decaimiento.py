#!/usr/bin/env python
# coding: utf-8

# In[9]:


# Code: Decaímiento espontáneo de estados metaestables
"""
El problema del decaimiento espontáneo de estados metaestables
se puede decir que se centra en principio en resolver la
siguiente ecuación diferencial,

\frac{\Delta N(t)}{N(t)} = -P\Delta t

"""
######################################################
##########             Librerias       ###############
######################################################
import numpy as np
import math
#get_ipython().run_line_magic('matplotlib', 'inline')
import matplotlib.pyplot as plt
from random import seed
from random import random
seed(1)
import random
from scipy import interpolate
from scipy.optimize import curve_fit
######################################################

######################################################
###      Condiciones iniciales y constantes        ###
######################################################

#Número de partículas iniciales
No  = float (1000)
Noi = [10, 100,1000, 10000, 100000]
# Paso temporal
dt  = 0.1
# Probabilidad por unidad de tiempo de que una partícula decaiga tiene el valor constante P,
P   = 1.3
#numero de interaciones ~ tiempo real
n   = int (1000)

#########################################################
## funciones f1(t)=At^(\alpha), y f2(t)=Bexp(-\beta*t) ##
#########################################################
def fit_func1(x, A, alpha):
    y = A*x**(alpha)
    return y
    
def fit_func2(x, B, beta):
    y = B*np.exp(-beta*x)
    return y
########################################################

########################################################
#######              Metodo de euler              ######
########################################################
######      No= numero de partículas inicial      ######
#  P= probabilidad/tiempo de que una partícula decaiga #
#                 n= numero de interaciones            #
########################################################
def metodo_euler(No,P,n):
    # Creación de los array tiempo, número de particulas N,
    # y delta N(t) -Nd
    t       =  np.linspace(0,n,int(n/dt))
    N       =  np.zeros(len(t))
    Ni      =  np.zeros(len(t))
    #fijando la condición inicial del número de partículas
    N[0]    =  No
    for n in range(0,len(t)-1):
        #N[n+1] = N[n] -P*N[n]*dt
        N[n+1] = N[n] -random.random()*2*P*N[n]*dt
        Ni[n+1]= abs (N[n]-N[n-1]) 
        if N[n]<=0.01:
            N  = N[:n]
            Ni = Ni[:n]
            t  = t[:n]
            break
    return N, Ni, t
##########################################################

##########################################################
###### llamada del metodo Euler para diferentes No #######
##########################################################
y,  delta_y,  time_simulacion    = metodo_euler(1e5, P,n)
y2, delta_y2, time_simulacion2   = metodo_euler(1e4, P,n)
y3, delta_y3, time_simulacion3   = metodo_euler(1e3, P,n)
y4, delta_y4, time_simulacion4   = metodo_euler(1e2, P,n)
y5, delta_y5, time_simulacion5   = metodo_euler(1e1, P,n)
#########################################################

fsize = (10,10)
fig   = plt.figure(figsize = fsize)
gs    = fig.add_gridspec(2, hspace=0)
axs   = gs.subplots(sharex=True, sharey=True)
# Rotate angle
angle =-20
l1    = np.array((1.5, 1))
axs[0].plot(time_simulacion/P,y,   "m--o", linewidth=2.0, markersize=10.0, markeredgecolor= "black", label="100000")
axs[0].plot(time_simulacion2/P,y2, "r--o", linewidth=2.0, markersize=10.0, markeredgecolor= "black", label="10000") 
axs[0].plot(time_simulacion3/P,y3, "g--o", linewidth=2.0, markersize=10.0, markeredgecolor= "black", label="1000") 
axs[0].plot(time_simulacion4/P,y4, "y--o", linewidth=2.0, markersize=10.0, markeredgecolor= "black", label="100") 
axs[0].plot(time_simulacion5/P,y5, "b--o", linewidth=2.0, markersize=10.0, markeredgecolor= "black", label="10") 
#axs[0].plot(time_simulacion/tau,No*np.exp(-P*time_simulacion), "r--o", linewidth=2.0, markersize=10.0, markeredgecolor= "black")
axs[1].plot(time_simulacion/P,  delta_y,  "m--o", linewidth=2.0, markersize=10.0, markeredgecolor= "black")    
axs[1].plot(time_simulacion2/P, delta_y2, "r--o", linewidth=2.0, markersize=10.0, markeredgecolor= "black") 
axs[1].plot(time_simulacion3/P, delta_y3, "g--o", linewidth=2.0, markersize=10.0, markeredgecolor= "black") 
axs[1].plot(time_simulacion4/P, delta_y4, "y--o", linewidth=2.0, markersize=10.0, markeredgecolor= "black") 
axs[1].plot(time_simulacion5/P, delta_y5, "b--o", linewidth=2.0, markersize=10.0, markeredgecolor= "black") 
plt.yscale("log") 
axs[0].set_xlabel("t/ $\tau$", fontsize=24) 
axs[1].set_xlabel("t/ $\tau$", fontsize=24) 
axs[0].set_ylabel("N(t)" , fontsize=24)
plt.xticks(fontsize=12)
plt.yticks(fontsize=12)
axs[0].legend()
# Hide x labels and tick labels for all but bottom plot.
for ax in axs:
    ax.label_outer()
plt.show()
########################################################################################
#       Ajuste los valores de N(t) suponiendo que tiene un comportamiento del tipo:    #
#                              f(t)=At^α                                               #
#                              f(t)=Be−λt                                              #
#para cada valor de N, encuentre cuál da un mejor ajuste y relacione los               #
#resultados obtenidos para las constantes con los parámetros del problema N0 y P       #
########################################################################################
# initial_guess= None
sofuncion                = r'${0:.3}\, t^{1:.2f}$'
initial_guess_o          = [1e6, P]
params_o, p_covarianza_o = curve_fit(fit_func1, time_simulacion, y, initial_guess_o)

plt.plot(time_simulacion/P, y,"ok", linewidth=2.0, markersize=10.0, markeredgecolor= "black")
#label=sofuncion.format(*params_o)
plt.plot(time_simulacion/P,fit_func1(time_simulacion, *params_o), 'r--', label= "ajuste")
plt.yscale("log")
plt.xscale("log")
plt.xlabel("t/tau", fontsize=16) 
plt.ylabel("N(t)", fontsize=16)
plt.xticks(fontsize=12)
plt.yticks(fontsize=12)
plt.grid(True)
plt.legend(loc="upper right", shadow= True)
plt.show()

print("Valores de los ajustes: \n f1(t)=Not^(\alpha)")
for j,v in enumerate(['No','alpha']):
    print("{} = {:.5g} ± {:.3g}".format(v, params_o[j], np.sqrt(p_covarianza_o[j,j])))           
    
    
# initial_guess= None
sfuncion= r'${0:.3}\, \exp({1:.2f} t)$'
initial_guess2= [1e6, P]
params, p_covarianza = curve_fit(fit_func2, time_simulacion, y, initial_guess2)
plt.plot(time_simulacion/P, y,"ok", alpha=0.6, markersize=10.0)
plt.plot(time_simulacion/P, fit_func2(time_simulacion, *params),'r--', label= "ajuste")
#label=sfuncion.format(*params)
plt.yscale("log")
plt.xscale("log")
plt.xlabel("$t/tau$", fontsize=16) 
plt.ylabel("N(t)", fontsize=16)
plt.xticks(fontsize=12)
plt.yticks(fontsize=12)
plt.grid(True)
#legend = plt.legend(loc="upper right", shadow= True, fontsize= "x-large")
#legend.get_frame().set_facecolor("C0")
plt.legend(loc="upper right", shadow= True)
plt.show()

print("Valores de los ajustes:\n N(t)= Noexp(-beta t)")
for j,v in enumerate(['No','beta']):
    print("{} = {:.5g} ± {:.3g}".format(v, params[j], np.sqrt(p_covarianza[j,j])))    
    
