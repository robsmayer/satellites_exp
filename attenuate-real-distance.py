'''
    Copy of calculate_attenuation with real distance.
'''

from skyfield.api import EarthSatellite, load, Distance, N,S,E,W, Topos
from skyfield.api import wgs84, Topos # Important to get latitute longitude (separately)
import time
import itur
import astropy.units as u
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter

# Global var time function
time_scale = load.timescale()

# Defined with caps because they are constant (in this case)
# Choose Dortmund as Ground Station - will be the drone
 
# IF ground will be the drone these things wont be global

GROUND_LATITUDE = 51.514244
GROUND_LONGITUDE = 7.468429
GROUND_ALTITUDE = 86.0

SAT_ALT = 35786 * u.km # Altitude or distance ?

# Satellite in realtime 

# Link parameters
f = 22.5 * u.GHz    # Link frequency
D = 1.2 * u.m       # Antenna diameters


# Define unavailabilities vector <- NO IDEA WHAT THIS IS 
unavailabilities = np.logspace(-1.5, 1.5, 100)


def load_sat(): # Be careful with the epoch thing - it means when it's most accurate
    # so if I want a better one, I need to search it - but that's a problem for later...
    
    line1 = '1 23839U 96020A   24020.91299453 -.00000053  00000+0  00000+0 0  9999'
    line2 = '2 23839   8.7526  54.0465 0004650 224.8333 246.4567  0.99975482101479'
    satellite = EarthSatellite(line1, line2, 'INMARSAT 3-F1', time_scale)
    
    return satellite

def get_lat_lon(satellite):
    t = time_scale.now()

    # return an (x,y,z) position relative to the Earth’s center in the Geocentric Celestial Reference System. 
    geocentric = satellite.at(t)
    
    print('INMARSAT ', geocentric.position.km) # is this TEME ?
    lat,lon = wgs84.latlon_of(geocentric)
    print('  - Latitude:', lat)
    print('  - Longitude:', lon)

    # I think the problem in the attenuation thing in this case is
    # type of the variable: because in the documentation
    # function x needs float not np.float64 - like it is

    
    t_lat = lat.dms() # t_lat is a copnverts lat touple  with (deg,','')
    
    lat_npfloat = t_lat[0] # If I want a precisse number I need to sum the seconds too
    float_lat = lat_npfloat.item() # transforms the np float to float
    
    
    t_lon = lon.dms() # Touple for longitude same stuff
    float_lon = t_lon[0].item() # Made it shorter .,,
    if(float_lat == -0):
        float_lat = 0.0    
    
    if(float_lon == -0): # I don't know if it's important but some results were 
        float_lon = 0.0  # -0 and -0 could be a problem ?

    print('sent longitude = ',type(float_lon) , float_lon) 
    print('sent latitude = ' ,type(float_lat) , float_lat)

    return float_lat, float_lon

def getHeight(satellite):
    try:
        t = time_scale.now()
        ground_station = wgs84.latlon(GROUND_LATITUDE,GROUND_LONGITUDE,GROUND_ALTITUDE)
        
        difference = satellite - ground_station # Study what does this means

        topocentric = difference.at(t)

        alt,az,distance = topocentric.altaz()

        if alt.degrees > 0:
            print("Sat is above the horizon")
        
        
        print('  - Altitude:', alt)
        print('  - Azimuth:', az)
        print('  - Distance: {:.1f} km'.format(distance.km)) # That is the most important
    
        d_altitude = alt.degrees

        alt_float = (d_altitude).item()
        
        d_km = distance.km # distance magnitude in km
        d_float = d_km.item() # converted to float 
        
        height = np.sin(np.deg2rad(alt_float)) * d_float # this is supossedly the height
        # following h = sin(alt) * distance
    
        return height

    except Exception as e:
        print("ERROR get height: ",e)



def start(satellite):
    
    lat, lon = get_lat_lon(satellite)
    sat_height = getHeight(satellite)
    # Compute the elevation angle between satellite and ground station
    el = itur.utils.elevation_angle(sat_height, lat, lon, GROUND_LATITUDE, GROUND_LONGITUDE)

        # Define unavailabilities vector
    unavailabilities = np.logspace(-1.5, 1.5, 100)

    # Compute the
    A_g, A_c, A_r, A_s, A_t = [], [], [], [], []
    for p in unavailabilities:
            a_g, a_c, a_r, a_s, a_t = itur.atmospheric_attenuation_slant_path(GROUND_LATITUDE, GROUND_LONGITUDE,
                                                                            f, el, p, D,
                                                                            return_contributions=True)
            A_g.append(a_g.value)
            A_c.append(a_c.value)
            A_r.append(a_r.value)
            A_s.append(a_s.value)
            A_t.append(a_t.value)

    # Plot the results
    ax = plt.subplot(1,1,1)
    ax.semilogx(unavailabilities, A_g, label='Gaseous attenuation')
    ax.semilogx(unavailabilities, A_c, label='Cloud attenuation')
    ax.semilogx(unavailabilities, A_r, label='Rain attenuation')
    ax.semilogx(unavailabilities, A_s, label='Scintillation attenuation')
    ax.semilogx(unavailabilities, A_t, label='Total atmospheric attenuation')

    ax.xaxis.set_major_formatter(ScalarFormatter())
    ax.set_xlabel('Percentage of time attenuation value is exceeded [%]')
    ax.set_ylabel('Attenuation [dB]')
    ax.grid(which='both', linestyle=':')

    plt.legend()
    plt.show()
    
if __name__=="__main__":
    satellite = load_sat()
    start(satellite)
