"""Original HOLE result ownership."""

from topomt.third_party.output import ProviderOutput


class HoleOutput(ProviderOutput):
    """Preserve original channel results without native feature admission."""

    provider = 'hole'
