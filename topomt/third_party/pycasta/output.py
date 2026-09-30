"""Original pyCASTA output contract."""

from topomt.third_party.output import ProviderOutput


class PyCASTAOutput(ProviderOutput):
    """pyCASTA pockets with original tetrahedron indices and reported metrics.

    See ProviderOutput for construction and shared access. Original result JSON,
    alpha arrays and native files remain recoverable. Representative points,
    depth, ranking and validation outcomes retain their distinct definitions;
    reconstructed mean centers do not replace original representative points.
    """

    provider = 'pycasta'
