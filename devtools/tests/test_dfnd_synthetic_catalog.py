"""Keep registered synthetic inputs, exports and historical aliases consistent."""

import hashlib
import re
from pathlib import Path

import numpy as np
import pytest

from devtools.dfnd import build_synthetic_catalog as catalog
from topomt.dfnd import synthetic

INPUT_DIR = Path(__file__).resolve().parents[2] / 'topomt/data/synthetic'
ADDITIONS = {
    'surface_groove',
    'surface_cleft',
    'surface_funnel',
    'pathological_thin_tube',
}
LEGACY_SHA256 = '3b811baaf3f2704e43d45aba9b3532f47df5988b6685efd7894945cfa295dd87'


def test_catalog_covers_every_stored_pdb_and_readme_entry() -> None:
    names = [name for name, *_ in catalog.CATALOG]
    assert len(names) == len(set(names)) == 73
    assert ADDITIONS <= set(names)
    assert {path.stem for path in INPUT_DIR.glob('*.pdb')} == set(names)
    rows = re.findall(
        r'^\| `([^`]+)\.pdb` \|', (INPUT_DIR / 'README.md').read_text(), re.M
    )
    assert len(rows) == len(names)
    assert set(rows) == set(names)


@pytest.mark.parametrize(
    'name, radius, spacing, atom_count, digest',
    [
        (
            'straight_tube_narrow_dense',
            3.5,
            2.5,
            81,
            'd5711d5755925bf1ae2400f21d96e656ff50b4b226f97e708abf4770b3eeccb8',
        ),
        (
            'straight_tube_wide_sparse',
            6.0,
            3.5,
            77,
            '73fc166e0c0bd3e06da852774aaeca737c9adf59aff7627273f46f8bb4e17eb1',
        ),
    ],
)
def test_straight_tube_names_preserve_exact_input_and_generator(
    name, radius, spacing, atom_count, digest, tmp_path
):
    builder = next(builder for case, builder, *_ in catalog.CATALOG if case == name)
    actual = builder()
    expected = synthetic.cylinder_tube(20.0, radius, spacing, jitter=0.1, seed=0)
    assert actual.coords.shape == (atom_count, 3)
    np.testing.assert_array_equal(actual.coords, expected.coords)
    np.testing.assert_array_equal(actual.radii, expected.radii)
    payload = (INPUT_DIR / f'{name}.pdb').read_bytes()
    assert hashlib.sha256(payload).hexdigest() == digest
    expected.to_pdb(tmp_path / f'{name}.pdb')
    assert (tmp_path / f'{name}.pdb').read_bytes() == payload


@pytest.mark.parametrize('name', ['surface_groove', 'surface_cleft', 'surface_funnel'])
def test_morphology_entries_preserve_generator_geometry(
    name: str, tmp_path: Path
) -> None:
    builder = next(builder for case, builder, *_ in catalog.CATALOG if case == name)
    system = builder()
    expected = getattr(synthetic, name)(seed=0)
    np.testing.assert_array_equal(system.coords, expected.coords)
    np.testing.assert_array_equal(system.radii, expected.radii)
    expected.to_pdb(tmp_path / f'{name}.pdb')
    assert (INPUT_DIR / f'{name}.pdb').read_bytes() == (
        tmp_path / f'{name}.pdb'
    ).read_bytes()


def test_catalog_build_preserves_and_discloses_the_historical_alias(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    legacy = (INPUT_DIR / 'pathological_thin_tube.pdb').read_bytes()
    assert hashlib.sha256(legacy).hexdigest() == LEGACY_SHA256
    assert catalog.PDB_ALIASES == {
        'pathological_thin_tube': 'pathological_thin_tube_r25'
    }
    other = (INPUT_DIR / 'pathological_thin_tube_r25.pdb').read_text()
    coordinates = [
        [
            [float(line[start : start + 8]) for start in (30, 38, 46)]
            for line in text.splitlines()
            if line.startswith('HETATM')
        ]
        for text in (legacy.decode(), other)
    ]
    assert len(coordinates[0]) == 30
    np.testing.assert_array_equal(coordinates[0], coordinates[1])
    monkeypatch.setattr(
        catalog, 'CATALOG', [row for row in catalog.CATALOG if row[0] in ADDITIONS]
    )
    # This exercises inventory/export work, without running a DFND study.
    monkeypatch.setattr(catalog, '_family_summary', lambda *args: 'not characterized')
    catalog.build(tmp_path)
    assert (tmp_path / 'pathological_thin_tube.pdb').read_bytes() == legacy
    assert {path.stem for path in tmp_path.glob('*.pdb')} == ADDITIONS
    readme = (tmp_path / 'README.md').read_text()
    assert 'historical alias' in readme
    assert 'pathological_thin_tube_r25' in readme
    monkeypatch.setattr(catalog, '_SOURCE_PDB_DIR', tmp_path)
    catalog.build(tmp_path)
    assert (tmp_path / 'pathological_thin_tube.pdb').read_bytes() == legacy


def test_catalog_rejects_a_missing_historical_input(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(
        catalog,
        'CATALOG',
        [row for row in catalog.CATALOG if row[0] == 'pathological_thin_tube'],
    )
    monkeypatch.setattr(catalog, '_SOURCE_PDB_DIR', tmp_path)
    monkeypatch.setattr(catalog, '_family_summary', lambda *args: 'not characterized')
    with pytest.raises(FileNotFoundError):
        catalog.build(tmp_path)
