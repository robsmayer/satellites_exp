# mix of loading sat with attenuation calculations
# Realtime + this

''' I think I should convert the info to astropy units'''
from skyfield.api import EarthSatellite, load, Distance, N,S,E,W, Topos
from skyfield.framelib import itrs
from astropy.coordinates import ICRS
from datetime import datetime
from skyfield.api import wgs84, Topos # Important to get latitute longitude (separately)
import time
from geopy.distance import lonlat, distance
import numpy as np 
from numpy import array2string
from astropy import units as u
from astropy.coordinates import TEME, CartesianDifferential, CartesianRepresentation, ITRS





time_sat = load.timescale()

# Defined with caps because they are constant (in this case)
# Choose Dortmund as observer latitude and longitude as basecenter for antena
# Observer is also like ground base 
OBSERVER_LAT = 51.514244
OBSERVER_LON = 7.468429
OBSERVER_ALT = 86.0


# Sat frequency global var (should it be global?)
frequency = 5000 


def load_sat(): # Be careful with the epoch thing - it means when it's most accurate
    # so if I want a better one, I need to search it - but that's a problem for later...
    
    line1 = '1 07646U 75010A   24004.89665482 -.00000138  00000+0  43355-5 0  9991'
    line2 = '2 07646  49.8254  34.4701 0205786 348.7382  10.8944 13.82323348470834'
    satellite = EarthSatellite(line1, line2, 'STARLETTE', time_sat)
    
    return satellite

  
def get_geocentric(satellite):
    try:
        t = time_sat.now()
        # Get pos of satellite
        geocentric = satellite.at(t) #this is TEME
        # geocentric is also barycentric
        print('STARLETTE' , geocentric.position.km) 
        lat, lon = wgs84.latlon_of(geocentric)
        print('Latitude:', lat)
        print('Longitude:', lon)
        
        
        # Comparing to Dortmund 51.514244, 7.468429
        # Get geographic position (this would be - could be the drone)
        
        # lat lon elevation
        #print("Trying to convert to astropy units")
        #units that I can work with

        #barycentric = geocentric.to_skycoord()
        #print(barycentric)
        
        to_TEME(satellite)
        #get_coordenates(satellite)
        
        #get_coordenates(satellite)

        #get_H_coord(satellite)
        #get_range_rate(satellite)
        
        

    except Exception as e:
        print("Error", e)

# Geo
def to_TEME(satellite):
    t = time_sat.now()
    # Every conversison is related to an observer, so if I want
    # to get the astropy values, I need to convert the units IDK
    
    observer_location = wgs84.latlon(OBSERVER_LAT,OBSERVER_LON, OBSERVER_ALT)
    satellite_pos = satellite.at(t)
    lat, lon = wgs84.latlon_of(satellite_pos)
    difference = satellite_pos - observer_location
    topocentric = difference.at(t)
    #subpoint = wgs84.geographic_position_of(satellite_pos)
   # print(subpoint.position.km)
    print(topocentric.position.km)
    

    
# Horizontal coordinate system (Trying to get satellite coordinates)
def get_coordenates(satellite):
    try:
        # Satellite altitude, azimuth, and distance
        # Find if sat bellow or above the horizont from position of observer
        t = time_sat.now()
        print("\n Get coordenates method \n")
        dortmund = wgs84.latlon(OBSERVER_LAT*N, OBSERVER_LON * W, elevation_m= OBSERVER_ALT)
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

        # Use format to get this thing 
        # gives number number print(alt.degrees)
        return topocentric
    
    except Exception as e:
        print("Error getting horizontal coordinates", e)

# who is position agent? 
        
''' Before this I need to discover who is positional agent 
def calculateFreeSpace(cell_elevation, satellite):
        
        position_basestation = wgs84.latlon(dor_latitude*N, dor_longitude * W, elevation_m= dor_altitude)
        # Would be someething + drone ? cell_altitude = 25 + cell_elevation 
        flat_distance = geopy.distance.distance(position_agent[:2], position_basestation[:2]).m
        dist3d = math.sqrt(math.pow(flat_distance, 2) + math.pow(cell_altitude- position_agent.altitude*1000, 2))
        #euclidian_distance = math.sqrt(flat_distance**2 + (position_basestation[2] - position_agent[2])**2)
        preferred_frequency = frequency
        print(f"{dist3d=}")
        print(f"{preferred_frequency=}")
        loss = 20*math.log10(dist3d/1000)+20*math.log10(preferred_frequency/1000)+92.44
        subcarrier_fix = 10*math.log10(12*(20/0.2))
        rsrp = (40-loss) - subcarrier_fix
        print(f"{loss=}")
        print(f"{rsrp=}")
        return {"rsrp": rsrp,"buildings": "", "elevation": ""} # Compute actual RSRP


'''

def start(satellite):
    try:
        while(True):
            get_geocentric(satellite)
            time.sleep(10)

    
    except KeyboardInterrupt:
        pass



if __name__ == "__main__":
    
    satellite = load_sat()
    '''get_pos(satellite)'''
    start(satellite)
    