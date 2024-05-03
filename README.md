spingen
=======

NMR Spectra generation through \
                 the use of spin matrices.

Installation
------------
1. Clone repository
```sh
git clone https://github.com/PhiMykah/spingen
```
2. Install through pip
```sh
cd spingen
pip install -e .
```

Usage
-----
Spingen can be run in command-line mode or in scripts.

### Command-line
```
usage: spingen [-h] [-help] -in File Path [-fs Value (MHZ)] [-pts Value]
               [-sw Value] [-obs Value] [-sc Values] [-d [{time,t,f,freq}]]
               [-out File Path] [-fmt ] [-convert NMR File]

Insert description here

options:
  -h, --help            show this help message and exit
  -help
  -in File Path, --input File Path
                        Input XML file for spin matrix
  -fs Value (MHZ), --field-strength Value (MHZ)
                        NMR instrument field strength for conversions
  -pts Value, --points Value
                        NMR resolution by number of points
  -sw Value, --spec-width Value
                        Spectral width of NMR data
  -obs Value, --obs-freq Value
                        Observation fequency value
  -sc Values, --sub-count Values
                        Number of independent subset spin matrices
  -d [{time,t,f,freq}], --domain [{time,t,f,freq}]
                        Data output domain type
  -out File Path, -output File Path
                        Designated output file location
  -fmt [], -format []   Designated output file format
  -convert NMR File     NMRPipe format file to convert to ppm
```

### Script Mode
```py
import spingen as sg

synth_peaks = sg.get_peaksXML(input, system_count, field_strength, points, spec_width, obs_freq)

# ----------
#     Or
# ----------

systems, line_widths = sg.loadSystems(xmlfile, system_count)
synth_peaks = sg.get_peaks(systems, line_widths, system_count, field_strength, points, spec_width, obs_freq)

real_peaks = sg.convert(nmr_file)
```
`loadSystems()` returns a list of `system` objects which hold relevant data for generating a system.

```py
"""
class system
============
system object with attributes describing spin matrix system

Parameters
----------
names : list[str]
    list of proton names
cshifts : list[Hz]
    list of chemical shifts per proton
cmat : ndarray
    coupling matrix
center : ppm
    center value for measurement
"""

newSystem = system(names, cshifts, cmat, center)

proton_names = system.names
chem_shifts = system.cshifts
coupling_matrix = system.cmat
center_value = system.center
```
#### Other Methods
get_peaksXML()
```
Obtain an x,y peaks array from an xml file with given parameters

Parameters
----------
input : str
    imput xml file path as a string
system_count : int, optional
    Number of submatrices in the system, by default 0
field_strength : Hz, optional
    Field strength of measurement device, by default 500
points : int, optional
    Number of points to sample, does not affect peaks but increases resolution, by default 1000
spec_width : float, optional
    Spectral width of system, by default 50
obs_freq : float, optional
    Observation frequency of measurement device, by default 50

Returns
-------
ndarray
    2D array of peaks of shape (len(x),2)
```
get_peaks()
```
Obtain an x,y peaks array from a system set with given parameters

Parameters
----------
systems : list[system]
    list of systems previously obtained from an xml file
line_widths : list[Hz]
    list of line widths for each spin matrix
system_count : int, optional
    Number of submatrices in the system, by default 0
field_strength : float, optional
    Field strength of measurement device, by default 500
points : int, optional
    Number of points to sample, does not affect peaks but increases resolution, by default 1000
spec_width : float, optional
    Spectral width of system, by default 50
obs_freq : float, optional
    Observation frequency of measurement device, by default 50

Returns
-------
ndarray
    2D array of peaks of shape (len(x),2)
```
load_system()
```
Obtain information from a coupling matrix xml file system

Parameters
----------
xmlfile : str
    File path for the xml file
system_count : int
    Number of submatrices in system (0 | 1 if only one)

Returns
-------
tuple[list[system], list[Hz]]
    - list of systems containing:
        - hydrogen name labels
        - chemical shift list
        - coupling matrix
        - center measurement in ppm
    - list of linewidths for main system and sub matrices
```
nmrConvert()
```
convert NMR data into an (x,y) array in PPM

Parameters
----------
convert : str
    converting file

Returns
-------
ndarray
    2D array of peaks of shape (NDSIZE,2)

Raises
------
ValueError
    Raises an error if the NMR data is multi-dimensional
```