 #######################################
# OC.Flarepy
# Erica Lastufka 17/5/17 

#Description: Class of functions to deal with all data,files,calculations of the study
#######################################

import numpy as np
import OCDatetimes as ocd
import OCFiles as ocf
import OCProperties as ocp
import OCObservation as oco
import OCCalc as occ

class OCFlare(object):
    ''' Object will have the following attributes:
            ID: RHESSI flare ID or generated ID
            Datetimes: OCDatetimes object (might inherit from OCData object)
            Files: OCFiles object that contains all information about file names and locations
            Data: OCData object (different from original) that contains methods for loading/accessing the data ->tag this onto Files?
            Properties: OCProperties object that contains all information about the flare itself
            Observation:OCObservation object that contains all information about the observations
            Calculations:OCCalc object that contains methods for and attributes of calculations
            Notes
        Methods will include:
            Method for translating between pickle, .sav and .csv
     '''
    def __init__(self, ID, legacy=True):
        '''Initialize the flare object from an ID, pickle files in given folder, or legacy .csv or .sav'''
        self.ID=ID
        #first see if we can just restore the objects from pickles...
        pickles=sorted(glob.glob(str(ID)+'*.p')):
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
                if p.endswith('OCCalc.p'):
                    self.CCalc=pickle.load(open(p,'rb'))
                else:
                    self.CCalcDatetime=occ.OCCalc(ID,legacy=legacy)
                               
        else:
            self.Datetimes=ocd.OCDatetimes(ID,legacy=legacy)
            self.Properties=ocp.OCProperties(ID,legacy=legacy)
            self.Files=ocf.OCFiles(ID,legacy=legacy)
            self.Observation=oco.OCObservation(ID,legacy=legacy)
            self.Calc=occ.OCCalc(ID,legacy=legacy)
            self.Notes= [""]
        
                
    def __iter__(self):
        '''Returns a generator that iterates over the object'''
        for attr, value in self.__dict__.iteritems():
            yield attr, value
                    
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

    def export2pickle(self, picklename):
        '''Replaces save_flare_list. Saves the data object in a .p file'''
        import pickle
        pickle.dump(self, open(picklename, 'wb'))


