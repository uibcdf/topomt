# Configuration file for TopoMT

from .logging_setup import setup_logging

# Set this variable true while testing
_testing = False

# Set this variable true while debugging
_debugging = False

# Units

def set_default_quantities_form(form='pint'):

    from topomt import pyunitwizard as puw
    puw.configure.set_default_form(form)

def set_default_quantities_parser(form='pint'):

    from topomt import pyunitwizard as puw
    puw.configure.set_default_parser(form)

def set_default_standard_units(standards=['nm', 'ps', 'K', 'mole', 'amu', 'e',
    'kJ/mol', 'kJ/(mol*nm**2)', 'N', 'degrees']):

    from topomt import pyunitwizard as puw
    puw.configure.set_standard_units(standards)

# NGLview and Sphinx

# Is sphinx working?
#from os import environ
#view_from_htmlfiles=('SPHINXWORKING' in environ)
#del(environ)

from .defaults import atom_label_format
