'''
    Considering Initial freuqncy of INMARSAT 1600

    1600 MHz

    If I sum all vals of the graph is it the real value of thing - idk 
    I want to sum and get the value quantified of attenuation
    

    All INMARSAT antennas operate with right-hand circular polarization. 
    The uplink frequency band is 1626.5 - 1660.5 MHz and the downlink frequency band is 1525.0 - 1559.0 MHz.
'''

from skyfield.api import EarthSatellite, load, Distance, N,S,E,W, wgs84, Topos
import itur
import astropy.units as u
import numpy as np 
import matplotlib.pyplot as plt
from scipy.constants import c
from matplotlib.ticker import ScalarFormatter
import os
from datetime import datetime

# Global var time function
time_scale = load.timescale()

# Defined with caps because they are constant (in this case)
# Choose Dortmund as Ground Station - will be the drone
 
# IF ground will be the drone these things wont be global

GROUND_LATITUDE = 51.514244
GROUND_LONGITUDE = 7.468429
GROUND_ALTITUDE = 86.0

FILE_NAME = "results_attenuate_frequency.txt"


# Satellite in realtime 
# No need for SAT_ALT = 35786 * u.km # Altitude or distance 

# Link parameters
f = 22.5 * u.GHz    # Link frequency
D = 1.2 * u.m       # Antenna diameters


# Define unavailabilities vector <- NO IDEA WHAT THIS IS 
unavailabilities = np.logspace(-1.5, 1.5, 100)


def load_sat(): # Be careful with the epoch thing - it means when it's most accurate
    # so if I want a better one, I need to search it - but that's a problem for later...
    
    line1 = '1 23839U 96020A   24049.61641156  .00000123  00000+0  00000+0 0  9995'
    line2 = '2 23839   8.8135  53.8221 0003720 264.9195  97.6922  0.9998217110176'
    satellite = EarthSatellite(line1, line2, 'INMARSAT 3-F1', time_scale)
    
    return satellite

def get_lat_lon(satellite):
    t = time_scale.now()

    # return an (x,y,z) position relative to the Earth’s center in the Geocentric Celestial Reference System. 
    geocentric = satellite.at(t)
    
    print('INMARSAT ', geocentric.position.km) # is this TEME ?
    lat,lon = wgs84.latlon_of(geocentric)

    # Print and save results
    print('  - Latitude:', lat)
    print('  - Longitude:', lon)
    line = '\n\t- Latitude: ' + str(lat) + '\t- Longitude: ' + str(lon)
    save_data(line)
    # I think the problem in the attenuation thing in this case is
    # type of the variable: because in the documentation
    # function x needs float not np.float64 - like it is
    
    
    t_lat = lat.dms() # t_lat is a copnverts lat touple  with (deg,','')
    
    lat_npfloat = t_lat[0] # If I want a precisse number I need to sum the seconds too
    print("\n\tlat ", t_lat[0], " " , t_lat[1], " " , t_lat[2])
    float_lat = lat_npfloat.item() # transforms the np float to float
    
    
    t_lon = lon.dms() # Touple for longitude same stuff
    float_lon = t_lon[0].item() # Made it shorter .,,
    if(float_lat == -0):
        float_lat = 0.0    
    
    if(float_lon == -0): # I don't know if it's important but some results were 
        float_lon = 0.0  # -0 and -0 could be a problem ?

    line = "\n\t- Float Latitude: " + str(float_lat) + "\t- Float Longitude: " + str(float_lon)
    save_data(line)

    return float_lat, float_lon

def getFrequency(satellite):
    
    t = time_scale.now()

    ground_station = wgs84.latlon(GROUND_LATITUDE,GROUND_LONGITUDE,GROUND_ALTITUDE)
            
    difference = satellite - ground_station # Study what does this means

    topocentric = difference.at(t)

    _, _, the_range, _, _, range_rate = topocentric.frame_latlon_and_rates(ground_station)

    print(np.array2string(the_range.km,precision=1), "km")
    print(np.array2string(range_rate.km_per_s, precision=2), "km/s")

    # Calculating frequency
    speed_of_light = c
    frequency = np.divide(speed_of_light,the_range.m)
    line = "\n\t# Speed of light: " + str(c) + "\t# The range: " + str(the_range.m)
    print("speed of light " , c ,"# the range ", the_range.m)
    
    # Print and save results
    print(frequency, "Hz")
    line += "\n\t# Range Rate: " + str(range_rate.km_per_s) + "\t# Frequency: " + str(frequency)
    save_data(line)

    return frequency
    

def getHeight(satellite):
    try:
        t = time_scale.now()
        ground_station = wgs84.latlon(GROUND_LATITUDE,GROUND_LONGITUDE,GROUND_ALTITUDE)
        
        difference = satellite - ground_station # Study what does this means

        topocentric = difference.at(t)

        alt,az,distance = topocentric.altaz()

        if alt.degrees > 0:
            line = "\t Sat is above the horizon"
            save_data(line)
            print(line)
        else:
            print("  !!! Out of sight !!! ") # Idea to search for next available sat
        
        print('  - Altitude:', alt)
        print('  - Azimuth:', az)
        print('  - Distance: {:.1f} km'.format(distance.km)) # That is the most important

        # Converting az to save it 
        az_degrees = az.degrees
        az_float = az_degrees.item()
        # Conversions necessary for calculations
        d_altitude = alt.degrees
        alt_float = (d_altitude).item()
        
        d_km = distance.km # distance magnitude in km
        d_float = d_km.item() # converted to float 
        
        height = np.sin(np.deg2rad(alt_float)) * d_float # this is supossedly the height
        # following h = sin(alt) * distance

        print("Height is ", height , " km")
        data = [ '\n\t- Altitude: ' + str(alt_float) + " degrees \n\t- Azimuth:'" + str(az_float) + ' degrees'+ "\n\t- Distance: " + str(d_float) + " km" + "\n\t- Height: " + str(height) + "km" ]
        save_data(data)
        return height

    except Exception as e:
        print("ERROR get height: ",e)

# I think that's wrong - summation of all points is not the total 
def quantify_attenuation(gaseos, rain, scintilation, cloud):
    print("Quantified attenuation values in dB:")
    # Gaseous
    g = np.sum(gaseos)
    
    gline = "Gaseous Attenuation: "+  str(g)
    print(gline)
    # Rain
    r = np.sum(rain)
    rline = "Rain Attenuation: " + str(r)
    print (rline)
    # Cloud
    c = np.sum(cloud)
    cline = "Cloud Attenuation: " + str(c)
    print(cline)
    # Scintilation (?) 
    s = np.sum(scintilation)
    sline = "Scintilation Attenuation: "+ str(s)
    print(sline)
    t = g+r+c+s
    # Total
    tline = "Total Attenuation: " + str(t) 
    print(tline)

    #data = ["\t", gline, "\t", rline, "\n \t", cline, "\t" , sline, "\n \t", tline]
    data = ["\t" +  gline +  "\t" + rline + "\n \t" + cline + "\t" + sline+ "\n \t"+ tline]
    save_data(data)
    

def test_start(satellite):
    
    write_file_date()

    lat, lon = get_lat_lon(satellite)
    sat_height = getHeight(satellite)
    frequency = getFrequency(satellite)

def start(satellite):
    
    write_file_date()

    lat, lon = get_lat_lon(satellite)
    sat_height = getHeight(satellite)
    frequency = getFrequency(satellite)

    # Compute the elevation angle between satellite and ground station
    el = itur.utils.elevation_angle(sat_height, lat, lon, GROUND_LATITUDE, GROUND_LONGITUDE)

        # Define unavailabilities vector
    unavailabilities = np.logspace(-1.5, 1.5, 100)

    # Compute the
    A_g, A_c, A_r, A_s, A_t = [], [], [], [], []
    for p in unavailabilities:
            a_g, a_c, a_r, a_s, a_t = itur.atmospheric_attenuation_slant_path(GROUND_LATITUDE, GROUND_LONGITUDE,
                                                                            frequency, el, p, D,
                                                                            return_contributions=True)
            A_g.append(a_g.value)
            A_c.append(a_c.value)
            A_r.append(a_r.value)
            A_s.append(a_s.value)
            A_t.append(a_t.value)

    # Print quantified values
    quantify_attenuation(A_g,A_r,A_s,A_c)
    # Plot the results
    g = np.sum(A_g)
    r = np.sum(A_r)
    c = np.sum(A_c)
    s = np.sum(A_s)
    t = np.sum(A_t)
    
    # Convert the selected float to string
    selected_float_str = "{:.4f}".format(g)
    # Concatenate with other strings
    line = "Gaseous attenuation " + selected_float_str    
    ax = plt.subplot(1,1,1)
    # ax.semilogx(unavailabilities, A_g, label='Gaseous attenuation')
    ax.semilogx(unavailabilities, A_g, label=line)

    # Cloud
    selected_float_str = "{:.4f}".format(c)
    line = 'Cloud attenuation ' + selected_float_str
    ax.semilogx(unavailabilities, A_c, label=line)

    # Rain
    selected_float_str = "{:.4f}".format(r)
    line = 'Rain attenuation ' + selected_float_str
    ax.semilogx(unavailabilities, A_r, label=line)
    
    # Scintilation
    selected_float_str = "{:.4f}".format(s)
    line = 'Scintilation attenuation ' + selected_float_str
    ax.semilogx(unavailabilities, A_s, label=line)

    # Total
    selected_float_str = "{:.4f}".format(t)
    line = 'Total attenuation ' + selected_float_str
    ax.semilogx(unavailabilities, A_t, label=line)

    ax.xaxis.set_major_formatter(ScalarFormatter())
    ax.set_xlabel('Percentage of time attenuation value is exceeded [%]')
    ax.set_ylabel('Attenuation [dB]')
    ax.grid(which='both', linestyle=':')

    plt.legend()
    plt.show()

def write_file_date():

    file_path = os.path.join(os.getcwd(),FILE_NAME)

    current_date_time = datetime.now()
    try:
        with open(file_path,mode="a") as file:
            

            # Format the date as a string
            current_date_string = current_date_time.strftime("%Y-%m-%d %H:%M:%S")

            help = ["\n\n# ", current_date_string, "\n"]
            line = "".join(help)
            file.write(line)
            
            
    except Exception as e:
            print("Problem saving date: ", e)

    


def save_data(some_data):
    file_path = os.path.join(os.getcwd(),FILE_NAME)

    try:
        with open(file_path,mode="+a") as file:
            help = "".join(str(item) for item in some_data)
            line = "".join(help)
            line = line + "\n"
            file.write(line)

    except Exception as e:
            print("Problem save_data: ", e)
     

if __name__=="__main__":
    satellite = load_sat()
    
    test_start(satellite)
