"""Power-cell progress is verified work, never an incomplete global answer."""

import json
from copy import deepcopy

import pytest

from devtools.reference_validator.model import Box, Model, point
from devtools.reference_validator.power_cells import topology_certificate
from devtools.reference_validator.power_runs import (
    finish_power_run,
    load_power_bundle,
    resume_power_run,
    save_power_bundle,
    start_power_run,
)
from devtools.reference_validator.verify.power_progress import check_progress


def _model():
    return Model.from_spheres(
        [(-8, 0, 0), (8, 0, 0)],
        [4, 4],
        1,
        domain=Box(point((-20, -3, -4)), point((20, 3, 4))),
    )


def test_interrupted_cells_resume_to_the_identical_complete_certificate(tmp_path):
    model = _model()
    state = start_power_run(model, cell_budget=1)
    assert check_progress(model, state)['topology_complete'] is False
    assert check_progress(model, state)['remaining_atom_ids'] == [1]
    with pytest.raises(ValueError, match='incomplete'):
        finish_power_run(model, state)
    save_power_bundle(tmp_path / 'step', model, state)
    saved = load_power_bundle(tmp_path / 'step', model)
    final = resume_power_run(model, saved, cell_budget=1)
    assert finish_power_run(model, final) == topology_certificate(model)
    assert state == saved  # resume never mutates the earlier evidence


@pytest.mark.parametrize(
    'field', ['remaining_atom_ids', 'model_sha256', 'kernel', 'cells']
)
def test_progress_rejects_omissions_changed_source_and_corrupt_cells(field):
    model = _model()
    state = deepcopy(start_power_run(model, cell_budget=1))
    if field == 'remaining_atom_ids':
        state[field] = []
    elif field == 'model_sha256':
        state[field] = '0' * 64
    elif field == 'kernel':
        state[field]['algorithm'] = 'changed'
    else:
        state[field][0]['vertices'].pop()
    with pytest.raises(ValueError):
        resume_power_run(model, state, cell_budget=1)


def test_cooperative_stop_keeps_previously_completed_cells_and_can_resume():
    model = _model()
    initial = start_power_run(model, cell_budget=1)
    stopped = resume_power_run(model, initial, cell_budget=1, stop=lambda: True)
    assert stopped['cells'] == initial['cells']
    assert stopped['stop_reason'] == 'cancelled'
    final = resume_power_run(model, stopped, cell_budget=1)
    assert finish_power_run(model, final) == topology_certificate(model)


def test_torn_bundle_and_changed_manifest_never_replace_the_last_valid_bundle(tmp_path):
    model = _model()
    state = start_power_run(model, cell_budget=1)
    save_power_bundle(tmp_path / 'valid', model, state)
    (tmp_path / 'torn').mkdir()
    (tmp_path / 'torn/progress.json').write_text(json.dumps(state))
    with pytest.raises(ValueError):
        load_power_bundle(tmp_path / 'torn', model)
    with pytest.raises(FileExistsError):
        save_power_bundle(tmp_path / 'valid', model, state)
    assert load_power_bundle(tmp_path / 'valid', model) == state


def test_changed_work_configuration_and_boolean_source_ids_are_rejected():
    model = _model()
    state = start_power_run(model, cell_budget=1)
    altered = deepcopy(state)
    altered['limits']['max_support_planes'] -= 1
    with pytest.raises(ValueError):
        resume_power_run(model, altered)
    altered = deepcopy(state)
    altered['remaining_atom_ids'] = [True]
    with pytest.raises(ValueError):
        resume_power_run(model, altered)


def test_stop_inside_a_new_cell_does_not_publish_that_partial_cell():
    model = _model()
    initial = start_power_run(model, cell_budget=1)
    calls = 0

    def stop():
        nonlocal calls
        calls += 1
        return calls >= 3

    stopped = resume_power_run(model, initial, stop=stop)
    assert stopped['cells'] == initial['cells']
    assert stopped['stop_reason'] == 'cancelled'
    assert finish_power_run(
        model, resume_power_run(model, stopped)
    ) == topology_certificate(model)
