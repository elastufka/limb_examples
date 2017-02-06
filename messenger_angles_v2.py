 #######################################
# messenger_angles.py
# Erica Lastufka 30/11/2016  

#Description: Check if Messenger can see an occulted flare
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

def import_flare_list(instrument,filename='test.csv', ):
    '''reads in list of occulted flare positions and time intervals'''
    data=pd.read_csv(filename,sep=',', header=0) #column 0 will be NaN because it's text

    dt = []
    for d,t in zip(data['Date'].tolist(),data['Start_Time'].tolist()):
        dt.append(d + ' '+ t)
    #print dt[0:5]
            
    flare_list = da.Data_Study(length=len(data['Date']))
    if instrument == 'Messenger':
        flare_list.Datetimes["Messenger_datetimes"] = dt
        flare_list.Flare_properties["Messenger_T"] = data['T1'].tolist()
        flare_list.Flare_properties["Messenger_EM1"] = data['EM1'].tolist()
    else:
        flare_list.Datetimes["RHESSI_datetimes"] = dt
        flare_list.Flare_properties['RHESSI_GOES'] = data['GOES'].tolist()

    flare_list.format_datetimes()    
    if 'Angle' in data.keys():
        flare_list.Angle=data['Angle'].tolist()
    if 'ID' in data.keys():
        flare_list.ID=data['ID'].tolist()
        
    return flare_list

def is_flare_observed(obj1,obj2, cutoff=7200):
    '''Checks if Messenger observed anything within the flare time intervals. Use Brian Dennis's flare list. They shouldn't be too different for an occulted flare? Cutoff time should be specified in seconds, default is 2 hours'''

    dt1=obj1.Datetimes['RHESSI_datetimes']
    dt2=obj2.Datetimes['Messenger_datetimes']
    id1=obj1.ID
    Rgoes=obj1.Flare_properties['RHESSI_GOES']
    
    IDs,newfoundlist, nMtime,nRtime,nMdt,nRdt=[],[],[],[],[],[]
    for dt,id in zip(dt1,id1):
        closest = map(lambda d: abs(d-dt), dt2) #this is a list
        for item,index in zip(closest, range(0,len(dt2))):
            if item.total_seconds() < cutoff:
                print dt, '    ',dt2[index]
                newfoundlist.append(str(dt.date()))
                #nMtime.append(str(dt2[index].time()))
                #nRtime.append(str(dt.time()))
                nMdt.append(dt2[index])
                nRdt.append(dt)
                IDs.append(id)

    new_list = da.Data_Study(length = len(IDs))
    new_list.ID = IDs
    new_list.Datetimes['RHESSI_datetimes'] = nRdt
    new_list.Datetimes['Messenger_datetimes'] = nMdt
    new_list.Flare_properties['RHESSI_GOES'] = Rgoes
    new_list.Flare_properties["Messenger_T"] = obj2.Flare_properties["Messenger_T"]
    new_list.Flare_properties["Messenger_EM1"] = obj2.Flare_properties["Messenger_EM1"]
    
    return new_list
       
def plot_angle_distribution(list_obj,ymax=10):
    '''make a histogram of the angle distributions'''
     
    fig = plt.figure()
    ax1 = fig.add_subplot(111)
    n, bins, patches = plt.hist(list_obj.Angle, 18, facecolor='green', alpha=0.75)
    
    plt.xlabel('Angle between Earth and Mercury (degrees)')
    plt.ylabel('Number of Events')
    ax1.set_ylim([0,ymax])
    #ax1.set_xlim([0,150])

    ax1.plot()

    fig.show()

def convert_goes2flux(goes_class):
    '''Converts Goes class to flux value'''
    flux = -1
    try:
        val = goes_class[0:1]
        if goes_class.endswith('*'):
            goes_class = goes_class[:-1]
        if val == 'A':
            flux = float(goes_class[1:])*10**-8
        if val == 'B':
            flux = float(goes_class[1:])*10**-7
        if val == 'C':
            flux = float(goes_class[1:])*10**-6
        if val == 'M':
            flux = float(goes_class[1:])*10**-5
        if val == 'X':
            flux = float(goes_class[1:])*10**-4   
    except TypeError:
        pass
    return flux
    
def plot_goes_ratio(list_obj, title= "", ymax=3, labels=1):
    '''make a plot of the GOEs ratio vs. angle'''
    ang,mvals,rvals,delta,colors=[],[],[],[],[]
    for angle, mval,rval in zip(list_obj.Angle,list_obj.Flare_properties["Messenger_GOES"],list_obj.Flare_properties["RHESSI_GOES"]):
        if type(rval) != float and len(rval) > 3:#:type(rval) != float : #or np.isnan(rval) == False:
            ang.append(angle)
            rf=convert_goes2flux(rval)
            mf=convert_goes2flux(mval)
            mvals.append(mf)
            rvals.append(rf)
            delta.append(5000*10*2**np.rint(np.log10(np.abs(rf-mf)))) #difference in size between the GOES classes
            col=np.rint(-np.log10(rf))
            if col == 4: colors.append('r')
            elif col == 5:colors.append('m')
            elif col == 6:colors.append('y')
            elif col == 7:colors.append('g')
            elif col == 8:colors.append('b')
            else: colors.append('k')
    ratio = np.array(mvals)/np.array(rvals)
    #print list_obj.Flare_properties["RHESSI_GOES"]
    print delta
    #print colors
    #print ratio
    #ratio = ratio[ratio != 0.0]
    #ratio = ratio[ratio > 0.0]
    #print ratio

    fig = plt.figure()
    ax1 = fig.add_subplot(111)
    ax1.scatter(np.array(ang), ratio, s=delta, c=colors,alpha=.75)
    ax1.axhline(y=1,linestyle='dashed',color='k')

    if labels == 1:
        for x,y,t in zip(np.array(ang),ratio,list_obj.ID):
            #print x,y,t
            ax1.annotate('%s' % t, xy=(x,y), textcoords='data')
        plt.grid()
    
    plt.xlabel('Angle between Earth and Mercury (degrees)')
    plt.ylabel('Messenger_GOES/RHESSI_GOES')
    #ax1.set_ylim([0,np.max(ratio)])
    ax1.set_ylim([0,ymax])
    ax1.set_xlim([0,180])
    plt.title(title)
    X = mpatches.Patch(color='red', label='X')
    M = mpatches.Patch(color='magenta', label='M')
    C = mpatches.Patch(color='yellow', label='C')
    B = mpatches.Patch(color='green', label='B')
    ax1.legend(handles=[X,M,C,B],loc='upper left',fontsize='medium')

    ax1.plot()

    fig.show()
    
def filter_source_vis(flare_list, field='Y'):
    '''Select certain flares from the list to be examined in sswidl'''
    vis = flare_list.Flare_properties['source_vis']
    indices=[]
    for i,v in enumerate(vis):
        if v == field:
            indices.append(i)
    flare_list.slice(indices)    
    return flare_list

def do_quicklook(flare_list, download=False, opent=False):
    import webbrowser
    import urllib
    dataurl = 'http://soleil.i4ds.ch/hessidata/metadata/qlook_image_plot'
    #subfolders by year, month,day (except 2001)
    listlen = len(flare_list.ID)
    for i,id,dt in zip(range(0,listlen -1),flare_list.ID,flare_list.Datetimes['RHESSI_datetimes']):
        newurl=dataurl+'/'+dt.strftime('%Y/%m/%d')
        filename='/hsi_qlimg_'+str(id)+'_012025.png' #get the 12-25 keV image
        image=newurl+filename
        if download:
            urllib.urlretrieve(image,'/Users/wheatley/Documents/Solar/occulted_flares/data/round2/'+filename)
        if opent:
            webbrowser.open_new_tab(image)
        else: #just save the data to the object
            flare_list.Data_properties['QL_images'][i] = image 

def open_in_RHESSI_browser(flare_list, opent=False):
    import webbrowser
    browserurl = 'http://sprg.ssl.berkeley.edu/~tohban/browser/?show=grth1+qlpcr+qlpg9+qli02+qli03+qli04+synff&date=' #20120917&time=061500'
    #subfolders by year, month,day (except 2001)
    #warn if you're opening more than 20 tabs
    if opent == True and len(flare_list.ID) > 20:
        ans = raw_input('You are about to open ' + str(len(flare_list.ID)) + ' tabs! Are you sure?')
        if ans != 'Y':
            opent = False        
    for i,dt in enumerate(flare_list.Datetimes['RHESSI_datetimes']):
        address=browserurl + dt.strftime('%Y%m%d') + '&time=' +dt.strftime('%H%M%S')
        flare_list.Data_properties['RHESSI_browser_urls'][i] = address
        if opent:
            webbrowser.open_new_tab(address)

def select_time_intervals(flare_list,before=10,after=10):
    '''Generate time intervals for use in sswidl'''
    #list=pickle.load(open('list_observed.p','rb'))
    Mstarttime,Mendtime,Rstarttime,Rendtime=[],[],[],[]
    #Format for time is YY/MM/DD, HHMM:SS.SSS
    #or alternatively, DD-Mon-YY HH:MM:SS.SSS -> '%d-%b-%Y %H:%M:%S.000'

    for index in range(0,len(flare_list['date'])):
        Mstarttime.append((flare_list['Messenger_datetime'][index] - td(minutes=before)).strftime('%d-%b-%Y %H:%M:%S.000'))
        Mendtime.append((flare_list['Messenger_datetime'][index] + td(minutes=after)).strftime('%d-%b-%Y %H:%M:%S.000'))
        Rstarttime.append((flare_list['Messenger_datetime'][index] - td(minutes=before)).strftime('%d-%b-%Y %H:%M:%S.000'))
        Rendtime.append((flare_list['Messenger_datetime'][index] + td(minutes=after)).strftime('%d-%b-%Y %H:%M:%S.000'))
    print type(Mstarttime),Mendtime
    time_intervals={'Mstart_time':Mstarttime,'Mend_time':Mendtime,'Rstart_time':Rstarttime,'Rend_time':Rendtime}
    flare_list.update(time_intervals) #adds these to the flare list dictionary
    return flare_list
    
#if __name__ == "__main__":
#    os.chdir('/Users/wheatley/Documents/Solar/occulted_flares/')
    #occulted_list = import_flare_list('RHESSI', filename='list_filtered.csv') #make these into Data_Study objects now
    #messenger_list = import_flare_list('Messenger',filename='messenger_list.csv') #make these into Data_Study objects now
    #list_observed = is_flare_observed(occulted_list, messenger_list,cutoff=3600) #this will basically 'merge' the two objects
    #list_observed.convert2idl('list_observed_obj.sav')
    #list_observed.export2pickle('list_observed_obj.p')
    #list_observed.export2csv('list_observed_obj.csv')

    #flares=pickle.load(open('list_observed_obj.p','rb'))
    #flares = da.Data_Study(filename='list_observed_goes.sav')
    #foo=plot_goes_ratio(flares)
    #flares.export2csv('list_observed_goes.csv')

    #flares = da.Data_Study(filename='list_observed_vis.csv')
    #new_list = filter_source_vis(flares)
    #new_list= da.Data_Study(filename='list_short.csv')
    #foo=plot_goes_ratio(flares, title='GOES ratio distribution for flares observed by both instruments',ymax=10)
    #foo=plot_goes_ratio(new_list,title='GOES ratio distribution for flares with visible coronal source')
    #new_list=pickle.load(open('list_short.p','rb'))
    #foo=plot_goes_ratio(new_list,title='GOES ratio distribution for flares with visible coronal source')
    #do_quicklook(new_list)
    #open_in_RHESSI_browser(new_list, opent=True)
    #list_selected=list_selected()
    #time_intervals=select_time_intervals(list_selected)
    #save_flare_list(time_intervals,'time_intervals.p')        
    #save_flare_list_idl(time_intervals,'time_intervals.sav')

    #mlist = import_flare_list('RHESSI', filename='list_matches.csv') #make these into Data_Study objects now
    #messenger_list = import_flare_list('Messenger',filename='messenger_list.csv') #make these into Data_Study objects now
    #list_observed = is_flare_observed(mlist, messenger_list,cutoff=3600) #this will basically 'merge' the two objects
    #list_observed.convert2idl('list_matches_obj.sav')
    #list_observed.export2pickle('list_matches_obj.p')
    #list_observed.export2csv('list_matches_obj.csv')

