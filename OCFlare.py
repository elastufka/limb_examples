 #######################################
# OC.Flare.py
# Erica Lastufka 17/5/17 

#Description: Class of functions to deal with all data,files,calculations of the study
#######################################

import numpy as np
import glob
import pickle
import sunpy.map
from datetime import datetime as dt

import OCDatetimes as ocd
import OCFiles as ocf
import OCProperties as ocp
import OCObservation as oco

class OCFlare(object):
    ''' Object will have the following attributes:
            ID: RHESSI flare ID or generated ID
            Datetimes: OCDatetimes object (might inherit from OCData object)
            Files: OCFiles object that contains all information about file names and locations
            Data: OCData object (different from original) that contains methods for loading/accessing the data ->tag this onto Files?
            Properties: OCProperties object that contains all information about the flare itself
            Observation:OCObservation object that contains all information about the observations
            Notes
        Methods will include:
            Method for translating between pickle, .sav and .csv
        A list of OCFlare objects will comprise an OCFlareList object, which will include all the plotting methods
     '''
    def __init__(self, ID, legacy=True, calc_times=False, calc_missing=False,gen=False):
        '''Initialize the flare object from an ID, pickle files in given folder, or legacy .csv or .sav'''
        self.ID=ID
        #first see if we can just restore the objects from pickles...
        pickles=sorted(glob.glob(str(ID)+'*.p')) #might want to make a special directory for these
        if pickles:
            for p in pickles:
                if p == str(ID)+'.p':
                    self=pickle.load(open(p,'rb')) #does this work? can test
                    break
                if p.endswith('OCDatetimes.p'):
                    self.Datetimes=pickle.load(open(p,'rb'))
                else:
                    self.Datetimes=ocd.OCDatetimes(ID,legacy=legacy)
                if p.endswith('OCProperties.p'):
                    self.Properties=pickle.load(open(p,'rb'))
                else:
                    self.Properties=ocp.OCProperties(ID,legacy=legacy)
                if p.endswith('OCFiles.p'):
                    self.Files=pickle.load(open(p,'rb'))
                else:
                    self.Files=ocf.OCFiles(ID,legacy=legacy)
                if p.endswith('OCObservations.p'):
                    self.Observations=pickle.load(open(p,'rb'))
                else:
                    self.Observations=oco.OCObservations(ID,legacy=legacy)                               
        else:
            self.Datetimes=ocd.OCDatetimes(ID,legacy=legacy,calc_times=calc_times)
            self.Properties=ocp.OCProperties(ID,legacy=legacy,calc_missing=calc_missing)
            self.Files=ocf.OCFiles(ID,legacy=legacy)
            self.Observation=oco.OCObservation(ID,legacy=legacy)
            self.Notes= [""]
        
    def export2csv(self, filename):
        '''Exports Python dictionary to csv file'''
        #from pandas.io.json import json_normalize
        #json_normalize(self.__dict__).to_csv(filename) #flattens the dictionaries so it looks ok in a spreadsheet... only it does this wrong!

        #first flatten the dictionaries - I should write a function to do this later:
        self.Data_properties['csv_name']=np.repeat(filename,len(self.ID))
        self.format_datetimes()
        #print self.Datetimes['Messenger_datetimes'][0:10]
        d=self.__dict__
        headers = ['ID','Messenger_datetimes','RHESSI_datetimes','Obs_start_time','Obs_end_time','Messenger_T','Messenger_EM1','Messenger_GOES','Messenger_total_counts','RHESSI_GOES','GOES_GOES','RHESSI_total_counts','Location','source_vis','Messenger_data_path','RHESSI_data_path','XRS_files','QL_images','RHESSI_browser_urls','csv_name','good_det','Angle','Notes']
        #zip them all together
        rows = zip(d['ID'],
                   d['Datetimes']['Messenger_datetimes'],d['Datetimes']['RHESSI_datetimes'],
                   d['Datetimes']['Obs_start_time'],d['Datetimes']['Obs_end_time'],
                   d['Flare_properties']['Messenger_T'],d['Flare_properties']['Messenger_EM1'],
                   d['Flare_properties']['Messenger_GOES'],d['Flare_properties']['Messenger_total_counts'],
                   d['Flare_properties']['RHESSI_GOES'],d['Flare_properties']['GOES_GOES'],d['Flare_properties']['RHESSI_total_counts'],
                   d['Flare_properties']['Location'],d['Flare_properties']['source_vis'],
                   d['Data_properties']['Messenger_data_path'],d['Data_properties']['RHESSI_data_path'],
                   d['Data_properties']['XRS_files'],d['Data_properties']['QL_images'],
                   d['Data_properties']['RHESSI_browser_urls'],d['Data_properties']['csv_name'],d['Data_properties']['good_det'],
                   d['Angle'],d['Notes'])

        import csv
        with open(filename,'wb') as f:
            writer=csv.writer(f)
            writer.writerow(headers)
            for row in rows:
                writer.writerow(row)

    def export2idl(self, savname):
        '''because the dictionaries might be to big to send directly, read it in from the csv file'''
        #convert datetimes to IDL-friendly format
        #Format for time is YY/MM/DD, HHMM:SS.SSS
        #or alternatively, DD-Mon-YY HH:MM:SS.SSS -> '%d-%b-%Y %H:%M:%S.000'

        for i,ang in enumerate(self.Angle):
            if np.isnan(ang) == 1:
                self.Angle[i] = 0.0 #to avoid any awkwardness with IDL when it does the calculation
        
        self.format_datetimes() #this should turn them all into datetimes UNLESS they are empty strings
        data = self.Datetimes
        for key in data.keys():
            #check that it's got quote marks then continue
            newval=[]
            if type(data[key][0]) == str:
                    continue #it's an empty string so let's leave it that way
            else: #make it an IDL-friendly string and put quotes around everything 
                for item in data[key]: 
                    newval.append("'"+item.strftime('%d-%b-%Y %H:%M:%S.000')+"'") 
                self.Datetimes[key]=newval

        #check if the csv file exists, if not, make it
        import glob
        if not savname[:-3]+'csv' in glob.glob('*.csv'):
            print 'no csv file found, converting to csv first'
            self.export2csv(savname[:-3]+'csv')
        else:
            ans=raw_input(savname[:-3]+'csv already exists! Overwrite? (Y/N)')
            if ans == 'Y':
                self.export2csv(savname[:-3]+'csv')

        import pidly
        idl = pidly.IDL('/Users/wheatley/Documents/Solar/sswidl_py.sh')
        idl('savname',savname)
        idl('csvname',savname[:-3]+'csv')
        idl('foo=read_csv(csvname)')
        idl('flare_list={ID:foo.field01,Datetimes:{Messenger_datetimes:foo.field02,RHESSI_datetimes:foo.field03,Obs_start_time:foo.field04,Obs_end_time:foo.field05},Flare_properties:{Messenger_T:foo.field06,Messenger_EM1:foo.field07,Messenger_GOES:foo.field08,Messenger_total_counts:foo.field09,RHESSI_GOES:foo.field10,GOES_GOES:foo.field11,RHESSI_total_counts:foo.field12,Location:foo.field13,source_vis:foo.field14},Data_properties:{Messenger_data_path:foo.field15,RHESSI_data_path:foo.field16,XRS_files:foo.field17,QL_images:foo.field18,RHESSI_browser_urls:foo.field19,csv_name:foo.field20,good_det:foo.field21},Angle:foo.field22,Notes:foo.field23}') 
        idl('save,flare_list, filename=savname')

    def export2pickle(self, picklename=False, allp=False):
        '''Replaces save_flare_list. Saves the data object in a .p file. Option to pickle all the individual objects as well.'''
        import pickle
        if not picklename:
            picklename=self.Files.dir+self.Files.folders['flare_lists']+'/'+str(self.ID)+'.p'
        pickle.dump(self, open(picklename, 'wb'))
        if allp:
            self.Datetimes.write()
            self.Properties.write()
            self.Observation.write()
            self.Files.write()

    #############################################  DATA READING & STORAGE METHODS  #######################################################

    #do I want the data to be an separate object? possibly....it would need to be initiated along with the other classes though to have the datetime/file info
    #it could be an optional attribute? I don't want to clog up memory
    #maybe don't store...
    
    def get_RHESSI_lightcurve(self, filename=False, save=False):
        '''Get data for this flare's rhessi lightcurve. Save in new file if requested.'''
        os.chdir(self.Files.dir + self.Files.folders['lightcurves'])        
        if self.Files.Raw['lightcurves'].endswith('.p'):
            pickle.load(self.Files.Raw['spectrogram']) #restore and be done. should be a mySpectrogram object
            os.chdir(self.Files.dir)
            return #think I probably have to assign a variable name...
            
        if self.Files.Raw['spectrogram'] == '': #get it from the sav file
            if not filename: filename='rerun_sgrams.sav'
            from scipy.io import readsav
            os.chidr('../')
            d=readsav(filename, python_dict=True)
            Rdata=d['data']['rdata'] #access via Rdata[0]['UT'], etc
            for j in len(data['len']):
                if self.Datetimes.Messenger_peak.date() == dt.strptime(Rdata['UT'][j][0],'%d-%b-%Y %H:%M:%S.000').date():
                    i=j #use this index
                    break
            Rdata=Rdata[i] #how is this organized again???
        if save:
            os.chdir(self.Files.dir + self.Files.folders['spectrograms'])
            newfname=str(self.ID)+'RHESSIlc.p'
            pickle.dump(a,open(newfname,'wb'))
            self.Files.Raw['lightcurves']=newfname
        os.chdir(self.Files.dir)       
        return Rdata

    def get_Messenger_lightcurve(self, filename=False, raw=False, save=False):
        '''Get data for this flare's Messenger lightcurve, and adjust to counts/s if specified (raw = False). Save in new file if requested.'''
        os.chdir(self.Files.dir + self.Files.folders['lightcurves'])        
        if self.Files.Raw['lightcurves'].endswith('.p'):
            pickle.load(self.Files.Raw['spectrogram']) #restore and be done. should be a mySpectrogram object
            os.chdir(self.Files.dir)
            return #think I probably have to assign a variable name...
            
        if self.Files.Raw['spectrogram'] == '': #get it from the sav file
            if not filename: filename='rerun_sgrams.sav'
            from scipy.io import readsav
            os.chidr('../')
            d=readsav(filename, python_dict=True)
            Mdata=d['data']['mdata']
            for j in len(data['len']):
                if self.Datetimes.Messenger_peak.date() == dt.strptime(Mdata['UT'][j][0],'%d-%b-%Y %H:%M:%S.000').date():
                    i=j #use this index
                    break
            Mdata=Mdata[i]

        def counts_ps(Mdata,n):
            '''Adjust messenger data to counts/s'''
            #get the time bin for each data point
            tim=Mdata['taxis'][0][n]
            mlen=Mdata['len'][0][n]
            nflares=np.shape(Mdata['taxis'][0])[0]/2
            Mtim,cps1,cps2=[],[],[]
            for t in tim: Mtim.append(dt.strptime(t,'%d-%b-%Y %H:%M:%S.%f')) #fix messenger times to datetimes
            M1=Mdata['phigh'][0][n][0:mlen-1]
            M2=Mdata['phigh'][0][n+nflares-1][0:mlen-1]

        for i in range(mlen-1):
            tbin=Mtim[i+1]-Mtim[i] #timedelta object in seconds
            cps1.append(M1[i]/tbin.total_seconds())
            cps2.append(M2[i]/tbin.total_seconds())
        return cps1,cps2

        if not Raw:
            #adjust counts
            cps1,cps2=counts_ps(Mdata,i)
            
        if save:
            os.chdir(self.Files.dir + self.Files.folders['spectrograms'])
            newfname=str(self.ID)+'Messengerlc.p'
            pickle.dump(Mdata,open(newfname,'wb'))
            self.Files.Raw['spectrogram']=newfname
            
        os.chdir(self.Files.dir)       
        return Mdata

    def get_GOES_lightcurve(self, filename=False, save=False):
        '''Get data for this flare's GOES lightcurve. Save in new file if requested.'''
        os.chdir(self.Files.dir + self.Files.folders['lightcurves'])        
        if self.Files.Raw['lightcurves'].endswith('.p'):
            pickle.load(self.Files.Raw['spectrogram']) #restore and be done. should be a mySpectrogram object
            os.chdir(self.Files.dir)
            return #think I probably have to assign a variable name...
            
        if self.Files.Raw['spectrogram'] == '': #get it from the sav file
            if not filename: filename='rerun_sgrams.sav'
            from scipy.io import readsav
            os.chidr('../')
            d=readsav(filename, python_dict=True)
            Gdata=d['data']['gdata']
            for j in len(data['len']):
                if self.Datetimes.Messenger_peak.date() == dt.strptime(Gdata['UT'][j][0],'%d-%b-%Y %H:%M:%S.000').date():
                    i=j #use this index
                    break
            Gdata={}
            
        if save:
            os.chdir(self.Files.dir + self.Files.folders['spectrograms'])
            newfname=str(self.ID)+'GOESlc.p'
            pickle.dump(a,open(newfname,'wb'))
            self.Files.Raw['spectrogram']=newfname
        os.chdir(self.Files.dir)       
        return Gdata

    def get_spectrogram(self, filename=False, save=False):
        '''Get data for this flare's RHESSI spectrogram. Save in new file if requested.'''
        import mySpectrogram as s
        os.chdir(self.Files.dir + self.Files.folders['spectrograms'])        
        if self.Files.Raw['spectrogram'].endswith('.p'):
            pickle.load(self.Files.Raw['spectrogram']) #restore and be done. should be a mySpectrogram object
            os.chdir(self.Files.dir)
            return #think I probably have to assign a variable name...
        if self.Files.Raw['spectrogram'] == '': #get it from the sav file
            if not filename: filename='rerun_sgrams.sav'
            from scipy.io import readsav
            os.chdir('../')
            d=readsav(filename, python_dict=True)
            data={'UT':0.,'rate':0.,'erate':0.,'ltime':0.,'len':0.}
            data['UT'] = d['data']['UT']
            data['rate']=d['data']['rate']
            data['erate']=d['data']['erate']
            data['len']=d['data']['len']
            ebins=d['ebins']
            eaxis=ebins[0:-1]
            last=int(data['len'][0]-1)
            time_axis=np.arange(0,last+1)*4.#data[0]['ltime'] #ndarray of time offsets,1D #need the 4 for RHESSI time interval
            for j in len(data['len']):
                if self.Datetimes.Messenger_peak.date() == dt.strptime(data['UT'][j][0],'%d-%b-%Y %H:%M:%S.000').date():
                    i=j #use this index
                    break
            start=dt.strptime(data['UT'][i][0],'%d-%b-%Y %H:%M:%S.000')
            try:
                end= dt.strptime(data['UT'][i][last],'%d-%b-%Y %H:%M:%S.000') #datetime #might want to modify this to be where the data =0
            except ValueError:
                end = start + datetime.timedelta(seconds=time_axis[-1])
                drate=np.transpose(np.log10(data['rate'][i][0:last+1])) #get rid of zeros before taking log10?
                drate[drate == -np.inf] = 0.0
            for n,col in enumerate(drate.T):
                if all([c ==0.0 for c in col]):
                    drate[:,n] = np.nan
            a=s.Spectrogram(data=drate,time_axis=time_axis,freq_axis=eaxis,start=start,end=end,instruments=['RHESSI'],t_label='',f_label='Energy (keV)',c_label='log(counts/cm^2 s)')
            if save:
                os.chdir(self.Files.dir + self.Files.folders['spectrograms'])
                newfname=str(self.ID)+'spectrogram.p'
                pickle.dump(a,open(newfname,'wb'))
                self.Files.Raw['spectrogram']=newfname
        os.chdir(self.Files.dir)
        return a

    def get_ospex_fit(self, filename=False, save=False):
        '''Get data for this flare's OSPEX fit to the Messenger lightcurve. Save in new file if requested. These are IDL sav files..'''

    def _query(self, path=False, AIA=False, STEREO=True, wave=False, timedelay = 30):
        '''Internal method to query VSO database for AIA or STEREO data and download it. Option to set time delay for stereo observations (in minutes). '''
        from sunpy.net import vso
        from datetime import datetime as dt
        from datetime import timedelta as td
        import astropy.units as u
        import sunpy.map

        vc = vso.VSOClient()
        if type(self.Datetimes.Messenger_peak) != dt: self.Datetimes.convert2datetime()
        if AIA:
            instr= vso.attrs.Instrument('AIA')
            sample = vso.attrs.Sample(24 * u.hour)
            if wave == '171': wave = vso.attrs.Wave(16.9 * u.nm, 17.2 * u.nm)
            elif wave == '193': wave = vso.attrs.Wave(19.1 * u.nm, 19.45 * u.nm)
            elif wave == '304': wave = vso.attrs.Wave(30 * u.nm, 31 * u.nm)            
            time = vso.attrs.Time(dt.strftime(self.Datetimes.Messenger_peak,'%Y-%m-%dT%H:%M:%S'),dt.strftime(self.Datetimes.Messenger_peak +td(seconds=2),'%Y-%m-%dT%H:%M:%S')) #should have data to within 1 s
            res=vc.query(wave, sample, time, instr)
        if STEREO:
            source=vso.attrs.Source('STEREO_'+self.Observation.STEREO) #this should be a string
            instr= vso.attrs.Instrument('EUVI')
            wave = vso.attrs.Wave(19.1 * u.nm, 19.45 * u.nm) #193
            time = vso.attrs.Time(dt.strftime(self.Datetimes.Messenger_peak+td(minutes=timedelay),'%Y-%m-%dT%H:%M:%S'),dt.strftime(self.Datetimes.Messenger_peak +td(minutes=timedelay+15),'%Y-%m-%dT%H:%M:%S')) #have to look 15 minutes after designated timedelay?
            res=vc.query(wave, source, time, instr)

        if not path: files = vc.get(res,path='/Users/wheatley/Documents/Solar/occulted_flares/data/stereo-aia/{file}').wait()
        else: files = vc.get(res,path=path+'{file}').wait()
        #put filenames in Files object
        if AIA:
            self.Files.Raw['aia'] = files[0]
        if STEREO:
            self.Files.Raw['stereo'] = files #take all of them in a list
                        
    def get_AIA(self, filename=False, save=False, wave='304'):
        '''Get data for this flare's AIA map of specified wavelength. Query the database if need be. Save in new file if requested.'''
        import astropy.units as u
        path=self.Files.dir + self.Files.folders['stereo-aia']+'/'
        os.chdir(path)
        #first check the if there is a local file with filename stored in Files object. 
        fname=self.Files.Raw['aia']
        if type(fname) == list:
            try:
                fname=[f for f in fname if wave in f][0]
            except IndexError:
                fname=''
        if fname.endswith('.p'):
            maps= pickle.load(open(fname,'rb')) #if it's a pickle just restore it. (do I need to assign it to maps or not?)
            os.chdir(self.Files.dir)
            return maps
        if fname == '' or not os.path.isfile(path+fname) or wave not in fname: #if not, query database. Now filename should be in the correct place in Files.
            self._query(AIA=True, STEREO=False, wave=wave)
            
        #convert to maps
        files=self.Files.Raw['aia']
        if type(files) == list:
            files=files[0]
        if files !=[]:
            smap= sunpy.map.Map(files)
            maps = {smap.instrument: smap.submap((-1100, 1100) * u.arcsec, (-1100, 1100) * u.arcsec)} #this could be empty if files is empty
        else: print 'No files found and no maps made!'
        
        if save: #pickle it?
            newfname=files[files.rfind('/')+1:files.rfind('.')]+'.p'
            pickle.dump(maps,open(newfname,'wb'))
            self.Files.Raw['aia']=newfname
        os.chdir(self.Files.dir)
        return maps

    def get_STEREO(self, filename=False, save=False):
        '''Get data for this flare's STEREO map. Query the database if need be. Save in new file if requested.'''
        import astropy.units as u
        path=self.Files.dir + self.Files.folders['stereo-aia']+'/'
        os.chdir(path)
        #first check the if there is a local file with filename stored in Files object. 
        fname=self.Files.Raw['stereo']
        try:
            if fname.endswith('.p'):
                maps = pickle.load(open(fname,'rb')) #if it's a pickle just restore it. (do I need to assign it to maps or not?)
                os.chdir(self.Files.dir)
                return maps
            if fname == '' or not os.path.isfile(path+fname) or fname==[]: #if not, query database. Now filename should be in the correct place in Files.
                self._query()
        except AttributeError: #it's a list of fits filenames
            pass    
            
        #convert to maps
        files=self.Files.Raw['stereo']
        maps=[]
        if files !=[]:
            #smap= sunpy.map.Map(files)
            for f in sunpy.map.Map(files):
                maps.append({f.instrument: f.submap((-1100, 1100) * u.arcsec, (-1100, 1100) * u.arcsec)}) #this could be empty if files is empty
            self.extract_stereo_times()
        else: print 'No files found and no maps made!'
        
        if save: #pickle it? 
            os.chdir(path)
            newfname=files[0][files[0].rfind('/')+1:files[0].rfind('.')]+'.p'
            pickle.dump(maps,open(newfname,'wb'))
            self.Files.Raw['stereo']=newfname
        os.chdir(self.Files.dir)

        return maps
    
    #############################################  MISC CALCULATION METHODS  #######################################################

    def extract_stereo_times(self):
        '''Put correct dates and times from downloaded stereo files into the datetimes.stereo_files list (except these are not actually the correct times, just the filenames. Can fix this later though, since right now the filename is more important)'''
        path=self.Files.dir + self.Files.folders['stereo-aia']
        os.chdir(path)
        try:
            fname= dt.strftime(self.Datetimes.stereo_start_time,'%Y%m%d')
        except TypeError:
            fname= dt.strftime(self.Datetimes.Messenger_peak,'%Y%m%d')
        ffiles=glob.glob(fname+'*eub.fts')
        ffiles.append(glob.glob(fname+'*eua.fts'))
        self.Datetimes.stereo_times=[]
        for f in ffiles:
            timestr=f[f.find('_')+1:f.rfind('_')]
            self.Datetimes.stereo_times.append(dt.strptime(fname+timestr,'%Y%m%d%H%M%S')) #parse the string and extract datetimes
        self.Files.Raw['stereo']=ffiles#put the filenames in Raw
        self.Files.Raw['aia']=glob.glob('aia_lev1*'+dt.strftime(self.Datetimes.Messenger_peak,'%Y_%m_%d')+'*.fits') #put the filenames in Raw
        os.chdir(self.Files.dir)

    def convert_coords_aia2stereo(self,map_aia=True,map_stereo=True,quiet=True,wave='304'):
        '''convert Properties.source_pos_disk to Properties.source_pos_STEREO for a given AIA and STEREO map'''
        from astropy.coordinates import SkyCoord
        import astropy.units as u
        #import astropy.wcs
        import sunpy.coordinates
        import sunpy.coordinates.wcs_utils

        if self.Properties.source_pos_disk == '': #think it should be this if empty
            coords=self.Properties.source_pos #is this in arcsec? how to check?
        else: coords=self.Properties.source_pos_disk
        #coords= [int(coords[:coords.find(',')]),int(coords[coords.find(',')+1:])]
        if not map_aia: #get the map
            if self.Files.Raw['aia'] !='' and glob.glob(self.Files.dir+ self.Files.folders['stereo-aia']+'/'+self.Files.Raw['aia']) !=[]:#first see if the pickle file is there
                os.chdir(self.Files.dir+ self.Files.folders['stereo-aia'])
                map_aia=pickle.load(open(self.Files.Raw['aia'],'rb'))
                os.chdir(self.Files.dir)               
            else: #download stuff and pickle it
                map_aia=self.get_AIA(filename=False, save=True, wave=wave)
                
        if not map_stereo: #get the map. Default is to take the first in the list
            if self.Files.Raw['stereo'] !='' and glob.glob(self.Files.dir+ self.Files.folders['stereo-aia']+'/'+self.Files.Raw['stereo']) !=[]:#first see if the pickle file is there
                os.chdir(self.Files.dir+ self.Files.folders['stereo-aia'])
                map_stereo=pickle.load(open(self.Files.Raw['stereo'],'rb'))
                os.chdir(self.Files.dir)
            else: #download stuff and pickle it
                map_stereo=self.get_STEREO(filename=False, save=True)
                if type(map_stereo) == list:
                    map_stereo=map_stereo[0]
            
        hpc_aia = SkyCoord(coords[0]*u.arcsec,coords[1]*u.arcsec, frame=map_aia[map_aia.keys()[0]].coordinate_frame)
        if not quiet: print(hpc_aia)

        hgs = hpc_aia.transform_to('heliographic_stonyhurst')
        hgs_val=np.isnan(hgs.lon.value) + np.isnan(hgs.lat.value)
        while hgs_val == 1: #while there are nan's
            coordstr=raw_input('Please enter integer coordinates on the AIA disk. Format: xxx,yyy')
            coords= [int(coordstr[:coordstr.find(',')]),int(coordstr[coordstr.find(',')+1:])]#format the string
            hpc_aia = SkyCoord(coords[0]*u.arcsec,coords[1]*u.arcsec, frame=map_aia[map_aia.keys()[0]].coordinate_frame)
            hgs = hpc_aia.transform_to('heliographic_stonyhurst')
            hgs_val= np.isnan(hgs.lon.value)+ np.isnan(hgs.lat.value)
        if not quiet: print(hgs)

        hgs.D0 = map_stereo['SECCHI'].dsun
        hgs.L0 = map_stereo['SECCHI'].heliographic_longitude
        hgs.B0 = map_stereo['SECCHI'].heliographic_latitude

        hpc_B = hgs.transform_to('helioprojective')
        if not quiet: print(hpc_B)

        self.Properties.source_pos_STEREO = [hpc_B.Tx.value,hpc_B.Ty.value] #is this right?
            
    ################################################# INDIVIDUAL PLOT METHODS  ###########################################################

    def plot_GM(Mdata,Gdata,n): #will probably have to deal with times to make them all the same...
        import matplotlib.dates as mdates
        tim=Mdata['taxis'][0][n]
        mlen=Mdata['len'][0]#[n]
        nflares=np.shape(Mdata['taxis'][0])[0]/2 #assume 2 energy ranges for now
        Mtim=[]
        for t in tim: Mtim.append(dt.strptime(t,'%d-%b-%Y %H:%M:%S.%f')) #fix messenger times to datetimes
        cps1,cps2=counts_ps(Mdata,n)
        print type(Mtim),np.shape(Mtim[:-1]),np.shape(cps1)
    
        gtim=Gdata['taxis'][0]#[n]
        glen=Gdata['len'][0]#[n]
        Gtim=[]
        for t in gtim: Gtim.append(dt.strptime(t,'%d-%b-%Y %H:%M:%S.%f')) #fix GOES times to datetimes
        glong=Gdata['ydata'][0][1,0:glen-1]#[n,1,0:glen-1] #what's up with these data?
        gshort=Gdata['ydata'][0][0,0:glen-1]#[n,0,0:glen-1]    

        fig,ax1=plt.subplots()
        ax2=ax1.twinx()
        l2,=ax1.step(Mtim[:-1],cps2,'g',label= '3-24.8 keV')
    
        myFmt = mdates.DateFormatter('%H:%M')
        ax1.xaxis.set_major_formatter(myFmt)
        plt.gcf().autofmt_xdate()
        #ax1.set_xlabel(dt.strftime(Mtim[0].date(),'%Y-%b-%d'))
        ax1.set_ylabel('Messenger counts $cm^{-2} keV^{-1} s^{-1}$')
        ax1.set_ylim([10**0,10**4])
        ax1.set_yscale('log')
        ax2.set_ylabel('GOES Flux W$m^{-2}$')
        ax2.set_yscale('log')
    
        plt.title(dt.strftime(Mtim[0].date(),'%Y-%b-%d'))
        ax1.set_xlim([Gtim[0],Gtim[glen-1]])
        #plt.legend((l1,l2,l3,l4),(l1.get_label(),l2.get_label(),l3.get_label(),l4.get_label()),loc='upper left',prop={'size':12})
        fig.show()
        fname='data/lightcurves/'+dt.strftime(Mtim[0].date(),'%Y-%b-%d')+'MG.png'
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
        if np.mean(Rdata['rate'][0][n+1]) != 0.0:
            ax1.plot(Rtim,Rdata['rate'][0][n+1],'g',label='12-18 keV') #second energy channel I think...
        if np.mean(Rdata['rate'][0][n+2]) != 0.0:
            ax1.plot(Rtim,Rdata['rate'][0][n+2],'c',label='18-30 keV') #etc
        if np.mean(Rdata['rate'][0][n+3]) != 0.0:
            ax1.plot(Rtim,Rdata['rate'][0][n+3],'k',label='30-80 keV') #etc
            #ax1.set_xlabel(dt.strftime(Rtim[0].date(),'%Y-%b-%d'))
        ax1.set_yscale('log')
        ax1.set_ylim([0,10**5])
        ax1.legend(loc='upper right')
        myFmt = mdates.DateFormatter('%H:%M')
        ax1.xaxis.set_major_formatter(myFmt)
        plt.gcf().autofmt_xdate()
        plt.title(dt.strftime(Rtim[0].date(),'%Y-%b-%d'))
        #plt.show()
        fname='data/lightcurves/'+dt.strftime(Rtim[0].date(),'%Y-%b-%d')+'R.png'
        fig.savefig(fname)

    def sunpy_spectrogram(filename,i): #since this is for one spectrogram move it to Flare?
        from scipy.io import readsav #import the spectrogram
        #format everything so it's right
        d=readsav(filename, python_dict=True)
        data={'UT':0.,'rate':0.,'erate':0.,'ltime':0.,'len':0.}
        data['UT'] = d['data']['UT']
        data['rate']=d['data']['rate']
        data['erate']=d['data']['erate']
        data['len']=d['data']['len']
        ebins=d['ebins']

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
        #create a figure of designated size - does this even work without a subplot?
        f=plt.figure(figsize=(8,5))
        fig=a.plot(figure=f)

        outfilename='data/spectrograms/'+s.get_day(a.start).strftime("%d%b%Y")+'sgram.png'
        fig.figure.savefig(outfilename)
        plt.clf()
        return a
    
    def plot_aia(self, AIAmap=True,zoom=False,save=False, wave='304',all_wave=False):                             
        '''Plot the stereo map(s) and overplot the limb and source_pos_STEREO. If all_wave, then subplots'''
        from astropy import units as u
        if not AIAmap:
            AIAmap=self.get_AIA(wave=wave)
        m=AIAmap[AIAmap.keys()[0]]
 
        if all_wave:
            maps = [self.get_AIA(wave=w) for w in ['171','193','304']]
            print maps.keys()
            fig = plt.figure(figsize=(len(maps)*3, 5))
        if not zoom:
            p=m.wcs
            if not all_wave:
                fig = plt.figure(figsize=(6, 5))
                ax = fig.add_subplot(1, 1, 1, projection=p)
                m.plot(axes=ax)
            if all_wave:
                for i in range(len(maps)):
                    ax = fig.add_subplot(1,len(maps),i+1, projection=p) #do the math
                    mm=maps[i][maps.keys()[0]] #I think
                    mm.plot(axes=ax)
                print maps.keys()
                
        if zoom: #zoom to a rectangle centered on source_pos
            width=400.*u.arcsec
            height=450.*u.arcsec
            coord=self.Properties.source_pos*u.arcsec
            submap = m.submap(u.Quantity((coord[0]-width/2,
                                        coord[0] + width/2)),
                            u.Quantity((coord[1]-height/2,
                                        coord[1] + height/2)))
            p=submap
            if not all_wave:
                fig = plt.figure(figsize=(6, 5))
                ax = fig.add_subplot(1, 1, 1, projection=p.wcs)
                submap.plot(axes=ax)
            if all_wave:
                for i in range(len(maps)):
                    ax = fig.add_subplot(1,len(maps),i+1, projection=p.wcs) #do the math
                    mm=maps[i][maps.keys()[0]] #I think
                    submap= mm.submap(u.Quantity((coord[0]-width/2,
                                        coord[0] + width/2)),
                            u.Quantity((coord[1]-height/2,
                                        coord[1] + height/2)))
                    submap.plot(axes=ax)

        fig.show()
        fname=self.Files.dir+self.Files.folders['plots']+'/'+dt.strftime(self.Datetimes.Messenger_peak.date(),'%Y%m%d')+'AIA_'+str(wave)
        if save:
            tag=raw_input('Identifying tag? ')
            fig.savefig(fname+tag+'.png')
                    
    def plot_stereo(self,AIAmap=True,maps=True,oplotlimb=False,oplotpoint=False,save=False,subplots=False,zoom=False,diff=False):
        '''Plot the stereo map(s) and overplot the limb and source_pos_STEREO. Enable the option to plot the difference of two maps, along with the original (map0)'''
        from astropy import units as u
        from astropy.coordinates import SkyCoord
        import copy
        
        if not AIAmap: AIAmap=self.get_AIA()
        if not maps: maps=self.get_STEREO()
        if subplots: fig = plt.figure(figsize=(len(maps)*3, 5))
        if self.Properties.source_pos_STEREO=='':
            self.convert_coords_aia2stereo(map_aia=AIAmap,map_stereo=maps[0],quiet=True) #because for each map it will be slightly different?
            
        for i,m in enumerate(maps):
            m=copy.deepcopy(m['SECCHI'])
            if diff:
                if i!=0:
                    m0=copy.deepcopy(maps[i-1]['SECCHI'])
                    md=copy.deepcopy(m)
                    m.data=md.data-m0.data #can I add color scaling somehow?
                    print i, i-1

            if not zoom:
                p=m.wcs
                pmap=m
                if not subplots:
                    fig = plt.figure(figsize=(len(maps)*3, 5))
                    ax = fig.add_subplot(1, 1, 1, projection=p)
                if subplots: ax = fig.add_subplot(1,len(maps),i+1, projection=p) #do the math
                m.plot(axes=ax)
                
            if zoom: #zoom to a rectangle centered on source_pos_STEREO
                width=400.*u.arcsec
                height=450.*u.arcsec
                coord=self.Properties.source_pos_STEREO*u.arcsec
                submap = m.submap(u.Quantity((coord[0]-width/2,
                                        coord[0] + width/2)),
                            u.Quantity((coord[1]-height/2,
                                        coord[1] + height/2)))
                p=submap
                pmap=submap
                if not subplots:
                    fig = plt.figure(figsize=(6, 5))
                    ax = fig.add_subplot(1, 1, 1, projection=p)
                if subplots: ax = fig.add_subplot(1,len(maps),i+1, projection=p) #do the math
                submap.plot(axes=ax)

            ax.set_autoscale_on(False)
            if oplotlimb: #do I need to abjust this for Stereo A? check...
                r = AIAmap[AIAmap.keys()[0]].rsun_obs.to(u.deg)-1*u.arcsec # remove the one arcsec so it's on disk.
                th = np.linspace(-180*u.deg, 0*u.deg)
                x = r * np.sin(th)
                y = r * np.cos(th)
                coords = SkyCoord(x, y, frame=AIAmap[AIAmap.keys()[0]].coordinate_frame)

                hgs = coords.transform_to('heliographic_stonyhurst')
                hgs.D0 = m.dsun
                hgs.L0 = m.heliographic_longitude
                hgs.B0 = m.heliographic_latitude
                limbcoords = hgs.transform_to(pmap.coordinate_frame)
                ax.plot_coord(limbcoords, color='w') #this is not overplotting in the zoomed version! why not? do I have to do this before the map.plot command?
                
            if oplotpoint: #overplot source_loc_STEREO
                scs=self.Properties.source_pos_STEREO*u.arcsec
                sc=SkyCoord(scs[0],scs[1],frame=pmap.coordinate_frame)
                ax.plot_coord(sc, color='r',marker='o',markersize=10) #might need to make it bigger
                #ax.plot([self.Properties.source_pos_STEREO[0]],[self.Properties.source_pos_STEREO[1]],marker='o',markersize=10,color='red',projection=p)
                print self.Properties.source_pos_STEREO

            #pmap.plot(axes=ax)

            fig.show()
            
        fname=self.Files.dir+self.Files.folders['plots']+'/'+dt.strftime(self.Datetimes.Messenger_peak.date(),'%Y%m%d')+'EUVI_'
        if save:
            tag=raw_input('Identifying tag? ')
            fig.savefig(fname+tag+'.png')

