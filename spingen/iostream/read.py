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

def loadSystems(xmlfile : str, 
                system_count : int,
                field_strength : int,
                points : int, 
                spec_width : int,
                obs_freq : int) -> list[SSystem]:
    """Load a number of spin systems based on the matrix size or submatrices

    Parameters
    ----------
    xmlfile : str
        String represesntation of the xml file path 
    system_count : int
        Number of sub matrices to look for, if -1 or 1 then attempt loading the first matrix
    field_strength : int
        Field strength for spin system initialization
    points : int
        Point count resolution for spin system initialization
    spec_width : int
        Spectral width for spin system initialization
    obs_freq : int
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

    tree = ET.parse(xmlfile)
    root = tree.getroot()
    
    # Set Line width value
    # --------------------
    # Extra code is used for typing assertion, casting allegedly does not affect runtime
    lw_element = root.find(LW_PATH)
    if root.find(LW_PATH) is None:
        line_width : Hz = 0.0
    elif cast(ele, lw_element).text is None:
        line_width : Hz = 0.0
    else:
        lw_str = cast(str, cast(ele, lw_element).text)
        line_width : Hz = float(lw_str)

    match system_count:
        # Check primary matric
        case 0 | 1:
            primary_spin_matrix = cast(ele, root.find(CMAT_PATH))

            # If the primary spin matrix is too large, check to see if sub matrices exist
            if len(primary_spin_matrix.findall(SPIN_NAME_PATH)) > MAT_MAX: 
                matrices = root.findall(CMAT_PATH)
                if len(matrices) <= 1:
                    raise(ValueError(
                        'Primary spin matrix of size {} is too large! Max size: {}'.format(
                            len(primary_spin_matrix.findall(SPIN_NAME_PATH), MAT_MAX)
                        )))
                else: 
                    for i in range(1, len(matrices)):
                        spin_systems.append(
                            loadSpinSystem(matrices[i], line_width, field_strength,
                                       points, spec_width, obs_freq)
                        )
                    return spin_systems
            
            spin_systems.append(
                loadSpinSystem(primary_spin_matrix, line_width, field_strength,
                                       points, spec_width, obs_freq)
            )
                    
        case _:
            matrices = root.findall(CMAT_PATH)
            for i in range(1, system_count+1):
                spin_systems.append(
                    loadSpinSystem(matrices[i], line_width, field_strength,
                                points, spec_width, obs_freq)
                )
            return spin_systems
        
    return spin_systems

def loadSpinSystem(spin_matrix : ele, line_width : Hz, field_strength : int,
               points : int, spec_width : int, obs_freq : int) -> SSystem:
    """Generate a spin system from an xml coupling matrix element

    Parameters
    ----------
    spin_matrix : ele
        Target coupling matrix xml element tree
    line_width : Hz
        Line width for the spin system
    field_strength : int
        Field strength for the spin system
    points : int
        Number of points resolution for spin system
    spec_width : int
        Spectral width for spin system
    obs_freq : int
        Observation frequency for spin system

    Returns
    -------
    SpinSystem
        Returns generate spin system using class wrapping nmrsim spinsystem

    Raises
    ------
    ValueError
        Raise a value error if number of chemical shifts does not match the number of hydrogens
    """
    spin_names : list[str] = []
    chem_shifts : list[ppm] = []
    couplings_list = []

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

    if (len(spin_name_list) != len(cshift_list)):
            raise ValueError(
                "Spin names count %i and Number of chemical shifts %i do not match" %
                (len(spin_name_list), len(cshift_list))
            )
    N : int = len(cshift_list)

    # Create coupling matrix
    # ----------------------
    cMatrix = np.zeros((N,N),dtype=(float,float))

    for i, j, val in couplings_list:
        if (i-1 < N and j-1 < N):
            cMatrix[i-1][j-1] = val
            cMatrix[j-1][i-1] = val

    # Create lw list
    # --------------
    if (type(line_width) == list[Hz]):
        lw_list: list[Hz] = line_width
    else:
        lw_list: list[Hz] = []
        for i in range(N):
            lw_list.append(line_width)

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

    return SSystem(spin_names, chem_shifts, lw_list, cMatrix.astype(float), field_strength, points, spec_width, obs_freq, center)