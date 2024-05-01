import sys
from spingen.parser import *
from spingen.data import SSystem, frequency_to_time
import numpy as np
from spingen.iostream import loadSystems
from pathlib import Path
from nmrsim.plt import mplplot

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
    convert = argv.convert

    # Somewhere specify solvent
    system_count = argv.sub_count

    systems = loadSystems(argv.input, system_count, field_strength, points, spec_width, obs_freq)

    output_system = systems[0]

    for i in range(1, len(systems)):
        output_system += systems[i]
    
    x,y = mplplot(output_system.peaklist(), hidden=True)
    peaks = np.array([x,y]).T
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
    
    print("Importing nmrPype...", file=sys.stderr)
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

    nmr_output = Path(convert).stem
    match format:
        case 'npy':
            np.save(nmr_output, converted_array)
        case 'csv':
            np.savetxt(f"{nmr_output}.{format}", converted_array, delimiter=',')
        case _:
            np.savetxt(f"{nmr_output}.{format}", converted_array)
if __name__ == "__main__":
    main()