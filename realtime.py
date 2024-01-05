from skyfield.api import EarthSatellite, load
from datetime import datetime
from skyfield.api import wgs84 # Important to get latitute longitude (separately)
import time

time_sat = load.timescale()

def load_sat():
    
    line1 = '1 07646U 75010A   24004.89665482 -.00000138  00000+0  43355-5 0  9991'
    line2 = '2 07646  49.8254  34.4701 0205786 348.7382  10.8944 13.82323348470834'
    satellite = EarthSatellite(line1, line2, 'STARLETTE', time_sat)
    
    return satellite

def get_info(satellite):
    t = time_sat.now()
    # Get pos 
    geocentric = satellite.at(t)
    print('STARLETTE' , geocentric.position.km)
    lat, lon = wgs84.latlon_of(geocentric)
    print('Latitude:', lat)
    print('Longitude:', lon)

def main(satellite):
    try:
        while(True):
            get_info(satellite)
            time.sleep(5)

    
    except KeyboardInterrupt:
        pass



if __name__ == "__main__":
    
    satellite = load_sat()
    '''get_pos(satellite)'''
    main(satellite)
    