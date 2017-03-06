 #######################################
#check_all_events.py
# Erica Lastufka 2/3/2017  

#Description: Get GOES data for every event listed in the Messenger flare list. Find outliers. Check RHESSI data to see if there's anything the flare list missed...
#######################################

#######################################
# Usage:

# for default output: python messenger_angles.py
######################################

import numpy as np
import scipy.constants as sc
import pandas as pd
from datetime import datetime
from datetime import timedelta as td
import os
import data_management as da
import pickle
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import copy
import messenger_angles_v2 as ma

def make_ids(flare_list):
    '''For events that don't have a RHESSI flare number, assign them a number based on date/time'''
    for i,flare in enumerate(flare_list.ID):
            if np.isnan(flare) == 1: #empty
                dt=datetime.strftime(flare_list.Datetimes['Messenger_datetimes'][i],'%Y%M%d%H%M')
                flare_list.ID[i]=int(dt)
    return flare_list

#if __name__ == "__main__":
#    os.chdir('/Users/wheatley/Documents/Solar/occulted_flares/flare_lists')
#    messenger_list = d.Data_Study('messenger_full_list.csv')
#    messenger_list = make_ids(messenger_list)
#    ma.download_messenger(messenger_list)
    #in IDL:
    #Get angles
    #Fit those that don't have a fit already
    #calculate Messenger GOES class
    #calculate GOES GOES class
    
    
def plot_goes_ratio(list_obj, title= "",ymin=0, ymax=3, labels=1,ylog=False, goes=False,mgoes=False, scatter = False):
    '''make a plot of the GOEs ratio vs. angle'''
    ang,mvals,rvals,delta,colors,coordlabel,labelang,labelratio=[],[],[],[],[],[],[],[]
    gc = list_obj.Flare_properties["RHESSI_GOES"]
    mc=list_obj.Flare_properties["Messenger_GOES"]
    ylabel='Messenger_GOES/RHESSI_GOES'
    if goes:
            mc = list_obj.Flare_properties["GOES_GOES"]
            gc=list_obj.Flare_properties["RHESSI_GOES"]
            ylabel='Calculated GOES/RHESSI_GOES'
    if mgoes:
            mc = list_obj.Flare_properties["Messenger_GOES"]
            gc=list_obj.Flare_properties["GOES_GOES"]
            ylabel='Messenger_GOES/Calculated_GOES'
    for angle, mval,rval,chisq,ids in zip(list_obj.Angle,mc,gc,list_obj.Notes,list_obj.ID):
        if type(rval) != float and len(rval) > 3:#:type(rval) != float : #or np.isnan(rval) == False:
            ang.append(angle)            
            if rval.startswith('X'): colors.append('r')
            elif rval.startswith('M'):colors.append('m')
            elif rval.startswith('C'):colors.append('y')
            elif rval.startswith('B'):colors.append('g')
            elif rval.startswith('A'):colors.append('b')
            else: colors.append('k')
            rf=convert_goes2flux(rval)
            mf=convert_goes2flux(mval)
            mvals.append(mf)
            rvals.append(rf)
            if rf != -1:
                coordlabel.append(ids)
                labelang.append(angle)
                labelratio.append(mf/rf)
            if scatter:
                delta = 50
            elif chisq == '':#notes column is empty
                delta.append(5000*10*2**np.rint(np.log10(np.abs(rf-mf)))) #difference in size between the GOES classes
            else: #notes carries chisq value
                 delta.append(50*10*2**np.rint(np.log10(float(chisq))))
    ratio = np.array(mvals)/np.array(rvals)
    #print list_obj.Flare_properties["RHESSI_GOES"]
    #print list_obj.Notes,delta
    #print colors
    print sorted(ratio)

    fig = plt.figure()
    ax1 = fig.add_subplot(111)
    ax1.scatter(np.array(ang), ratio, s=delta, c=colors,alpha=.75)
    ax1.axhline(y=1,linestyle='dashed',color='k')

    if labels == 1:
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

    fig.show()
    return ratio

