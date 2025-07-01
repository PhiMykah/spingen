import xml.etree.ElementTree as ET 

from ..data import *
CMAT_PATH = 'coupling_matrix'
LW_PATH = CMAT_PATH + "/lw"
SPIN_NAME_PATH = 'spin_names/spin'
CSHIFT_PATH = 'chemical_shifts_ppm/cs'
COUPLING_PATH = 'couplings_Hz'
CENTER_PATH = 'DSS_region'
MAT_MAX = 8
MAT_NAME = "spin_matrix"
type ele = ET.Element

def generateSystems(xmlfile : str, 
                system_count : int,
                field_strength : float,
                points : int, 
                spec_width : float,
                obs_freq : float) -> list[SSystem]:
    """Load from xml and then create number of spin systems based on the matrix size or submatrices

    Parameters
    ----------
    xmlfile : str
        String represesntation of the xml file path 
    system_count : int
        Number of sub matrices to look for, if -1 or 1 then attempt loading the first matrix
    field_strength : float
        Field strength for spin system initialization
    points : int
        Point count resolution for spin system initialization
    spec_width : float
        Spectral width for spin system initialization
    obs_freq : float
        Observation frequency for spin system

    Returns
    -------
    list[SSystem]
        List of spin systems loaded from XML file

    Raises
    ------
    ValueError
        If the spin matrix is too large, it will not be able to be loaded in storage
    """
    # Ensure positive integer
    system_count = system_count if system_count >= 0 else -1 * system_count
    spin_systems : list[SSystem] = []
    systems : list[System] = []
    line_widths : list[Hz] = []
    systems, line_widths = loadSystems(xmlfile, system_count)

    for syst in systems:
        spin_systems.append(
            SSystem(syst.names, syst.cshifts, line_widths, syst.cmat.astype(float), field_strength, points, spec_width, obs_freq, syst.center)
        )
        
    return spin_systems


def get_line_widths(root: ele) -> list[Hz]:
    # Set Line width value
    # --------------------
    # Extra code is used for typing assertion, casting allegedly does not affect runtime
    lw_elements = root.findall(LW_PATH)
    if root.findall(LW_PATH) is None:
        line_widths : list[Hz] = [0.0]
    elif cast(ele, lw_elements[0]).text is None:
        line_widths : list[Hz] = [0.0]
    else:
        line_widths : list[Hz] = [float(cast(str, cast(ele, element).text)) for element in lw_elements]

    return line_widths


def loadSystems(xmlfile : str, system_count : int = 0) -> tuple[list[System], list[Hz]]:
    """Obtain information from a coupling matrix xml file system

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
    """
    tree = ET.parse(xmlfile)
    root = tree.getroot()

    line_widths = get_line_widths(root)

    systems = []
    match system_count:
        case 0 | 1:
            primary_spin_matrix = cast(ele, root.find(CMAT_PATH))
            if len(primary_spin_matrix.findall(SPIN_NAME_PATH)) > MAT_MAX: 
                matrices = root.findall(CMAT_PATH)
                if len(matrices) <= 1:
                    raise(ValueError(
                        'Primary spin matrix of size {} is too large! Max size: {}'.format(
                            len(primary_spin_matrix.findall(SPIN_NAME_PATH)), MAT_MAX)
                        ))
                else: 
                    for i in range(1, len(matrices)):
                        systems.append(get_system(matrices[i]))

                    return systems, line_widths

            systems.append(get_system(primary_spin_matrix))

        case _:
            matrices = root.findall(CMAT_PATH)
            for i in range(1, system_count+1):
                systems.append(get_system(matrices[i]))

    return systems, line_widths

def loadSystemFromFile(file : str) -> System:
    """
    Parse a text file and return a System object.

    Parameters
    ----------
    file : str
        File path for the text file

    Returns
    -------
    System
        Returns a system with:
            - hydrogen name labels
            - chemical shift list
            - coupling matrix
            - center measurement in ppm
    """

    with open(file, 'r') as f:
        lines = [line.strip() for line in f if line.strip()]

    # Last line is spin names
    spin_names = lines[0].split() # skip the first column header

    # All lines except last are matrix rows
    matrix_lines = lines[1:-1]  # skip the first header and last spin names

    N = len(spin_names)
    cmat = np.zeros((N, N), dtype=float)
    chem_shifts = []

    for i, line in enumerate(matrix_lines):
        parts = line.split()
        # Diagonal value is the chemical shift
        chem_shifts.append(float(parts[i+1]))
        for j in range(N):
            if i == j:
                cmat[i, j] = 0.0  # Set diagonal (chemical shift) to 0
            else:
                cmat[i, j] = float(parts[j+1])
    # Reflect cmat across the diagonal to ensure symmetry
    cmat = (cmat + cmat.T)

    # No center value in this format, set to 0.0
    center = 0.0

    return System(spin_names, chem_shifts, cmat, center)

def get_system(spin_matrix : ele) -> System:
    spin_names = get_spin_names(spin_matrix)
    chem_shifts = get_chemical_shifts(spin_matrix)
    cMatrix = get_coupling_matrix(spin_matrix, len(chem_shifts))
    center = get_center(spin_matrix)
    return System(spin_names, chem_shifts, cMatrix, center)

def get_spin_names(spin_matrix : ele ) -> list[str]:
    spin_names = []

    # Set Spin names
    # --------------
    # Extra code is used for typing assertion, casting allegedly does not affect runtime
    spin_name_list = spin_matrix.findall(SPIN_NAME_PATH)
    idx = 0
    while(len(spin_names) < len(spin_name_list)):
        spindex = spin_name_list[idx].get('index')
        spindex = int(spindex) if spindex is not None else None
        if spindex is None: 
            break
        else:
            if (idx == (int(spindex)-1)):
                name = spin_name_list[idx].get('name')
                if name is not None:
                    spin_names.append(cast(str, name))
                idx = idx + 1 % len(spin_name_list)

    return spin_names

def get_chemical_shifts(spin_matrix : ele) -> list[float]:
    chem_shifts : list[ppm] = []

    # Set Chemical Shift values
    # -------------------------
    # Extra code is used for typing assertion, casting allegedly does not affect runtime
    cshift_list = spin_matrix.findall(CSHIFT_PATH)
    idx = 0
    while(len(chem_shifts) < len(cshift_list)):
        spindex = cshift_list[idx].get('index')
        spindex = int(spindex) if spindex is not None else None
        if spindex is None:
            break
        else:
            if (idx == (int(spindex)-1)):
                val = cshift_list[idx].get('ppm')
                if val is not None:
                    chem_shifts.append(float(val))
                idx = idx + 1 % len(cshift_list)

    return chem_shifts

def get_coupling_matrix(spin_matrix : ele, N : int) -> np.ndarray:
    couplings_list = []

    # Coupling values
    # ---------------
    # Extra code is used for typing assertion, casting allegedly does not affect runtime
    cpl_list = spin_matrix.findall(COUPLING_PATH + "/coupling")
    idx = 0
    while(len(couplings_list) < len(cpl_list)):
        spindex_pair = (cpl_list[idx].get('from_index'),cpl_list[idx].get('to_index'))
        if None in spindex_pair:
            break
        else:
            spindex_pair = (cast(str, spindex_pair[0]), cast(str, spindex_pair[1]))
            val = cpl_list[idx].get('value')
            if val is not None:
                couplings_list.append((int(spindex_pair[0]), int(spindex_pair[1]), float(val)))
            idx = idx + 1 % len(cpl_list)

    # Create coupling matrix
    # ----------------------
    cMatrix = np.zeros((N,N),dtype=(float,float))

    for i, j, val in couplings_list:
        if (i-1 < N and j-1 < N):
            cMatrix[i-1][j-1] = val
            cMatrix[j-1][i-1] = val

    return cMatrix

def get_center(spin_matrix : ele) -> ppm:
    # Obtain center point
    # -------------------
    center_min = spin_matrix.find(CENTER_PATH + '/min_ppm')
    center_max = spin_matrix.find(CENTER_PATH + '/max_ppm')

    if (center_min is None or center_max is None):
        center : ppm = 0.0
    elif (cast(ele, center_min).text is None or cast(ele, center_max).text is None):
        center : ppm = 0.0
    else:
        center_left = cast(str, cast(ele, center_min).text)
        center_right = cast(str, cast(ele, center_max).text)
        center : ppm = (float(center_left) + float(center_right)) / 2

    return center

"""
def loadSpinSystem(spin_matrix : ele, line_widths : list[Hz], field_strength : int,
               points : int, spec_width : int, obs_freq : int) -> SSystem:
    # Generate a spin system from an xml coupling matrix element

    # Parameters
    # ----------
    # spin_matrix : ele
    #     Target coupling matrix xml element tree
    # line_width : Hz
    #     Line width for the spin system
    # field_strength : int
    #     Field strength for the spin system
    # points : int
    #     Number of points resolution for spin system
    # spec_width : int
    #     Spectral width for spin system
    # obs_freq : int
    #     Observation frequency for spin system

    # Returns
    # -------
    # SpinSystem
    #     Returns generate spin system using class wrapping nmrsim spinsystem

    # Raises
    # ------
    # ValueError
    #     Raise a value error if number of chemical shifts does not match the number of hydrogens

    # Set Spin names
    # --------------
    spin_names : list[str] = get_spin_names(spin_matrix)

    # Set Chemical Shift values
    # -------------------------
    chem_shifts : list[ppm] = get_chemical_shifts(spin_matrix)

    N = len(chem_shifts)

    # Create coupling matrix
    # ----------------------
    cMatrix = get_coupling_matrix(spin_matrix, N)
    
    # Obtain center point
    # -------------------
    center = get_center(spin_matrix)

    return SSystem(spin_names, chem_shifts, line_widths, cMatrix.astype(float), field_strength, points, spec_width, obs_freq, center)
"""