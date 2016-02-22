"""
stopping unit, seq, title and translation coefficient
"""

# (index, coefficient, title1, title2)
# title1 is the string should match with 
#    'Stopping Units =  MeV/(mg/cm2)' line in output by SR.exe
# title2 is by SRModule.exe
params = [
    (1, 1.0597E+01, 'eV / Angstrom', 'eV/Angstrom'),
    (2, 1.0597E+02, 'keV / micron', 'keV/micron'),
    (3, 1.0597E+02, 'MeV / mm', 'MeV/mm'), 
    (4, 1.0000E+00, 'keV / (ug/cm2)', 'keV/(ug/cm2)'),
    (5, 1.0000E+00, 'MeV / (mg/cm2)', 'MeV/(mg/cm2)'),
    (6, 1.0000E+03, 'keV / (mg/cm2)', 'keV/(mg/cm2)'),
    (7, 9.7198E+00, 'eV / (1E15 atoms/cm2)', 'eV/(1E15 atoms/cm2)'),
    (8, 4.3194E+00, 'L.S.S. reduced units', 'L.S.S. reduced units')]

by_title = dict([(i[2], i) for i in params] +
                [(i[3], i) for i in params])
by_index = dict([(i[0], i) for i in params])
