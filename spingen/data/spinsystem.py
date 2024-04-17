from nmrsim import SpinSystem
import numpy as np
from typing import Literal, cast
import sys 

type Hz = float
type MHz = Hz
type ppm = float

def ppm_to_hz(ppm, spec_freq):
    """Given a chemical shift in ppm and spectrometer frequency in MHz, return the corresponding chemical shift in Hz."""
    return [d * spec_freq for d in ppm]

def frequency_to_time(array : np.ndarray) -> np.ndarray:
    """Convert 1D Frequency Data stored as X,Y to time domain

    Parameters
    ----------
    array : np.ndarray
        2D numpy array with shape (N, 2)

    Returns
    -------
    np.ndarray
        Time-domain version of input array
    """
    if array.ndim != 2:
        print(f"Array of shape {array.shape} does not match excepted (N,2) shape.", file=sys.stderr)
        print(f"Data has not been changed.", file=sys.stderr)
        return array
    elif array.shape[1] != 2:
        print(f"Array of shape {array.shape} does not match excepted (N,2) shape.", file=sys.stderr)
        print(f"Data has not been changed.", file=sys.stderr)
        return array
    
    x_vals : np.ndarray = array.T[0]
    fd_data : np.ndarray = array.T[1]

    # Perform discrete inverse fast fourier transform
    td_data : np.ndarray = np.fft.ifft(fd_data)

    # Reconstruct 2D array
    td_array : np.ndarray = np.array([x_vals, td_data.real], dtype=array.dtype)

    return td_array.T


class SSystem(SpinSystem):
    def __init__(self, 
            spin_names : list[str], chem_shifts : list[ppm], line_widths : list[Hz], 
            cMatrix : np.ndarray, field_strength : Hz, points : int, 
            spec_width : Hz, obs_freq : MHz, center : ppm):
        
        self.spin_names = spin_names
        self.chem_shifts = ppm_to_hz(chem_shifts, field_strength)
        self.line_widths = line_widths

        if (len(spin_names) != len(chem_shifts) != len(line_widths)):
            raise ValueError(
                "Spin names count %i, Number of chemical shifts %i and number of line widths %i do not match" %
                (len(spin_names), len(chem_shifts), len(line_widths))
            )
        
        self.N = len(chem_shifts)

        self.cMatrix = cMatrix

        if cMatrix.shape != (self.N, self.N):
            raise ValueError(
                f"Coupling matrix of shape {cMatrix.shape} does not match expected shape of ({self.N}, {self.N})"
            )
        
        self.field_strength = field_strength
        self.points = points
        self.spec_width = spec_width
        self.obs_freq = obs_freq
        self.center = center

        super().__init__(self.chem_shifts, cMatrix)
