 #######################################
# OC.Flarepy
# Erica Lastufka 17/5/17 

#Description: Class of functions to deal with all data,files,calculations of the study
#######################################

import numpy as np
import os
import pickle
import glob
import OCFlare

class OCFlareList(object):
    ''' This object will have the following attributes:
            List of OCFlare objects
            Notes
        Methods will include:
            All selection/filtering/sorting methods
            All the plotting methods
            All statistics methods
     '''
    def __init__(self, IDs=True, folder=False):
        '''Options to initialize from list of flare IDs, file with column of flare IDs, or directory with object pickle files in them?'''
        self.list=[]
        if IDs and type(IDs) == list:
            #initialize from list of flare IDs
            for i in IDs:
                if os.file_exists(str(i)+'OCFlare.p'):
                    self.list.append(pickle.load(open(str(i)+'OCFlare.p','rb')))
                else:
                    #initialize all the other objects from the default legacy files?
                    self.list.append(OCFlare.OCFlare(i))
        elif IDs and type(IDs) == str:
            #assume it's a csv or sav file that has a column of flare ids in it
            import data_managementv2 as d
            with d.OCData(IDs) as o:
                for i in o.ID:
                    self.list.append(OCFlare.OCFlare(i))
            
        if folder:
            #restore all the Flare pickle files and combine into list
            os.chdir(folder)
            pickles=sorted(glob.glob('*.p')) #sorted by name... may want to change that, or change my ID naming convention
            for p in pickles:
                self.list.append(pickle.load(open(str(i)+'OCFlare.p','rb')))
            os.chdir('/Users/wheatley/Documents/Solar/occulted_flares')

        self.Notes=['']*len(self.list) #list of empty strings with the same length as flare list
            
    def __iter__(self):
        '''Returns a generator that iterates over the object'''
        for attr, value in self.__dict__.iteritems():
            yield attr, value

    def slice(self, indices):
        for n,i in enumerate(indices):
            self.ID[n]=self.ID[i]
            self.Angle[n]=self.Angle[i]
            self.Notes[n]=self.Notes[i]
            for key in self.Datetimes.keys():
                #print key,type(key),i
                self.Datetimes[key][n] = self.Datetimes[key][i]
            for key in self.Flare_properties.keys():
                self.Flare_properties[key][n] = self.Flare_properties[key][i]
            for key in self.Data_properties.keys():
                self.Data_properties[key][n] = self.Data_properties[key][i]
        self.ID = self.ID[0:n-1]
        self.Angle=self.Angle[0:n-1]
        self.Notes=self.Notes[0:n-1]
        for key in self.Datetimes.keys():
            self.Datetimes[key]= self.Datetimes[key][0:n-1]
        for key in self.Flare_properties.keys():
            self.Flare_properties[key]= self.Flare_properties[key][0:n-1]
        for key in self.Data_properties.keys():
            self.Data_properties[key]= self.Data_properties[key][0:n-1]

    def select_outliers(self, angle=90.,threshold=10.): #greater than given angle... need to fix bug/feature with ratio
        '''Select certain flares from the list to be examined in visually'''
        indices=[]
        newlist=copy.deepcopy(self)
        for i,flare in enumerate(self.ID):
            if np.abs(ratio[i]) > threshold and self.Angle[i] < angle:
                indices.append(i)
        newlist.slice(indices)    
        return newlist

    def plot_angle_distribution(self,ymax=10):
        '''make a histogram of the angle distributions'''
     
        fig = plt.figure()
        ax1 = fig.add_subplot(111)
        n, bins, patches = plt.hist(list_obj.Angle, 18, facecolor='green', alpha=0.75)
    
        plt.xlabel('Angle between Earth and Mercury (degrees)')
        plt.ylabel('Number of Events')
        ax1.set_ylim([0,ymax])
        ax1.set_xlim([0,180])

        ax1.plot()

        fig.show()
    
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
        K= mpatches.Patch(color='black', label='<A')
        ax1.legend(handles=[X,M,C,B,A,K],loc='upper left',fontsize='medium')

        ax1.plot()
        if save:
            plt.savefig(save)
        if show:
            fig.show()

def hist_ratio(flare_list,title='All flares',gc='all', save=False,show=True):
    '''Make histogram to see distribution of ratios by goes class'''
    ratio=get_ratio(flare_list)
    ratio = ratio[np.where(ratio != -1)]
    #print ratio
    fig = plt.figure()
    ax1 = fig.add_subplot(111)
    goes=np.array(convert_goes2flux(flare_list.Flare_properties['GOES_GOES']))
    #print goes
    
    if gc == 'all':
        n, bins, patches = plt.hist(ratio, np.logspace(-3,3,12), facecolor='orange', alpha=0.75)
    if gc == 'A':
        gt,lt =np.where(goes > 10**-8),np.where(goes < 10**-7)
        all=set(gt[0]) & set(lt[0])
        ratio= ratio[list(all)]
        n, bins, patches = plt.hist(ratio, np.logspace(-3,3,12), facecolor='blue', alpha=0.75)
    if gc == 'B':
        gt,lt =np.where(goes > 10**-7),np.where(goes < 10**-6)
        all=set(gt[0]) & set(lt[0])
        ratio= ratio[list(all)]
        n, bins, patches = plt.hist(ratio,np.logspace(-3,3,12) , facecolor='green', alpha=0.75)
    if gc == 'C':
        gt,lt =np.where(goes > 10**-6),np.where(goes < 10**-5)
        all=set(gt[0]) & set(lt[0])
        ratio= ratio[list(all)]
        n, bins, patches = plt.hist(ratio, np.logspace(-3,3,12), facecolor='yellow', alpha=0.75)
    if gc == 'M':
        gt,lt =np.where(goes > 10**-5),np.where(goes < 10**-4)
        all=set(gt[0]) & set(lt[0])
        ratio= ratio[list(all)]
        n, bins, patches = plt.hist(ratio, np.logspace(-3,3,12), facecolor='magenta', alpha=0.75)
    if gc == 'overlay':
        gt,lt =np.where(goes > 10**-8),np.where(goes < 10**-7)
        all=set(gt[0]) & set(lt[0])
        ratioA= ratio[list(all)]
        plt.hist(ratioA, np.logspace(-3,3,12), facecolor='blue', alpha=0.6)
        gt,lt =np.where(goes > 10**-7),np.where(goes < 10**-6)
        all=set(gt[0]) & set(lt[0])
        ratioB= ratio[list(all)]
        plt.hist(ratioB,np.logspace(-3,3,12) , facecolor='green', alpha=0.6)
        gt,lt =np.where(goes > 10**-6),np.where(goes < 10**-5)
        all=set(gt[0]) & set(lt[0])
        ratioC= ratio[list(all)]
        plt.hist(ratioC, np.logspace(-3,3,12), facecolor='yellow', alpha=0.6)
        gt,lt =np.where(goes > 10**-5),np.where(goes < 10**-4)
        all=set(gt[0]) & set(lt[0])
        ratioM= ratio[list(all)]
        plt.hist(ratioM, np.logspace(-3,3,12), facecolor='magenta', alpha=0.6)
        
        M = mpatches.Patch(color='magenta', label='M')
        C = mpatches.Patch(color='yellow', label='C')
        B = mpatches.Patch(color='green', label='B')
        A= mpatches.Patch(color='blue', label='A')
        ax1.legend(handles=[M,C,B,A],loc='upper left',fontsize='medium')
        
    
    plt.xlabel('Ratio between Messenger GOES and actual GOES')
    plt.ylabel('Number of Events')
    plt.gca().set_xscale("log")
    plt.title(title)
    ax1.set_ylim([0,100])
    #ax1.set_xlim([0,150])

    ax1.plot()
    if save:
        plt.savefig(save)
    if show:
        fig.show()
        
    return goes
