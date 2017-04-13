 #######################################
# lightcurves.py
# Erica Lastufka 5/4/2017  

#Description: Plot Messenger and RHESSI lightcurves together
#######################################

#######################################
# Usage:

######################################

import numpy as np
import scipy.constants as sc
import pandas as pd
from datetime import datetime as dt
from datetime import timedelta as td
import os
import data_management as da
import pickle
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import copy

def import_data(filename):
    '''Import lightcurve data from IDL into a pandas dataframe'''
    from scipy.io import readsav
    #format everything so it's right
    d=readsav(filename, python_dict=True)
    Rdata=d['data']['rdata'] #access via Rdata[0]['UT'], etc
    Mdata=d['data']['mdata']
    Gdata=d['data']['gdata']
    return Rdata[0],Mdata[0],Gdata[0]

def loop_GM(g,m):
    for n in range(0,26):
        if n not in [2,8]:
            foo=plot_GM(m,g,n)

def plot_GM(Mdata,Gdata,n): #will probably have to deal with times to make them all the same...
    import matplotlib.dates as mdates
    tim=Mdata['taxis'][0][n]
    mlen=Mdata['len'][0][n]
    nflares=np.shape(Mdata['taxis'][0])[0]/2 #assume 2 energy ranges for now
    Mtim=[]
    for t in tim: Mtim.append(dt.strptime(t,'%d-%b-%Y %H:%M:%S.%f')) #fix messenger times to datetimes

    gtim=Gdata['taxis'][0][n]
    glen=Gdata['len'][0][n]
    Gtim=[]
    for t in gtim: Gtim.append(dt.strptime(t,'%d-%b-%Y %H:%M:%S.%f')) #fix GOES times to datetimes
    glong=Gdata['ydata'][0][n,1,0:glen-1] #what's up with these data?
    gshort=Gdata['ydata'][0][n,0,0:glen-1]    

    #plt.plot(Mtim[0:mlen-1],Mdata['phigh'][0][n][0:mlen-1],'b') #first energy channel
    #plt.plot(Mtim[0:mlen-1],Mdata['phigh'][0][n+nflares-1][0:mlen-1],'g') #second energy channel I think...check that this is plotting the right thing
    fig,ax1=plt.subplots()
    ax2=ax1.twinx()
    l1,=ax1.step(Mtim[0:mlen-1],Mdata['phigh'][0][n][0:mlen-1],'b',label='1.5-12.4 keV') #first energy channel
    l2,=ax1.step(Mtim[0:mlen-1],Mdata['phigh'][0][n+nflares-1][0:mlen-1],'g',label= '3-24.8 keV') #second energy channel I think...
    #plt.axis #add y-axis for GOES flux
    l3,=ax2.plot(Gtim[0:glen-1],gshort,'k',label='GOES 1-8 $\AA$') #goes short - plot with
    l4,=ax2.plot(Gtim[0:glen-1],glong,'m',label='GOES .5-4 $\AA$') #goes long
    myFmt = mdates.DateFormatter('%H:%M')
    ax1.xaxis.set_major_formatter(myFmt)
    plt.gcf().autofmt_xdate()
    #ax1.set_xlabel(dt.strftime(Mtim[0].date(),'%Y-%b-%d'))
    ax1.set_ylabel('Messenger counts $cm^{-2} keV^{-1}$')
    ax1.set_ylim([10**3,10**7])
    ax1.set_yscale('log')
    ax2.set_ylabel('GOES Flux W$m^{-2}$')
    ax2.set_yscale('log')
    
    plt.title(dt.strftime(Mtim[0].date(),'%Y-%b-%d'))
    ax1.set_xlim([Gtim[0],Gtim[glen-1]])
    print np.max(glong),np.max(gshort)
    plt.legend((l1,l2,l3,l4),(l1.get_label(),l2.get_label(),l3.get_label(),l4.get_label()),loc='upper right')
    fig.show()
    fname='plots/lightcurves/'+dt.strftime(Mtim[0].date(),'%Y-%b-%d')+'MG.png'
    fig.savefig(fname)
    return glong,gshort

def plotR(Rdata,n):
    import matplotlib.dates as mdates
    fig = plt.figure()
    ax1 = fig.add_subplot(111)
    n=n*4
    tim=Rdata['UT'][0][n][:,0]#since there are 4 channels per flare
    #rlen=Rdata['len'][0][n]

    Rtim=[]
    nflares=np.shape(Rdata['rate'][0])[0]/4 #assume 4 energy ranges for now
    for t in tim: Rtim.append(dt.strptime(t,'%d-%b-%Y %H:%M:%S.%f'))

    #get the energy bins - or do I need to do this since they should be the same? check first
        
    if np.mean(Rdata['rate'][0][n]) != 0.0:
        ax1.plot(Rtim,Rdata['rate'][0][n],'m',label='4-9 keV') #first energy channel
        print Rdata['erange'][0][n],Rdata['UT'][0][n][0]
    if np.mean(Rdata['rate'][0][n+1]) != 0.0:
        ax1.plot(Rtim,Rdata['rate'][0][n+1],'g',label='12-18 keV') #second energy channel I think...
        print Rdata['erange'][0][n+1],Rdata['UT'][0][n+1][0]
    if np.mean(Rdata['rate'][0][n+2]) != 0.0:
        ax1.plot(Rtim,Rdata['rate'][0][n+2],'c',label='18-30 keV') #etc
        print Rdata['erange'][0][n+2],Rdata['UT'][0][n+2][0]
    if np.mean(Rdata['rate'][0][n+3]) != 0.0:
        ax1.plot(Rtim,Rdata['rate'][0][n+3],'k',label='30-80 keV') #etc
        print Rdata['erange'][0][n+3],Rdata['UT'][0][n+3][0]
    #ax1.set_xlabel(dt.strftime(Rtim[0].date(),'%Y-%b-%d'))
    ax1.set_yscale('log')
    ax1.set_ylim([0,10**5])
    ax1.legend(loc='upper right')
    myFmt = mdates.DateFormatter('%H:%M')
    ax1.xaxis.set_major_formatter(myFmt)
    plt.gcf().autofmt_xdate()
    plt.title(dt.strftime(Rtim[0].date(),'%Y-%b-%d'))
    #plt.show()
    fname='plots/'+dt.strftime(Rtim[0].date(),'%Y-%b-%d')+'R.png'
    fig.savefig(fname)
    
def loop_R(r):
    for n in range(0,26):
        foo=plotR(r,n)
        
def plot_goes_ratio(list_obj, title= "",ymin=0, ymax=3, labels=1,ylog=False, goes=False,mgoes=False, scatter = False,cc='GOES',save=False,show=True):
    '''make a plot of the GOEs ratio vs. angle'''
    ang,mvals,rvals,delta,colors,coordlabel,labelang,labelratio=[],[],[],[],[],[],[],[]
    gc = list_obj.Flare_properties["RHESSI_GOES"]
    mc=list_obj.Flare_properties["Messenger_GOES"]
    ylabel='Messenger_GOES/RHESSI_GOES'
    if goes:
            mc = list_obj.Flare_properties["GOES_GOES"]
            gc=list_obj.Flare_properties["RHESSI_GOES"]
            ylabel='Observed GOES/RHESSI_GOES'
    if mgoes:
            mc = list_obj.Flare_properties["Messenger_GOES"]
            gc=list_obj.Flare_properties["GOES_GOES"]
            ylabel='Messenger_GOES/Observed_GOES'
    for angle, mval,rval,chisq,ids,dts in zip(list_obj.Angle,mc,gc,list_obj.Notes,list_obj.ID,list_obj.Datetimes['Obs_start_time']):
        try:
            rval=float(rval)
            mval=float(mval)
            #ang.append(angle)
            if cc=='GOES':
                #print np.rint(-np.log10(rval))
                if np.rint(-np.log10(rval)) <= 4.0:colors.append('r')
                elif np.rint(-np.log10(rval)) == 5.0:colors.append('m')
                elif np.rint(-np.log10(rval)) == 6.0:colors.append('y')
                elif np.rint(-np.log10(rval)) == 7.0:colors.append('g')
                elif np.rint(-np.log10(rval)) == 8.0:colors.append('b')
                elif np.rint(-np.log10(rval)) == 9.0:colors.append('k')
            else: #color code by other one
                if np.rint(-np.log10(mval)) <= 4.0:colors.append('r')
                elif np.rint(-np.log10(mval)) == 5.0:colors.append('m')
                elif np.rint(-np.log10(mval)) == 6.0:colors.append('y')
                elif np.rint(-np.log10(mval)) == 7.0:colors.append('g')
                elif np.rint(-np.log10(mval)) == 8.0:colors.append('b')
                elif np.rint(-np.log10(mval)) == 9.0:colors.append('k')
            rf=rval                
            mf=mval
        except ValueError:
            if type(rval) != float and len(rval) > 3:#:type(rval) != float : #or np.isnan(rval) == False:
                #ang.append(angle)
                if cc=='GOES':
                    if rval.startswith('X'): colors.append('r')
                    elif rval.startswith('M'):colors.append('m')
                    elif rval.startswith('C'):colors.append('y')
                    elif rval.startswith('B'):colors.append('g')
                    elif rval.startswith('A'):colors.append('b')
                    else: colors.append('k')
                else: #color code by other one
                    if mval.startswith('X'): colors.append('r')
                    elif mval.startswith('M'):colors.append('m')
                    elif mval.startswith('C'):colors.append('y')
                    elif mval.startswith('B'):colors.append('g')
                    elif mval.startswith('A'):colors.append('b')
                    else: colors.append('k')                
            rf=convert_goes2flux(rval)
            mf=convert_goes2flux(mval)

        mvals.append(mf)
        rvals.append(rf)
        ang.append(angle)
        if rf != -1 and rf !=0.:
            labelang.append(angle)
            labelratio.append(mf/rf)
            if labels==1:
                coordlabel.append(ids)
            else: #0 or 2
                coordlabel.append(datetime.strftime(dts,'%D %H:%M'))
        if scatter:
              delta = 50
        elif chisq == '':#notes column is empty
            delta.append(5000*10*2**np.rint(np.log10(np.abs(rf-mf)))) #difference in size between the GOES classes
        else: #notes carries chisq value
            delta.append(50*10*2**np.rint(np.log10(float(chisq))))

    ratio = np.array(mvals)/np.array(rvals)
    full_ratio = ratio #for now ...
    #print list_obj.Flare_properties["RHESSI_GOES"]
    #print list_obj.Notes,delta
    #print colors
    #print sorted(ratio)

    fig = plt.figure()
    ax1 = fig.add_subplot(111)
    ax1.scatter(np.array(ang), ratio, s=delta, c=colors,alpha=.75)
    ax1.axhline(y=1,linestyle='dashed',color='k')

    if labels != 0: 
        for x,y,t in zip(np.array(labelang),labelratio,coordlabel):
            #print x,y,t
            ax1.annotate('%s' % t, xy=(x,y), textcoords='data')
        plt.grid()

   
    plt.xlabel('Angle between Earth and Mercury (degrees)')
    plt.ylabel(ylabel)

    if ylog:
        ax1.set_yscale('log')
    ax1.set_ylim([ymin,ymax])
    ax1.set_xlim([0,180])
    plt.title(title)
    X = mpatches.Patch(color='red', label='X')
    M = mpatches.Patch(color='magenta', label='M')
    C = mpatches.Patch(color='yellow', label='C')
    B = mpatches.Patch(color='green', label='B')
    A= mpatches.Patch(color='blue', label='A')
    K= mpatches.Patch(color='black', label='>A')
    ax1.legend(handles=[X,M,C,B,A,K],loc='upper left',fontsize='medium')

    ax1.plot()
    if save:
        plt.savefig(save)
    if show:
        fig.show()
    return ratio,full_ratio

