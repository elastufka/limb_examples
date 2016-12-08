 #######################################
# messenger_goes_class.py
# Erica Lastufka 30/11/2016  

#Description: Determine GOES class of messenger flare
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
import csv
import scipy.constants as sc
import messenger_angles as ma


def messenger_goes_class_take1():
    #in idl:
    goes_fluxes,30,1,flong,fshort,sat=15  
    print,goes_value2class(flong)  
