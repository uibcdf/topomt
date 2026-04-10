import pytest
import numpy as np
import molsysmt as msm
from topomt.dfnd import dfnd

pytestmark = pytest.mark.skip(reason="DFND is postponed and not yet implemented")
from topomt.features import Pocket, Void
import topomt as tmt # Assuming topomt is installed and demo data is accessible

# Use a standard PDB from the demo data for testing
def get_sample_molecular_system():
    # Example: HIV-1 Protease 1HIV
    pdb_file = tmt.demo['HIV-1 Protease']['1HIV.pdb']
    return pdb_file

def test_dfnd_returns_expected_structure():
    """
    Test that dfnd runs and returns a dictionary with the expected 'wet' and 'dry' keys
    and that their contents are lists of topomt.features.Pocket/Void or dicts for dry.
    """
    sample_molecular_system = get_sample_molecular_system()
    # Run DFND with default parameters
    result = dfnd(sample_molecular_system)

    # Assert top-level structure
    assert isinstance(result, dict)
    assert 'wet' in result
    assert 'dry' in result

    # Assert 'wet' structure and content types
    assert isinstance(result['wet'], dict)
    assert 'pockets' in result['wet']
    assert 'voids' in result['wet']
    assert isinstance(result['wet']['pockets'], list)
    assert isinstance(result['wet']['voids'], list)
    
    # Assert type of features in 'wet' part
    if result['wet']['pockets']:
        assert isinstance(result['wet']['pockets'][0], Pocket)
        assert hasattr(result['wet']['pockets'][0], 'atom_indices')
        assert hasattr(result['wet']['pockets'][0], 'tetrahedron_indices')
    if result['wet']['voids']:
        assert isinstance(result['wet']['voids'][0], Void)
        assert hasattr(result['wet']['voids'][0], 'atom_indices')
        assert hasattr(result['wet']['voids'][0], 'tetrahedron_indices')

    # Assert 'dry' structure and content types (raw dicts expected for now)
    assert isinstance(result['dry'], dict)
    assert 'core' in result['dry']
    assert 'islands' in result['dry']
    
    if result['dry']['core']:
        assert isinstance(result['dry']['core'], dict)
        assert 'tetrahedron_indices' in result['dry']['core']
        assert 'atom_indices' in result['dry']['core']
    if result['dry']['islands']:
        assert isinstance(result['dry']['islands'], list)
        assert isinstance(result['dry']['islands'][0], dict)


def test_dfnd_parameters_affect_output():
    """
    Test that changing probe_radius affects the number of pockets/voids found.
    """
    sample_molecular_system = get_sample_molecular_system()

    # Run with default probe_radius (1.4)
    result_default = dfnd(sample_molecular_system)
    n_pockets_default = len(result_default['wet']['pockets'])
    n_voids_default = len(result_default['wet']['voids'])

    # Run with a larger probe_radius (should yield fewer/smaller features)
    result_larger_probe = dfnd(sample_molecular_system, probe_radius=2.0)
    n_pockets_larger = len(result_larger_probe['wet']['pockets'])
    n_voids_larger = len(result_larger_probe['wet']['voids'])

    # These are qualitative checks for now, without specific numerical assertions
    # A larger probe should generally mean fewer/smaller features, so counts might decrease
    # or remain same but not increase significantly for well-defined features.
    assert n_pockets_larger <= n_pockets_default
    assert n_voids_larger <= n_voids_default

    # Run with a very large probe_radius (should yield very few or zero features)
    result_very_large_probe = dfnd(sample_molecular_system, probe_radius=5.0)
    n_pockets_very_large = len(result_very_large_probe['wet']['pockets'])
    n_voids_very_large = len(result_very_large_probe['wet']['voids'])

    assert n_pockets_very_large <= n_pockets_larger
    assert n_voids_very_large <= n_voids_larger
