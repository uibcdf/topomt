"""Undefined original measurements survive live and portable receiving."""

import json
from pathlib import Path

import numpy as np
import pytest

from tests.methods.pycasta.test_input_context import fake_original as fake_original
from tests.methods.pycasta.test_input_context import source as source
from topomt.third_party.output import _from_topography
from topomt.third_party.pycasta import library
from topomt.third_party.pycasta.files import load_output
from topomt.third_party.pycasta.output import PyCASTAOutput


@pytest.mark.parametrize('marker', ['nan', 'inf', '-inf'])
@pytest.mark.parametrize(
    'field,name',
    [
        ('ranking_scores', 'score'),
        ('pocket_depths', 'depth'),
        ('mouth_area', 'mouth_area'),
        ('mouth_perimeter', 'mouth_perimeter'),
        ('pocket_volumes', 'volume'),
    ],
)
def test_tagged_original_measurement_is_preserved(
    source, fake_original, tmp_path, monkeypatch, field, name, marker
):
    root, _ = fake_original
    execute = library.subprocess.run

    def with_undefined(command, **options):
        result = execute(command, **options)
        path = Path(command[-2])
        state = json.loads(path.read_text())
        state[field][0] = float(marker)
        path.write_text(json.dumps(state))
        return result

    monkeypatch.setattr(library.subprocess, 'run', with_undefined)
    original = _from_topography(
        library.get_topography(
            source, upstream_root=root, structure_indices=1, chemical_state=1
        ),
        PyCASTAOutput,
    )
    bundle = tmp_path / 'undefined.zip'
    original.run.save(bundle)
    recovered = load_output(source, bundle_file=bundle)
    assert recovered.run == original.run
    raw = json.loads(original.run.get_artifact('output/topomt_returned_result.json'))
    assert raw[field][0] == {'nonfinite': marker}
    for output in (original, recovered):
        value = output.pockets[0].measurements[name]
        if marker == 'nan':
            assert np.isnan(value.original_value)
        else:
            assert value.original_value == float(marker)
        assert value.status == 'external_only'
