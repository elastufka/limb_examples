 #######################################
# limb_example.py
# Erica Lastufka 27/6/17 

#Description: Example of overplotting the limb using Sunpy coordinate transformations.
#######################################

import numpy as np
import sunpy.map
import matplotlib.pyplot as plt
import astropy.units as u
from astropy.coordinates import SkyCoord

aiamap= sunpy.map.Map('data/stereo-aia/aia_lev1.193A_2013_04_27T10_49_54.84Z.image_lev1.fits')
AIAmap={aiamap.instrument: aiamap.submap((-1100, 1100) * u.arcsec, (-1100, 1100) * u.arcsec)}

euvmap= sunpy.map.Map('data/stereo-aia/20130427_105530_n4eua.fts')
EUVmap={euvmap.instrument: euvmap.submap((-1100, 1100) * u.arcsec, (-1100, 1100) * u.arcsec)}

m=EUVmap['SECCHI']

#current_map_time=m.date

fig = plt.figure(figsize=(len(maps)*3, 5))
ax = fig.add_subplot(1, 1, 1, projection=m)
m.plot(axes=ax)
                
ax.set_autoscale_on(False)
r = AIAmap[AIAmap.keys()[0]].rsun_obs.to(u.deg)-1*u.arcsec # remove the one arcsec so it's on disk.
th = np.linspace(-360*u.deg, -180*u.deg) #x<0
                    
x = r * np.sin(th)
y = r * np.cos(th)
coords = SkyCoord(x, y, frame=AIAmap[AIAmap.keys()[0]].coordinate_frame)

hgs = coords.transform_to('heliographic_stonyhurst')
hgs.D0 = m.dsun
hgs.L0 = m.heliographic_longitude-1*u.arcsec # put back the 1 arcsec                    
hgs.B0 = m.heliographic_latitude
limbcoords = hgs.transform_to(m.coordinate_frame)
ax.plot_coord(limbcoords, color='w') 

fig.show()
            
