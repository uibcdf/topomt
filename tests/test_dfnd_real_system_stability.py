from pathlib import Path
from zipfile import ZipFile

import pytest

from topomt import Topography, get_topography
from topomt.dfnd.graph import DelaunayFlowNetwork


SMALL_CASTPFOLD_SYSTEMS = ('1crn', '1rop')
PUBLIC_DOMAIN_FAMILIES = {
    'void',
    'pocket',
    'channel',
}


def _extract_pdb_from_castpfold_zip(pdb_id: str, tmp_path: Path) -> Path:
    zip_path = Path('topomt/data/CASTpFold_server') / f'{pdb_id}.zip'
    assert zip_path.exists()
    with ZipFile(zip_path) as zip_file:
        pdb_names = sorted(
            name for name in zip_file.namelist() if name.lower().endswith('.pdb')
        )
        assert pdb_names
        output_path = tmp_path / f'{pdb_id}.pdb'
        output_path.write_bytes(zip_file.read(pdb_names[0]))
        return output_path


@pytest.mark.parametrize('pdb_id', SMALL_CASTPFOLD_SYSTEMS)
def test_dfnd_real_small_system_stability_smoke(pdb_id, tmp_path):
    pdb_path = _extract_pdb_from_castpfold_zip(pdb_id, tmp_path)

    topography = get_topography(
        str(pdb_path),
        method='dfnd',
        selection="molecule_type in ['protein', 'peptide']",
        probe_radius=1.4,
        min_size=0,
        hydrogen_policy='exclude',
        transit_policy='with_connectors',
    )

    assert isinstance(topography, Topography)
    assert topography.dfnd is not None
    records = topography.dfnd.raw
    assert records['parameters']['selection'] == "molecule_type in ['protein', 'peptide']"
    assert records['parameters']['transit_policy'] == 'with_connectors'
    assert len(records['tetrahedra']) > 0
    assert len(records['faces']) == 4 * len(records['tetrahedra'])
    assert len(records['wet_components']) >= 1

    expected_public_count = sum(
        1
        for domain in records['wet_components']
        if domain['family'] in PUBLIC_DOMAIN_FAMILIES
    )
    public_features = topography.get_features(by='shape', value='concavity')
    assert len(public_features) == expected_public_count
    # Phase 3 promotes each mouth to a child Mouth feature, so the total feature
    # count includes those boundary features in addition to the concavities.
    assert len(topography) >= expected_public_count

    for domain in records['wet_components']:
        assert domain['volume_solvent_estimate'] >= 0.0
        assert domain['volume_solvent_estimate'] <= domain['volume_topological_resident']
        assert domain['n_nodes'] == len(domain['tetrahedron_ids'])
        assert domain['n_resident_nodes'] == len(domain['resident_tetrahedron_ids'])
        assert domain['n_transit_connector_nodes'] == len(
            domain['transit_connector_tetrahedron_ids']
        )


@pytest.mark.parametrize('pdb_id', ('1rop', '2pk4'))
def test_dfnd_selection_all_vs_protein_only_composition_smoke(pdb_id, tmp_path):
    pdb_path = _extract_pdb_from_castpfold_zip(pdb_id, tmp_path)

    protein_topography = get_topography(
        str(pdb_path),
        method='dfnd',
        selection="molecule_type in ['protein', 'peptide']",
        probe_radius=1.4,
        min_size=0,
        hydrogen_policy='exclude',
        transit_policy='with_connectors',
    )
    all_topography = get_topography(
        str(pdb_path),
        method='dfnd',
        selection='all',
        probe_radius=1.4,
        min_size=0,
        hydrogen_policy='exclude',
        transit_policy='with_connectors',
    )

    protein_records = protein_topography.dfnd.raw
    all_records = all_topography.dfnd.raw
    assert (
        protein_records['parameters']['selection']
        == "molecule_type in ['protein', 'peptide']"
    )
    assert all_records['parameters']['selection'] == 'all'

    protein_atoms = {
        atom_index
        for tetrahedron in protein_records['tetrahedra']
        for atom_index in tetrahedron['atom_indices']
    }
    all_atoms = {
        atom_index
        for tetrahedron in all_records['tetrahedra']
        for atom_index in tetrahedron['atom_indices']
    }
    assert protein_atoms < all_atoms
    assert len(all_records['tetrahedra']) > len(protein_records['tetrahedra'])
    assert len(all_records['faces']) == 4 * len(all_records['tetrahedra'])
    assert len(protein_records['faces']) == 4 * len(protein_records['tetrahedra'])

    for records in (protein_records, all_records):
        for domain in records['wet_components']:
            assert domain['volume_solvent_estimate'] >= 0.0
            assert (
                domain['volume_solvent_estimate']
                <= domain['volume_topological_resident']
            )
            assert domain['n_nodes'] == len(domain['tetrahedron_ids'])


@pytest.mark.parametrize('pdb_id', ('1crn', '1rop'))
def test_dfnd_network_can_be_reused_for_multiple_probe_radii(pdb_id, tmp_path):
    pdb_path = _extract_pdb_from_castpfold_zip(pdb_id, tmp_path)
    network = DelaunayFlowNetwork(
        str(pdb_path),
        selection="molecule_type in ['protein', 'peptide']",
        hydrogen_policy='exclude',
    )

    low_probe = network.get_topography(
        probe_radius=1.0,
        min_size=0,
        transit_policy='with_connectors',
    )
    high_probe = network.get_topography(
        probe_radius=1.4,
        min_size=0,
        transit_policy='with_connectors',
    )

    low_tetrahedra = low_probe['raw']['tetrahedra']
    high_tetrahedra = high_probe['raw']['tetrahedra']
    assert len(low_tetrahedra) == len(high_tetrahedra) == network.n_tetrahedra

    low_resident = sum(
        1 for record in low_tetrahedra if record['residence_state'] == 'resident'
    )
    high_resident = sum(
        1 for record in high_tetrahedra if record['residence_state'] == 'resident'
    )
    low_permeable_faces = sum(
        1
        for record in low_probe['raw']['faces']
        if record['permeability_state'] == 'permeable'
    )
    high_permeable_faces = sum(
        1
        for record in high_probe['raw']['faces']
        if record['permeability_state'] == 'permeable'
    )
    low_volume = sum(
        domain['volume_solvent_estimate']
        for domain in low_probe['raw']['wet_components']
    )
    high_volume = sum(
        domain['volume_solvent_estimate']
        for domain in high_probe['raw']['wet_components']
    )

    assert low_resident >= high_resident
    assert low_permeable_faces >= high_permeable_faces
    assert low_volume >= high_volume
