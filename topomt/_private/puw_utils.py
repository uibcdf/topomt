from topomt import pyunitwizard as puw
import numpy as np

def get_magnitude(obj, unit='nm'):
    """
    Robustly extract the magnitude of a quantity in the specified unit.
    Handles quantities, strings, and pure numpy arrays/floats.
    """
    if obj is None:
        return None
        
    if puw.is_quantity(obj):
        try:
            return float(puw.get_value(obj, to_unit=unit))
        except Exception:
            # Maybe dimensionless?
            return float(puw.get_value(obj))
            
    if isinstance(obj, str):
        try:
            return float(puw.get_value(puw.quantity(obj), to_unit=unit))
        except Exception:
            return float(puw.get_value(puw.quantity(obj)))
            
    # If it's a numpy array, it might be a magnitude already
    if isinstance(obj, np.ndarray):
        return obj.astype(float)
        
    # Fallback for floats/ints
    return float(obj)

def get_magnitudes(obj, unit='nm'):
    """
    Robustly extract magnitudes from an array-like object.
    """
    if obj is None:
        return None
        
    if puw.is_quantity(obj):
        try:
            return puw.get_value(obj, to_unit=unit)
        except Exception:
            return puw.get_value(obj)
            
    return np.asarray(obj, dtype=float)
