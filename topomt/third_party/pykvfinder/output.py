"""Original pyKVFinder cavity results, separate from native classification."""

from topomt.third_party.output import ProviderOutput


class PyKVFinderOutput(ProviderOutput):
    """Original dual-probe grid cavities and attributed descriptors."""

    provider = 'pykvfinder'
