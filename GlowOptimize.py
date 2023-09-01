#!/usr/bin/env python3
"""
Use GLOW with scipy.optimize.minimize to fit DASC brightness with GLOW
model vis input precipitation parameters (here, a Maxwellian distribution).

When this works, one would then add GNSS TEC data to the fit.

General idea based of off https://github.com/space-physics/histfeas
"""

# https://github.com/space-physics/ncarglow
import mahali_dasc.dasc as dasc

import argparse
from pathlib import Path
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)

R = Path(__file__).parent / "data"

p = argparse.ArgumentParser()
p.add_argument(
    "data_dir", help="directory where TEC and image data are", default=R, nargs="?"
)
P = p.parse_args()

data_dir = Path(P.data_dir)

Nenergy = 250
# number of Energy bins

# %% load a DASC image
# hardcoded filenames for simplicity
time = datetime(2015, 10, 7, 6, 19, 13, 20000)
millisec = int(time.microsecond / 1e3)

image_name_time = time.strftime("%Y%m%d_%H%M%S.") + f"{millisec:03d}"
image_name = f"PKR_DASC_0558_{image_name_time}.FITS"
image_file = data_dir / image_name

# %% as a test, average a small neighborhood of pixels
"""
this is arbitrary, we need to get a precise location vis magnetic zenith
as intended in SingleBin.py
"""
x_arbitrary = 100
y_arbitrary = 100
neighborhood = 5

image, image_header = dasc.image(image_file)
glat = image_header["GLAT"]
glon = image_header["GLON"]

brightness_observed = image[
    x_arbitrary - neighborhood : x_arbitrary + neighborhood,
    y_arbitrary - neighborhood : y_arbitrary + neighborhood,
].mean()


# %%
