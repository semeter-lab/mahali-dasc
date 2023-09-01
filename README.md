# mahali-dasc

Looking at GNSS vis all sky data and the [GLOW](https://github.com/space-physics/NCAR-GLOW) model, using Python.

## Setting up computer

If using macOS we need [Homebrew](https://brew.sh) and a compiler.
Then install

```sh
brew install git cmake gcc
```

You can get Python as well

```sh
brew install miniconda
```


## Verify image orientation

First we have to load the data and verify the orientation.
If the data isn't registered to physical coordinates properly, all the analysis is meaningless.
I plan to use the moon as a reference with Stellarium, since it is a bright, well-known object that gets through DASC narrow-band filters.

## GlOW estimated precipitating electron flux via scipy.optimize.minimize

The [GLOW Python interface](https://github.com/space-physics/NCAR-GLOW) allows running GLOW from Python and has Example scripts.
Currently the GLOW altitude grid is
[set in command-line program interface glowpython.f90](https://github.com/space-physics/ncar-glow/tree/main/src/ncarglow/fortran/glowpython.f90)
by function
[alt_grid in utils.f90](https://github.com/space-physics/NCAR-GLOW/blob/main/src/ncarglow/fortran/utils.f90)

First approach to check feasibility:
use
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
