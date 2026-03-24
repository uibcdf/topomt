import sys

from importlib.resources import files
def path(package, file_or_dir):
    return files(package).joinpath(file_or_dir)


def first_existing_path(package, *candidates):
    for candidate in candidates:
        candidate_path = files(package).joinpath(candidate)
        if candidate_path.is_file() or candidate_path.is_dir():
            return candidate_path
    return files(package).joinpath(candidates[0])

demo = {}

# TcTIM

demo['TcTIM'] = {}
demo['TcTIM']['1tcd.pdb'] = first_existing_path(
    'topomt.data.TcTIM.CASTp_1tcd',
    '1tcd.bcif.gz',
    '1tcd.pdb',
)
demo['TcTIM']['1TCD.pdb'] = demo['TcTIM']['1tcd.pdb']
demo['TcTIM']['CASTp_1tcd'] = path('topomt.data.TcTIM', 'CASTp_1tcd')

# HIV-1 Protease

demo['HIV-1 Protease'] = {}
demo['HIV-1 Protease']['1hiv.pdb'] = first_existing_path(
    'topomt.data.HIV-1-Protease.CASTp_1hiv',
    '1hiv.bcif.gz',
    '1hiv.pdb',
)
demo['HIV-1 Protease']['1HIV.pdb'] = demo['HIV-1 Protease']['1hiv.pdb']
demo['HIV-1 Protease']['CASTp_1hiv'] = path('topomt.data.HIV-1-Protease', 'CASTp_1hiv')

# fpocket reference systems

demo['fpocket'] = {}
demo['fpocket']['1ATP.pdb'] = first_existing_path('topomt.data.fpocket4.sample', '1ATP.bcif.gz', '1ATP.pdb')
demo['fpocket']['1CEN.pdb'] = first_existing_path('topomt.data.fpocket4.sample', '1CEN.bcif.gz', '1CEN.pdb')
demo['fpocket']['1GG0.pdb'] = first_existing_path('topomt.data.fpocket4.sample', '1GG0.bcif.gz', '1GG0.pdb')
demo['fpocket']['1N57.pdb'] = first_existing_path('topomt.data.fpocket4.sample', '1N57.bcif.gz', '1N57.pdb')
demo['fpocket']['1YCR.pdb'] = first_existing_path('topomt.data.fpocket4.sample', '1YCR.bcif.gz', '1YCR.pdb')
demo['fpocket']['2GI9.pdb'] = first_existing_path('topomt.data.fpocket4.sample', '2GI9.bcif.gz', '2GI9.pdb')
demo['fpocket']['2H05.pdb'] = first_existing_path('topomt.data.fpocket4.sample', '2H05.bcif.gz', '2H05.pdb')
demo['fpocket']['2HGR.pdb'] = first_existing_path('topomt.data.fpocket4.sample', '2HGR.bcif.gz', '2HGR.pdb')
demo['fpocket']['3LKF.pdb'] = first_existing_path('topomt.data.fpocket4.sample', '3LKF.bcif.gz', '3LKF.pdb')
demo['fpocket']['3LKF_out'] = path('topomt.data.fpocket4.sample', '3LKF_out')
demo['fpocket']['E15ALA.pdb'] = first_existing_path('topomt.data.fpocket4.sample', 'E15ALA.bcif.gz', 'E15ALA.pdb')
