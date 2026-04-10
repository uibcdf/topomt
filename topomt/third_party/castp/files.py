from topomt.io.load_CASTp import load_CASTp


def load_topography(*, zip_file=None, dir_path=None, molecular_system=None, **kwargs):
    """Load CASTp-family results from files or archives."""

    return load_CASTp(
        zip_file=zip_file,
        dir_path=dir_path,
        molecular_system=molecular_system,
        **kwargs,
    )
