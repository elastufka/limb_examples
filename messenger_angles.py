 #######################################
# messenger_angles.py
# Erica Lastufka 30/11/2016  

#Description: Check if Messenger can see an occulted flare
#######################################

#######################################
# Usage:

# for default output: python messenger_angles.py
######################################

#import glob
#import os
import numpy as np
#import grid_eff_area as ga
import pidly #set up pidly
#import csv
import scipy.constants as sc
import pandas as pd
from datetime import datetime
import os
import pickle

def read_flare_list(filename='test.csv'):
    '''reads in list of occulted flare positions and time intervals'''
    #fit_resK = pd.read_csv('Occulted_Results_23.csv', sep=',', index_col=0) - Frederic's data
    #fit_resO = pd.read_csv('Occulted_Results_24.csv', sep=',', index_col=0)
    #fit_res = pd.concat([fit_resK,fit_resO])

    data=pd.read_csv(filename,sep=',', header=0) #column 0 will be NaN because it's text
    print data.keys()
    datelen=data['Date']
    newdates=[]

    strdates=newdates
    #print newdates[1:10], vars(newdates), newdates.tolist()
    for (date,i) in zip(data['Date'],range(0,len(datelen)-1)):
        try:
            newdates.append(str(datetime.strptime(date, '%Y %b %d').strftime('%m/%d/%y')))
        except ValueError:
            newdates=datelen.tolist()
            break
                       
    flare_list = {'date':newdates,'stime':data['Start_Time'].tolist(),'etime':data['End_Time'].tolist()}
    if 'Angle' in data.keys():
        flare_list['Angle']=data['Angle'].tolist()
    return flare_list

def is_flare_observed(list1,list2):
    '''Checks if Messenger observed anything within the flare time intervals. Use Brian Dennis's flare list. They shouldn't be too different for an occulted flare?'''
    #appends a boolean value to each flare list entry. Saves final flare list? Or append angle first?
    #same day?
    aa=list1['date']
    bb=list2['date']
    cc= list2['stime']
    dd=list1['stime']
    #print len(cc),len(dd), len(aa)
    #print aa[0:10],bb[0:10]#, aa[0:10]-bb[0:10]
    #test=['03/28/02', '04/04/02', '04/04/02', '04/18/02', '04/22/02', '04/29/02', '04/30/02', '04/30/02', '05/17/02', '05/17/02']
    #test2=['05/28/07', '05/28/07', '04/04/02', '05/29/07', '05/29/07', '05/30/07', '06/01/07', '06/01/07', '06/01/07', '06/01/07']
    found_list = list(set(aa) & set(bb))

    for item in found_list:
        index1 = aa.index(item)
        index2 = bb.index(item)
        print 'flare date: ',item,'Messenger time: ',cc[index2], 'Occulted Flare Time:' ,dd[index1]
    #about the same time?
    #There's only one! :(
    return found_list
    
def messenger_flare_angle(flare_list):
    '''Executes sswidl function messenger_flare_angle()'''
    angle_list=[]
    idl = pidly.IDL('/Users/wheatley/Documents/Solar/sswidl_py.sh')
   
    for flare in flare_list['date'][0:10]:
        #is_observed == False:
        #    angle=-1
        #else:
        #print flare
        #time=flare['date']
        if flare > '8/30/2007' and flare < '4/1/2014':
            #time=flare[0]+','+flare[1]#.tolist()
            print flare
            xloc=-200.
            yloc=200.
            aa=idl('print,"this is idl"')
            print aa
            angle = idl.messenger_flare_angle([-200.,200.], '15-feb-2011') #mess_helio_lonlat=mess_helio_lonlat
            #append angle to flare list
            angle_list.append(angle)
    idl.close()
    print angle_list
    #print time,angle_list
    return angle_list

def save_flare_list(flare_list):
    '''save the final flare list'''
    pickle(flare_list, filename='flare_list.p')

def plot_angle_distribution(angle_list):
    '''make a histogram of the angle distributions'''
     
    fig = plt.figure()
    ax1 = fig.add_subplot(111)
    n, bins, patches = plt.hist(angle_list['Angle'], 18, facecolor='green', alpha=0.75)
    
    plt.xlabel('Angle between Earth and Mercury (degrees)')
    plt.ylabel('Number of Events')
    #ax1.set_ylim([0,1])
    #ax1.set_xlim([0,150])
    #plt.title("Effective area of grids "+ substrate_properties['material'] + ' '+ substrate_properties['thickness'] + '$\mu$m, ' + slit_properties['material'] + ' '+ slit_properties['thickness']+'$\mu$m' )
    #ax1.legend(loc='upper right',fontsize='medium')

    ax1.plot()

    fig.show()
    
if __name__ == "__main__":
    os.chdir('/Users/wheatley/Documents/Solar/MiSolFA/statistics')
    #occulted_list = read_flare_list(filename='full_output.csv')
    #messenger_list = read_flare_list(filename='messenger_list.csv')
    #list_observed = is_flare_observed(occulted_list, messenger_list)
    #angle_list = messenger_flare_angle(messenger_list)
    #plot_angle_distribution(angle_list)
    #save_flare_list(angle_list)
    angle_list = read_flare_list(filename='messenger_angles.csv')
    plot_angle_distribution(angle_list)

    
