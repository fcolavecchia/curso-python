#IF YOU ARE USING JYPYTER, PLEASE READ THIS IF YOU HAVE ANY ISSUE AT RUNNING LIKE PLOTS NOT SHOWING!
#!conda install --yes --prefix {sys.prefix} plotly
#if you want to run the code on jupyter please do the following pior to starting the app
#jupyter nbextension enable --py widgetsnbextension 
import numpy as np
import math
import sys
import argparse #for input arguments
from sklearn.linear_model import LinearRegression #for linear regresion
import gzip #for uncompressing
#graphic imports
import plotly.graph_objects as go
from plotly.subplots import make_subplots #to create a plot made of suplots
import plotly.express as px #to allow the use of easy plotlies figures
#import plotly.offline as pyo #allow the use of plotly offline to make htm display without online connection
#from ipywidgets import widgets #to allow the use of boxes of widgets on jupyter (allowing more than 1 interactive widget at the same time)
import dash #for allowing plottly plots on a web enviorment with interactive widgets working
from dash import dcc#part of dash 
from dash import html #part of dash 
from dash.dependencies import Input, Output #for plot interaction
import webbrowser #for opening a webbroser when running scrips

#from IPython.display import display #to allow display/no display of widget
#We add the following line to run plotly in offline mode with jupyter.
    #in this solutyion this service will not be used but could be desired in the future...or maybe not.
#pyo.init_notebook_mode() #to be able to plot on jupyter while working ofline
#-------------------------------------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------------------------------------
#FUNCTIONS DECLARATIONS
#-------------------------------------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------------------------------------
def array3d_slices_rotate(data_sliced,center,angle):
    #this function recives slices of data, the center of the slice, the distribution center of each data and the angle of rotation
    #returns an structure of slices
    z_rl=len(data_sliced)
    #Then we perform the rotation for all the slices
    data_sliced_rotated=[array2d_translate_rotate(data_sliced[i],center[i],angle[i]) for (i) in range(z_rl)]   
    return(data_sliced_rotated)        
        
def array3d_get_slices(array3d, z_slices=np.array([-4.5,-3.5,-2.5,-1.5,-0.5,0.5,1.5,2.5,3.5,4.5]),z_slice=0.5):
    #returns an structure of slice, linear regression, center and angles for each of the slice
        #defacult values where created for the sample fata
    z_rl=len(z_slices) #get the range of the slices arrat
    #array3d_slice_v = np.vectorize(array3d_slice,excluded=['array3d'])#create a vecctorised version of the function
    data_sliced=[array3d_slice(array3d,2,z_slices[i]-z_slice,z_slices[i]+z_slice) for (i) in range(z_rl)] #obtain the slices
    linear_reg=[array3d_linear_reg(data_sliced[i]) for (i) in range(z_rl)]    
    linear_reg_a=np.array(linear_reg,dtype=object)#added dtype beacuse of warning at running
    x_reg=linear_reg_a[:,0] #store the x values of regression for each slice
    y_reg=linear_reg_a[:,1]#store the y values of regression for each slice
    center=(np.array([*linear_reg_a[:,2]])) #stores the x y center value for each slice
    angle=linear_reg_a[:,3] ##stores the angle value for each slice
    return(data_sliced,x_reg,y_reg,center,angle)

def array3d_slice(array3d,axis,slice_down,slice_up):
    #find index of the selected axis of a 3D matrix that futfill  slice_down<axis<slice_up condition
        #then use thoses indexes to get the values of the 3 axis and return the new matrix
    axis_spec=np.array(array3d[:,axis])
    index_slice=np.array(np.where((axis_spec<slice_up)&(axis_spec>slice_down)))#get the index of the slice
    index_s=index_slice[0,:]
    array3d_sliced=array3d[index_s,:] #generate the 3D matrix based of the 1D index matrix
    return(array3d_sliced)
#perform a rotation and center of x and y points of an array
def array2d_translate_rotate(array2d,center,angle):
    #center must be a (2,1) matrix
    #angle must be in degrees
    x_offset=center[0]
    y_offset=center[1]
    array2d[:,0]=array2d[:,0]-x_offset #perform translation
    array2d[:,1]=array2d[:,1]-y_offset#perform translation
    rads = np.radians(angle)#converts degree to radians
    c, s = np.cos(rads), np.sin(rads) #rotation matrix values
    R = np.array(((c, -s), (s, c))) #creates the rotation matrix
    array2d_rotated=np.zeros((len(array2d[:,0]),2))
    array2d_rotated=np.matmul(array2d[:,0:2],R) #perform rotationb
    return(array2d_rotated)

#generates an background histogram of 100 points
def array2d_histogram_background(array2d):
    x=array2d[:,0]
    y=array2d[:,1]
    scale=1.05 #scale factor to ensure proper filling when rotating front histogram
    x_max=np.amax(x)*scale
    x_min=np.amin(x)*scale
    x_rand=np.random.rand(100)*x_max/100
    y_max=np.amax(y)*scale
    y_min=np.amin(y)*scale
    y_rand=np.random.rand(100)*y_max/100
    x_h=np.append([x_min,x_max],x_rand)
    y_h=np.append([y_min,y_max],y_rand)
    hist_x_y=go.Histogram2d(x = x_h,y = y_h,showscale=False)
    return(hist_x_y)

#allows you to get histograms in axis x, y and both
def array2d_histograms (array2d):
    x=array2d[:,0]
    y=array2d[:,1]
    hist_x=go.Histogram(x = x,name="Hist. eje X")
    hist_y=go.Histogram(y=x,name="Hist. eje Y")
    hist_x_y=go.Histogram2d(x = x,y = y,showscale=False,name="Histograma 2D")
    return(hist_x_y,hist_x,hist_y)

#peform a weighted 2D linear regression of a 3D data.
def array3d_linear_reg (array3d):
    #this regression will take into acount the concentration of Z points
    x=array3d[:,0]
    y=array3d[:,1]
    z=array3d[:,2]    
    #now we perform a weigthed the regression and fit of the model
    sample_weight=((z-z.min())/(z.max()-z.min()))+0.0001
    n_samples=len(x)
    x_reg=np.array((x).reshape((n_samples, 1))).astype(float)
    y_reg = y[:n_samples]
    regr = LinearRegression()
    #regr.fit(x_reg, y_reg, 1/sample_weight)#1/sample_weight
    regr.fit(x_reg, y_reg)#1/sample_weight
    #We get the extermes of the curve                   
    x_reg_res=[ x_reg[0,0] ,x_reg[-1,0] ]
    y_reg_res=regr.predict([x_reg[0,:] ,x_reg[-1,:]])#y_reg_result=regr.predict(x_reg)
    #get the slope and angle
    m=(y_reg_res[1]-y_reg_res[0])/(x_reg_res[1]-x_reg_res[0])
    angle=math.atan(m)*(360/math.pi)#angle is measured in degrees
    #gets the center
    center=np.array([np.median(x),np.median(y)])
    #create the interpolation of the rect with lessser points (only two) to improve performance
    x_range=[np.amin(x),np.amax(x)] #select the max and min value of x
    y_range=(x_range-center[0])*m+center[1] #get the values related to y
    #create the array for return
    array2d_reg= np.zeros((2,2)) #this will be the data to plot
    array2d_reg[:,0]=x_range
    array2d_reg[:,1]=y_range
    return(array2d_reg[:,0],array2d_reg[:,1],center,angle)

#creates a range of slices around Z axis based on the size of the slice and their max/min value
def generate_zrange(z_range,dz):
    z_limits=dz*np.around(np.array(z_range)/dz)
    val=(round((z_limits[1]-z_limits[0])/(dz*2))).astype(int)
    z_slices=np.linspace(z_limits[0]+dz, z_limits[1]-dz,val)
    return(z_slices)

#converts an string to a float numpy array
def str_to_npfloata(corte):
    corte_l=(corte).split()
    corte_a=[float(i) for i in corte_l]
    z_slices=np.array(corte_a)#convert the slices to array
    return(z_slices)
    
def read_dat_gz(string,matrix_dim=3):
    #Read the compressed ffiles
    f = gzip.open(string, 'r') #open the compresses file to read it
    file_content=f.read() #store the read contents of files in variable
    #do the conversion from text to a float numpy array
    s=str(file_content) #converts the content to string, including 'b at the begginning (0:1)  and ' at the end (-1)
    s_in=((s[2:-1]).replace('n',' ')).replace('\ ',' ') #remove "\n" lines and elements redisual drom the reading process
    s_split=s_in.split() #do the split to separate the floats
    vector=np.array(s_split)#convert the list to a numpy array
    #START DATA INTEGRITY CHECK
    array_elements=len(vector)#get the lenght of the array
    matrix_len=round(array_elements/matrix_dim)#get the amounts of elements of the matrix to construc
    integrity_check=array_elements/matrix_dim -matrix_len
    if (integrity_check>0):
        print("Inconsistencia en lectura de archivo: Hay un elemento de mas en la ultima fila y sera eliminado")
        vector=vector[:-1]#eliminates the last element
        array_elements=len(vector)#get the lenght of the array
        matrix_len=round(array_elements/matrix_dim)#get the amounts of elements of the matrix to construc
    if (integrity_check<0):
        print("Inconsistencia en lectura de archivo: Hay dos elementos de mas en la ultima fila y seran eliminados")
        vector=vector[:-2]#eliminates the last two elements
        array_elements=len(vector)#get the lenght of the array
        matrix_len=round(array_elements/matrix_dim)#get the amounts of elements of the matrix to construc
    #generates the array
    array=vector.reshape(matrix_len, matrix_dim)#convert the array to a matrix
   # print(array)
    return((np.array(array)).astype(float))
#-------------------------------------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------------------------------------
#INTERACTIVE FUNCTION DECLARATION
#-------------------------------------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------------------------------------
def plot_update_slice(cut):
    #This functions activ
    s = list(scatter_angle.marker.size)
    s=[s[-1] for i in s]
    s[cut] = s[-1]*2    #change the selected point to the   
     #we now proceed to perform the updates (in batch mode to improve user experience)
    with fig_widget.batch_update(): #to perform all the updates at the same time
            scatter_angle.marker.size = s #updated the points of angle plot
            scatter_centerx.marker.size = s #updated the points of x center plot  
            scatter_centery.marker.size = s# updated the points of angle plot  
            #now we update the tittlee and annotation
            fig_widget.update_layout(title="Centro de corte en Z: "+str(z_slices[cut]))
    with fig3d.batch_update():#to perform all the updates of 3D plot at the same time
            for i in range(len(fig3d_data)-1):#we only parse until the last item
                fig3d_data[i].opacity=(fig3d_data[-1]).opacity #set default opacity of all planes
            fig3d_data[cut+1].opacity=1 #set 1 opacity for upper plane of slice
            fig3d_data[cut].opacity=1     #set 1 opacity for lower plane of slice
            
    with fig_widget.batch_update():#we add 2 to let know the user the update request was sended
        #now we need to choose the proper slice and get the histograms
            hist_x_y,hist_x,hist_y=array2d_histograms(data_sliced_r[cut])#get the histograms
        #now we update the traces with the selected cut and all histograms
            fig_widget.data[8].x=[(center[cut])[0]]#update graph with new values
            fig_widget.data[8].y=[(center[cut])[1]]#update graph with new values
            fig_widget.data[7].x=x_reg[cut]#update graph with new values
            fig_widget.data[7].y=y_reg[cut]#update graph with new values
            fig_widget.data[6].x=hist_x_y.x#update graph with new values
            fig_widget.data[6].y=hist_x_y.y#update graph with new values
            fig_widget.data[3].x=hist_x.x #update graph with new values
            fig_widget.data[4].y=hist_y.y #update graph with new values
#----------------------------------------------------------------------------

def widget_plot_detect_click_point(trace, points, selector):
    #This functions activ
    if len(points.point_inds)>0:#secure the acces to the correct graph
        cut=points.point_inds[0] #we get the index of the cut
        plot_update_slice(cut) #invoke the plot update
#-------------------------------------------------------------------------------------------------------------------------------------

#-------------------------------------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------------------------------------
#MAIN PROGRAM (READ THIS TO UNDERSTAND HOW IT WORKS)
#-------------------------------------------------------------------------------------------------------------------------------------
#STEPS    
#               PARSER ARGUMENTS READ
#                                 |
#               PROCESSING THE ARGUMENTS
#                   (ENSURE SELECTED OPTIONS CONSiSTENCY WITH AN STATE MACHINE)
#                                 |
#               LOAD THE DATA
#                                 |
#              IF DATA=!NULL, PERFORM PROCESS BASED ON SELECTED OPTIONS
#                                 |
#              CREATES PLOTS AND FIG WIDGET OBJET
#                                 |
#                       CREATES DASH INTERACTIVE OBJETS AND DISPLAY
#                                 |
#------------------------------------------------------------------------------------------------------------------------------------- 
#-------------------------------------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------------------------------------
layout_tittle="Analisis de Datos - Andres Oliva Trevisan"
distancia_corte_default=0.5
layout3d_opacity_3d=0.2
layout3d_opacity_slice=0.5
parser = argparse.ArgumentParser(
description='Este programa le permite graficar datos de puntos en el espacio tridimencional en formato 3D o en histogramas, ya sea por cortes o en forma interactiva.')
parser.add_argument('-n', '--nombre', action="store", dest='name',type=str, default='medicion3D_0',
                                help='Permite ingresar el nombre del archivo a abrir SIN su extension.'+
                                         'Ej: Si el archivo se llama "medicion3D_0.dat.gz" debe ingresar "-n medicion3D_0" para abrir el archivo. '  )
parser.add_argument('-dz', '--dcorte', action="store",type=float, dest='distancia', default=distancia_corte_default,
                                help='Permite ingresar el valor de distancia entre cortes en el eje Z y calcula los cortes de los mismos a partir de este valor '+
                                         'Ej: "-dz 0.5" (valor por defecto), se obtiene el valor max/min del eje Z (-5,5) se obtienen'+ 
                                        ' cortes de ancho 2*0.5=1 que ocupen todo el rango de Z (-5,5), dando un total de 10 cortes'+
                                         'Ej2: "-dz 0.25" (valor por defecto), se obtiene el valor max/min del eje Z (-5,5) se obtienen'+ 
                                        ' cortes de ancho 2*0.25=0.5 que ocupen todo el rango de Z (-5,5), dando un total de 20 cortes')
parser.add_argument('-z', '--corte', nargs="+", dest='corte',type=float, default=[],
                                help='Permite ingresar los centros de los cortes a analizar, realizando un grafico de histograma para cada corte (mientras no se use el modo interactivo)'+
                                         'Ej1: ingresa "-z 4.5 3.5 1.5" creara los cortes cuyos intervalos seran [5. 4.] [4. 3] [2. 1.].' +
                                         'Ej2: ingresa "-z 4.5 3.5 1.5 -z 0.25" creara los cortes cuyos intervalos seran [4.75 4.25] [3.75 3.25] [1.75 1.25].' +
                                         'Nota: Si se selecciona la opcion de grafico -i (interactivo) se ignoraran los cortes seleccionados'  )       
parser.add_argument('-t', '--todos',action='store_true', dest='plot_todos',default=True,
                                help='Grafico de todos los datos: grafica todos los datos en un unico grafico.'+
                                         'Nota: Si se selecciona la opcion de grafico -i (interactivo) y/o -z (corte) no se g'  )                   
parser.add_argument('-i', '--interactivo', action="store_true", dest='plot_iteractivo', default=False,
                                help='Grafico interactivo:realiza el grafico iterativo,'+
                                         'Nota: Si se selecciona la opcion de grafico, los graficos correspondientes a -t -z (corte) no se generaran' ) 
parser.add_argument('-r', '--transform', action="store_true", dest='plot_rotate', default=False,
                                help='Al ingresar esta opcion, grafica los datos rotados. Si se utiliza la opcion de corte o de grafico iterativo realiza la rotacion para cada corte ingresado o seleccionado')
parser.add_argument('-3dno', '--3d_plot_no', action="store_false", dest='plot_3d', default=True,
                                help='Ingresando esta opcion, el programa NO realizara el grafico 3D de los puntos')
args, unknown = parser.parse_known_args()
#-----assign the arguments to variables used
#code example: -n medicion3D_0 -z -3.5 -0.5 2.5 4.5'
dz=args.distancia#The distante to the cut, default=0.5    
flag_cut=False #this is set to false at the beggining
if len(args.corte)>0:#Is slices values were inputed, then we change flag_cut to true
    flag_cut=True
flag_all=args.plot_todos
flag_iterative=args.plot_iteractivo
flag_rotate=args.plot_rotate
flag_3d=args.plot_3d

#------------------------------------------------------------------------------------------------------------------------------------- 
#(ENSURE SELECTED OPTIONS CONSYSTENCY WITH AN STATE MACHINE)
#-------------------------------------------------------------------------------------------------------------------------------------
#we parse the args input value to ensure consistency
    #this works as an state machine to avoid plotting not requested information
if flag_iterative==True:
    flag_all=False
    flag_cut=False
    layout3d_opacity=layout3d_opacity_3d
if flag_cut==True: 
    flag_all=False
    flag_iterative=False
    layout3d_opacity=layout3d_opacity_slice
if flag_all==True: 
    flag_cut=False
    flag_iterative=False  
  #after this we finish to perform the set up based on the plot type selection  
#------------------------------------------------------------------------------------------------------------------------------------- 
# DATA READ ----------------------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------------------------------------
#first we read the data'medicion3D_1'                                       
data=read_dat_gz(args.name+'.dat.gz') #read the data from a compressed file and gets a matrix n*3
#------------------------------------------------------------------------------------------------------------------------------------- 
# DATA PROCESSING --------------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------------------------------------
if (len(data))>0:#then we check if there is data to be analised
    #now we need to check if we plot the data complete or slice 
     #gets the limits of the axis
    x_range=[np.amin(data[:,0]),np.amax(data[:,0])]
    y_range=[np.amin(data[:,1]),np.amax(data[:,1])]
    z_range=[np.amin(data[:,2]),np.amax(data[:,2])]
    z_slices=[]#we define this as part of the software
    if flag_iterative==True:#we select to generate
        z_slices=generate_zrange(z_range,dz)#np.array([-4.5,-3.5,-2.5,-1.5,-0.5,0.5,1.5,2.5,3.5,4.5])#all the slices
    if flag_cut==True:#we select to generate
        z_slices=np.array(args.corte)#z_slices=str_to_npfloata(args.corte) #NON USED
            #perform the linear regression
    x_reg1,y_reg1,center1,angle1=array3d_linear_reg(data)
            #check if data must be rotared        
    if flag_rotate==True:
            data_r=array2d_translate_rotate(data,center1,angle1)
            center1=np.array([0,0])
            x_reg1=np.array(x_range)
            y_reg1=np.array([0,0])
    else:
            data_r=data
#-----------create the data for plot
    if (flag_iterative==True)or(flag_cut==True):
            #get the histograms for the data
            if (flag_iterative==True):
                hist_x_y,hist_x,hist_y=array2d_histograms(data_r)
            #Now we get all the slices
            data_sliced,x_reg,y_reg,center,angle=array3d_get_slices(data,z_slices,dz)
            #Now we check if we must rotate the slices
            if flag_rotate==True:
                data_sliced_r=array3d_slices_rotate(data_sliced,center,angle)
                x_reg=np.array([x_range for i in range(len(angle))])
                y_reg=np.array([[0,0] for i in range(len(angle))] )
                angle=np.array([0 for i in range(len(angle))])
                center=np.array([[0,0] for i in range(len(angle))] )
            else:
                   data_sliced_r=data_sliced    
#------------------------------------------------------------------------------------------------------------------------------------- 
# DATA PLOTTING --------------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------------------------------------
    #defines of plots
    layout_template='plotly_dark'
    layout3d_colorscale='blugrn'
    
    #now we plot based on selection
    if flag_iterative==True:        
            fig = make_subplots(
                rows=5, cols=7,
                specs=[[None,None,{"colspan": 4},None,None,None,None],
                       [{"rowspan": 2, "colspan": 2},{},{"rowspan": 4, "colspan": 4},{},{},{},{"rowspan": 4}],
                       [None,None,None,None,None,None, None],
                       [{"rowspan": 2, "colspan": 2},None, None,None,None, None,None],
                       [None,None, None,None,None, None,None]], #last plot is to add a 
                print_grid=False)#,
            #Add the figures
            #DO NOT CHANGE OR REMOVE THE ORDER IN WHICH THE TRACES ARE ADDED
                #IF YOU DO SO, PLEASE CHECK THE INTERACTION FUNCTION #plot_detect_click_point#
            fig.add_trace(go.Scatter(x=z_slices, y=angle, name="Angulo"), row=2, col=1)#This should be the first trace to be added
            fig.add_trace(go.Scatter(x=z_slices, y=center[:,0], name="Centro eje x"), row=4, col=1)
            fig.add_trace(go.Scatter(x=z_slices, y=center[:,1], name="Centro eje y"), row=4, col=1)
            fig.add_trace(hist_x,row=1, col=3)
            fig.add_trace(hist_y, row=2, col=7)
            fig.add_trace(array2d_histogram_background(data), row=2, col=3)
            fig.add_trace(hist_x_y, row=2, col=3)
            fig.add_trace(go.Scatter(x=x_reg1, y=y_reg1, name="Eje central"), row=2, col=3)
            fig.add_trace(go.Scatter(x=[center1[0]], y=[center1[1]], name="Centro", mode='markers',marker=dict(
                        color='DarkSlateGrey',
                        size=10,
                        )), row=2, col=3)
            #We add an annotation to keep track of the Z slice selected by user
            fig.update_xaxes(title_text="Centro de Corte en Z", row=4, col=1)
            fig.update_yaxes(title_text="Centro", row=4, col=1)
            fig.update_yaxes(title_text="Angulo [grados]", row=2, col=1)
            fig.update_xaxes(title_text="Distribución en X-Y", row=2, col=3)
            #we change the layout
            fig.update_layout(template='plotly_dark', title="Grafico Interactivo")
            
            #-------------------------------------------------------------------
            #--------now we create the widget based on the figure
            #----------NOTE: THIS ONLY WORKS WITH JUPYTER 
            #----------DASH interaction module was added, but code was conserved    
            #-------------------------------------------------------------------
            fig_widget = go.FigureWidget(fig)
            #now we add the interactive properties to the widget
            fig_widget.layout.hovermode = 'closest'
            #now we store the plots we want to be interactive and assign the interaction event
            scatter_centery = fig_widget.data[2] #data0 contains the slice centery plot}
            scatter_centery.marker.size = [10] * (len(z_slices) +1)
            scatter_centery.on_click(widget_plot_detect_click_point)
            scatter_centerx = fig_widget.data[1] #data1 contains the slice centerx plot}
            scatter_centerx.marker.size = [10] * (len(z_slices) +1)
            scatter_centerx.on_click(widget_plot_detect_click_point)
            scatter_angle = fig_widget.data[0] #data0 contains the slice center y plot}
            scatter_angle.marker.size = [10] * (len(z_slices) +1)
            scatter_angle.on_click(widget_plot_detect_click_point)#angle should we the last object to be added
    if flag_cut==True :
        fig_cut_list=[]#to save figure list elements
        for i in range(len(z_slices)):
            fig_cut = px.density_heatmap(data_sliced_r[i], x=0, y=1, marginal_x="histogram", marginal_y="histogram",
                                         labels={'0':'Distribución en X','1':'Distribución en Y'},)  
            fig_cut.add_trace(go.Scatter(x=x_reg[i], y=y_reg[i], name="Eje central"))
            fig_cut.add_trace(go.Scatter(x=[(center[i])[0]], y=[(center[i])[1]], name="Centro", mode='markers',marker=dict(
                        color='DarkSlateGrey',
                        size=10,
                        )))
            fig_cut.update_layout(template=layout_template, title='Distribución para corte centrado en Z='+str(z_slices[i])
                             +" ("+str(z_slices[i]-dz)+' ,'+str(z_slices[i]+dz)+')')
            #fig_cut.show() #to show without dash 
            fig_cut_list.append(fig_cut)#append to list for later manipulation with dash plot 
    if flag_all==True :
            fig_all = px.density_heatmap(data_r, x=0, y=1, marginal_x="histogram", marginal_y="histogram",
                                labels={'0':'Distribución en X','1':'Distribución en Y'},)  
            fig_all.update_layout(template=layout_template)
            #fig_all.show() #to show without dash    
#we create the 3D plot if requested
    if flag_3d==True :        
        fig3dd = go.Figure([go.Scatter3d(x=data_r[:,0], y=data_r[:,1], z=data[:,2],
                                       mode='markers',marker=dict(size=5,
                                                color=data[:,2],  #make color based on Z axis value
                                                colorscale='Viridis',   # choose a colorscale
                                                opacity=0.8
                                                )
                                                )]) 
        x_surface = np.outer(np.linspace(x_range[0], x_range[1], 2), np.ones(2))
        y_surface = np.outer(np.linspace(y_range[0], y_range[1], 2), np.ones(2)).T
        if (len(z_slices))>0:
            z_surface = np.outer(np.ones(2), np.ones(2))*(z_slices[0]-dz)
    #for different colors https://plotly.com/python/templates
            fig3dd.add_trace(go.Surface(x=x_surface, y=y_surface, z=z_surface, colorscale=layout3d_colorscale,showscale=False, opacity=layout3d_opacity,name="Z="+str(z_slices[0]-dz)))
            for i in range(len(z_slices)):    
                z_surface = np.outer(np.ones(2), np.ones(2))*(z_slices[i]+dz)
                fig3dd.add_trace(go.Surface(x=x_surface, y=y_surface, z=z_surface, colorscale=layout3d_colorscale,showscale=False, opacity=layout3d_opacity,name="Z="+str(z_slices[i]+dz)))
    #we add another trace at the bottom for reference pourpose during click event
            z_surface = np.outer(np.ones(2), np.ones(2))*(z_slices[0]-dz*1.01)
            fig3dd.add_trace(go.Surface(x=x_surface, y=y_surface, z=z_surface, colorscale=layout3d_colorscale,showscale=False, opacity=layout3d_opacity,name="Z="+str(z_slices[0]-dz)))
         #if we have the cut, 
            if flag_cut==True :
                for i in range(len(z_slices)):    
                    z_surface = np.outer(np.ones(2), np.ones(2))*(z_slices[i]-dz)
                    fig3dd.add_trace(go.Surface(x=x_surface, y=y_surface, z=z_surface, colorscale=layout3d_colorscale,showscale=False, opacity=layout3d_opacity,name="Z="+str(z_slices[i]-dz)))
    #we add the layout
        fig3dd.update_layout(template=layout_template, title="Posición de puntos en el espacio")
        #we converte the plot to widget to allow dynamic update
        fig3d = go.FigureWidget(fig3dd)
        #we add the intective information if we work in interactive mode
        if flag_iterative==True: 
    #we converte the plot to widget to allow dynamic update
            fig3d_data=[fig3d.data[1]] #add the -1 point
            for i in range(len(z_slices)):
                fig3d_data.append(fig3d.data[i+2])
                fig3d_data.append(fig3d.data[-1])
#we create the boxes based on your selection    

else:                    
    print("No se encontraron datos en el archivo, por favor revise el nombre o el contenido del mismo")
#now we display the widget with its properties 
#pyo.plot(fig_widget) #for html off line display 
#fig_widget   #for display inside IDE, but you can only display ONE WIDGET AT THE SAME TIME WITH THIS!
#fig_box#display the box, this must be the last line

#################### Creating App Object ############################               
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
theme = {
    'dark': True,
    'main': '#111111',
    'text': '#7FDBFF',
    'secondary': '#6E6E6E',
}

####################### Setting Graphs as HTML Children ############## 
#now we create the childr3ends based on the selected options
if flag_iterative==True:          
            graph_interactivo = dcc.Graph(
                    id='graph_interactivo',
                    figure=fig_widget,
                    )
if flag_3d==True :
            graph_3D = dcc.Graph(
                    id='graph_3D',
                    figure=fig3d,
                    )
if flag_cut==True :
            graph_slices_plots=[]#list of dash graph plots
            for i in range(len(z_slices)):
                graph_slices_plots.append(dcc.Graph(id='graph_slice'+str(i),figure=fig_cut_list[i]))            

if flag_all==True :
            graph_all = dcc.Graph(
                    id='graph_all',
                    figure=fig_all,
                    )

############### Creating Widgets For Each Graph #########################    


######################### Laying out Charts & Widgets to Create App Layout ##########
header = html.H2(children=layout_tittle,style={'color':theme['text']})
#now we create the layout based on the selected options
if flag_iterative==True:
    if flag_3d==True:
        row = html.H1(children=[graph_interactivo,graph_3D])
    else:
        row = html.H1(children=[graph_interactivo])
if flag_cut==True:
    if flag_3d==True:
        graph_slices_plots.insert(0, graph_3D) #add the 3d plot as the first element
        row = html.H1(children=graph_slices_plots)
    else:
        row = html.H1(children=[graph_slices_plots])    
if flag_all==True:
    if flag_3d==True:
        row = html.H1(children=[graph_3D,graph_all])
    else:
        row = html.H1(children=[graph_all])

#row1 = html.Div(children=[graph_interactivo, graph_3D])
layout = html.Div(children=[header, row], style={
        "text-align": "center", "justifyContent":"center",'backgroundColor':theme['main']})

############### Setting App Layout ########################################
app.layout = layout


################## Creating Callbacks for Each Widget ############################
@app.callback(
    dash.dependencies.Output('graph_interactivo','figure'),#we want to update graph_interactivo
                      Output('graph_3D','figure'),#we want to update graph_3D
    [dash.dependencies.Input('graph_interactivo', 'clickData')])#the dash input will be the graph 1
def dash_plot_detect_click_point(clickData):
    if clickData!=None:#check if the object existi, this is to avoid initalization issues with callback
        if ((clickData['points'][0])['curveNumber'])<3:#ensure the click is from the desired curves
            cut=clickData['points'][0]['pointIndex']#get the point number
            plot_update_slice(cut)#call the function to update the plots
    return(fig_widget,fig3d)#returns the figures for updating the plots


################## Running App #####################################

if __name__ == "__main__":
    webbrowser.open_new("http://127.0.0.1:8050/")
    app.run_server(debug=False)#put the debug as true for debugging pourpose