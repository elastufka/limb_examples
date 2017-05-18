 #######################################
# flare_class.py
# Erica Lastufka 17/5/17 

#Description: Class of functions to deal with all data,files,calculations of the study. Maybe merge this with calculations since they are so interrelated
#######################################

import numpy as np

class OCProperties(object):
    ''' Object will have the following attributes:
            T1: 
            EM1:
            T2: 
            EM2: 
            chisq: chisq value from ospex fit
            GOES_GOES: GOES flux 
            Messenger_GOES: Same for Messenger
            source_vis:
            source_pos:
            source_pos_STEREO: 
            f1pos: in case this is different than what is used in the loops?
            f2pos:  
            loop: dictionary of loop data
            Rheight: Calculated rhessi height above limb
            occ_percent: occultation percentage
            ratio: GOES ratio
            e1: empty field for addition later (in case I can't figure out how to make this dynamic)
            e2
            e3
            e4
            e5
            e6
            e7
            e8
            e8
            e10
            Notes
        Methods are:
            all the calculation methods...'''
    
    def __init__(self, ID, legacy=True, calc_missing=True):
        '''Return an empty Data_Study object, unless a filename to a correctly formatted csv is given. Do I need to be able to go from a dictionary to an object too?'''
        tags=['CLEAN','Rcountrate','Mcountrate','Rpflux','Mpflux','Rebins','Mebins','Swave','Slos','AIAwave']
        if legacy: #get info from legacy OCData object and the associated csv/sav files
            if not filename:
                filename= '/Users/wheatley/Documents/Solar/occulted_flares/flare_lists/list_final.csv'#default file to read
            import pandas as pd
            data=pd.read_csv(filename,sep=',', header=0) #column 0 will be NaN because it's text
            i=self.get_index(ID,data) #get the index of the flare if it's in a list
            self.Angle=data["Angle"][i]
            self.Det=data[""][i]
            self.STEREO=data["Notes"][i]
            self.CLEAN=data[""][i]
            for att,key in zip(tags,tags):
                self.setattr(att,'')
 
        if not legacy:
            #read attributes from csv file (can just restore the pickle file otherwise. Build this into OCFlare class):
            if not filename:
                filename= '/Users/wheatley/Documents/Solar/occulted_flares/flare_lists/'+str(ID)+'OCProperties.csv'#default file to read - need an except in case it doesn't exist
            import pandas as pd
            data=pd.read_csv(filename,sep=',', header=0) #column 0 will be NaN because it's text
            i=self.get_index(ID,data) #get the index of the flare if it's in a list
            for att,key in zip(tags,tags):
                self.setattr(att,data[key])

        #set some defaults
        if self.Rebins == '': self.Rebins=[[],[],[],[],[],[]]
        if self.Mebins == '': self.Mebins=[[],[]]
        if self.Swave == '': self.Swave=193
        if self.AIAwave == '': self.AIAwave=[171,193,304]

        self.Notes=''

    def get_index(self,ID,data):
        '''Get index of flare in flare list file'''
        i= np.where(ID == data['ID'])
        return i[0][0]
    
    def write(self, picklename=False):
        '''Write object to pickle'''
        import pickle
        if not picklename:
            picklename=str(self.ID)+'OCProperties.p'
        pickle.dump(self, open(picklename, 'wb'))

    def write_csv(self, csvname=False):
        if not csvname: csvname= str(ID) + 'OCProperties.csv'
        d=self.__dict__
        with open(csvname,'wb') as f:
            w=csv.writer(f)
            w.writerow(d.keys())
            w.writerow(d.values())

    def get_T_EM(self): #work together with the files object to read in both values? Or should all the file-bound values be re-distributed once the Files object is initiated?
