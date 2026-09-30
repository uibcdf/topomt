"""Original AlphaSpace2 output contract."""

from topomt.third_party.output import ProviderOutput


class AlphaSpace2Output(ProviderOutput):
    """AlphaSpace2 pockets with alpha/beta sites and original contact state.

    See ProviderOutput for construction and shared access. Run artifacts retain
    receptor, optional binder, full snapshot and exports. Alpha-space, nonpolar
    contributions and weighted occupancy keep AlphaSpace2's definitions; they
    are not geometric intersections or binding probabilities.
    """

    provider = 'alphaspace2'
