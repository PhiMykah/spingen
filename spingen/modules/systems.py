from ..data import SSystem, system, Hz
from ..iostream import generateSystems
from nmrsim.plt import mplplot
import numpy as np
from sys import stderr

def get_peaksXML(input : str, system_count : int = 0, field_strength : Hz = 500, 
                 points : int =1000, spec_width : float = 50, obs_freq : float = 50) -> np.ndarray:
    """Obtain an x,y peaks array from an xml file with given parameters

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
    """
    systems : list[SSystem] = []
    systems = generateSystems(input, system_count, field_strength, points, spec_width, obs_freq)

    output_system = systems[0]

    for i in range(1, len(systems)):
        output_system += systems[i]
    
    x,y = mplplot(output_system.peaklist(), hidden=True)
    peaks = np.array([x,y]).T

    return peaks

def get_peaks(systems : list[system], line_widths : list[Hz], system_count : int = 0,
              field_strength : float = 500, points : int = 1000, spec_width : float = 50,
              obs_freq : float = 50) -> np.ndarray:
    """Obtain an x,y peaks array from a system set with given parameters

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
    """
    ssystems = []
    for syst in systems:
        ssystems.append(SSystem(syst.names, syst.cshifts, line_widths, syst.cmat.astype(float), field_strength, points, spec_width, obs_freq, syst.center))
    
    output_system = ssystems[0]

    for i in range(1, len(ssystems)):
        output_system += ssystems[i]

    x,y = mplplot(output_system.peaklist(), hidden=True)
    peaks = np.array([x,y]).T

    return peaks


def nmrConvert(convert) -> np.ndarray:
    """convert NMR data into an (x,y) array in PPM

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
    """
    print("Importing nmrPype...", file=stderr)
    import nmrPype

    df = nmrPype.DataFrame(convert)

    if df.array.ndim != 1:
        raise ValueError("Unsupported NMRPipe file dimensionality!")
    
    x_vals = np.arange(1, len(df.array)+1)

    sw = df.getParam("NDSW") 
    obs = df.getParam("NDOBS")
    orig = df.getParam("NDORIG")
    size = df.getParam("NDSIZE")

    sw  = 1.0 if (sw == 0.0) else sw
    obs = 1.0 if (obs == 0.0) else obs

    delta = -sw/(size)
    first = orig - delta*(size - 1)

    specValPPM  = (first + (x_vals - 1.0)*delta)/obs

    converted_array = np.array([specValPPM, df.array]).T

    return converted_array
    