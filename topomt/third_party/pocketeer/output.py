"""Original Pocketeer output contract."""

from topomt.third_party.output import ProviderOutput


class PocketeerOutput(ProviderOutput):
    """Pocketeer pockets with masks, residues, sphere identities and SASA.

    See ProviderOutput for construction and shared access. Record fields retain
    filtered/provider and source defining-atom maps; the original JSON and mask
    supplement remain in the run. Residue membership is not geometric lining.
    """

    provider = 'pocketeer'
