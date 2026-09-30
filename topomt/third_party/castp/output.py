"""Original CASTp/CASTpFold output contract."""

from topomt.third_party.output import ProviderOutput


class CASTpOutput(ProviderOutput):
    """All CASTp pocket rows and auxiliary mouth aggregates with source links.

    See ProviderOutput for construction and shared access. Closed cavities and
    multiple-opening rows remain in pockets regardless of legacy classification.
    SA/MS definitions, counts, atom labels and aggregate multiplicity remain
    explicit; mouth rows do not become individual localized openings.
    Server identity, when supplied, is recorded in run metadata.
    """

    provider = 'castp'
