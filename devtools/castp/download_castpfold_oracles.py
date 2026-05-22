"""Download CASTpFold oracle ZIPs for a PDB-id benchmark list."""

from __future__ import annotations

import argparse
import time
from pathlib import Path
from urllib.request import urlopen

import topomt


DEFAULT_LIST_FILE = Path('topomt/data/CASTpFold_server/list_pycast_pdbs.md')
DEFAULT_OUTPUT_DIR = Path('topomt/data/CASTpFold_server')
DEFAULT_PDB_CACHE_DIR = Path('/tmp/topomt_castpfold_pdb_cache')
RCSB_PDB_URL = 'https://files.rcsb.org/download/{pdb_id}.pdb'


def parse_pdb_id_list(list_file: str | Path) -> list[str]:
    """Return unique PDB IDs in first-seen order."""

    list_file = Path(list_file)
    pdb_ids = []
    seen = set()
    for raw_line in list_file.read_text().splitlines():
        line = raw_line.strip()
        if line == '' or line.startswith('#'):
            continue
        pdb_id = line.split()[0].lower()
        if pdb_id in seen:
            continue
        seen.add(pdb_id)
        pdb_ids.append(pdb_id)
    return pdb_ids


def existing_zip_ids(output_dir: str | Path) -> set[str]:
    """Return PDB IDs already present as ZIP files."""

    output_dir = Path(output_dir)
    return {path.stem.lower() for path in output_dir.glob('*.zip')}


def pending_pdb_ids(pdb_ids: list[str], output_dir: str | Path) -> list[str]:
    """Return list IDs without a persisted oracle ZIP."""

    existing = existing_zip_ids(output_dir)
    return [pdb_id for pdb_id in pdb_ids if pdb_id.lower() not in existing]


def download_pdb_from_rcsb(
    pdb_id: str,
    pdb_cache_dir: str | Path = DEFAULT_PDB_CACHE_DIR,
    *,
    timeout: int = 60,
) -> Path:
    """Download one PDB file from RCSB into a local cache."""

    pdb_id = pdb_id.lower()
    pdb_cache_dir = Path(pdb_cache_dir)
    pdb_cache_dir.mkdir(parents=True, exist_ok=True)
    pdb_path = pdb_cache_dir / f'{pdb_id}.pdb'
    if pdb_path.exists() and pdb_path.stat().st_size > 0:
        return pdb_path

    with urlopen(RCSB_PDB_URL.format(pdb_id=pdb_id.upper()), timeout=timeout) as response:
        pdb_path.write_bytes(response.read())
    return pdb_path


def download_castpfold_oracle(
    pdb_id: str,
    output_dir: str | Path = DEFAULT_OUTPUT_DIR,
    pdb_cache_dir: str | Path = DEFAULT_PDB_CACHE_DIR,
    *,
    probe_radius: float = 1.4,
    wait: int = 20,
    extra_wait: int = 30,
    retries: int = 3,
    timeout: int = 60,
    overwrite: bool = False,
) -> Path:
    """Download one CASTpFold oracle ZIP and return its path."""

    pdb_id = pdb_id.lower()
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    output_zip = output_dir / f'{pdb_id}.zip'
    if output_zip.exists() and not overwrite:
        return output_zip

    pdb_path = download_pdb_from_rcsb(
        pdb_id,
        pdb_cache_dir=pdb_cache_dir,
        timeout=timeout,
    )
    topomt.third_party.castp.get_topography(
        pdb_path,
        backend='server',
        server='castpfold',
        probe_radius=probe_radius,
        wait=wait,
        extra_wait=extra_wait,
        retries=retries,
        timeout=timeout,
        output_zip_file=output_zip,
    )
    return output_zip


def _selected_ids(args: argparse.Namespace) -> list[str]:
    if args.ids:
        pdb_ids = []
        seen = set()
        for pdb_id in args.ids:
            normalized = pdb_id.lower()
            if normalized not in seen:
                seen.add(normalized)
                pdb_ids.append(normalized)
    else:
        pdb_ids = parse_pdb_id_list(args.list_file)

    if args.pending:
        pdb_ids = pending_pdb_ids(pdb_ids, args.output_dir)

    if args.start_after:
        start_after = args.start_after.lower()
        if start_after in pdb_ids:
            pdb_ids = pdb_ids[pdb_ids.index(start_after) + 1 :]

    if args.limit is not None:
        pdb_ids = pdb_ids[: int(args.limit)]

    return pdb_ids


def main() -> None:
    """Run the CASTpFold oracle downloader."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--list-file', type=Path, default=DEFAULT_LIST_FILE)
    parser.add_argument('--output-dir', type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument('--pdb-cache-dir', type=Path, default=DEFAULT_PDB_CACHE_DIR)
    parser.add_argument('--ids', nargs='*', help='Explicit PDB IDs to download.')
    parser.add_argument('--pending', action='store_true', help='Skip ZIPs already present.')
    parser.add_argument('--limit', type=int, default=None)
    parser.add_argument('--start-after', default=None)
    parser.add_argument('--overwrite', action='store_true')
    parser.add_argument('--dry-run', action='store_true')
    parser.add_argument('--probe-radius', type=float, default=1.4)
    parser.add_argument('--wait', type=int, default=20)
    parser.add_argument('--extra-wait', type=int, default=30)
    parser.add_argument('--retries', type=int, default=3)
    parser.add_argument('--timeout', type=int, default=60)
    parser.add_argument(
        '--sleep-between-downloads',
        type=float,
        default=10.0,
        help='Seconds to wait between completed CASTpFold jobs.',
    )
    args = parser.parse_args()

    pdb_ids = _selected_ids(args)
    print(f'selected {len(pdb_ids)} ids')
    if args.dry_run:
        for pdb_id in pdb_ids:
            print(pdb_id)
        return

    for index, pdb_id in enumerate(pdb_ids, start=1):
        print(f'[{index}/{len(pdb_ids)}] {pdb_id}')
        output_zip = download_castpfold_oracle(
            pdb_id,
            output_dir=args.output_dir,
            pdb_cache_dir=args.pdb_cache_dir,
            probe_radius=args.probe_radius,
            wait=args.wait,
            extra_wait=args.extra_wait,
            retries=args.retries,
            timeout=args.timeout,
            overwrite=args.overwrite,
        )
        print(f'  saved {output_zip}')
        if index < len(pdb_ids) and args.sleep_between_downloads > 0:
            time.sleep(float(args.sleep_between_downloads))


if __name__ == '__main__':
    main()
