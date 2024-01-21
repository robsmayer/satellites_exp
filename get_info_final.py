from skyfield.api import EarthSatellite, load, Distance, N,S,E,W, Topos
from skyfield.api import wgs84, Topos # Important to get latitute longitude (separately)
import time

# Cleaner version of calculate

# Global var time function
time_scale = load.timescale()

# Defined with caps because they are constant (in this case)
# Choose Dortmund as observer latitude and longitude as basecenter for antena
# Observer is also like ground base 
OBSERVER_LATITUDE = 51.514244
OBSERVER_LONGITUDE = 7.468429
OBSERVER_ALTITUDE = 86.0

# Should satellite be a class ? < IDEA
# I could also send observer as parameter ?
# Load from TLE string 
def load_sat(): # Be careful with the epoch thing - it means when it's most accurate
    # so if I want a better one, I need to search it - but that's a problem for later...
    
    line1 = '1 23839U 96020A   24020.91299453 -.00000053  00000+0  00000+0 0  9999'
    line2 = '2 23839   8.7526  54.0465 0004650 224.8333 246.4567  0.99975482101479'
    satellite = EarthSatellite(line1, line2, 'INMARSAT 3-F1', time_scale)
    
    return satellite

def get_info(satellite):
    try:
        t = time_scale.now() # IDK what is a timescale will search later
        
        # Getting geocentric position of sat
        geocentric = satellite.at(t)

        print('INMARSAT ', geocentric.position.km) # is this TEME ?
        lat,lon = wgs84.latlon_of(geocentric)
        print('  - Latitude:', lat)
        print('  - Longitude:', lon)
        #print()

        relative_pos_xyz(satellite)
        #print()
        relativ_pos_altitude_azimuth(satellite)
        print()

    except Exception as e:
        print("Error in get info: ", e)

#  “where will the satellite be relative to my location?”
# Getting relative position (x,y,z)

def relative_pos_xyz(satellite):
    try:
        t = time_scale.now()
        observer = wgs84.latlon(OBSERVER_LATITUDE, OBSERVER_LONGITUDE, OBSERVER_ALTITUDE)
        
        difference = satellite - observer # Vector subtraction
        print("Relative position x,y,z")
        topocentric = difference.at(t)
        print('  - ',topocentric.position.km)
    except Exception as e:
        print("Error relative_xyz:", e)


# Same situation topocentric position for its altitude and azimuth
# A negative altitude means the satellite is that many degrees below the horizon.

def relativ_pos_altitude_azimuth(satellite):
    try:
        print("Relative position - Altitude Azimuth method")
        t = time_scale.now()

        observer = wgs84.latlon(OBSERVER_LATITUDE, OBSERVER_LONGITUDE, OBSERVER_ALTITUDE)
        difference = satellite - observer # so this is a vector ?

        topocentric = difference.at(t)

        alt,az, distance = topocentric.altaz()

        if alt.degrees > 0:
            print('The ISS is above the horizon')

        print('  - Altitude:', alt)
        print('  - Azimuth:', az)
        print('  - Distance: {:.1f} km'.format(distance.km)) # That is the most important
    except Exception as e:
        print("Error altitude azimuth ", e)

def start(satellite):
    try:
        while(True):
            get_info(satellite)
            time.sleep(10)
    except KeyboardInterrupt:
        pass

if __name__=="__main__":
    satellite = load_sat()
    start(satellite)