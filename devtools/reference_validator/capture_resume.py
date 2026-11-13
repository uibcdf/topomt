"""Retain a bounded resume chain and an uninterrupted exact control."""

import argparse
import hashlib
import json
import os
import resource
import subprocess
import time
from pathlib import Path
from typing import Any

from .contracts import Configuration
from .model import Model, record_digest
from .runs import resume_run, start_run
from .storage import load_bundle, read_record_with_digest, save_bundle
from .verify.records import verify_run, verify_transition


def capture(protocol_path: Path, output: Path) -> None:
    """Capture the frozen same-model resume experiment with one CPU affinity.

    Every step is saved, read back and independently checked. The original
    model and every earlier evidence directory are preserved. This developer
    helper requires Linux resource controls and an external time/memory cap.
    """
    root = Path(__file__).resolve().parents[2]
    spec, protocol_digest = read_record_with_digest(protocol_path)
    if spec['schema'] != 'topomt.reference-validator.resume-pilot/1':
        raise ValueError('Unsupported resume pilot protocol')
    model_record, source_digest = read_record_with_digest(root / spec['model'])
    model = Model.from_record(model_record)
    if (
        source_digest != spec['model_file_sha256']
        or model.digest != spec['model_sha256']
    ):
        raise ValueError('Resume pilot model differs from the frozen protocol')
    if len(os.sched_getaffinity(0)) != 1:
        raise ValueError('Resume pilot requires one CPU affinity')
    output.mkdir(parents=True, exist_ok=False)
    start = time.monotonic()
    configuration = Configuration.from_record(spec['configuration'])
    steps: list[dict[str, Any]] = []
    checkpoint = None
    for index, budget in enumerate(spec['step_split_budgets']):
        parent = checkpoint
        if parent is None:
            checkpoint, run = start_run(
                model, configuration=configuration, split_budget=budget
            )
        else:
            checkpoint, run = resume_run(model, parent, split_budget=budget)
        directory = output / f'step_{index:02d}'
        save_bundle(directory, model, checkpoint, run)
        checkpoint, run = load_bundle(directory, model)
        checked = (
            verify_run(model, run, checkpoint)
            if parent is None
            else verify_transition(model, parent, checkpoint, run)
        )
        steps.append(
            {
                'directory': directory.name,
                'checkpoint_sha256': checked['checkpoint_sha256'],
                'run_record_sha256': checked['run_record_sha256'],
                'stop_reason': checked['stop_reason'],
                'n_components': checked['n_components'],
                'total_splits': checked['total_splits'],
                'volume_lower': checked['volume_lower'],
                'volume_upper': checked['volume_upper'],
            }
        )
    control, control_run = start_run(
        model, configuration=configuration, split_budget=spec['control_split_budget']
    )
    save_bundle(output / 'continuous', model, control, control_run)
    if checkpoint is None or checkpoint['certificate'] != control['certificate']:
        raise ValueError('Resumed proof differs from continuous calculation')
    if steps[-1]['n_components'] != spec['expected_final_components']:
        raise ValueError('Resume pilot did not establish the selected control')
    files = {
        str(p.relative_to(output)): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in sorted(output.rglob('*.json'))
    }
    receipt = {
        'schema': 'topomt.reference-validator.resume-receiving/1',
        'protocol_sha256': protocol_digest,
        'model_sha256': model.digest,
        'source_revision': subprocess.check_output(
            ['git', 'rev-parse', 'HEAD'], cwd=root, text=True
        ).strip(),
        'kernel': checkpoint['kernel'],
        'run_sha256': checkpoint['run_sha256'],
        'steps': steps,
        'same_as_continuous': True,
        'control_checkpoint_sha256': record_digest(control),
        'files': files,
        'elapsed_seconds': time.monotonic() - start,
        'peak_rss_kib_linux': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        'cpu_affinity': sorted(os.sched_getaffinity(0)),
        'address_space_limit_bytes': resource.getrlimit(resource.RLIMIT_AS)[0],
        'scope': 'Operational same-model resume and exact tetrahedron exclusion; no general connected-region or requested volume-precision qualification',
    }
    with (output / 'receipt.json').open('x') as stream:
        json.dump(receipt, stream, indent=2, allow_nan=False)
        stream.write('\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('protocol', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    capture(args.protocol, args.output)
