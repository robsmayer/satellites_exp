# mix of loading sat with attenuation calculations
# Realtime + this

''' I think I should convert the info to astropy units'''
from skyfield.api import EarthSatellite, load
from datetime import datetime
from skyfield.api import wgs84 # Important to get latitute longitude (separately)
import time

from numpy import array2string

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
        dortmund = wgs84.latlon(dor_latitude, dor_longitude, dor_altitude)
        # difference  = satellite - dortmund
        pos = (satellite - dortmund).at(t)
        
        # Finding range rate - I think it's important
        # Range rate refers to the rate at which the distance 
        # between two points or objects is changing with respect to time.
        _, _, the_range, _, _, range_rate = pos.frame_latlon_and_rates(dortmund)

        print(array2string(the_range.km, precision=1), 'km')
        print(array2string(range_rate.km_per_s, precision=2), 'km/s')

        # Getting values for calculation 

        sat_latitude = lat.degrees
        sat_longitude = lon.degrees # maybe depending if > 180 I need to subtract to get the real negative value
        sat_height = wgs84.height_of(geocentric)
        
        

    except Exception as e:
        print("Error", e)


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
    