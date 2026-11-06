"""Exercise a bounded original-fpocket handoff; see topomt#101.

Run from the repository with ``python -m devtools.qualify_fpocket_handoff``.
This source-level pilot requires MolSysMT's ChemicalStates and permute_atoms APIs.
It does not qualify an installed distribution or a PharmacophoreMT calculation.
"""

import argparse
import hashlib
import json
import shutil
import tempfile
from pathlib import Path
from typing import Any

import molsysmt as msm
import numpy as np

import topomt as tmt
from devtools.provider_handoff import (
    chemical_state_context as _state_context,
)
from devtools.provider_handoff import (
    pocket_outputs_agree as _same_output,
)
from devtools.provider_handoff import (
    pocket_signature as _signature,
)
from devtools.provider_handoff import (
    prepare_reference_source,
)
from topomt import pyunitwizard as puw
from topomt.provider_output import ProviderRun
from topomt.third_party.fpocket.output import FpocketOutput


def qualify(pdb_file: Path, fpocket_cmd: str, output_dir: Path) -> dict[str, Any]:
    """Execute fpocket and verify a detached, persisted source-frame handoff.

    Parameters
    ----------
    pdb_file : Path
        Single-frame molecular file with protein and auxiliary atoms: PDB for
        the 3PTB spatial control, or prepared H5MSM for chemical consumption.
    fpocket_cmd : str
        Original fpocket executable name or path; absence is an error.
    output_dir : Path
        New directory for original.zip, source.h5msm and receipt.json.

    Returns
    -------
    dict
        Machine-readable checks, source context and executable identity.

    Raises
    ------
    FileNotFoundError
        If the original executable is unavailable.
    FileExistsError
        If output_dir already exists.
    ValueError
        If the profile or a handoff check fails.

    Examples
    --------
    >>> receipt = qualify(Path('3ptb.pdb'), 'fpocket', Path('handoff'))  # doctest: +SKIP
    """
    executable = shutil.which(fpocket_cmd)
    if executable is None:
        raise FileNotFoundError(
            f'Original fpocket executable unavailable: {fpocket_cmd}'
        )
    source, selection = prepare_reference_source(pdb_file)
    nonconsecutive = bool(np.any(np.diff(np.asarray(selection, dtype=int)) > 1))
    output_dir.mkdir(parents=True, exist_ok=False)
    source_file = output_dir / 'source.h5msm'
    msm.convert(source, to_form='file:h5msm', output_filename=source_file)
    original = tmt.get_provider_output(
        source,
        method='fpocket',
        selection=selection,
        structure_indices=1,
        fpocket_cmd=executable,
    )
    original.run.save(output_dir / 'original.zip')
    run = ProviderRun.load(output_dir / 'original.zip')
    restored = msm.convert(source_file, to_form='molsysmt.MolSys')
    expected = _signature(original)
    checks = {
        'nonempty_pockets': bool(expected),
        'bundle_identity': run == original.run,
        'chemical_state_round_trip': _state_context(restored) == _state_context(source),
        'source_labels_round_trip': msm.get(restored, element='atom', atom_id=True)
        == msm.get(source, element='atom', atom_id=True),
        'source_frames_round_trip': np.array_equal(
            puw.get_value(msm.get(restored, coordinates=True), to_unit='nm'),
            puw.get_value(msm.get(source, coordinates=True), to_unit='nm'),
        ),
    }
    with tempfile.TemporaryDirectory(prefix='topomt_handoff_') as temporary:
        root = Path(temporary)
        for name, data in run.artifacts:
            target = root / name  # ProviderRun.load validated names and digests.
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
        inputs = list((root / 'input').glob('*.pdb'))
        if len(inputs) != 1:
            raise ValueError('Pilot requires exactly one submitted PDB.')

        def recover(molecular_system: Any) -> FpocketOutput:
            return tmt.get_provider_output(
                molecular_system,
                method='fpocket',
                backend='files',
                pdb_file=inputs[0],
                output_dir=root / 'output',
                selection=selection,
                structure_indices=1,
                submitted_atom_indices=run.metadata['submitted_atom_indices'],
                chemical_state_context=run.metadata.get('chemical_state_context'),
            )

        recovered = recover(restored)
        checks['persisted_recovery'] = _signature(recovered) == expected
        checks['source_snapshot_recovery'] = (
            recovered.input_points_nm == original.input_points_nm
        )
        with puw.context(standard_units=['angstrom', 'fs']):
            checks['alternate_unit_policy'] = _same_output(recover(restored), original)
        msm.set(
            source,
            coordinates=msm.get(source, coordinates=True) + puw.quantity(1.0, 'nm'),
        )
        checks['detached_after_source_mutation'] = _signature(original) == expected
        checks['incompatible_source_rejected'] = False
        try:
            recover(source)
        except ValueError as error:
            if 'coordinates disagree' not in str(error):
                raise
            checks['incompatible_source_rejected'] = True
    if not all(checks.values()):
        raise ValueError(f'Handoff qualification failed: {checks}')
    receipt = {
        'profile': 'original-fpocket-source-handoff-1',
        'pocket_count': len(original.pockets),
        'selection_is_nonconsecutive': nonconsecutive,
        'selection': selection,
        'structure_index': 1,
        'chemical_state': _state_context(restored),
        'checks': checks,
        'run_id': run.run_id,
        'input_sha256': hashlib.sha256(pdb_file.read_bytes()).hexdigest(),
        'executable_sha256': hashlib.sha256(Path(executable).read_bytes()).hexdigest(),
        'source_sha256': hashlib.sha256(source_file.read_bytes()).hexdigest(),
        'limitations': [
            'Source compatibility pilot; not installed-package qualification.',
            'One reference chemical state; no alternative-state admission.',
            'Provider evidence only; no PharmacophoreMT model or scientific validation.',
        ],
    }
    (output_dir / 'receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
    return receipt


def main() -> None:
    """Run the bounded pilot with explicit input, executable and output paths."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('pdb_file', type=Path)
    parser.add_argument('output_dir', type=Path)
    parser.add_argument('--fpocket-cmd', default='fpocket')
    args = parser.parse_args()
    receipt = qualify(args.pdb_file, args.fpocket_cmd, args.output_dir)
    print(
        json.dumps({key: receipt[key] for key in ('pocket_count', 'checks')}, indent=2)
    )


if __name__ == '__main__':
    main()
