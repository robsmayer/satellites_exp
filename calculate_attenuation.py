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

SAT_ALT = 35786 * u.km

# Satellite in realtime 

# Link parameters
f = 22.5 * u.GHz    # Link frequency
D = 1.2 * u.m       # Antenna diameters


# Define unavailabilities vector <- NO IDEA WHAT THIS IS 
unavailabilities = np.logspace(-1.5, 1.5, 100)



# Someting is wrong - fixing it 



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

    t_lat = lat.dms()
    r_lat = t_lat[0] + (t_lat[1] * 0.01)
    t_lon = lon.dms()
    r_lon = t_lon[0] + (t_lat[1]* 0.01)

    return float(r_lat), float(r_lon)

def attenuate(el):
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

def start(satellite):
    try:
        while (True):
            lat, lon = get_lat_lon(satellite)

            el = itur.utils.elevation_angle(SAT_ALT, lat, lon, GROUND_LATITUDE, GROUND_LONGITUDE)
            print(el)
            attenuate(el)
            time.sleep(5)
    except KeyboardInterrupt:
         pass


if __name__=="__main__":
    satellite = load_sat()
    start(satellite)
