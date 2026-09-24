from topomt.third_party.castp.servers.castpfold import (
    CastpFoldClient as CastpFoldClient,
)
from topomt.third_party.castp.servers.castpfold import get_topography


def get_topography_with_castpfold(*args, **kwargs):
    return get_topography(*args, **kwargs)
