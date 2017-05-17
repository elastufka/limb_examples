 #######################################
# OCDatetimes.py
# Erica Lastufka 17/5/17 

#Description: Class of functions to deal with all datetimes for one flare
#######################################

import numpy as np
import os
import glob
import pickle
from datetime import datetime as dt
import re

class OCDatetimes(object):
    ''' Data for this object will have the following attributes:
            Messenger Peak
            Rhessi peak
            Obs_start_time
            Obs_end_time
            Spec_start_time
            Spec_end_time
            lc_start_time
            lc_end_time
            pf_loop_time
         Methods are:
            format_datetimes() to format for reading from/exporting to csv/sav
            extend_time_int() does the time interval extensions
            '''
    def __init__(self, ID,legacy=True,filename=False):
        '''Initialize the object, given the flare ID. This requires use of the OCFiles object I think...'''
        if legacy: #get info from legacy OCData object and the associated csv/sav files
            if not filename:
                filename= '/Users/wheatley/Documents/Solar/occulted_flares/flare_lists/list_final.csv'#default file to read
            import pandas as pd
            data=pd.read_csv(filename,sep=',', header=0) #column 0 will be NaN because it's text
            i=self.get_index(ID,data) #get the index of the flare if it's in a list
            self.Messenger_peak=data["Messenger_datetimes"][i]
            self.RHESSI_peak=data["RHESSI_datetimes"][i]
            self.Obs_start_time=data["Obs_start_time"][i]
            self.Obs_end_time=data["Obs_end_time"][i]
            try:
                self.Spec_start_time=data["Spec_start_time"][i]
            except KeyError:
                self.Spec_start_time=self.Obs_start_time #actually should modify this to do whatever time extension the code did
            try:
                self.Spec_end_time=data["Spec_end_time"][i]
            except KeyError:
                self.Spec_end_time=self.Obs_end_time
            try:                
                self.lc_start_time=data["lc_start_time"][i]
            except KeyError:
                self.lc_start_time=self.Obs_start_time
            try:                               
                self.lc_end_time=data["lc_end_time"][i]
            except KeyError:
                self.lc_end_time=self.Obs_end_time
            try:                
                self.pf_loop_time=data["pf_loop_time"][i]
            except KeyError:
                self.pf_loop_time=self.Obs_start_time
 
        if not legacy:
            #read datetimes csv file (can just restore the pickle file otherwise. Build this into OCFlare class):
            if not filename:
                filename= '/Users/wheatley/Documents/Solar/occulted_flares/flare_lists/OCDatetimes.csv'#default file to read
            import pandas as pd
            data=pd.read_csv(filename,sep=',', header=0) #column 0 will be NaN because it's text
            i=self.get_index(ID,data) #get the index of the flare if it's in a list
            self.Messenger_peak=data["Messenger_peak"][i]
            self.RHESSI_peak=data["RHESSI_peak"][i]
            self.Obs_start_time=data["Obs_start_time"][i]
            self.Obs_end_time=data["Obs_end_time"][i]
            self.Spec_start_time=data["Spec_start_time"][i]
            self.Spec_end_time=data["Spec_end_time"][i]
            self.lc_start_time=data["lc_start_time"][i]
            self.lc_end_time=data["lc_end_time"][i]
            self.pf_loop_time=data["pf_loop_time"][i]

        self.convert2datetime()
        #update the OCFiles object with the file used to generate this instance of the object
        
    def __iter__(self):
        '''Returns a generator that iterates over the object - not sure if it's needed here but whatever'''
        for attr, value in self.__dict__.iteritems():
            yield attr, value

    def write(self, picklename=False):
        '''Write object to pickle'''
        import pickle
        if not picklename:
            picklename=str(self.ID)+'OCDatetimes.p'
        pickle.dump(self, open(picklename, 'wb'))

    def get_index(self,ID,data):
        '''Write object to pickle'''
        i= np.where(ID == data['ID'])
        return i[0][0]
    
    def convert2datetime(self):
        '''If it's a string make it a datetime'''
        for a in dir(self):
            if not a.startswith('__') and not callable(getattr(self,a)) and type(getattr(self,a)) == str:
                val=getattr(self,a)
                #print a,val
                if val == '':
                    fc=''
                elif ('AM' or 'PM') in val:
                    fc = '%m/%d/%y %I:%M:%S %p'
                elif '/' in val:
                    fc = '%m/%d/%y %H:%M:%S.00'
                elif re.search('[a-z]', val) is not None: #not None if there is a letter
                    fc ='%d-%b-%Y %H:%M:%S' #current format code - might need to add .000
                else: #it's come straight from idl ....
                    fc ='%Y-%m-%d %H:%M:%S'
                if fc != '':
                    if val.startswith("'"):
                        try:
                            setattr(self,a,dt.strptime(val[1:-1], fc))
                        except ValueError:
                            fc=fc ='%d-%b-%Y %H:%M:%S.000'
                            setattr(self,a,dt.strptime(val[1:-1], fc))
                    else:
                        try:
                            setattr(self,a,dt.strptime(val, fc))
                        except ValueError:
                            fc=fc ='%d-%b-%Y %H:%M:%S.000'
                            setattr(self,a,dt.strptime(val, fc))

    def convert2string(self):
        '''If it's a datetime make it a string'''
        for a in dir(self):
            if not a.startswith('__') and not callable(getattr(self,a)) and type(getattr(self,a)) == dt:
                val=getattr(self,a)
                fc='%d-%b-%Y %H:%M:%S.000'
                setattr(self,a,dt.strftime(val,fc))
