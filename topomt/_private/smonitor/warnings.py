from __future__ import annotations

from smonitor.integrations import CatalogWarning

from .emitter import warn, warn_once


class TopoMTCatalogWarning(CatalogWarning):
    def __init__(self, **kwargs):
        from . import CATALOG, META

        super().__init__(catalog=CATALOG, meta=META, **kwargs)


class UserTopoMTWarning(TopoMTCatalogWarning):
    pass


class NotDigestedArgumentWarning(TopoMTCatalogWarning):
    catalog_key = 'NotDigestedArgumentWarning'

    def __init__(self, argument, caller=None):
        super().__init__(extra={'argument': argument, 'caller': caller})


class PocketeerDelaunayWarning(UserTopoMTWarning):
    catalog_key = 'PocketeerDelaunayWarning'

    def __init__(self, reason):
        super().__init__(extra={'reason': reason})


class PocketeerSasaBackendWarning(UserTopoMTWarning):
    catalog_key = 'PocketeerSasaBackendWarning'

    def __init__(self, reason: str):
        super().__init__(extra={'reason': reason})


__all__ = [
    'UserTopoMTWarning',
    'NotDigestedArgumentWarning',
    'PocketeerDelaunayWarning',
    'PocketeerSasaBackendWarning',
    'warn',
    'warn_once',
]
