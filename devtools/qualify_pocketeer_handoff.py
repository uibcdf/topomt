"""Qualify original Pocketeer source-bound receiving; topomt#101.

The shared developer recorder orchestrates public MolSysMT/TopoMT tools. It does
not prepare chemistry or construct pharmacophores.
"""

from pathlib import Path
from typing import Any

from devtools.qualify_library_handoff import qualify_library_source, run_cli


def qualify(input_file: Path, output_dir: Path) -> dict[str, Any]:
    """Run the explicit original Pocketeer source profile.

    Parameters
    ----------
    input_file : pathlib.Path
        Prepared single-frame MolSysMT source with one reference state at zero.
    output_dir : pathlib.Path
        New source.h5msm, original.zip and receipt.json destination.

    Returns
    -------
    dict
        Provider identity, original parameters, source/state/frame context,
        checks and artifact hashes. See qualify_library_source for the profile.

    Raises
    ------
    ValueError
        If the bounded source profile, original engine or recovery disagrees.
    FileExistsError
        If output_dir exists.
    LibraryNotFoundError
        If the requested original is unavailable.

    Examples
    --------
    >>> receipt = qualify(Path('prepared.h5msm'), Path('handoff'))  # doctest: +SKIP
    """
    return qualify_library_source(input_file, output_dir, method='pocketeer')


def main() -> None:
    """Run the original Pocketeer profile with explicit input/output paths."""
    run_cli('pocketeer')


if __name__ == '__main__':
    main()
