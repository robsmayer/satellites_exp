# satellites_exp
Getting satellite exp

[link to documentation (https://rhodesmill.org/skyfield/toc.html)]

### TODO
continue attenuation thing :)

## Loading a Satellite

'''
from skyfield.api import EarthSatellite, load
from datetime import datetime

ts = load.timescale()
line1 = '1 01520U 65065H   24004.88423715  .00000109  00000+0  19149-3 0  9994'
line2 = '2 01520  89.9593 128.8254 0070679 106.6182  14.1898 13.36021334843288'
satellite = EarthSatellite(line1, line2, 'Calisto', ts)
print(satellite)
'''

## Loading many

'''
active_stations_url = 'http://celestrak.org/NORAD/elements/stations.txt'
satellites = load.tle_file(active_stations_url)
print('Loaded', len(satellites), 'satellites')
'''

## Time 

Make global time = load.timescale

then after use 
t = time.now()
