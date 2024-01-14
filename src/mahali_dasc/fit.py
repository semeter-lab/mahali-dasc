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

# import numpy.linalg as linalg


def optfun(
    Phi0,
    brightness_observed: float,
    time: datetime,
    glat: float,
    glon: float,
    Nenergy: int,
    optical_wavelength_AA: str,
):
    """
    provides the quantity to minimize based on scipy.optimize
    guesses for E0 and Q

    Parameters
    ----------

    time: datetime.datetime
        time of the image

    """

    E0 = Phi0[0]
    Q = Phi0[1]

    iono = ncarglow.maxwellian(time, glat, glon, Q, E0, Nenergy)

    """
    the .sum() assumes looking straight up the field line--generally we'd
    have to account for oblique viewing angle
    """
    brightness_model = iono["vertical_column_brightness"].loc[:, optical_wavelength_AA]

    # this is the "2-norm" https://en.wikipedia.org/wiki/Norm_(mathematics)#p-norm
    # err_norm linalg.norm(brightness_model - brightness_observed, ord=2)

    # special case for scalar
    err_norm = np.absolute(brightness_model - brightness_observed)

    logging.info(
        f"Guess for E0: {E0:f}  Q: {Q:f} "
        f"brightness: {brightness_model:.1e} residual: {err_norm:.1e}"
    )

    return err_norm


def difffun(jfit, nEnergy=33, sx=109):
    """used only for slsqp method"""
    # computes difference down columns (top to bottom)
    return 1e5 - np.absolute(np.diff(jfit, n=1, axis=0)).max()


def fit_brightness(
    method: str,
    max_iter: int,
    Phi0,
    brightness_observed: float,
    time_model: datetime,
    glat: float,
    glon: float,
    Nenergy: int,
    optical_wavelength_AA: str,
):
    """
    method: str
        scipy.optimize.minimize method
    max_iter: int
        maximum number of iteration (might run forever if it's not converging fast enough)
    Phi0: vector of model input parameter
        Initially, this is length-2 vector (E0, Q)
    https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.minimize.html
    """

    constraints: dict[str, typing.Any] = {}

    bounds = sciopt.Bounds(0, np.inf)
    # lower bound: non-negativity
    # upper bound: no limit

    opts: dict[str, typing.Any] = {"maxiter": max_iter}
    match method:
        case "nelder-mead":
            pass
            # 100
        case "bfgs":
            opts["norm"] = 2
            bounds = None
            # 20
        case "tnc":
            pass
            # 20
        case "l-bfgs-b":
            # https://docs.scipy.org/doc/scipy/reference/optimize.minimize-lbfgsb.html#optimize-minimize-lbfgsb
            opts = opts
            # opts |= {"maxcor": 10, "ftol": 1e-10, "gtol": 1e-10}
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
        x0=Phi0,
        args=(
            brightness_observed,
            time_model,
            glat,
            glon,
            Nenergy,
            optical_wavelength_AA,
        ),
        method=method,
        bounds=bounds,  # non-negativity
        constraints=constraints,
        options=opts,
    )

    logging.info(f"{time.monotonic() - tic:0.1f} seconds to fit brightness with {method}")
    logging.info(f"Minimizer says: {Phifit.message}")
    logging.info(f"residual={Phifit.fun:.1e} after {Phifit.nfev} func evaluations")

    return Phifit
