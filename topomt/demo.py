import sys

from importlib.resources import files
def path(package, file_or_dir):
    return files(package).joinpath(file_or_dir)

demo = {}

# TcTIM

demo['TcTIM'] = {}
demo['TcTIM']['1tcd.pdb'] = path('topomt.data.TcTIM.CASTp_1tcd', '1tcd.pdb')
demo['TcTIM']['CASTp_1tcd'] = path('topomt.data.TcTIM', 'CASTp_1tcd')

# HIV-1 Protease

demo['HIV-1 Protease'] = {}
demo['HIV-1 Protease']['1hiv.pdb'] = path('topomt.data.HIV-1-Protease.CASTp_1hiv', '1hiv.pdb')
demo['HIV-1 Protease']['CASTp_1hiv'] = path('topomt.data.HIV-1-Protease', 'CASTp_1hiv')

# FPocket2

demo['FPocket2'] = {}
demo['FPocket2']['1ATP.pdb'] = path('topomt.data.fpocket2.sample', '1ATP.pdb')
demo['FPocket2']['1CEN.pdb'] = path('topomt.data.fpocket2.sample', '1CEN.pdb')
demo['FPocket2']['1GG0.pdb'] = path('topomt.data.fpocket2.sample', '1GG0.pdb')
demo['FPocket2']['1N57.pdb'] = path('topomt.data.fpocket2.sample', '1N57.pdb')
demo['FPocket2']['1YCR.pdb'] = path('topomt.data.fpocket2.sample', '1YCR.pdb')
demo['FPocket2']['2GI9.pdb'] = path('topomt.data.fpocket2.sample', '2GI9.pdb')
demo['FPocket2']['2H05.pdb'] = path('topomt.data.fpocket2.sample', '2H05.pdb')
demo['FPocket2']['2HGR.pdb'] = path('topomt.data.fpocket2.sample', '2HGR.pdb')
demo['FPocket2']['3LKF.pdb'] = path('topomt.data.fpocket2.sample', '3LKF.pdb')
demo['FPocket2']['3LKF_out'] = path('topomt.data.fpocket2.sample', '3LKF_out')
demo['FPocket2']['E15ALA.pdb'] = path('topomt.data.fpocket2.sample', 'E15ALA.pdb')


