"""Original fpocket output contract."""

from topomt.third_party.output import ProviderOutput


class FpocketOutput(ProviderOutput):
    """fpocket pockets with PDB/PQR, info fields and sphere IDs/types/charges.

    See ProviderOutput for construction and shared access. Raw fpocket geometry
    fields use angstroms; common geometries use explicit nanometer quantities.
    Attributed info measurements retain their source units and definitions.
    Four defining atoms are not invented when absent from the upstream PQR.
    """

    provider = 'fpocket'
