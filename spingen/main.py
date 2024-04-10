import sys
from spingen.parser import *
from spingen.data import SSystem
import numpy as np
from spingen.iostream import readXML
from pathlib import Path

def main():
    """Main entry-point
    """
    argv = parse(sys.argv[1:])
    names, shifts, widths, matrix, center = readXML(argv.input)
    
    field_strength = argv.field_strength
    points = argv.points
    spec_width = argv.spec_width
    obs_freq = argv.obs_freq
    output_file = Path(argv.out).stem
    format = argv.fmt
    # Somewhere specify solvent

    newSystem = SSystem(names, shifts, widths, matrix, field_strength, points, spec_width, obs_freq, center)

    peaks = np.array(newSystem.peaklist())

    if format == 'npy':
        np.save(output_file, peaks)
    elif format == 'csv':
        np.savetxt(f"{output_file}.{format}", peaks, delimiter=',')
    else:
        np.savetxt(f"{output_file}.{format}", peaks)

if __name__ == "__main__":
    main()