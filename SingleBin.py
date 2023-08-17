#!/usr/bin/env python3
"""
use a single location bin to show the concept of fitting GNSS vs. DASC brightness
As a next step, we would create bin along the ground distance. But I think it's nice
to show the fundamental algorithm first and then add geographic and altitude grid.
"""

import argparse
from pathlib import Path
from datetime import datetime

from astropy.io import fits
import numpy as np

from matplotlib.pyplot import figure, show

# %% load Azimuth, Elevation for DASC to determine pixel index of magnetic zenith
"""
We're starting by using only a single pixel brightness from DASC.
"""

p = argparse.ArgumentParser()
p.add_argument(
    "data_dir", help="directory where TEC and image data are", default=".", nargs="?"
)
P = p.parse_args()

data_dir = Path(P.data_dir)

# %% load data
"""
Get Declination and Inclination from IGRF2020
I did it manually, but this could be done using https://github.com/space-physics/igrf someday

https://www.ngdc.noaa.gov/geomag/calculators/magcalc.shtml#igrfwmm

Model Used:	IGRF2020
Latitude:	65.126° N
Longitude:	147.479° W
Elevation:	0.0 km GPS

Date        Declination Inclination Horizontal 	 North Comp	East Comp  Vertical Comp Total Field
            ( +E | -W)  (+ D | - U) Intensity  (+ N | -S) (+ E | -W)   (+ D | -U)
2015-10-07	18.6471°	77.4757°	12,332.2 nT	11,684.9 nT	3,943.1 nT	55,515.5 nT	56,868.7 nT
"""

inclination = 77.4757
declination = 18.6471

# hardcoded filenames for simplicity
time = datetime(2015, 10, 7, 6, 19, 13, 20000)
millisec = int(time.microsecond / 1e3)

image_name_time = time.strftime("%Y%m%d_%H%M%S.") + f"{millisec:03d}"
azimuth_name = "PKR_DASC_0558_20150213_Az.FIT"
elevation_name = "PKR_DASC_0558_20150213_El.FIT"
image_name = f"PKR_DASC_0558_{image_name_time}.FITS"

azimuth_file = data_dir / azimuth_name
elevation_file = data_dir / elevation_name
image_file = data_dir / image_name


with fits.open(azimuth_file) as f:
    azimuth = f[0].data
# convert counter-clockwise to clockwise azimuth
azimuth = 360 - np.ma.masked_where(azimuth == 0, azimuth)

fg = figure()
axs = fg.subplots(1, 2, sharex=True, sharey=True)
ax = axs[0]
h = ax.pcolormesh(azimuth)
ax.set_title("Azimuth (degrees clockwise from north)")
ax.set_xlabel("x (pixels)")
ax.set_ylabel("y (pixels)")
fg.colorbar(h, ax=ax)

with fits.open(elevation_file) as f:
    elevation = f[0].data
elevation = np.ma.masked_where(elevation == 0, elevation)

ax = axs[1]
h = ax.pcolormesh(elevation)
ax.set_title("Elevation (degrees from horizon)")
fg.colorbar(h, ax=ax)

with fits.open(image_file) as f:
    image_header = f[0].header

image_glat = image_header["GLAT"]
image_glon = image_header["GLON"]

print("image_glat (-90..90), image_glon [-180..180) East", image_glat, image_glon)

# %% find the index of the image pixel closest to the magnetic zenith
"""
minimum hypotenuse of azimuth elevation as closest index
"""

err = np.hypot(azimuth - declination, elevation - inclination)

show()
