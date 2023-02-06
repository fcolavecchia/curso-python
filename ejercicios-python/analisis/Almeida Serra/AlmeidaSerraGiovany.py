import numpy as np
import matplotlib.pyplot as plt
import argparse
from matplotlib.widgets import Cursor


###############################################################################
#############USO DE ARGPARSE PARA ARGUMENTOS POR LINEA DE COMANDOS#############
###############################################################################
parser = argparse.ArgumentParser(description='"Este programa acepta argumentos por linea de comandos"')
parser.add_argument('-fn','--filename',action='store',default='medicion3D.dat',type=str,dest='filename')
parser.add_argument('-t','--todos',action='store',default=True,type=bool,dest='is_todos')
parser.add_argument('-z','--corte',action='store',default=[0.],type=list,dest='z_corte')
parser.add_argument('-i','--interactivo',action='store',default=False,type=bool,dest='is_interactivo')
parser.add_argument('-r','--transform',action='store',default=True,type=bool,dest='is_transform')
args = parser.parse_args()

filename=args.filename
is_todos=args.is_todos
z_corte=args.z_corte
is_interactivo=args.is_interactivo
is_transform=args.is_transform


###############################################################################
################################LEER DATOS#####################################
###############################################################################
x_data,y_data,z_data=np.loadtxt(filename,unpack=True)
ancho_bins=0.5


###############################################################################
#####################PARA CALCULAR LIMITES DEL GRAFICO#########################
###############################################################################
def limites(x,y,ancho_bins):
    xlm=int(np.min(x_data))
    xlM=int(np.max(x_data))
    ylm=int(np.min(y_data))
    ylM=int(np.max(y_data))
    x_bins=int(((xlM-xlm)/ancho_bins))
    y_bins=int(((ylM-ylm)/ancho_bins))
    bins=max(x_bins,y_bins)
    return [xlm,xlM,ylm,ylM,bins]


###############################################################################
########################OBTENCION DE DATOS DE CORTE############################
###############################################################################
def datos_corte(x,y,z,z0):
    x_aux=[]
    y_aux=[]
    z_aux=[]
    for i in range(len(z)):
        if z[i]<=(z0+0.5) and z[i]>=(z0-0.5):
            x_aux.append(x[i])
            y_aux.append(y[i])
            z_aux.append(z[i])
    x_aux=np.array(x_aux)
    y_aux=np.array(y_aux)
    z_aux=np.array(z_aux)
    return x_aux,y_aux,z_aux


###############################################################################
#################################ACTION CLICK##################################
###############################################################################
def action_click(event):
    z_0=event.xdata
    z_get=z_cut_int[np.argmin(np.abs(z_cut_int-z_0))]
    z_get_ind=np.argmin(np.abs(z_cut_int-z_0))
    fig3_ax31d.cla()
    
    ###CENTRO Vs. Z CORTE###
    l1,=fig3_ax31d.plot(z_cut_int,x0_int,marker='.',markerfacecolor='tab:blue',color='tab:blue',label=r'$y_0$',zorder=1)
    l2,=fig3_ax31d.plot(z_cut_int,y0_int,marker='.',markerfacecolor='tab:red',color='tab:red',label=r'$x_0$',zorder=2)
    fig3_ax31d.set_xlim(-5,5)
    l3=fig3_ax31d.set_xlabel('z_corte')
    fig3_ax31d.set_ylabel('coordenadas centro')
    l4=fig3_ax31d.scatter(z_get,x0_int[z_get_ind],color='tab:green',marker='o',zorder=6)
    l5=fig3_ax31d.scatter(z_get,y0_int[z_get_ind],color='tab:green',marker='o',zorder=7)
    fig3_ax31d.legend()
    ###ANGULO Vs. Z CORTE###
    fig3_ax31u.cla()
    fig3_ax31u.plot(z_cut_int,np.rad2deg(theta),marker='.',markerfacecolor='orange',color='orange',zorder=1)
    fig3_ax31u.set_ylabel(r'$\Theta$ (grados)')
    fig3_ax31u.tick_params(axis="x", labelbottom=False)
    fig3_ax31u.scatter(z_get,np.rad2deg(theta[z_get_ind]),color='tab:green',marker='o', label=r'z_corte = {:.1f}'.format(z_cut_int[z_get_ind]),zorder=4)
    fig3_ax31u.legend()
    
    ###GRAFICO PRINCIPAL###
    fig3_ax32.cla()
    fig3_ax32.hist2d(x_data_int[z_get_ind][:],y_data_int[z_get_ind][:],lim[4])
    fig3_ax32.set_xlabel('Dirección x')
    fig3_ax32.tick_params(axis="y", labelleft=False)
    ###CENTRO###
    fig3_ax32.plot(x0_int[z_get_ind],y0_int[z_get_ind],marker='o',color='tab:red')
    ###EJE###
    x_recta=np.linspace(lim[0],lim[1],len(x_data_int))
    fig3_ax32.plot(x_recta,m_int[z_get_ind]*x_recta+n_int[z_get_ind],color='tab:red',ls='--')        
    ###DISTRIBUCION###
    fig3_ax32x.cla()
    fig3_ax32x.hist(x_data_int[z_get_ind], bins=lim[4])
    fig3_ax32x.set_title(r'z_corte = {:.1f}'.format(z_cut_int[z_get_ind]), loc='center')
    ###DISTRIBUCION###
    fig3_ax32y.cla()
    fig3_ax32y.hist(y_data_int[z_get_ind], bins=lim[4], orientation='horizontal')
    fig3_ax32y.set_ylabel('Dirección y')
    fig3_ax32y.yaxis.set_label_position('right')


###############################################################################
#####################GRAFICANDO TODOS LOS DATOS################################
###############################################################################
if is_todos==True or z_corte==None:
    lim=limites(x_data,y_data,ancho_bins)
    fig1=plt.figure(1,figsize=(6,6),constrained_layout=True)
    gs1=fig1.add_gridspec(2,2,width_ratios=(8,2),height_ratios=(2,8),left=0.1,right=0.9,bottom=0.1,top=0.9,wspace=0.01,hspace=0.01)
    
    ###DATOS COMPLETOS EN X-Y###
    fig1_ax3=fig1.add_subplot(gs1[1,0])
    fig1_ax3.hist2d(x_data,y_data,bins=lim[4],range=([lim[0],lim[1]],[lim[2],lim[3]]))
    fig1_ax3.set_xlim(lim[0],lim[1])
    fig1_ax3.set_ylim(lim[2],lim[3])
    fig1_ax3.set_xlabel('Dirección x')
    fig1_ax3.set_ylabel('Dirección y')
    
    ###DISTRIBUCION EN EL EJE X###
    fig1_ax1=fig1.add_subplot(gs1[0,0],sharex=fig1_ax3)
    fig1_ax1.hist(x_data,bins=lim[4])
    fig1_ax1.tick_params(axis="x",labelbottom=False)
    fig1_ax1.set_title('Datos en plano x-y', loc='center')
    
    ###DISTRIBUCION EN EL EJE Y###
    fig1_ax2=fig1.add_subplot(gs1[1,1],sharey=fig1_ax3)
    fig1_ax2.hist(y_data,bins=lim[4],orientation='horizontal')
    fig1_ax2.tick_params(axis="y", labelleft=False)
       
    #######################################################################
    #########DATOS ROTADOS, EJE PRINCIPAL HORIZONTAL#######################
    #######################################################################
    if is_transform==True:
        ###CENTRO DE LA DISTRIBUCION###
        x0=np.mean(x_data)
        y0=np.mean(y_data)
        fig1_ax3.scatter(x0,y0,color='tab:red')
        x_recta=np.linspace(lim[0],lim[1],len(x_data))
        
        ###EJE PRINCIPAL DE LA DISTRIBUCION###
        m0,n0 = np.polyfit(x_data,y_data,1)
        fig1_ax3.plot(x_recta,m0*x_recta+n0,color='tab:red',ls='--')        
        
        x_data_trans=x_data-x0
        y_data_trans=y_data-y0
        
        if m0<0:
            alpha=np.arctan(m0)
            angle=np.pi+alpha
        else:
            angle=np.arctan(m0)
        alpha_degree=np.rad2deg(alpha)
               
        x_data_trans_rot=x_data_trans*np.cos(angle)-y_data_trans*np.sin(angle)
        y_data_trans_rot=y_data_trans*np.cos(angle)+x_data_trans*np.sin(angle)
        
        lim=limites(x_data_trans_rot,y_data_trans_rot,ancho_bins)
        x_recta=np.linspace(lim[0],lim[1],len(x_data_trans_rot))
        
        fig1=plt.figure(2,figsize=(6,6),constrained_layout=True)
        gs1=fig1.add_gridspec(2,2,width_ratios=(8,2),height_ratios=(2,8),left=0.1,right=0.9,bottom=0.1,top=0.9,wspace=0.01,hspace=0.01)
        
        ###DATOS EN X-Y CORTADOS EN Z###
        fig1_ax3=fig1.add_subplot(gs1[1,0])
        fig1_ax3.hist2d(x_data_trans_rot,y_data_trans_rot,bins=lim[4],range=([lim[0],lim[1]],[lim[2],lim[3]]))
        fig1_ax3.set_xlim(lim[0],lim[1])
        fig1_ax3.set_ylim(lim[2],lim[3])
        fig1_ax3.set_xlabel('Dirección x')
        fig1_ax3.set_ylabel('Dirección y')
        
        ###DISTRIBUCION EN EL EJE X###
        fig1_ax1=fig1.add_subplot(gs1[0,0],sharex=fig1_ax3)
        fig1_ax1.hist(x_data_trans_rot,bins=lim[4])
        fig1_ax1.tick_params(axis="x",labelbottom=False)
        fig1_ax1.set_title(f'\n Corrección de ángulo respecto a la horizontal \n θ={alpha_degree:.2f} °', loc='center')
        
        ###DISTRIBUCION EN EL EJE Y###
        fig1_ax2=fig1.add_subplot(gs1[1,1],sharey=fig1_ax3)
        fig1_ax2.hist(y_data_trans_rot,bins=lim[4],orientation='horizontal')
        fig1_ax2.tick_params(axis="y", labelleft=False)
        
        ###CENTRO DE LA DISTRIBUCION###
        x1=np.mean(x_data_trans_rot)
        y1=np.mean(y_data_trans_rot)
        fig1_ax3.scatter(x1,y1,color='tab:red')
        
        ###EJE PRINCIPAL DE LA DISTRIBUCION###
        m1,n1 = np.polyfit(x_data_trans_rot,y_data_trans_rot,1)
        fig1_ax3.plot(x_recta,m1*x_recta+n1,color='tab:red',ls='--')
        

###############################################################################
############################GRAFICAS DE CORTES#################################
###############################################################################
if z_corte!=None:
    L=len(z_corte)
    for i in range(L):
        x_data_cut,y_data_cut,z_data_cut=datos_corte(x_data, y_data, z_data, z_corte[i])
        lim=limites(x_data_cut,y_data_cut,ancho_bins)
        x_recta=np.linspace(lim[0],lim[1],len(x_data_cut))
        fig1=plt.figure(i+3,figsize=(6,6),constrained_layout=True)
        gs1=fig1.add_gridspec(2,2,width_ratios=(8,2),height_ratios=(2,8),left=0.1,right=0.9,bottom=0.1,top=0.9,wspace=0.01,hspace=0.01)
    
        ###DATOS EN X-Y CORTADOS EN Z###
        fig1_ax3=fig1.add_subplot(gs1[1,0])
        fig1_ax3.hist2d(x_data_cut,y_data_cut,bins=lim[4],range=([lim[0],lim[1]],[lim[2],lim[3]]))
        fig1_ax3.set_xlim(lim[0],lim[1])
        fig1_ax3.set_ylim(lim[2],lim[3])
        fig1_ax3.set_xlabel('Dirección x')
        fig1_ax3.set_ylabel('Dirección y')
        
        ###DISTRIBUCION EN EL EJE X###
        fig1_ax1=fig1.add_subplot(gs1[0,0],sharex=fig1_ax3)
        fig1_ax1.hist(x_data_cut,bins=lim[4])
        fig1_ax1.tick_params(axis="x",labelbottom=False)
        fig1_ax1.set_title('Corte en z='+str(z_corte[i]), loc='center')
        
        ###DISTRIBUCION EN EL EJE Y###
        fig1_ax2=fig1.add_subplot(gs1[1,1],sharey=fig1_ax3)
        fig1_ax2.hist(y_data_cut,bins=lim[4],orientation='horizontal')
        fig1_ax2.tick_params(axis="y", labelleft=False)
        
        ###CENTRO DE LA DISTRIBUCION###
        x0=np.mean(x_data_cut)
        y0=np.mean(y_data_cut)
        fig1_ax3.scatter(x0,y0,color='tab:red')
        
        ###EJE PRINCIPAL DE LA DISTRIBUCION###
        m0,n0 = np.polyfit(x_data_cut,y_data_cut,1)
        fig1_ax3.plot(x_recta,m0*x_recta+n0,color='tab:red',ls='--')        
                
        #######################################################################
        #########DATOS ROTADOS, EJE PRINCIPAL HORIZONTAL#######################
        #######################################################################
        if is_transform==True:
            x_data_cut_trans=x_data_cut-x0
            y_data_cut_trans=y_data_cut-y0
            if m0<0:
                alpha=np.arctan(m0)
                angle=np.pi+alpha
            else:
                angle=np.arctan(m0)
            alpha_degree=np.rad2deg(alpha)
            x_data_cut_trans_rot=x_data_cut_trans*np.cos(angle)-y_data_cut_trans*np.sin(angle)
            y_data_cut_trans_rot=y_data_cut_trans*np.cos(angle)+x_data_cut_trans*np.sin(angle)

            lim=limites(x_data_cut_trans_rot,y_data_cut_trans_rot,ancho_bins)
            x_recta=np.linspace(lim[0],lim[1],len(x_data_cut_trans_rot))
            
            fig1=plt.figure(i+3+L,figsize=(6,6),constrained_layout=True)
            gs1=fig1.add_gridspec(2,2,width_ratios=(8,2),height_ratios=(2,8),left=0.1,right=0.9,bottom=0.1,top=0.9,wspace=0.01,hspace=0.01)
            
            ###DATOS EN X-Y CORTADOS EN Z###
            fig1_ax3=fig1.add_subplot(gs1[1,0])
            fig1_ax3.hist2d(x_data_cut_trans_rot,y_data_cut_trans_rot,bins=lim[4],range=([lim[0],lim[1]],[lim[2],lim[3]]))
            fig1_ax3.set_xlim(lim[0],lim[1])
            fig1_ax3.set_ylim(lim[2],lim[3])
            fig1_ax3.set_xlabel('Dirección x')
            fig1_ax3.set_ylabel('Dirección y')
            
            ###DISTRIBUCION EN EL EJE X###
            fig1_ax1=fig1.add_subplot(gs1[0,0],sharex=fig1_ax3)
            fig1_ax1.hist(x_data_cut_trans_rot,bins=lim[4])
            fig1_ax1.tick_params(axis="x",labelbottom=False)
            fig1_ax1.set_title('Corte en z=' +str(z_corte[i]) + f'\n Corrección de ángulo respecto a la horizontal \n θ={alpha_degree:.2f} °', loc='center')
            
            ###DISTRIBUCION EN EL EJE Y###
            fig1_ax2=fig1.add_subplot(gs1[1,1],sharey=fig1_ax3)
            fig1_ax2.hist(y_data_cut_trans_rot,bins=lim[4],orientation='horizontal')
            fig1_ax2.tick_params(axis="y", labelleft=False)
            
            ###CENTRO DE LA DISTRIBUCION###
            x1=np.mean(x_data_cut_trans_rot)
            y1=np.mean(y_data_cut_trans_rot)
            fig1_ax3.scatter(x1,y1,color='tab:red')
            
            ###EJE PRINCIPAL DE LA DISTRIBUCION###
            m1,n1 = np.polyfit(x_data_cut_trans_rot,y_data_cut_trans_rot,1)
            fig1_ax3.plot(x_recta,m1*x_recta+n1,color='tab:red',ls='--')
        

###############################################################################
###############################INTERACTIVIDAD##################################
###############################################################################
if is_interactivo==True:
    z_cut_int=[-4.5,-3.5,-2.5,-1.5,-0.5,0.5,1.5,2.5,3.5,4.5]
    L=len(z_cut_int)
    x_data_int=[]
    y_data_int=[]
    z_data_int=[]
    m_int=[]
    n_int=[]
    for i in range(L):
        x_aux,y_aux,z_aux=datos_corte(x_data,y_data,z_data,z_cut_int[i])
        m_aux,n_aux=np.polyfit(x_aux,y_aux,1)
        x_data_int.append(x_aux.tolist())
        y_data_int.append(y_aux.tolist())
        z_data_int.append(z_aux.tolist())
        m_int.append(m_aux)
        n_int.append(n_aux)
    x_data_int=np.array(x_data_int)
    y_data_int=np.array(y_data_int)
    z_data_int=np.array(z_data_int)
    m_int=np.array(m_int)
    n_int=np.array(n_int)
    
    theta=np.arctan(m_int)
    x0_int=[np.mean(val) for val in x_data_int]
    y0_int=[np.mean(val) for val in y_data_int]
    
    lim=limites(x_data_int[0][:],y_data_int[0][:],ancho_bins)
    
    fig3=plt.figure(figsize=(8,8),constrained_layout=True)
    gs3=fig3.add_gridspec(3,3,width_ratios=(8,8,2),height_ratios=(2,4,4),left=0.1,right=0.9,bottom=0.1,top=0.9,wspace=0.05,hspace=0.05)
    
    fig3_ax31d=fig3.add_subplot(gs3[2,0])
    fig3_ax31u=fig3.add_subplot(gs3[1,0],sharex=fig3_ax31d)
    fig3_ax32=fig3.add_subplot(gs3[1:3,1])
    fig3_ax32x=fig3.add_subplot(gs3[0,1],sharex=fig3_ax32)
    fig3_ax32y=fig3.add_subplot(gs3[1:3,2],sharey=fig3_ax32)
    
    ###CENTRO Vs. Z CORTE###
    l1,=fig3_ax31d.plot(z_cut_int,x0_int,marker='.',markerfacecolor='tab:blue',color='tab:blue',label=r'$y_0$',zorder=1)
    l2,=fig3_ax31d.plot(z_cut_int,y0_int,marker='.',markerfacecolor='tab:red',color='tab:red',label=r'$x_0$',zorder=2)
    fig3_ax31d.set_xlim(-5,5)
    l3=fig3_ax31d.set_xlabel('z_corte')
    fig3_ax31d.set_ylabel('coordenadas centro')
    l4=fig3_ax31d.scatter(z_cut_int[0],x0_int[0],color='tab:green',marker='o',zorder=6)
    l5=fig3_ax31d.scatter(z_cut_int[0],y0_int[0],color='tab:green',marker='o',zorder=7)
    fig3_ax31d.legend()
    
    ###ANGULO Vs. Z CORTE###
    fig3_ax31u.plot(z_cut_int,np.rad2deg(theta),marker='.',markerfacecolor='blue',color='blue',zorder=1)
    fig3_ax31u.set_ylabel(r'$\Theta$ (grados)')
    fig3_ax31u.tick_params(axis="x", labelbottom=False)
    fig3_ax31u.scatter(z_cut_int[0],np.rad2deg(theta[0]),color='tab:green',marker='o', label=r'z_corte = {:.1f}'.format(z_cut_int[0]),zorder=4)
    fig3_ax31u.legend()
    ###GRAFICO PRINCIPAL###
    fig3_ax32.hist2d(x_data_int[0][:],y_data_int[0][:],lim[4])
    fig3_ax32.set_xlabel('Dirección x')
    fig3_ax32.tick_params(axis="y", labelleft=False)
    ###CENTRO###
    fig3_ax32.plot(x0_int[0],y0_int[0],marker='o',color='tab:red')
    ###EJE###
    x_recta=np.linspace(lim[0],lim[1],len(x_data_int))
    fig3_ax32.plot(x_recta,m_int[0]*x_recta+n_int[0],color='tab:red',ls='--')        
    ###DISTRIBUCION###
    fig3_ax32x.hist(x_data_int[0], bins=lim[4])
    fig3_ax32x.set_title(r'z_corte = {:.1f}'.format(z_cut_int[0]), loc='center')
    ###DISTRIBUCION###
    fig3_ax32y.hist(y_data_int[0], bins=lim[4], orientation='horizontal')
    fig3_ax32y.set_ylabel('Dirección y')
    fig3_ax32y.yaxis.set_label_position('right')
    ###GREGAR CURSORES###
    cursor=Cursor(fig3_ax31d,horizOn=True,vertOn=True,useblit=True,color='k',linewidth=1)
    cursor=Cursor(fig3_ax31u,horizOn=True,vertOn=True,useblit=True,color='k',linewidth=1)
    fig3.canvas.mpl_connect('button_press_event', action_click)

plt.show()

















