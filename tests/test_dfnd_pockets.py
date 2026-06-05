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
    assert len(result['raw']['wet_components']) == 1
    assert result['raw']['wet_components'][0]['family'] == 'void'


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

    from topomt.dfnd.components import WetComponent, DryComponent

    assert isinstance(topography, Topography)
    assert topography.dfnd is not None
    dfnd_data = topography.dfnd
    components = dfnd_data.dfn.components
    # the typed registry mirrors Topography; components are typed objects
    assert len(components.wet) == len(dfnd_data.raw['wet_components'])
    assert all(isinstance(c, WetComponent) for c in components.wet)
    assert all(isinstance(c, DryComponent) for c in components.dry)
    assert components.by_family('void')                        # void domain promoted below
    # graph-level relations still reference the raw records
    assert dfnd_data.dfn.graph.external_links is dfnd_data.raw['external_links']
    assert components.interfaces is dfnd_data.raw['dry_interfaces']
    assert components.motifs is dfnd_data.raw['dry_motifs']
    assert isinstance(components.surface_concavities, list)
    assert isinstance(components.nonresident_passages, list)
    assert isinstance(components.degenerate_subprobes, list)
    assert dfnd_data.dfn.parameters['transit_policy'] == 'resident_only'
    assert len(dfnd_data.mesh.faces) == 4 * len(dfnd_data.mesh.tetrahedra)
    voids = topography.get_features(by='type', value='void')
    assert len(voids) == 1
    void = next(iter(voids))
    assert void.source == 'dfnd'
    assert void.family == 'void'
    assert void.raw_record['family'] == 'void'


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
    assert topography.dfnd is not None
    records = topography.dfnd.raw
    assert records['parameters']['selection'] == "molecule_type in ['protein', 'peptide']"
    assert records['parameters']['transit_policy'] == 'with_connectors'
    assert len(records['tetrahedra']) > 0
    assert len(records['faces']) == 4 * len(records['tetrahedra'])
    assert len(records['wet_components']) >= 1

    n_public_domains = sum(
        1
        for domain in records['wet_components']
        if domain['family'] in {
            'void',
            'pocket',
            'channel',
        }
    )
    assert len(topography.get_features(by='shape', value='concavity')) == n_public_domains
    # Phase 3 also promotes each mouth (external link) to a child Mouth feature,
    # so the total feature count includes those boundary features as well.
    assert len(topography) >= n_public_domains

    public_families = {
        'void',
        'pocket',
        'channel',
    }
    required_fields = {
        'atom_indices',
        'center',
        'family',
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
        assert feature.family in public_families
        assert feature.raw_record['family'] == feature.family
        assert feature.raw_record['atom_indices'] == feature.atom_indices
        assert feature.raw_record['tetrahedron_indices'] == feature.tetrahedron_indices
        assert feature.raw_record['volume_solvent_estimate'] >= 0.0
        assert feature.raw_record['volume_solvent_estimate'] <= feature.raw_record[
            'volume_topological_resident'
        ]
