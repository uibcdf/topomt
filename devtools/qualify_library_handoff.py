"""Qualify original library execution and source-bound recovery; topomt#101.

This developer control changes only source ordering and a declared coordinate
frame through public MolSysMT operations. It neither prepares chemistry nor
builds pharmacophores. Use a separately prepared source for chemical receiving.
"""

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Literal

import molsysmt as msm
import numpy as np

import topomt as tmt
from devtools.provider_handoff import (
    chemical_state_context,
    pocket_outputs_agree,
    pocket_signature,
    prepare_reference_source,
)
from topomt import pyunitwizard as puw
from topomt.provider_output import ProviderRun


def qualify_library_source(
    input_file: Path,
    output_dir: Path,
    *,
    method: Literal['pocketeer', 'alphaspace2', 'pycasta'],
) -> dict[str, Any]:
    """Run the installed original and persist a verified selected-frame handoff.

    Parameters
    ----------
    input_file : pathlib.Path
        Single-frame source accepted by prepare_reference_source. Receptor
        chemistry is supplied by MolSysMT and must already be prepared.
    method : {'pocketeer', 'alphaspace2', 'pycasta'}
        Explicit original library. AlphaSpace2 uses its default min_vertices=20
        and no binder; all selected protein atoms, including H, are submitted.
    output_dir : pathlib.Path
        New directory for source.h5msm, original.zip and receipt.json.

    Returns
    -------
    dict
        Actual original-provider identity, selection/state/frame, checks and
        artifact hashes. An explicitly selected pocket may subsequently be
        consumed through PharmacophoreMT's public tools.

    Raises
    ------
    ValueError
        If the analytical source profile, installed original identity or any
        source/recovery/physical check disagrees.
    FileExistsError
        If output_dir already exists.
    LibraryNotFoundError
        If the requested original engine is unavailable.

    Examples
    --------
    >>> receipt = qualify_library_source(  # doctest: +SKIP
    ...     Path('prepared.h5msm'), Path('handoff'), method='alphaspace2')
    """
    if method not in {'pocketeer', 'alphaspace2', 'pycasta'}:
        raise ValueError(
            'Select an original Pocketeer, AlphaSpace2 or pyCASTA library.'
        )
    if output_dir.exists():
        raise FileExistsError(output_dir)
    source, selection = prepare_reference_source(input_file)
    output_dir.mkdir(parents=True, exist_ok=False)
    source_file, bundle = output_dir / 'source.h5msm', output_dir / 'original.zip'
    msm.convert(source, to_form='file:h5msm', output_filename=source_file)
    original = tmt.get_provider_output(
        source,
        method=method,
        selection=selection,
        structure_indices=1,
        chemical_state=0,
    )
    if original.run.metadata.get('distribution_version') is None:
        raise ValueError(
            f'The control requires an unshadowed installed original {method}.'
        )
    original.run.save(bundle)
    run = ProviderRun.load(bundle)
    restored = msm.convert(source_file, to_form='molsysmt.MolSys')

    def recover(molecular_system: Any):
        return tmt.get_provider_output(
            molecular_system, method=method, backend='files', bundle_file=bundle
        )

    recovered = recover(restored)
    expected = pocket_signature(original)
    snapshot = puw.get_value(original.input_coordinates, to_unit='nm').copy()
    checks = {
        'nonempty_pockets': bool(original.pockets),
        'bundle_identity': run == original.run,
        'original_run_identity_after_recovery': recovered.run == original.run,
        'selected_source_map': run.metadata['selected_atom_indices'] == selection,
        'chemical_state_round_trip': chemical_state_context(restored)
        == chemical_state_context(source),
        'source_labels_round_trip': msm.get(restored, element='atom', atom_id=True)
        == msm.get(source, element='atom', atom_id=True),
        'source_frames_round_trip': np.array_equal(
            puw.get_value(msm.get(restored, coordinates=True), to_unit='nm'),
            puw.get_value(msm.get(source, coordinates=True), to_unit='nm'),
        ),
        'persisted_recovery': pocket_outputs_agree(recovered, original),
        'source_snapshot_recovery': np.allclose(
            puw.get_value(recovered.input_coordinates, to_unit='nm'),
            snapshot,
            rtol=0,
            atol=1e-12,
        ),
    }
    with puw.context(standard_units=['pm', 'fs', 'radians']):
        alternate = recover(restored)
        checks['alternate_unit_policy'] = (
            alternate.run == original.run
            and pocket_outputs_agree(alternate, original)
            and np.allclose(
                puw.get_value(alternate.input_coordinates, to_unit='nm'),
                snapshot,
                rtol=0,
                atol=1e-12,
            )
        )
    msm.structure.translate(
        source, translation=puw.quantity([[[1.0, 1.0, 1.0]]], 'nm'), in_place=True
    )
    checks['detached_after_source_mutation'] = pocket_signature(
        original
    ) == expected and np.array_equal(
        puw.get_value(original.input_coordinates, to_unit='nm'), snapshot
    )
    checks['incompatible_source_rejected'] = False
    try:
        recover(source)
    except ValueError as error:
        if 'coordinates' not in str(error).lower():
            raise
        checks['incompatible_source_rejected'] = True
    if not all(checks.values()):
        raise ValueError(f'{method} handoff qualification failed: {checks}')
    provider_fields = {
        'pocketeer': ('version', 'api_sha256', 'parameters'),
        'alphaspace2': (
            'snapshot_source_sha256',
            'snapshot_settings',
            'min_vertices',
            'binder',
        ),
        'pycasta': ('source_sha256', 'version_tag', 'configuration'),
    }[method]
    receipt_fields = {
        'version': 'version_label',
        'source_sha256': 'provider_source_sha256',
    }
    receipt = {
        'profile': f'original-{method}-source-handoff-1',
        'provider': run.provider,
        'backend': run.backend,
        'distribution_version': run.metadata['distribution_version'],
        **{receipt_fields.get(key, key): run.metadata[key] for key in provider_fields},
        'output_protocol': run.metadata['output_protocol'],
        'pocket_count': len(original.pockets),
        'pocket_ids': [pocket.source_id for pocket in original.pockets],
        'selection_is_nonconsecutive': bool(np.any(np.diff(selection) > 1)),
        'selection': selection,
        'structure_index': 1,
        'chemical_state': chemical_state_context(restored),
        'checks': {key: bool(value) for key, value in checks.items()},
        'run_id': run.run_id,
        'input_sha256': hashlib.sha256(input_file.read_bytes()).hexdigest(),
        'source_sha256': hashlib.sha256(source_file.read_bytes()).hexdigest(),
        'original_bundle_sha256': hashlib.sha256(bundle.read_bytes()).hexdigest(),
        'limitations': [
            'Source control; not installed-package qualification.',
            'One reference chemical state at index 0 and nonperiodic frame 1.',
            'Provider evidence only; no chemical preparation or pharmacophore model.',
            'Pocket membership and alpha spheres do not define an exact closed region.',
            'Pocket rank is not affinity or pharmacophoric importance.',
        ],
    }
    (output_dir / 'receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
    return receipt


def run_cli(method: Literal['pocketeer', 'alphaspace2', 'pycasta']) -> None:
    """Run the bounded source profile with explicit input and output paths."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input_file', type=Path)
    parser.add_argument('output_dir', type=Path)
    args = parser.parse_args()
    receipt = qualify_library_source(args.input_file, args.output_dir, method=method)
    print(
        json.dumps({key: receipt[key] for key in ('pocket_count', 'checks')}, indent=2)
    )
