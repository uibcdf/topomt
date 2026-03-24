# Configure PyUnitWizard

import pyunitwizard

standards = [
    'nm',      # length: nanometer
    'ps',      # time: picosecond
    'K',       # temperature: kelvin
    'mole',    # amount: mole
    'dalton',  # mass
    'e',       # charge: elementary charge
    'kJ/mol',  # energy: kilojoules/mole
    'kJ/(mol*nm)',
    'kJ/(mol*nm**2)',
    'radians',
]

pyunitwizard.configure.set_default_form('pint')
pyunitwizard.configure.set_default_parser('pint')
pyunitwizard.configure.set_standard_units(standards)
pyunitwizard.register_fast_track('nanometers', pyunitwizard.unit('nm'))
pyunitwizard.register_fast_track('picoseconds', pyunitwizard.unit('ps'))
pyunitwizard.register_fast_track('kelvin', pyunitwizard.unit('K'))

