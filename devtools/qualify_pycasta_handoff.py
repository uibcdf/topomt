"""Qualify original pyCASTA source-bound receiving; topomt#101."""

from pathlib import Path
from typing import Any

from devtools.qualify_library_handoff import qualify_library_source, run_cli


def qualify(input_file: Path, output_dir: Path) -> dict[str, Any]:
    """Run the explicit original pyCASTA source profile.

    Parameters
    ----------
    input_file : pathlib.Path
        Prepared single-frame MolSysMT source with one reference state at zero.
    output_dir : pathlib.Path
        New source.h5msm, original.zip and receipt.json destination.

    Returns
    -------
    dict
        Original identity and configuration, source context, recovery checks
        and artifact hashes. No chemistry or query model is generated here.

    Raises
    ------
    ValueError
        If the original execution or source-bound recovery disagrees.
    FileExistsError
        If output_dir exists.
    LibraryNotFoundError
        If the requested original is unavailable.

    Examples
    --------
    >>> receipt = qualify(Path('prepared.h5msm'), Path('handoff'))  # doctest: +SKIP
    """
    return qualify_library_source(input_file, output_dir, method='pycasta')


def main() -> None:
    """Run the original pyCASTA profile with explicit input/output paths."""
    run_cli('pycasta')


if __name__ == '__main__':
    main()
