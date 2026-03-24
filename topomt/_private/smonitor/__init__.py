# SMonitor initialization for TopoMT
from pathlib import Path
from .catalog import CATALOG
from .meta import META
from typing import Any, Optional

PACKAGE_ROOT = Path(__file__).parents[2]

from smonitor.integrations import CatalogException, CatalogWarning

class TopoMTException(CatalogException):
    def __init__(self, **kwargs):
        """
        Base exception for TopoMT that automatically bundles non-standard 
        keyword arguments into the 'extra' dictionary for SMonitor.
        """
        standard_keys = {'message', 'code', 'extra', 'catalog', 'meta'}
        
        # Extract or initialize 'extra'
        extra = kwargs.get('extra', {})
        if not isinstance(extra, dict):
            extra = {'_raw_extra': extra}
            
        # Move any non-standard keyword arguments into 'extra'
        captured_keys = [k for k in kwargs if k not in standard_keys]
        for k in captured_keys:
            extra[k] = kwargs.pop(k)
            
        # Ensure default catalog and meta are used if not provided
        kwargs.setdefault('catalog', CATALOG)
        kwargs.setdefault('meta', META)
        kwargs['extra'] = extra
            
        super().__init__(**kwargs)

class TopoMTWarning(CatalogWarning):
    def __init__(self, **kwargs):
        """
        Base warning for TopoMT that automatically bundles non-standard 
        keyword arguments into the 'extra' dictionary for SMonitor.
        """
        standard_keys = {'message', 'code', 'extra', 'catalog', 'meta'}
        extra = kwargs.get('extra', {})
        if not isinstance(extra, dict):
            extra = {'_raw_extra': extra}
            
        captured_keys = [k for k in kwargs if k not in standard_keys]
        for k in captured_keys:
            extra[k] = kwargs.pop(k)
            
        kwargs.setdefault('catalog', CATALOG)
        kwargs.setdefault('meta', META)
        kwargs['extra'] = extra
            
        super().__init__(**kwargs)

class LibraryNotFoundError(TopoMTException):
    catalog_key = "LibraryNotFoundError"

class ArgumentError(TopoMTException):
    catalog_key = "ArgumentError"

class NotDigestedArgumentWarning(TopoMTWarning):
    catalog_key = "NotDigestedArgumentWarning"
