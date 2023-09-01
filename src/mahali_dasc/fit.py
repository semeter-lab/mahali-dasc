"""
functions using for fitting brightness to a model
"""

import ncarglow

import time
from datetime import datetime
import logging
import typing

import numpy as np
import scipy.optimize as sciopt
import numpy.linalg as linalg


def optfun(
    E0: float,
    Q: float,
    brightness_observed: float,
    time: datetime,
    glat: float,
    glon: float,
    Nenergy: int,
    optical_wavelength_nm: str,
):
    """
    provides the quantity to minimize based on scipy.optimize
    guesses for E0 and Q

    Parameters
    ----------

    time: datetime.datetime
        time of the image

    """

    iono = ncarglow.maxwellian(time, glat, glon, Q, E0, Nenergy)

    """
    the .sum() assumes looking straight up the field line--generally we'd
    have to account for oblique viewing angle
    """
    brightness_model = iono["ver"].loc[:, optical_wavelength_nm].sum()

    # this is the "2-norm" https://en.wikipedia.org/wiki/Norm_(mathematics)#p-norm
    return linalg.norm(brightness_model - brightness_observed, ord=2)


def difffun(jfit, nEnergy=33, sx=109):
    """used only for slsqp method"""
    # computes difference down columns (top to bottom)
    return 1e5 - np.absolute(np.diff(jfit, n=1, axis=0)).max()


def fit_brightness(
    method: str,
    max_iter: int,
    E0: float,
    Q: float,
    brightness_observed: float,
    time_model: datetime,
    glat: float,
    glon: float,
    Nenergy: int,
    optical_wavelength_nm: str,
):
    """
    method: str
        scipy.optimize.minimize method
    max_iter: int
        maximum number of iteration (might run forever if it's not converging fast enough)
    Phi0: float
        first guess for precipi
    https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.minimize.html
    """

    constraints: dict[str, typing.Any] = {}

    bounds = (0, np.inf)
    # non-negativity

    opts: dict[str, typing.Any] = {"maxiter": max_iter}
    match method:
        case "nelder-mead":
            pass
            # 100
        case "bfgs":
            opts["norm"] = 2
            # 20
        case "tnc":
            pass
            # 20
        case "l-bfgs-b":
            pass
            # defaults: maxfun=5*nEnergy*sx, maxiter=10
            # 100 maxiter works well
        case "slsqp":
            pass
            # 2
            constraints = {"type": "ineq", "fun": difffun}
        case "cobyla":
            opts |= {"rhobeg": 1e1, "tol": 1}
            # 10
        case _:
            raise TypeError(f"unknown minimization method: {method}")

    tic = time.monotonic()

    Phifit = sciopt.minimize(
        optfun,
        x0=(E0, Q),
        args=(brightness_observed, time_model, glat, glon),
        method=method,
        bounds=bounds,  # non-negativity
        constraints=constraints,
        options=opts,
    )

    logging.info(f"{time.monotonic() - tic:0.1f} seconds to fit brightness with {method}")
    logging.info(f"Minimizer says: {Phifit.message}")
    logging.info(f"residual={Phifit.fun:.1e} after {Phifit.nfev} func evaluations")

    return Phifit
