"""
library to parse output data from SRIM SR
"""

import sys
import argparse

import srim_srout.stoppingunit

class Error(Exception):
    pass

def parse(input):
    """parse output file

    Args:
        input (file): input stream

    Returns:
        parsed data object

    Raises:
        Error: Parse format error
    """

    d = {}
    
    # output from SR.exe (SRIM-2013.00) or SRModule.exe (SRIM-2012.01)
    d['filetype'] = 'sr.exe'  # or 'srmodule.exe'

    # _s suffix means string data read as it is

    # ==================================================================
    d['header_ruler0_s'] = input.readline().strip()

    # test 'Calculation using SRIM-2006' 
    line = input.readline().strip()
    if line == 'Calculation using SRIM-2006':
        d['header_extra_s'] = line
        d['filetype'] = 'srmodule.exe'
        line = input.readline().strip()

    # SRIM version ---> SRIM-2012.01
    d['header_srim_version_s'] = line

    # Calc. date   ---> February 22, 2016 
    d['header_date_s'] = input.readline().strip()

    # ==================================================================
    d['header_ruler1_s'] = input.readline().strip()

    # skip one line
    input.readline()

    # Disk File Name = Hydrogen in 1_3 Propanediol
    d['disk_file_name_s'] = input.readline().strip()

    # skip one line
    input.readline()

    # (sr.exe)       Ion = Hydrogen [1] , Mass = 1.008 amu
    # (srmodule.exe) Ion = Hydrogen     [1] , Mass = 1.008 amu
    d['projectile1_s'] = input.readline().strip()

    # skip one line
    input.readline()

    # (sr.exe)       Target Density =  1.0597E+00 g/cm3 = 1.0903E+23 atoms/cm3
    # (srmodule.exe) Density =  1.0597E+00 g/cm3 = 1.0902E+23 atoms/cm3
    d['density_s'] = input.readline().strip()

    # ======= Target  Composition ========
    d['target_comp_ruler0_s'] = input.readline().strip()

    # Atom   Atom   Atomic    Mass     
    d['target_comp_header1_s'] = input.readline().strip()

    # Name   Numb   Percent   Percent  
    d['target_comp_header2_s'] = input.readline().strip()

    # ----   ----   -------   -------  
    d['target_comp_subrulee_s'] = input.readline().strip()

    # read target compsition data
    d['target_composition_s'] = []
    d['target_composition'] = []

    while True:
        # H      1    061.54    010.60   
        #    or
        # ====================================
        line = input.readline().strip()
        if line == '====================================':
            d['target_comp_ruler1_s'] = line
            break
        else:
            d['target_composition_s'].append(line)

    # Bragg Correction = -5.43%
    d['bragg_corr_s'] = input.readline().strip()

    # (sr.exe)       Stopping Units =  MeV / (mg/cm2) 
    # (srmodule.exe) Stopping Units =  MeV/(mg/cm2) 
    d['stopping_units_s'] = input.readline().strip()

    # See bottom of Table for other Stopping units 
    d['stopping_units_comment_s'] = input.readline().strip()

    # skip one line
    input.readline()

    # (sr.exe)       (no element)
    # (srmodule.exe) Ion = Hydrogen     [1] , Mass = 1.008 amu
    if d['filetype'] == 'srmodule.exe':
        d['projectile_extra_s'] = input.readline().strip()
        # skip one line
        input.readline()

    # Ion        dE/dx      dE/dx     Projected  Longitudinal   Lateral
    d['tbl_header1_s'] = input.readline().strip()
    # Energy      Elec.      Nuclear     Range     Straggling   Straggling
    d['tbl_header2_s'] = input.readline().strip()
    # --------------  ---------- ---------- ----------  ----------  ----------
    d['tbl_ruler0_s'] = input.readline().strip()

    d['tbl_data_s'] = []
    d['tbl_data'] = []

    while True:
        line = input.readline().strip()
        # 10.00 keV   4.945E-01  8.762E-03    2247 A       544 A       576 A   
        #   or
        # -----------------------------------------------------------
        if line == '-----------------------------------------------------------':
            # end of parse
            d['tbl_ruler1_s'] = line
            return d
        else:
            d['tbl_data_s'].append(line)
            # parse data

# run as script
def main(args=sys.argv):
    aparser = argparse.ArgumentParser()

    aparser.add_argument('input', nargs='?',
            type=argparse.FileType('rt'),
            help='input file to parse default is sys.stdin',
            default=sys.stdin)
    aparser.add_argument('output', nargs='?',
            type=argparse.FileType('wt'),
            help='output stream default is sys.stdout',
            default=sys.stdout)

    try:
        args = aparser.parse_args(args[1:])
    except SystemExit as err:
        # copy from sphinx-quickstart using optparse (not argparse)
        return err.code
    except:
        # other exception during parse arguments
        return

    d = parse(args.input)

    print(d, file=args.output)

if __name__ == '__main__':
    sys.exit(main(sys.argv))
