import sys
from spingen.parser import *
import numpy as np
from pathlib import Path
from spingen.modules import nmrConvert, get_peaksXML, get_peaks_from_file

def main():
    """Main entry-point
    """
    argv = parse(sys.argv[1:])
    
    field_strength = argv.field_strength
    points = argv.points
    spec_width = argv.spec_width
    obs_freq = argv.obs_freq
    input : str = argv.input
    lws : list[float] | None = argv.lw
    output = Path(argv.out).stem
    format = argv.fmt
    domain = argv.domain
    convert = argv.convert
    w = argv.w

    # Somewhere specify solvent
    system_count = argv.sub_count

    if input.lower().endswith('.xml'):
        peaks = get_peaksXML(input, system_count, field_strength, points, spec_width, obs_freq, w)
    else:
        if lws is None:
            lws = [1.0]
        peaks = get_peaks_from_file(input, lws, field_strength, points, spec_width, obs_freq, w)
    
    # if domain in ['t', 'time']:
    #     peaks = frequency_to_time(peaks)
    # if len(systems) == 1:
    #     output = output_file
    # else:
    #     output = output_file + "_{:02}".format(i+1)
    match format:
        case 'npy':
            np.save(output, peaks)
        case 'csv':
            np.savetxt(f"{output}.{format}", peaks, delimiter=',')
        case _:
            np.savetxt(f"{output}.{format}", peaks)
    
    if not convert:
        return
    
    nmr_peaks = nmrConvert(convert)

    nmr_output = Path(convert).stem
    match format:
        case 'npy':
            np.save(nmr_output, nmr_peaks)
        case 'csv':
            np.savetxt(f"{nmr_output}.{format}", nmr_peaks, delimiter=',')
        case _:
            np.savetxt(f"{nmr_output}.{format}", nmr_peaks)

if __name__ == "__main__":
    main()