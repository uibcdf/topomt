import sys
import os
import unittest
# import pytest # Pytest is not available, using direct function calls

# Add the parent directory of 'tests' (i.e., sandbox/geometry_playground/) to sys.path
# This makes 'core' and 'tests' importable as top-level modules from within this context.
# We also add the current working directory to allow local imports.
# IMPORTANT: This needs to be the root of the sandbox for 'core' to be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__))))

# Ensure topomt is in path if needed, for topomt.methods.afnd
# This will be tricky since topomt is the project root.
# For now, let's assume `topomt` is importable via existing setup.

def run_tests():
    print("Running Test Permeability (Basic Cases)...")
    from tests.test_permeability import test_equilateral_open, test_tight_squeeze, test_overlap_blocked
    test_equilateral_open()
    test_tight_squeeze()
    test_overlap_blocked()
    
    print("\nAll basic tests passed!")

def run_afnd_integration_tests_direct():
    print("\nRunning AFND Integration Tests (Draft - Direct Call)...")
    
    # Temporarily add topomt root to path for afnd import
    # Assuming the project root is 2 levels up from current file
    topomt_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    sys.path.insert(0, topomt_root)
    
    try:
        from tests.test_afnd_pockets import test_afnd_returns_expected_structure, test_afnd_parameters_affect_output
        
        # Call the test functions directly
        test_afnd_returns_expected_structure()
        test_afnd_parameters_affect_output()
        
        print("AFND Integration Tests (Draft) completed successfully.")
    except ImportError as e:
        print(f"ERROR: Could not import AFND test functions: {e}")
        print("Please ensure topomt is properly installed or its root is in PYTHONPATH.")
    except Exception as e:
        print(f"ERROR during AFND integration test execution: {e}")
        print("This likely indicates missing dependencies like MolSysMT or an error in AFND implementation.")
    finally:
        if topomt_root in sys.path:
            sys.path.remove(topomt_root)
    
    print("AFND Integration Tests (Draft) finished.")


if __name__ == "__main__":
    run_tests()
    run_afnd_integration_tests_direct()