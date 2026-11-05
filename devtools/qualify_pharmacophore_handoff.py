"""Consume a qualified original fpocket run through public PharmacophoreMT tools.

This opt-in integration recorder owns no molecular recognition or pharmacophore
algorithm. Its explicit hydrophobic projections are an analytical composition
control, not a proposed binding model. See topomt#101.
"""

import argparse
import hashlib
import json
import tempfile
from pathlib import Path
from typing import Any

import molsysmt as msm
import numpy as np

import topomt as tmt
from topomt import pyunitwizard as puw
from topomt.provider_output import ProviderRun


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _sites(model: Any) -> list[dict[str, Any]]:
    return [
        {
            'features': site.features,
            'atom_indices': site.metadata['atom_indices'],
            'center': {
                'value': puw.get_value(site.center, to_unit='nm').tolist(),
                'unit': 'nm',
            },
            'radius': {
                'value': float(puw.get_value(site.shape.radius, to_unit='nm')),
                'unit': 'nm',
            },
            'essential': site.essential,
            'weight': site.weight,
        }
        for site in model.interaction_sites
    ]


def _same_sites(first: Any, second: Any) -> bool:
    left, right = _sites(first), _sites(second)
    if len(left) != len(right):
        return False
    for a, b in zip(left, right):
        for field in ('center', 'radius'):
            x, y = a.pop(field), b.pop(field)
            if x['unit'] != y['unit'] or not np.allclose(
                x['value'], y['value'], rtol=0, atol=1e-12
            ):
                return False
    # Only physical conversion tolerates roundoff; identity and query semantics
    # (features, source atoms, requiredness and weights) compare exactly.
    return left == right


def consume(
    handoff_dir: Path,
    output_dir: Path,
    *,
    pocket_id: str,
    projection_direction: tuple[float, float, float],
    distance: str,
    radius: str,
) -> dict[str, Any]:
    """Build and persist an explicit hydrophobic query from one original pocket.

    Parameters
    ----------
    handoff_dir : Path
        Output of qualify_fpocket_handoff: source.h5msm, original.zip and receipt.json.
        Molecular chemistry must already support MolSysMT native recognition.
    output_dir : Path
        New directory for query.json and the consumer receipt.
    pocket_id : str
        Exact provider source ID. Ranking is not interpreted as importance.
    projection_direction : tuple of float
        Dimensionless, caller-declared query direction; no molecular inference.
    distance, radius : str
        Explicit-unit projection distance and matching tolerance. PharmacophoreMT
        validates and interprets these scientific choices.

    Returns
    -------
    dict
        Context, site correspondence, recipe, checks and artifact identities.

    Raises
    ------
    ValueError
        If the bounded handoff context, integrity or membership is unsupported.
    KeyError
        If pocket_id is absent.
    FileExistsError
        If output_dir exists.

    Notes
    -----
    Provider recognition exceptions propagate. This recorder does not prepare
    chemistry, repair an incomplete graph or substitute a pocket engine. The
    accepted profile has one reference state (0) and selected coordinate frame 1.

    Examples
    --------
    >>> report = consume(Path('handoff'), Path('consumer'),  # doctest: +SKIP
    ...     pocket_id='fpocket:1', projection_direction=(1., 0., 0.),
    ...     distance='0.30 nm', radius='0.15 nm')
    """
    if output_dir.exists():
        raise FileExistsError(output_dir)
    evidence = json.loads((handoff_dir / 'receipt.json').read_text())
    if evidence.get('chemical_state') != {'count': 1, 'reference_index': 0}:
        raise ValueError(
            'A single explicit reference chemical-state context is required.'
        )
    if evidence.get('structure_index') != 1:
        raise ValueError('This handoff profile requires source structure context 1.')
    if evidence.get('profile') != 'original-fpocket-source-handoff-1' or not (
        evidence.get('checks')
        and all(value is True for value in evidence['checks'].values())
    ):
        raise ValueError('A successful original fpocket handoff receipt is required.')
    source_file = handoff_dir / 'source.h5msm'
    if _sha256(source_file) != evidence.get('source_sha256'):
        raise ValueError('The source checksum disagrees with the handoff receipt.')
    run = ProviderRun.load(handoff_dir / 'original.zip')
    if (
        run.run_id != evidence.get('run_id')
        or run.provider != 'fpocket'
        or run.backend != 'cli'
        or run.metadata.get('structure_indices') != 1
    ):
        raise ValueError('Original run identity or structure context disagrees.')
    source = msm.convert(source_file, to_form='molsysmt.MolSys')
    if (
        source.chemical_states.n_chemical_states != 1
        or source.chemical_states.reference_chemical_state_index != 0
    ):
        raise ValueError('Restored source chemical-state context disagrees.')
    before = puw.get_value(msm.get(source, coordinates=True), to_unit='nm').copy()
    with tempfile.TemporaryDirectory(prefix='topomt_consumer_') as temporary:
        root = Path(temporary)
        for name, data in run.artifacts:
            target = root / name  # ProviderRun.load validated names and checksums.
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
        inputs = list((root / 'input').glob('*.pdb'))
        if len(inputs) != 1:
            raise ValueError('Exactly one submitted PDB is required.')
        output = tmt.get_provider_output(
            source,
            method='fpocket',
            backend='files',
            pdb_file=inputs[0],
            output_dir=root / 'output',
            selection=run.metadata['selection'],
            structure_indices=1,
            submitted_atom_indices=run.metadata['submitted_atom_indices'],
        )
    pocket = next(
        (record for record in output.pockets if record.source_id == pocket_id), None
    )
    if pocket is None:
        raise KeyError(f'Original pocket not found: {pocket_id}')
    if pocket.atom_indices is None:
        raise ValueError('Pocket source membership is unavailable.')
    if not pocket.atom_indices:
        raise ValueError('Pocket source membership is available but empty.')

    # Optional consumer imports belong at the explicit integration boundary.
    from pharmacophoremt import __version__ as consumer_version
    from pharmacophoremt.io import load_json, to_json
    from pharmacophoremt.modeler import from_receptor_projections, get_features

    inventory = get_features(
        source,
        selection=list(pocket.atom_indices),
        structure_index=1,
        chemical_state=0,
        features=['hydrophobicity'],
    )
    if not inventory['features']:
        raise ValueError(
            'The declared pocket has no hydrophobic features for this control.'
        )
    if any(
        not set(record['atom_indices']) <= set(pocket.atom_indices)
        for record in inventory['features']
    ):
        raise ValueError(
            'Consumer features fall outside the original pocket membership.'
        )
    context = {
        'original_run_id': run.run_id,
        'pocket_id': pocket_id,
        'source_sha256': evidence['source_sha256'],
        'structure_index': 1,
        'chemical_state': 0,
        'membership_role': pocket.atom_role,
        'interpretation': 'explicit analytical projection; not binding relevance',
    }
    model = from_receptor_projections(
        inventory,
        projection_specs=[
            {
                'feature_index': index,
                'projection_direction': puw.quantity(
                    projection_direction, 'dimensionless'
                ),
                'distance': distance,
                'label': f'{pocket_id} explicit hydrophobic control {index}',
                'evidence': context,
            }
            for index in range(len(inventory['features']))
        ],
        radius=radius,
        name=f'{pocket_id} analytical consumer control',
    )
    model.metadata['topomt_handoff'] = context
    output_dir.mkdir(parents=True, exist_ok=False)
    to_json(model, output_dir / 'query.json')
    restored = load_json(output_dir / 'query.json')
    checks = {
        'nonempty_query': model.n_interaction_sites > 0,
        'native_site_round_trip': _same_sites(restored, model),
        'native_context_round_trip': restored.metadata == model.metadata,
        'source_coordinates_unchanged': np.array_equal(
            before, puw.get_value(msm.get(source, coordinates=True), to_unit='nm')
        ),
        'source_bytes_unchanged': _sha256(source_file) == evidence['source_sha256'],
    }
    if not all(checks.values()):
        raise ValueError(f'Consumer handoff failed: {checks}')
    receipt = {
        'profile': 'fpocket-pharmacophoremt-hydrophobic-control-1',
        'context': context,
        'pharmacophoremt_version_label': consumer_version,
        'pocket_atom_indices': list(pocket.atom_indices),
        'site_count': model.n_interaction_sites,
        'sites': _sites(model),
        'recipe': {
            'projection_direction': {
                'value': list(projection_direction),
                'unit': 'dimensionless',
            },
            'distance': distance,
            'radius': radius,
            'features': ['hydrophobicity'],
        },
        'checks': checks,
        'query_sha256': _sha256(output_dir / 'query.json'),
        'original_bundle_sha256': _sha256(handoff_dir / 'original.zip'),
        'limits': [
            'Source integration control; no installed/public qualification.',
            'One explicitly prepared reference chemical state and nonperiodic frame.',
            'Declared hydrophobic placements; no affinity, fit or biological validation.',
            'Pocket atoms and alpha spheres do not define an exact volumetric region.',
        ],
    }
    (output_dir / 'receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
    return receipt


def main() -> None:
    """Run the explicit consumer control against an existing original run."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('handoff_dir', type=Path)
    parser.add_argument('output_dir', type=Path)
    parser.add_argument('--pocket-id', required=True)
    parser.add_argument('--direction', type=float, nargs=3, required=True)
    parser.add_argument('--distance', required=True)
    parser.add_argument('--radius', required=True)
    args = parser.parse_args()
    receipt = consume(
        args.handoff_dir,
        args.output_dir,
        pocket_id=args.pocket_id,
        projection_direction=(args.direction[0], args.direction[1], args.direction[2]),
        distance=args.distance,
        radius=args.radius,
    )
    print(
        json.dumps(
            {'site_count': receipt['site_count'], 'checks': receipt['checks']}, indent=2
        )
    )


if __name__ == '__main__':
    main()
