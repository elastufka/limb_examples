 #######################################
# flare_class.py
# Erica Lastufka 17/5/17 

#Description: Class of functions to deal with all plotting. This should be optionally initialized, after an entire group of flares is created in the object
#######################################

import numpy as np

class OCPlots(object):
    ''' Data for this object will have the following attributes:
            plot params 
        Methods:
            all the plotting methods I've written for this study
    '''

    def __init__(self, ID,legacy=True,filename=False):
        '''Initialize the object, given the flare ID. This requires use of the OCFiles object I think...'''
        if legacy: #get info from legacy OCData object and the associated csv/sav files
            if not filename:
                filename= '/Users/wheatley/Documents/Solar/occulted_flares/flare_lists/list_final.csv'#default file to read
            import pandas as pd
            data=pd.read_csv(filename,sep=',', header=0) #column 0 will be NaN because it's text
            i=self.get_index(ID,data) #get the index of the flare if it's in a list
            self.dir='/Users/wheatley/Documents/Solar/occulted_flares/' #top level directory
            self.folders=glob.glob() #all the subfolders
            self.Raw={'xrs_files':data["xrs_files"][i]}
            self.Lists={data["RHESSI_datetimes"][i]}
            self.Plots={data["Obs_start_time"][i]}
            self.Notes= '' #if I need to write a note about this iteration
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
                filename= '/Users/wheatley/Documents/Solar/occulted_flares/flare_lists/OCFiles.csv'#default file to read
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
 

