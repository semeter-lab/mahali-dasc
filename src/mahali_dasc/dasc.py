from __future__ import annotations
from pathlib import Path

import numpy as np
from astropy.io import fits


def cal(azimuth_file, elevation_file: Path) -> tuple:
    """
    read DASC calibration files
    """

    with fits.open(azimuth_file) as f:
        azimuth = f[0].data
    # convert counter-clockwise to clockwise azimuth
    azimuth = 360 - np.ma.masked_where(azimuth == 0, azimuth)

    with fits.open(elevation_file) as f:
        elevation = f[0].data
    elevation = np.ma.masked_where(elevation == 0, elevation)

    return azimuth, elevation


def image(image_file: Path) -> tuple:
    """
    read DASC image
    """
    with fits.open(image_file) as f:
        return f[0].data, f[0].header
