from __future__ import annotations
from typing import Any

def digest_method(method: str, caller: str | None = None) -> str | Any:
    """
    Digest the 'method' argument for topography detection.
    """
    valid_methods = {'pocketeer', 'fpocket', 'fpocket4', 'alphaspace2', 'dfnd', 'castp', 'pycasta'}
    
    if isinstance(method, str):
        method_lower = method.lower()
        if method_lower in valid_methods:
            return method_lower
            
    # If we are here, something is wrong. 
    # ArgDigest expects us to return the error or raise it.
    from topomt._private.smonitor import TopoMTException
    
    class ArgumentError(TopoMTException):
        catalog_key = "ArgumentError"
        
    return ArgumentError(arg_name='method', reason=f"Unknown method '{method}'. Valid: {valid_methods}")
