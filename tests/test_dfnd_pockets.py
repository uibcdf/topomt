from pathlib import Path

from topomt.dfnd import dfnd


def _write_minimal_pdb(path: Path) -> None:
    path.write_text(
        '\n'.join(
            [
                'ATOM      1  C1  GLY A   1       1.874   1.874   1.874  1.00  0.00           C',
                'ATOM      2  C2  GLY A   1       1.874  -1.874  -1.874  1.00  0.00           C',
                'ATOM      3  C3  GLY A   1      -1.874   1.874  -1.874  1.00  0.00           C',
                'ATOM      4  C4  GLY A   1      -1.874  -1.874   1.874  1.00  0.00           C',
                'END',
                '',
            ]
        )
    )


def test_dfnd_public_api_smoke_with_molsysmt_input(tmp_path):
    pdb_path = tmp_path / 'minimal.pdb'
    _write_minimal_pdb(pdb_path)

    result = dfnd(
        str(pdb_path),
        probe_radius=1.4,
        min_size=0,
        hydrogen_policy='exclude',
        transit_policy='resident_only',
    )

    assert 'raw' in result
    assert 'wet' in result
    assert 'dry' in result
    assert result['raw']['parameters']['hydrogen_policy'] == 'exclude'
    assert result['raw']['parameters']['transit_policy'] == 'resident_only'
    assert len(result['raw']['tetrahedra']) == 1
    assert len(result['raw']['concavity_domains']) == 1
    assert result['raw']['concavity_domains'][0]['domain_family'] == 'void_domain'


def test_get_topography_dfnd_returns_topography_with_raw_records(tmp_path):
    from topomt import Topography, get_topography

    pdb_path = tmp_path / 'minimal.pdb'
    _write_minimal_pdb(pdb_path)

    topography = get_topography(
        str(pdb_path),
        method='dfnd',
        probe_radius=1.4,
        min_size=0,
        hydrogen_policy='exclude',
        transit_policy='resident_only',
    )

    assert isinstance(topography, Topography)
    assert hasattr(topography, 'dfnd_records')
    assert hasattr(topography, 'dfnd_result')
    assert topography.dfnd_concavity_domains is topography.dfnd_records['concavity_domains']
    assert topography.dfnd_external_links is topography.dfnd_records['external_links']
    assert topography.dfnd_dry_components is topography.dfnd_result['dry']['components']
    assert topography.dfnd_dry_interfaces is topography.dfnd_records['dry_interfaces']
    assert topography.dfnd_dry_motifs is topography.dfnd_records['dry_motifs']
    assert (
        topography.dfnd_surface_concavities
        is topography.dfnd_result['wet']['surface_concavities']
    )
    assert (
        topography.dfnd_nonresident_passages
        is topography.dfnd_result['wet']['nonresident_passages']
    )
    assert (
        topography.dfnd_degenerate_subprobe_domains
        is topography.dfnd_result['wet']['degenerate_subprobe_domains']
    )
    assert topography.dfnd_records['parameters']['transit_policy'] == 'resident_only'
    voids = topography.get_features(by='type', value='void')
    assert len(voids) == 1
    void = next(iter(voids))
    assert void.source == 'dfnd'
    assert void.domain_family == 'void_domain'
    assert void.raw_record['domain_family'] == 'void_domain'


def test_get_topography_dfnd_smoke_with_real_small_pdb():
    from topomt import Topography, get_topography

    pdb_path = Path('topomt/data/CASTp_3.0_server/3ptb.pdb')
    assert pdb_path.exists()

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
    assert hasattr(topography, 'dfnd_records')
    records = topography.dfnd_records
    assert records['parameters']['selection'] == "molecule_type in ['protein', 'peptide']"
    assert records['parameters']['transit_policy'] == 'with_connectors'
    assert len(records['tetrahedra']) > 0
    assert len(records['faces']) == 4 * len(records['tetrahedra'])
    assert len(records['concavity_domains']) >= 1

    n_public_domains = sum(
        1
        for domain in records['concavity_domains']
        if domain['domain_family'] in {
            'void_domain',
            'pocket_domain',
            'multi_external_link_domain',
        }
    )
    assert len(topography) == n_public_domains
    assert len(topography.get_features(by='shape', value='concavity')) == n_public_domains

    public_families = {
        'void_domain',
        'pocket_domain',
        'multi_external_link_domain',
    }
    required_fields = {
        'atom_indices',
        'center',
        'domain_family',
        'flags',
        'mouth_area',
        'mouth_face_clusters',
        'mouths',
        'n_mouths',
        'raw_record',
        'resident_tetrahedron_indices',
        'source',
        'source_id',
        'tetrahedron_indices',
        'transit_connector_tetrahedron_indices',
        'volume_solvent_estimate',
        'volume_topological_resident',
    }
    for feature in topography.get_features(by='shape', value='concavity'):
        for field in required_fields:
            assert hasattr(feature, field)
        assert feature.source == 'dfnd'
        assert feature.domain_family in public_families
        assert feature.raw_record['domain_family'] == feature.domain_family
        assert feature.raw_record['atom_indices'] == feature.atom_indices
        assert feature.raw_record['tetrahedron_indices'] == feature.tetrahedron_indices
        assert feature.raw_record['volume_solvent_estimate'] >= 0.0
        assert feature.raw_record['volume_solvent_estimate'] <= feature.raw_record[
            'volume_topological_resident'
        ]
