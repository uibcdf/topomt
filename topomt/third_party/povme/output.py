"""Original POVME result ownership."""

from topomt.third_party.output import ProviderOutput


class PovmeOutput(ProviderOutput):
    """Preserve original region results without native feature admission."""

    provider = 'povme'
