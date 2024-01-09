# mix of loading sat with attenuation calculations
# Realtime + this

''' I think I should convert the info to astropy units'''
from skyfield.api import EarthSatellite, load, Distance, N,S,E,W
from datetime import datetime
from skyfield.api import wgs84 # Important to get latitute longitude (separately)
import time
from geopy.distance import lonlat, distance
from numpy import array2string
from astropy import units as u

time_sat = load.timescale()

# Dortmund latitude and longitude as basecenter for antena
dor_latitude = 51.514244
dor_longitude = 7.468429
dor_altitude = 86.0

# Sat frequency that I dont know how to get (yet)
# todo

def load_sat():
    
    line1 = '1 07646U 75010A   24004.89665482 -.00000138  00000+0  43355-5 0  9991'
    line2 = '2 07646  49.8254  34.4701 0205786 348.7382  10.8944 13.82323348470834'
    satellite = EarthSatellite(line1, line2, 'STARLETTE', time_sat)
    
    return satellite

  
def get_info(satellite):
    try:
        t = time_sat.now()
        # Get pos of satellite
        geocentric = satellite.at(t)
        print('STARLETTE' , geocentric.position.km)
        lat, lon = wgs84.latlon_of(geocentric)
        print('Latitude:', lat)
        print('Longitude:', lon)
        
        # Comparing to Dortmund 51.514244, 7.468429
        # Get geographic position (this would be - could be the drone)

        # lat lon elevation
        print("Related to Dortmund")


        # Getting values for calculation 
        dort_pos = (dor_longitude, dor_latitude)
        #sat_pos = (lon,lat)

        get_H_coord(satellite)
        get_range_rate(satellite)
        
        

    except Exception as e:
        print("Error", e)

def get_range_rate(satellite):
    # If you’re interested in the Doppler shift of the radio signal 
    # from a satellite, you’ll want to know the rate at which the 
    # satellite’s range to your antenna is changing.
    try:
        t = time_sat.now()
        
        dortmund = wgs84.latlon(dor_latitude, dor_longitude, dor_altitude)
        # difference  = satellite - dortmund
        pos = (satellite - dortmund).at(t)
        
        # Finding range rate - I think it's important
        # Range rate refers to the rate at which the distance 
        # between two points or objects is changing with respect to time.
        _, _, the_range, _, _, range_rate = pos.frame_latlon_and_rates(dortmund)

        print("Range ", array2string(the_range.km, precision=1), 'km')
        print("Range rate",array2string(range_rate.km_per_s, precision=2), 'km/s')

    except Exception as e:
        print("Error getting range rate ", e)

# Horizontal coordinate system
def get_H_coord(satellite):
    try:
        # Satellite altitude, azimuth, and distance
        # Find if sat bellow or above the horizont from position of observer
        t = time_sat.now()

        dortmund = wgs84.latlon(dor_latitude*N, dor_longitude * W, elevation_m= dor_altitude)
        difference = satellite - dortmund

        # I dont know what is topocentric but
        topocentric = difference.at(t)
        print(topocentric.position.km)

        alt, az, distance = topocentric.altaz()

        if alt.degrees > 0:
            print("SAT is above horizon")
        
        print("Altitude:",alt)
        print("Azimuth:", az)
        print("Distance {:.1f} km".format(distance.km))

    except Exception as e:
        print("Error getting horizontal coordinates", e)
        

def main(satellite):
    try:
        while(True):
            get_info(satellite)
            time.sleep(10)

    
    except KeyboardInterrupt:
        pass



if __name__ == "__main__":
    
    satellite = load_sat()
    '''get_pos(satellite)'''
    main(satellite)
    