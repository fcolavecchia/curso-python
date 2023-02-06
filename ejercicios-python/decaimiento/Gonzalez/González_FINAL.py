import numpy as np
import math
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from  scipy import constants
from scipy.optimize import curve_fit
import argparse
import sys


plt.rcParams['text.usetex'] = True
dt = 4.0625*pow(10,-8)
P = 3.2*pow(10,6)
Pdt = P*dt

def decay(Initial_N):
	"""
	Los decaimientos son tratados como un proceso de Poisson donde
	nu== N(t)*P*dt. El proceso se detiene cuando N(t)=0.
	Parametros
	----------
	Initial_N : np.array de enteros.
				Representan el número inicial de partículas que
				decaeran en cada caso.
	Retorna
	-------
	N_t :  lista de np.arrays de enteros.
		   Cada elemento en la lista representa la evolución del 
		   número de particulas en el tiempo para una dada población
		   inicial.
	dN_t : lista de np.arrays de enteros.
		   Cada elemento en la lista representa el número de 
		   decaimientos de partículas ocurridos en el intervalo
		   de tiempo [t, t+dt].
	"""
	N_t = []
	dN_t = []
	for N0 in Initial_N:
		Nparts = np.empty(0) 
		dNparts = np.empty(0)
		Nparts = np.append(Nparts, N0)
		while (Nparts[-1]>=1):
			dN = 1*np.random.poisson(Nparts[-1]*Pdt) # calcula número de decaimientos
			N = int(Nparts[-1] - dN)
			dNparts = np.append(dNparts, dN)
			Nparts = np.append(Nparts, N)
		if (Nparts[-1]<0):		#la población no puede ser un número negativo
			Nparts[-1] = 0
			dNparts[-1] = Nparts[-2]
		N_t.append(Nparts)
		dN_t.append(dNparts)
	return N_t, dN_t

def graph_decay(Nparts, dNparts):
	"""
	Grafica el decaimiento de las diferentes poblaciones en el
	tiempo. Grafica también el número de decaimientos.
	Parametros
	----------
	Nparts:    lista de np.arrays de enteros.
		       Cada elemento en la lista representa la evolución del 
		       número de particulas en el tiempo para una dada población
		       inicial.
	dNNparts : lista de np.arrays de enteros.
			   Cada elemento en la lista representa el número de 
			   decaimientos de partículas ocurridos en el intervalo
			   de tiempo [t, t+dt].

	Retorna
	-------
	fig : 	figura de matplotlib con dos subplots.
			El subplot superior muesta la evolución del número
			de particulas en el tiempo para todas las poblaciones.
			El subplot del fondo muestra el número de decaimientos
			en el intervalo de tiempo [t, t+dt] para todas las 
			poblaciones. 
			En ambos casos la variable del eje x es time/tau,
			donde tau es el tiempo característico de decaimiento
			(tomado como la reciproca de la probabilidad por 
			unidad de tiempo).
	"""
	fig, ax = plt.subplots(ncols=1, nrows=2)
	plt.subplots_adjust( hspace=0.05)
	ax[0].grid(); ax[1].grid()
	xmax = Pdt*len( sorted(Nparts, key=len)[-1] ); #para saber el rango en x
	ax[0].set_xlim(0,xmax);				ax[1].set_xlim(0,xmax) # fija parametros del plot
	ax[0].set_ylim(1, 1.1*Nparts[-1][0]);	ax[1].set_ylim(1, 1.1*dNparts[-1][0])
	ax[0].set_yscale('log');  ax[1].set_yscale('log');
	ax[0].set_ylabel('$N(t)$', fontsize=20); ax[1].set_ylabel('$ \Delta N(t)$',fontsize=20); 
	ax[1].set_xlabel('$ t/ \\tau$', fontsize=20);
	ax[0].tick_params(axis='y',  labelsize=15); ax[0].tick_params(axis='x',  labelsize=0)
	ax[1].tick_params(axis='both',  labelsize=15)
	for N,dN in zip(Nparts,dNparts):
		time = np.linspace(0, Pdt*N.shape[0], N.shape[0])
		line, = ax[0].plot(time,N, marker= "o")
		line, = ax[1].plot(time[1:],dN, marker= "o")
		ax[0].text(10*Pdt,N[0]*0.2, s= int(N[0]),rotation=-18, fontsize=12)
	return fig


def fit_function(kind):
	"""
	Crea un objeto del tipo function que se usara para 
	ajusta el decaimiento de las poblaciones en función
	del tiempo.
	Parametros
	----------
	kind :  variable int para elegir la función
			de ajuste.
			1: power law
			2: exponential decay
	Retorna
	-------
	Un objeto del tipo función que se usará para ajustar
	el decaimiento del número de partículas con el tiempo.
	"""
	if (kind == 1):#power law
		def decay_function(time, A, alpha, k):
			return A*pow(time+ k,alpha)
		return decay_function
	else:#decaimiento exponencial
		def decay_function(time,A,alpha):
			return A*np.exp(-1.*alpha*time)
		return decay_function


def fit_decay(Nparts,kind=2):
	"""
	Ajusta el decaimiento de las diferentes poblaciones
	en el tiempo. Retorna los parametros del ajuste y el
	chi^2.
	Parametros
	----------
	Nparts : lista de np.arrays de enteros.
			 Cada elemento en la lista representa la evolución del 
			 número de particulas en el time para una dada población
		     inicial.
	Retorna
	-------
	pars :   Una lista 2D. Cada elemento representa el 
			 ajuste de todos los parámetros a una dada
			 población inicial.
	chi : 	 lista de float. Cada elemento representa el chi^2
			 reducido del ajuste fit a una dada población.
	"""
	pars = []
	chi = []
	for N in Nparts:
		time = np.linspace(0, dt*N.shape[0], N.shape[0])#datos de la variable independiente 
		if ( kind==1 ):
			initial_guess= [9*N[0], -math.log(N[0]-time[-1]), 5 ]
		else:
			initial_guess = [N[0], math.log(N[0])/time[-1]]
		func = fit_function(kind)
		#realiza el ajuste conn los daots y forma funcional indicados
		params, p_covarianza = curve_fit(func, time, N, initial_guess, absolute_sigma=True)
		chi.append( chi_sqr(time,N, func,kind, params) ) #calcula el chi^2 reducido
		pars.append(params) #guarda los parametros del ajuste
	return pars,chi

def chi_sqr(time, N,f,kind,param):
	"""
	Calcula el chi^2 del ajuste a una dada población.
	Parametros
	----------
	time :  np. array de float.
	N :     np.array de integers.
		    Cada elemento en la lista representa la evolución del 
			número de particulas en el time para una dada población
			inicial.
	f :     Un objeto del tipo función usado para ajustar el 
	        decaimiento del número de partículas con el tiempo.
	kind :  variable int para elegir la función de ajuste.
	param : Lista de float. Cada elemento representa un 
			parametro del ajuste.
	Retorna
	-------
	chi/N.shape[0]: El chi^2 del ajuste dividido 
					por el número de data points.
	"""
	chi = 0
	if kind==1:
		y = f(time,param[0],param[1],param[2])
	else:
		y = f(time,param[0],param[1])
	for i,n in zip(y,N):
		chi = (n-i)*(n-i)/i
	return chi/N.shape[0]

def results_table(Initial_N, fit_results, chi, kind):
	"""
	Imprime el resultado del ajuste.
	Parametros
	----------
	Initial_N :  np.array de enteros.
				 Representan el número inicial de partículas que
				 decaeran en cada caso.
	fit_results: Una lista 2D. Cada elemento representa el 
				 ajuste de todos los parámetros a una dada
				 población inicial.
	chi: 	     El chi^2 reducido del ajuste.
	kind :  variable int para elegir la función de ajuste.
	Retorna
	-------
	table: 	    tabla con os resultados del ajuste.
	"""
	table = ""
	if (kind==1):
		table += "La funcion de ajuste fue de la forma: f= No* (t+t_0)^alpha\n"
	elif (kind==2):
		table +="La funcion de ajuste fue de la forma: f= No*exp(-t/alpha)\n"
	else:
		table +="Funcion de ajuste desconocida\n"
	table +=' Parametros del ajuste:\n'
	table +='|'+86*'='+'|\n'
	table +='|    N    |      No     |  N/No  |    P    |   alpha   |  \
P/alpha  |   t_0   |  chi^2  |\n'
	table +='|'+86*'-'+'|\n'
	for N,params, c in zip(Initial_N, fit_results, chi):
		s = str(int(N))
		table += '|'+ (9-len(s)) *' ' + s +''
		s = f"{params[0]:.2f}"
		table += '|'+ (13-len(s))*' ' + s +''
		s = f"{N/params[0]:.2f}"
		table += '|'+ (8-len(s))*' ' + s +''
		s = str(int(P))
		table +='|'+ (9-len(s)) *' ' + s +''
		s = f"{params[1]:.2f}"
		table +='|'+ (11-len(s))*' ' + s +''
		s = f"{P/params[1]:.2f}"
		table +='|'+ (11-len(s))*' ' + s +''
		if kind==1:
			s = f"{params[2]:.2f}"
			table += '|'+ (9-len(s))*' ' + s +''
		else:
			s = ""
			table += '|'+ (9-len(s))*' ' + s +''
		s = f"{c:.5f}"
		table += '|'+ (9-len(s))*' ' + s +'|\n'
	table += '|'+86*'='+'|'
	return table



def electron_energy(dN):
	"""
	Calcula la energía con la que los electrons resultado
	del decaimiento de las partículas son emitidos.
	Parametros
	----------
	dN : int. Número de decaimientos de partículas que 
		 ocurrieron en un dado intervalo.
	Retorna
	-------
	energies : np.array de float. La energía con la 
			   que cada electrón fue emitido
	"""
	E_avrg = 10
	sigma_E = E_avrg/10
	energies = np.random.normal( E_avrg, sigma_E, int(dN) )
	return energies

def spherical_electron_emission(Nparts, dNparts, A=1, L=1 ):
	"""
	Calcula el tiempo de llegada (y posición en el detector)
	de los electrones emitidos por el decaimientode los estados.
	Se asume simetría esférica.
	Parametros
	----------
	Nparts :  np.arrays de enteros. Cada elemento del arreglo representa
			  número de particulas para un dado tiempo.
	dNparts : np.arrays de enteros. Cada elemento del arreglo representa
			  el número decaimientos de partículas ocurridos en el
			  intervalo de tiempo [t, t+dt].
	A : float. Area del detector. El default es 1.
	L : float, Distancia del detector a la muestra. El default es 1.

	Retorna
	-------
	detection : np.array de tuplas(float,float,float).
				Cada elemento en el arreglo representa:
				- tiempo del llegada al detector (primer elemento de la tupla),
				- posición x en el detector (segundo elemento de la tupla),
				- posición y en el detector (tercer elemento de la tupla).
	"""
	time = np.linspace(0, dt*Nparts.shape[0], dNparts.shape[0])
	detection =[]
	energies = []
	for dN,t in zip(dNparts,time):
		energies = electron_energy(dN)
		#el electron viaja el linea recta a velocidades no relativistas
		arrival_times = L*np.sqrt( constants.m_e/(2*energies*constants.eV) )
		arrival_times +=  t
		for e, detection_time in zip(energies,arrival_times):
			nro = np.random.random()
			#si cae sobre el detector lo registro
			if ( nro <= (A/(4.*np.pi*L*L)) ):
				x_det,y_det =  math.sqrt(A)*(np.random.random(2)-0.5)
				detection.append((detection_time, x_det, y_det))
	detection.sort()#ordeno temporalmente
	detection = np.vstack(detection)
	return detection

def spherical_detector(electrons):
	"""
	Muestra una anumación de las partículas como son 
	recibidas en el detector esférico.
	Parametros
	----------
	electrons : np.array de tuples(float,float,float).
				Cada elemento en el arreglo representa:
				- tiempo del llegada al detector (primer elemento de la tupla),
				- posición x en el detector (segundo elemento de la tupla),
				- posición y en el detector (tercer elemento de la tupla).
	Retorna
	-------
	line_ani: animación matplotlib animation del detector.

	"""
	data = electrons
	xmax,ymax = data[:,1:].max(axis=0)
	xmin,ymin = data[:,1:].min(axis=0)

	fig, ax = plt.subplots(figsize=(12,8))
	s = "Tiempo: " + f"{data[0][0]:.8f}"+ " s, número de particulas: " + str(1)
	L, = ax.plot([], [], 'o', label = s, color='b')
	L2, = ax.plot([], [], 'o', color='b')
	leg = ax.legend(loc='center left', bbox_to_anchor=(0.64, 1.03))
	ax.set_xlim(xmin, xmax)
	ax.set_ylim(ymin, ymax)
	ax.grid()
	ax.set_xlabel('x [m]',  fontsize=20); ax.set_ylabel('y [m]',  fontsize=20)
	ax.set_title('Detección de partículas',fontsize=20)
	ax.tick_params(axis='both',  labelsize=20)
	
	def update_line(num, data, line,line2):
		"""
		Actualiza la animación con un nuevo frame.
		"""
		line.set_alpha(0.5)
		line.set_data(data[:,1:].T[:, num-9:num])
		line2.set_alpha(1)
		line2.set_data(data[:,1:].T[:, num])
		s = "Tiempo: " + f"{data[num][0]:.8f}"+ " s, número de particulas: " + str(num+1)
		leg.texts[0].set_text(s)
		return line, line2,
	
	line_ani = animation.FuncAnimation(fig, update_line, data.shape[0], fargs=(data, L,L2), interval=1, blit=False)
	plt.show()
	return line_ani 


def wall_electron_emission( Nparts, dNparts, A=1, L=1 ):
	"""
	Calcula el tiempo de llegada (y posición en el detector)
	de los electrones emitidos por el decaimientode los estados.
	El detector es plano y se encuentra sobre ele eje z.
	Parametros
	----------
	Nparts :  np.arrays de enteros. Cada elemento del arreglo representa
			  número de particulas para un dado tiempo.
	dNparts : np.arrays de enteros. Cada elemento del arreglo representa
			  el número decaimientos de partículas ocurridos en el
			  intervalo de tiempo [t, t+dt].
	A : float. Area del detector. El default es 1.
	L : float, Distancia del detector a la muestra. El default es 1.
	Retorna
	-------
	detection : np.array de tuplas(float,float,float).
				Cada elemento en el arreglo representa:
				- tiempo del llegada al detector (primer elemento de la tupla),
				- posición x en el detector (segundo elemento de la tupla),
				- posición y en el detector (tercer elemento de la tupla).
	"""
	time = np.linspace(0, dt*Nparts.shape[0], dNparts.shape[0])
	detection_time =[]
	energies = []
	for dN,t in zip(dNparts,time):
		energies = electron_energy(dN)
		for e in energies:
			costheta, cosphi = 2*np.random.random(2)-1
			#si sale sobre el plano xy o para z<0 nunca llega al detector
			if(costheta <= 0):
				continue
			sintheta = math.sqrt(1-costheta*costheta)
			sinphi = math.sqrt(1-cosphi*cosphi)
			v = math.sqrt(2*e*constants.eV/constants.m_e)
			#asumo viaje en linea recta a velocidades no relativistas
			arrival_time = L/(v*costheta)+t
			x = arrival_time*v*sintheta*cosphi
			y = arrival_time*v*sintheta*sinphi
			#si cae sobre el detector lo registro
			if ( (A == np.inf) or ( (abs(x)<= math.sqrt(A)/2) and (abs(y)<= math.sqrt(A)/2) ) ):
				detection_time.append((arrival_time, x,y))
	detection_time.sort() #ordeno temporalmente
	return np.vstack(detection_time)



def detections(dNparts, electrons, sphere=True):
	"""
	Grafica el número de electrones recibidos (en el detector)
	y emitidos.
	Parametros
	----------
	dNparts :   np.arrays de enteros. Cada elemento del arreglo representa
			    el número decaimientos de partículas ocurridos en el
			    intervalo de tiempo [t, t+dt]..
	electrons : np.array de float.
				Cada elemento representa el tiempo de llegada de un 
				electron en el detector.
	sphere : 	variable booleana. Si true camvia el título del plot
				para indicar que estamos tratando con un detector 
				esférico. El defautl es True.
	Retorna
	-------
	None.
	"""
	#los tiempos de emisión y de detectección no son los mismos
	emission_times = np.linspace(0, P*dt*(len(dNparts)+1), len(dNparts))
	detection_times = electrons[:,0]
	#crea histograma
	detection_histogram = np.histogram(detection_times,dNparts.shape[0])
	x = P*(detection_histogram[1][1:] + detection_histogram[1][:-1])/2
	fig, ax = plt.subplots(figsize=(12,8))
	ax.set_title('Cuentas por unidad de tiempo en un detector plano', fontsize=20)
	ax.set_yscale('log');
	ax.grid()
	if sphere:
		ax.set_title('Cuentas por unidad de tiempo en un detector esférico',fontsize=20)
	ax.set_ylabel('$ \Delta N(t)$',fontsize=20); 
	ax.set_xlabel('$ t/ \\tau$',fontsize=20);
	line, = ax.plot(emission_times,dNparts, marker= "", label = "Electrones emitidos")
	line, = ax.plot(x,detection_histogram[0], marker= "", label = "Electrones detectados")
	plt.show()
	return None
	



simulation_parser = argparse.ArgumentParser(description='Process some physical parameters.')
simulation_parser.add_argument( '-n', action="store", dest="nmin", type=int, default=10, help='Smallest population of partcles to decay.')
simulation_parser.add_argument( '-N', action="store", dest="nmax", type=int, default=100000, help='Bigest population of partcles to decay.')
simulation_parser.add_argument( '-p', action="store", dest="npops", type=int, default=5, help='Number of population that will decay.')
simulation_parser.add_argument( '-f', action="store", dest="kind", type=int, default=2, help='Kind of fitting function that will be used.')
simulation_parser.add_argument( '--ac', action="store", dest="area_sph", type=float, default=1, help='Area of the spherical detector.')
simulation_parser.add_argument( '--lc', action="store", dest="Lc", type=float, default=1, help='Distance to the spherical detector.')
simulation_parser.add_argument( '--aw', action="store", dest="area_wall", type=float, default=1, help='Area of the wall detector.')
simulation_parser.add_argument( '--lw', action="store", dest="Lw", type=float, default=1, help='Position along the z axis of the wall detector.')
simulation_parser.add_argument('--output', '-o', action="store", dest="output", type=str, default=sys.stdout, help='Output')
simulation = simulation_parser.parse_args()




#crea las poblaiones iniciales de estados
Initial_N = np.logspace(math.log10(simulation.nmin), math.log10(simulation.nmax),\
			simulation.npops)
Nparts, dNparts = decay(Initial_N)	# simula el decaimiento de las diferentes poblaciones
decay_plot = graph_decay(Nparts, dNparts) #grafica dicho decaimiento



fit_results,chi = fit_decay(Nparts) # ajusta dicho decaimiento y da la posibilidad de hacer otro ajuste.
if (simulation.output==sys.stdout):
	print(results_table(Initial_N,fit_results, chi, simulation.kind))
else:
	with open(simulation.output, 'w') as output_file:
		output_file.write(results_table(Initial_N,fit_results, chi, simulation.kind))
		
tofit = bool(input("Do you want to fit the data with another model? y for yes, Any other key for no:\n") == 'y')
while tofit:
	kind = input("Select a fitting function.  1 for power law, 2 for exponential decay:\n")
	while ( not(kind == '1') and not(kind == '2') ):
		kind = input("Invalid fitting function selected. Select 1 for power law, 2 for exponential decay:\n")
	fit_results,chi = fit_decay(Nparts, int(kind))
	if (simulation.output==sys.stdout):
		print(results_table(Initial_N,fit_results, chi, int(kind)))
	else:
		with open(simulation.output, 'a') as output_file:
			output_file.write("\n")
			output_file.write(results_table(Initial_N,fit_results, chi, int(kind)))
	tofit = bool(input("Do you want to fit the data with another model? y for yes, Any other key for no:\n") == 'y')
	
	


#simula la deteccion de electrones en un detector esferico, crea una animacion del mismo y muestra las cuentas por unidad de tiempo
electrons = spherical_electron_emission(Nparts[-1],dNparts[-1],A = simulation.area_sph ,L = simulation.Lc)
anim = spherical_detector(electrons)
detections(dNparts[-1], electrons)

#simula la deteccion de electrones en un detector plano y muestra las cuentas por unidad de tiempo
electrons = wall_electron_emission(Nparts[-1],dNparts[-1], A = simulation.area_wall, L = simulation.Lw)
detections(dNparts[-1], electrons, False)

