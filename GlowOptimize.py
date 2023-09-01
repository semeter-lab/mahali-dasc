#!/usr/bin/env python3
"""
Use GLOW with scipy.optimize.minimize to fit DASC brightness with GLOW
model vis input precipitation parameters (here, a Maxwellian distribution).

When this works, one would then add GNSS TEC data to the fit.

General idea based of off https://github.com/space-physics/histfeas
"""

# https://github.com/space-physics/ncarglow
import mahali_dasc.dasc as dasc
import mahali_dasc.fit as dasc_fit

import argparse
from pathlib import Path
from datetime import datetime
import logging

import numpy as np

logging.basicConfig(level=logging.INFO)

R = Path(__file__).parent / "data"

p = argparse.ArgumentParser()
p.add_argument(
    "fit_method",
    help="scipy.optimize.minimize method",
    choices=["nelder-mead", "l-bfgs-b", "bfgs", "slsqp", "tnc", "cobyla"],
)
p.add_argument(
    "max_iter",
    help="maximum number of iteration (might run forever if it's not converging fast enough)",
    type=int,
)
p.add_argument(
    "data_dir", help="directory where TEC and image data are", default=R, nargs="?"
)
P = p.parse_args()

data_dir = Path(P.data_dir)

Nenergy = 250
# number of Energy bins

optical_wavelength_AA = "5577"
# for indexing GLOW output data

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

# %% fit brightness

# Initial guess
E0 = 100  # eV
Q = 1  # total electron flux

# scipy.optimize needs a vector of parameters to optimize
Phi0 = np.array([E0, Q])


Phifit = dasc_fit.fit_brightness(
    P.fit_method,
    P.max_iter,
    Phi0,
    brightness_observed,
    time,
    glat,
    glon,
    Nenergy,
    optical_wavelength_AA,
)

print("Estimated Maxwellian precipitation parameters:")
print(f"E0 = {Phifit.x[0]:.2f} eV")
print(f"Q = {Phifit.x[1]:.2e} eV/cm^2/s")
