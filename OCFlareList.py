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
    def __init__(self, IDs=True, folder=False,calc_times=False, calc_missing=False,gen=False):
        '''Options to initialize from list of flare IDs, file with column of flare IDs, or directory with object pickle files in them?'''
        self.list=[]
        if IDs and type(IDs) == list:
            #initialize from list of flare IDs
            for i in IDs:
                if os.path.isfile(str(i)+'OCFlare.p'):
                    self.list.append(pickle.load(open(str(i)+'OCFlare.p','rb')))
                else:
                    #initialize all the other objects from the default legacy files?
                    self.list.append(OCFlare.OCFlare(i,calc_times=calc_times, calc_missing=calc_missing,gen=gen))
        elif IDs and type(IDs) == str:
            #assume it's a csv or sav file that has a column of flare ids in it
            import data_managementv2 as d
            with d.OCData(IDs) as o:
                for i in o.ID:
                    self.list.append(OCFlare.OCFlare(i,calc_times=calc_times, calc_missing=calc_missing,gen=gen))
            
        if folder:
            #restore all the Flare pickle files and combine into list
            os.chdir(folder)
            pickles=sorted(glob.glob('*.p')) #sorted by name... may want to change that, or change my ID naming convention
            for p in pickles:
                self.list.append(pickle.load(open(str(i)+'OCFlare.p','rb')))
            os.chdir('/Users/wheatley/Documents/Solar/occulted_flares')

        self.Notes=['']*len(self.list) #list of empty strings with the same length as flare list

    def write(self,picklename=False):
        import pickle
        pickle.dump(self, open(picklename, 'wb'))

    def __iter__(self):
        '''Returns a generator that iterates over the object'''
        for attr, value in self.__dict__.iteritems():
            yield attr, value

    #def slice(self, indices): #this is deprecated because now each flare is an individual object

    def select_outliers(self, angle=90.,threshold=10.): #greater than given angle... need to fix bug/feature with ratio
        '''Select certain flares from the list to be examined in visually'''
        indices=[]
        #newlist=copy.deepcopy(self)
        for i,flare in enumerate(self.ID):
            if np.abs(self.list[i].Properties.ratio) > threshold and self.list[i].Observation.Angle < angle:
                indices.append(i)
                newlist.append(self.list[i])    
        return newlist #this won't have all the plot methods attached to it... maybe I should let an object be initialized from list of objects and just tack on the methods

    def isolate_att(self,att,key=False):
        '''Make a list of all the values of the given attribute. Either input name of attribute, or name of dictionary and keyword ie loops['length1']'''
        alist=[]
        if hasattr(self.list[0].Datetimes,att):
            for i in np.arange(0,len(self.list)): alist.append(getattr(self.list[i].Datetimes,att))
        elif hasattr(self.list[0].Properties,att):
            for i in np.arange(0,len(self.list)):
                if not key:
                    alist.append(getattr(self.list[i].Properties,att))
                else:
                    alist.append(getattr(self.list[i].Properties,att)[key])
        elif hasattr(self.list[0].Files,att):
            for i in np.arange(0,len(self.list)):
                if not key:
                    alist.append(getattr(self.list[i].Files,att))
                else:
                    alist.append(getattr(self.list[i].Files,att)[key])                    
        elif hasattr(self.list[0].Observation,att):
            for i in np.arange(0,len(self.list)):
                if not key:
                    alist.append(getattr(self.list[i].Observation,att))
                else:
                    alist.append(getattr(self.list[i].Observation,att)[key])
        elif att=='ID':
            alist.append(getattr(self.list[i],'ID'))
        return alist

####################################################  PLOT METHODS  ##################################################################

    def plot_angle_distribution(self,ymax=10):
        '''make a histogram of the angle distributions'''
        fig = plt.figure()
        ax1 = fig.add_subplot(111)
        angle=isolate_att('Angle')
        n, bins, patches = plt.hist(angle, 18, facecolor='green', alpha=0.75)
    
        plt.xlabel('Angle between Earth and Mercury (degrees)')
        plt.ylabel('Number of Events')
        ax1.set_ylim([0,ymax])
        ax1.set_xlim([0,180])

        ax1.plot()

        fig.show()
    
    def plot_goes_ratio(self,title= "",ymin=0, ymax=3, labels=1,ylog=True, scatter = True,cc='GOES',save=False,show=True):
        '''make a plot of the GOEs ratio vs. angle'''
        mc=self.isolate_att("Messenger_GOES")
        gc=self.isolate_att("GOES_GOES")
        angle=self.isolate_att("Angle")
        chisq=self.isolate_att("chisq")
        ids=self.isolate_att("ID")
        dts=self.isolate_att("chisq")
        ylabel='Messenger_GOES/Observed_GOES'
        colors,labelang,labelratio,coordlabel=[],[],[],[]
        for mval,gval,cs,ID,dt,ang in zip(mc,gc,chisq,ids,dts,angle):
            if cc=='GOES':
                #print np.rint(-np.log10(rval))
                if np.rint(-np.log10(gval)) <= 4.0:colors.append('r')
                elif np.rint(-np.log10(gval)) == 5.0:colors.append('m')
                elif np.rint(-np.log10(gval)) == 6.0:colors.append('y')
                elif np.rint(-np.log10(gval)) == 7.0:colors.append('g')
                elif np.rint(-np.log10(gval)) == 8.0:colors.append('b')
                elif np.rint(-np.log10(gval)) == 9.0:colors.append('k')
            else: #color code by other one
                if np.rint(-np.log10(mval)) <= 4.0:colors.append('r')
                elif np.rint(-np.log10(mval)) == 5.0:colors.append('m')
                elif np.rint(-np.log10(mval)) == 6.0:colors.append('y')
                elif np.rint(-np.log10(mval)) == 7.0:colors.append('g')
                elif np.rint(-np.log10(mval)) == 8.0:colors.append('b')
                elif np.rint(-np.log10(mval)) == 9.0:colors.append('k')

            labelang.append(ang) #?
            labelratio.append(mval/gval) #?
            if labels==1:
                coordlabel.append(ID)
            else: #0 or 2
                coordlabel.append(datetime.strftime(dt,'%D %H:%M'))
            if scatter:
                delta = 50
            elif cs == '':#notes column is empty
                delta.append(5000*10*2**np.rint(np.log10(np.abs(mval-gval)))) #difference in size between the GOES classes
            else: #notes carries chisq value
                delta.append(50*10*2**np.rint(np.log10(float(cs))))

        ratio = np.array(mc/gc)

        fig = plt.figure()
        ax1 = fig.add_subplot(111)
        ax1.scatter(np.array(angle), ratio, s=delta, c=colors,alpha=.75)
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

   def hist_ratio(self,title='All flares',gc='all', save=False,show=True):
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

    def sunpy_spectrogram(data,ebins,i): #since this is for one spectrogram move it to Observations?
        #from sunpy.spectra import spectrogram as s
        import mySpectrogram as s
        eaxis=ebins[0:-1]
        last=int(data['len'][0]-1)
        time_axis=np.arange(0,last+1)*4.#data[0]['ltime'] #ndarray of time offsets,1D #need the 4 for RHESSI time interval
        start= dt.strptime(data['UT'][i][0],'%d-%b-%Y %H:%M:%S.000') #datetime
        try:
            end= dt.strptime(data['UT'][i][last],'%d-%b-%Y %H:%M:%S.000') #datetime #might want to modify this to be where the data =0
        except ValueError:
            import datetime
            end = start + datetime.timedelta(seconds=time_axis[-1])
            #print dt.strptime(data['UT'][i][last-1],'%d-%b-%Y %H:%M:%S.000')
        drate=np.transpose(np.log10(data['rate'][i][0:last+1])) #get rid of zeros before taking log10?
        #drate=np.nan_to_num(drate)
        drate[drate == -np.inf] = 0.0
        for n,col in enumerate(drate.T):
            if all([c ==0.0 for c in col]):
                drate[:,n] = np.nan
        a=s.Spectrogram(data=drate,time_axis=time_axis,freq_axis=eaxis,start=start,end=end,instruments=['RHESSI'],t_label='',f_label='Energy (keV)',c_label='log(counts/cm^2 s)')
        fig=a.plot()

        outfilename='data/spectrograms/'+s.get_day(a.start).strftime("%d%b%Y")+'sgram.png'
        fig.figure.savefig(outfilename)
        plt.clf()
        return a
