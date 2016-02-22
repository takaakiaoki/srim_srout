"""
library to parse output data from SRIM SR
"""

import sys
import argparse
import json

from srim_srout import stoppingunit
from srim_srout import version

class Error(Exception):
    pass

# energy conversion to keV
energy_conversion = {
    'eV': 1.0e-3,
    'keV': 1.0,
    'MeV': 1.0e3,
    'GeV': 1.0e6}

# length conversion to A
length_conversion = {
    'A': 1.0,
    'nm': 10.0,
    'um': 10.0e3,
    'mm': 10.0e6}

def parse_projectile_line(r):
    """parse projectile data line in numerical values
    Args:
        r (str): input row string, like
                 Ion = Hydrogen [1] , Mass = 1.008 amu
    Returns:
        tuple of (
            Species name,
            Atomic number,
            Atomic mass (in amu))

    Raises:
        Error: raised when number of columns or data is not sufficient.
    """
    c = r.split()
    d = (
        c[2], # Species name
        int(c[3][1:-1]), # Atomic Number
        float(c[7]) # Atomic Mass
        )

    return d

def parse_density_line(r):
    """parse density data line in numerical values
    Args:
        r (str): input row string, like
                 (sr.exe)       Target Density =  1.0597E+00 g/cm3 = 1.0903E+23 atoms/cm3
                 (srmodule.exe) Density =  1.0597E+00 g/cm3 = 1.0902E+23 atoms/cm3
                 Thus tokens should be counted from the tail.
    Returns:
        tuple of (
            mass density (in g/cm3),
            atom density (in /cm3))

    Raises:
        Error: raised when number of columns or data is not sufficient.
    """
    c = r.split()
    d = (
        float(c[-5]), # mass density
        float(c[-2]) # Atomic Number
        )

    return d

def parse_target_composition_row(r):
    """parse target composition row data in numerical values
    Args:
        r (str): input row string, like
                 H      1    061.54    010.60   
    Returns:
        tuple of (
            Symbol,
            Atomic number,
            Atomic Percent,
            Mass Percent)

    Raises:
        Error: raised when number of columns or data is not sufficient.
    """
    c = r.split()
    d = (
        c[0], # Symbol
        float(c[1]), # Atomic Number
        float(c[2]), # Atomic Percent
        float(c[3])  # Mass Percent
        )

    return d



def parse_tbl_row(r):
    """parse tbl row data in numerical values

    Args:
        r (str): input row string, like
                 10.00 keV   4.945E-01  8.762E-03    2247 A       544 A       576 A   

    Returns:
        tuple of (
            energy (in Kev),
            dE/dx Elec. (in given unit, in the file),
            dE/dx Nucl. (in given unit, in the file),
            Proj. Range (in AA),
            Long. Strgl. (in AA),
            Lat. Strgl. (in AA))

    Raises:
        Error: raised when number of columns or data is not sufficient.

    Note:
        dE/dx should be better to be normalized according to transformation table
    """
    c = r.split()
    d = (
        float(c[0]) * energy_conversion[c[1]], # energy (in Kev)
        float(c[2]), # dE/dx Elec. (in given unit, in the file),
        float(c[3]), # dE/dx Nucl. (in given unit, in the file),
        float(c[4]) * length_conversion[c[5]], # Proj. Range (in AA),
        float(c[6]) * length_conversion[c[7]], # Long. Strgl. (in AA),
        float(c[8]) * length_conversion[c[9]] # Lat. Strgl. (in AA))
        )

    return d



def parse(input):
    """parse output file

    Args:
        input (file): input stream

    Returns:
        A dict mapping keys of parsed data

    Raises:
        Error: Parse format error
    """

    # dbg = d['debug_string'] stores all string to be parsed.
    # dbg['xxx'] corresponds to the value of d['xxx']
    dbg = {}
    d = {'debug_string':dbg}

    # output from SR.exe (SRIM-2013.00) or SRModule.exe (SRIM-2012.01)
    d['filetype'] = 'sr.exe'  # or 'srmodule.exe'


    # ==================================================================
    dbg['header_ruler0'] = input.readline().strip()

    # test 'Calculation using SRIM-2006' 
    line = input.readline().strip()
    if line == 'Calculation using SRIM-2006':
        dbg['header_extra'] = line
        d['filetype'] = 'srmodule.exe'
        line = input.readline().strip()

    # SRIM version ---> SRIM-2012.01
    dbg['header_srim_version'] = line

    # Calc. date   ---> February 22, 2016 
    dbg['header_date'] = input.readline().strip()

    # ==================================================================
    dbg['header_ruler1'] = input.readline().strip()

    # skip one line
    input.readline()

    # Disk File Name = Hydrogen in 1_3 Propanediol
    dbg['disk_file_name'] = input.readline().strip()

    # skip one line
    input.readline()

    # (sr.exe)       Ion = Hydrogen [1] , Mass = 1.008 amu
    # (srmodule.exe) Ion = Hydrogen     [1] , Mass = 1.008 amu
    dbg['projectile'] = input.readline().strip()
    d['projectile_name'], d['projectile_z'], d['projectile_amu'] \
        = parse_projectile_line(dbg['projectile'])

    # skip one line
    input.readline()

    # (sr.exe)       Target Density =  1.0597E+00 g/cm3 = 1.0903E+23 atoms/cm3
    # (srmodule.exe) Density =  1.0597E+00 g/cm3 = 1.0902E+23 atoms/cm3
    dbg['density'] = input.readline().strip()
    d['density_mass'], d['density_atom'] = parse_density_line(dbg['density'])

    # ======= Target  Composition ========
    dbg['target_comp_ruler0'] = input.readline().strip()

    # Atom   Atom   Atomic    Mass     
    dbg['target_comp_header1'] = input.readline().strip()

    # Name   Numb   Percent   Percent  
    dbg['target_comp_header2'] = input.readline().strip()

    # ----   ----   -------   -------  
    dbg['target_comp_subrulee'] = input.readline().strip()

    # read target compsition data
    d['target_composition'] = []
    dbg['target_composition'] = []

    while True:
        # H      1    061.54    010.60   
        #    or
        # ====================================
        line = input.readline().strip()
        if line == '====================================':
            dbg['target_comp_ruler1'] = line
            break
        else:
            dbg['target_composition'].append(line)
            d['target_composition'].append(parse_target_composition_row(line))

    # Bragg Correction = -5.43%
    dbg['bragg_corr'] = input.readline().strip()
    sp = dbg['bragg_corr'].split()
    d['bragg_corr'] = float(sp[-1][:-1])  # store in percent

    # (sr.exe)       Stopping Units =  MeV / (mg/cm2) 
    # (srmodule.exe) Stopping Units =  MeV/(mg/cm2) 
    dbg['stopping_units'] = input.readline().strip()
    # d['stopping_units'] stores in more compact format, description by SRModule.exe
    s = dbg['stopping_units'][len('Stopping Units ='):].strip()
    d['stopping_units'] = stoppingunit.by_title[s][3]

    # See bottom of Table for other Stopping units 
    dbg['stopping_units_comment'] = input.readline().strip()

    # skip one line
    input.readline()

    # (sr.exe)       (no element)
    # (srmodule.exe) Ion = Hydrogen     [1] , Mass = 1.008 amu
    if d['filetype'] == 'srmodule.exe':
        dbg['projectile_extra'] = input.readline().strip()
        # skip one line
        input.readline()

    # Ion        dE/dx      dE/dx     Projected  Longitudinal   Lateral
    dbg['tbl_header1'] = input.readline().strip()
    # Energy      Elec.      Nuclear     Range     Straggling   Straggling
    dbg['tbl_header2'] = input.readline().strip()
    # --------------  ---------- ---------- ----------  ----------  ----------
    dbg['tbl_ruler0'] = input.readline().strip()

    d['tbl_data'] = []
    dbg['tbl_data'] = []

    while True:
        line = input.readline().strip()
        # 10.00 keV   4.945E-01  8.762E-03    2247 A       544 A       576 A   
        #   or
        # -----------------------------------------------------------
        if line == '-----------------------------------------------------------':
            # end of parse
            dbg['tbl_ruler1'] = line
            return d
        else:
            dbg['tbl_data'].append(line)
            # parse data
            d['tbl_data'].append(parse_tbl_row(line))


# run as script
def main(args=sys.argv):
    aparser = argparse.ArgumentParser()

    aparser.add_argument('input', nargs='?',
            type=argparse.FileType('rt'),
            help='input file to parse default is sys.stdin',
            default=sys.stdin)
    aparser.add_argument('output', nargs='?',
            type=argparse.FileType('wt'),
            help='JSON output stream default is sys.stdout',
            default=sys.stdout)
    aparser.add_argument('--verbose', '-v', action='store_true',
            help='dump including raw input string data',
            default=False) 

    try:
        args = aparser.parse_args(args[1:])
    except SystemExit as err:
        # copy from sphinx-quickstart using optparse (not argparse)
        return err.code
    except:
        # other exception during parse arguments
        return

    d = parse(args.input)

    if not args.verbose:
        del(d['debug_string'])

    # dump as json
    json.dump(d, args.output, indent=2)

if __name__ == '__main__':
    sys.exit(main(sys.argv))
