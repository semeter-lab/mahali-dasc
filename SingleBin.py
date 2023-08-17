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

# %% geographic to geomagnetic conversion
"""
I used IGRF for this manually https://omniweb.gsfc.nasa.gov/vitmo/cgm.html
If we make this script apply to more than one location,
we could someday make it programmatic. https://github.com/space-physics/igrf
"""

# too bothersome to not hard code filenames; someday we could use argparse.
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

with fits.open(elevation_file) as f:
    elevation = f[0].data

with fits.open(image_file) as f:
    image_header = f[0].header

image_glat = image_header["GLAT"]
image_glon = image_header["GLON"]
