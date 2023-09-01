#!/usr/bin/env python3
"""
use a single location bin to show the concept of fitting GNSS vs. DASC brightness
As a next step, we would create bin along the ground distance. But I think it's nice
to show the fundamental algorithm first and then add geographic and altitude grid.
"""

import mahali_dasc.dasc as dasc

import argparse
from pathlib import Path
from datetime import datetime

import numpy as np

from matplotlib.pyplot import figure, show
import matplotlib.colors

# %% load Azimuth, Elevation for DASC to determine pixel index of magnetic zenith
"""
We're starting by using only a single pixel brightness from DASC.
"""

R = Path(__file__).parent / "data"

p = argparse.ArgumentParser()
p.add_argument(
    "data_dir", help="directory where TEC and image data are", default=R, nargs="?"
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

mag_zenith_azimuth = 180 + declination
mag_zenith_elevation = inclination

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

azimuth, elevation = dasc.cal(azimuth_file, elevation_file)

image, image_header = dasc.image(image_file)

image_glat = image_header["GLAT"]
image_glon = image_header["GLON"]

print("image_glat (-90..90), image_glon [-180..180) East", image_glat, image_glon)

# %% find the index of the image pixel closest to the magnetic zenith
"""
minimum hypotenuse of azimuth elevation as closest index
"""

err = np.hypot(azimuth - mag_zenith_azimuth, elevation - mag_zenith_elevation)
irow, icol = np.unravel_index(np.argmin(err), err.shape)

"""
Reference figure 3 from https://agupubs.onlinelibrary.wiley.com/doi/10.1002/2017GL073570
"""
fg = figure()
ax = fg.gca()

ax.pcolormesh(image, cmap="Greens", norm=matplotlib.colors.LogNorm())

ax.contour(
    range(image.shape[0]), range(image.shape[1]), azimuth, levels=range(0, 360, 30)
)

ax.scatter(icol, irow, marker="x", color="red")
ax.set_title(image_name)

show()
