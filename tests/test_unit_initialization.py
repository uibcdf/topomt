"""Qualify import-time unit configuration in independent real sessions."""

import subprocess
import sys
import textwrap

import pytest


@pytest.mark.parametrize('session', ['fresh', 'loaded', 'application', 'suite'])
def test_import_preserves_unit_registry_and_policy(session):
    script = textwrap.dedent(
        """
        import sys
        import warnings
        import pyunitwizard as puw

        session = sys.argv[1]
        assert not puw.configure.has_active_policy()
        assert 'pint' not in puw.configure.get_libraries_loaded()
        puw.configure.set_pint_registry_cache(False)
        if session != 'fresh':
            original = puw.quantity(10, 'angstroms', form='pint')
            assert 'pint' in puw.configure.get_libraries_loaded()
        if session == 'application':
            puw.configure.set_standard_units(
                ['pm', 'fs', 'degrees'], provenance='application'
            )
        elif session == 'suite':
            puw.configure.set_standard_units(
                ['nm', 'ps', 'radians'], provenance='suite'
            )
        before = puw.configure.report()
        cache_before = puw.configure.get_pint_registry_cache()

        with warnings.catch_warnings(record=True) as captured:
            warnings.simplefilter('always')
            import topomt

        assert topomt.pyunitwizard is puw
        assert not any(
            'set_pint_registry_cache() has no effect' in str(w.message)
            for w in captured
        ), [str(w.message) for w in captured]
        after = puw.configure.report()
        if session in {'application', 'suite'}:
            for field in ('standard_units', 'provenance', 'default_form', 'default_parser'):
                assert after[field] == before[field], (field, before, after)
            expected_length = 'pm' if session == 'application' else 'nm'
            assert puw.has_unit(puw.standardize(original), expected_length)
        else:
            assert after['provenance'] == 'topomt'
            assert after['standard_units'] == topomt._pyunitwizard.STANDARD_UNITS
            assert puw.has_unit(puw.standardize(puw.quantity(1, 'angstroms')), 'nm')

        if session == 'fresh':
            assert puw.configure.get_pint_registry_cache() == ':auto:'
        else:
            assert puw.configure.get_pint_registry_cache() == cache_before
            # Pint quantities from one registry share their bound quantity class.
            assert type(puw.quantity(1, 'nm')) is type(original)
            assert puw.get_value(original, to_unit='nm') == 1

        for name, unit, value, source in (
            ('nanometers', 'nm', 1, '10 angstroms'),
            ('picoseconds', 'ps', 1, '1000 fs'),
            ('kelvin', 'K', 300, '300 K'),
        ):
            result = getattr(puw.fast_track, 'to_' + name)(puw.quantity(source))
            assert puw.has_unit(result, unit)
            assert puw.get_value(result, to_unit=unit) == value
        """
    )
    result = subprocess.run(
        [sys.executable, '-c', script, session],
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
