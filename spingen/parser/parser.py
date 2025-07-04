from argparse import ArgumentParser
from argparse import Namespace

def parse(argv : list[str]) -> Namespace:
    parser = ArgumentParser(prog='spingen', description='Insert description here')

    parser.add_argument('-help', action='help')
    parser.add_argument('-in', '--input', type=str, metavar='File Path',
                        required=True, help="Input XML file for spin matrix or spin matrix text")
    parser.add_argument('-lw', '--line-widths', type=list, metavar='Line Width Values', dest='lw',
                        nargs='+', default=None, help='Line widths for each molecule when loading text')
    parser.add_argument('-fs', '--field-strength', type=float, metavar='Value (MHZ)', 
                        default=500, help="NMR instrument field strength for conversions")
    parser.add_argument('-pts', '--points', type=int, metavar='Value',
                        default=1000, help="NMR resolution by number of points")
    parser.add_argument('-sw', '--spec-width', type=float, metavar='Value',
                        default=50, help="Spectral width of NMR data")
    parser.add_argument('-obs', '--obs-freq', type=float, metavar='Value',
                        default=50, help='Observation fequency value')
    parser.add_argument('-sc', '--sub-count', type=int, metavar='Values',
                        dest='sub_count', default=0, help='Number of independent subset spin matrices')
    parser.add_argument('-d', '--domain', type=str, choices=['time', 't', 'f', 'freq'],
                        dest='domain', nargs='?', default='f', const='f', help='Data output domain type')
    parser.add_argument('-out', '-output', type=str, metavar='File Path',
                        default='output_peaks', help='Designated output file location')
    parser.add_argument('-fmt', '-format', type=str, metavar='', choices=['csv','txt','npy'],
                        nargs='?', default='csv', const='csv', help='Designated output file format')
    parser.add_argument('-convert', type=str, metavar='NMR File', dest='convert',
                        default='', help='NMRPipe format file to convert to ppm')
    parser.add_argument('-w', type=float, default=1, metavar='[1]', dest='w', help='Peak width at half height')
    return parser.parse_args(argv)