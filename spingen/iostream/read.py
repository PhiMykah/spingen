import xml.etree.ElementTree as ET 

from ..data import *
MAT_ROOT = 'coupling_matrix'
LW_PATH = MAT_ROOT
SPIN_NAME_PATH = MAT_ROOT + '/spin_names'
CSHIFT_PATH = MAT_ROOT + '/chemical_shifts_ppm'
COUPLING_PATH = MAT_ROOT + '/couplings_Hz'
CENTER_PATH = MAT_ROOT + '/DSS_region'

type ele = ET.Element

def readXML(xmlfile : str) -> tuple[list[str], list[ppm], list[Hz], np.ndarray, ppm]:
    spin_names : list[str] = []
    chem_shifts : list[ppm] = []
    couplings_list = []

    tree = ET.parse(xmlfile)
    root = tree.getroot()

    # Set Line width value
    # --------------------
    # Extra code is used for typing assertion, casting allegedly does not affect runtime
    lw_element = root.find(LW_PATH + "/lw")
    if root.find(LW_PATH) is None:
        line_width : Hz = 0.0
    elif cast(ele, lw_element).text is None:
        line_width : Hz = 0.0
    else:
        lw_str = cast(str, cast(ele, lw_element).text)
        line_width : Hz = float(lw_str)

    # Set Spin names
    # --------------
    # Extra code is used for typing assertion, casting allegedly does not affect runtime
    spin_name_list = root.findall(SPIN_NAME_PATH + "/spin")
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
    cshift_list = root.findall(CSHIFT_PATH + "/cs")
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
    cpl_list = root.findall(COUPLING_PATH + "/coupling")
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
    center_min = root.find(CENTER_PATH + '/min_ppm')
    center_max = root.find(CENTER_PATH + '/max_ppm')

    if (center_min is None or center_max is None):
        center : ppm = 0.0
    elif (cast(ele, center_min).text is None or cast(ele, center_max).text is None):
        center : ppm = 0.0
    else:
        center_left = cast(str, cast(ele, center_min).text)
        center_right = cast(str, cast(ele, center_max).text)
        center : ppm = (float(center_left) + float(center_right)) / 2


    return spin_names, chem_shifts, lw_list, cMatrix.astype(float), center