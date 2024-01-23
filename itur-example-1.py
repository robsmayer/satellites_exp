"""
    Single location attenuation

    Here we will compute the link attenuation vs. at a 
    frequency of 22.5 GHz for a link between a satellite in GEO 
    at the orbital slot 77 W and a ground station in Boston.
    
    """

import itur
import astropy.units as u
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter

# Ground station coordinates

lat_GS = 42.3601
lon_GS = -71.0942

# Satellite coordinates  (GEO, 77 W)

lat_sat = 0
lon_sat = -77
h_sat = 35786 * u.km


# Compute the elevation angle between satellite and ground station
el = itur.utils.elevation_angle(h_sat, lat_sat, lon_sat, lat_GS, lon_GS)

# Define link parameters

f = 22.5 * u.GHz    # Link frequency
D = 1.2 * u.m       # Antenna diameters

# Define unavailabilities vector
unavailabilities = np.logspace(-1.5, 1.5, 100)

# Compute the
A_g, A_c, A_r, A_s, A_t = [], [], [], [], []
for p in unavailabilities:
        a_g, a_c, a_r, a_s, a_t = itur.atmospheric_attenuation_slant_path(lat_GS, lon_GS,
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

# Show results
plt.show()   