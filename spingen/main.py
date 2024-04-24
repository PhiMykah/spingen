import sys
from spingen.parser import *
from spingen.data import SSystem, frequency_to_time
import numpy as np
from spingen.iostream import loadSystems
from pathlib import Path

def main():
    """Main entry-point
    """
    argv = parse(sys.argv[1:])

    systems : list[SSystem] = []
    
    field_strength = argv.field_strength
    points = argv.points
    spec_width = argv.spec_width
    obs_freq = argv.obs_freq
    output = Path(argv.out).stem
    format = argv.fmt
    domain = argv.domain
    # Somewhere specify solvent
    system_count = argv.sub_count

    systems = loadSystems(argv.input, system_count, field_strength, points, spec_width, obs_freq)

    output_system = systems[0]

    for i in range(1, len(systems)):
        output_system += systems[i]
    
    peaks = np.array(output_system.peaklist())
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
                

if __name__ == "__main__":
    main()