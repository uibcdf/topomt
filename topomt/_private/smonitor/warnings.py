from smonitor.integrations import CatalogWarning

from .emitter import warn, warn_once


class TopoMTCatalogWarning(CatalogWarning):
    def __init__(self, message=None, **kwargs):
        from . import CATALOG, META

        super().__init__(message, catalog=CATALOG, meta=META, **kwargs)


class UserTopoMTWarning(TopoMTCatalogWarning):
    pass


class NotDigestedArgumentWarning(TopoMTCatalogWarning):
    catalog_key = 'NotDigestedArgumentWarning'

    def __init__(self, message=None, *, argument=None, caller=None):
        extra = (
            {'argument': argument, 'caller': caller} if argument is not None else None
        )
        super().__init__(message, extra=extra)


class PocketeerDelaunayWarning(UserTopoMTWarning):
    catalog_key = 'PocketeerDelaunayWarning'

    def __init__(self, message=None, *, reason=None):
        super().__init__(
            message, extra={'reason': reason} if reason is not None else None
        )


class PocketeerSasaBackendWarning(UserTopoMTWarning):
    catalog_key = 'PocketeerSasaBackendWarning'

    def __init__(self, message=None, *, reason: str | None = None):
        super().__init__(
            message, extra={'reason': reason} if reason is not None else None
        )


__all__ = [
    'UserTopoMTWarning',
    'NotDigestedArgumentWarning',
    'PocketeerDelaunayWarning',
    'PocketeerSasaBackendWarning',
    'warn',
    'warn_once',
]
