"""Developer-only saved verification and bounded partition production.

Use ``python -m devtools.reference_validator verify MODEL CERTIFICATE`` or
``python -m devtools.reference_validator produce MODEL OUTPUT --max-depth 4``.
Run under external CPU/memory/time limits. No optional scientific provider or
DFND module is imported by the verification command.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from .model import Model
from .verify import verify


def _unique(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f'Duplicate JSON field: {key}')
        result[key] = value
    return result


def _read(path: Path) -> Any:
    with path.open('rb') as stream:
        data = stream.read(16 * 1024**2 + 1)
    if len(data) > 16 * 1024**2:
        raise ValueError('Pilot input exceeds 16 MiB limit')
    return json.loads(data, object_pairs_hook=_unique)


def main() -> int:
    """Execute a bounded developer operation; report invalid evidence as failure."""
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    check = commands.add_parser('verify')
    check.add_argument('model', type=Path)
    check.add_argument('certificate', type=Path)
    produce = commands.add_parser('produce')
    produce.add_argument('model', type=Path)
    produce.add_argument('output', type=Path)
    produce.add_argument('--max-depth', type=int, default=4)
    produce.add_argument('--max-leaves', type=int, default=4096)
    freeze = commands.add_parser('freeze-tetrahedron')
    freeze.add_argument('input', type=Path)
    freeze.add_argument('output', type=Path)
    freeze.add_argument('--probe-angstroms', type=float, required=True)
    args = parser.parse_args()
    try:
        if args.command == 'freeze-tetrahedron':
            from .receiving import freeze_tetrahedron

            model = freeze_tetrahedron(args.input, probe_angstroms=args.probe_angstroms)
            with args.output.open('x') as stream:
                json.dump(model.to_record(), stream, indent=2, allow_nan=False)
                stream.write('\n')
            print(json.dumps({'model_sha256': model.digest}))
            return 0
        model = Model.from_record(_read(args.model))
        if args.command == 'verify':
            result = verify(model, _read(args.certificate))
        else:
            from .producer import partition

            certificate = partition(
                model, max_depth=args.max_depth, max_leaves=args.max_leaves
            )
            result = verify(model, certificate)
            with args.output.open('x') as stream:
                json.dump(certificate, stream, indent=2, allow_nan=False)
                stream.write('\n')
        print(json.dumps(result, sort_keys=True, allow_nan=False))
    except (ValueError, TypeError, OverflowError, OSError) as exc:
        print(f'Reference validation failed: {exc}', file=sys.stderr)
        return 2
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
