# mahali-dasc

Looking at GNSS vis all sky data and the [GLOW](https://github.com/space-physics/NCAR-GLOW) model, using Python.

First approach to check feasibility: use 
[scipy.optimize.minimize](https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.minimize.html)
with GLOW optical output and characteristic energy input vs. DASC brightness.

Next steps:

Use more than one GLOW "cell".
Use multiple bins between GNSS receiver and satellite using a 2D grid with ground distance vs. altitude
That is, convert GNSS satellite ECI to lat,lon,altitude and then use Vincenty algorithm to compute ground distance in 
[pymap3d](https://github.com/geospace-code/pymap3d).


Later steps (for few percent additional accuracy):

* extinction via [LOWTRAN](https://github.com/space-physics/lowtran)
* Van Rhijn factor (I may have lost the Python code I have for this, I couldn't find it when searching my repos)