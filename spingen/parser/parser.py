from argparse import ArgumentParser
from argparse import Namespace

def parse(argv : list[str]) -> Namespace:
    parser = ArgumentParser(prog='spingen', description='Insert description here')

    parser.add_argument('-help', action='help')
    parser.add_argument('-in', '--input', type=str, metavar='File Path',
                        required=True, help="Input XML file for spin matrix")
    parser.add_argument('-fs', '--field-strength', type=int, metavar='Value (HZ)', 
                        default=500, help="NMR instrument field strength for conversions")
    parser.add_argument('-pts', '--points', type=int, metavar='Value',
                        default=1000, help="NMR resolution by number of points")
    parser.add_argument('-sw', '--spec-width', type=int, metavar='Value',
                        default=50, help="Spectral width of NMR data")
    parser.add_argument('-obs', '--obs-freq', type=int, metavar='Value',
                        default=50, help='Observation fequency value')
    parser.add_argument('-d', '--domain', type=str, choices=['time', 't', 'f', 'freq'],
                        dest='domain', nargs='?', default='f', const='f', help='Data output domain type')
    parser.add_argument('-out', '-output', type=str, metavar='File Path',
                        default='output_peaks', help='Designated output file location')
    parser.add_argument('-fmt', '-format', type=str, metavar='', choices=['csv','txt','npy'],
                        nargs='?', default='csv', const='csv', help='Designated output file format')
    return parser.parse_args(argv)