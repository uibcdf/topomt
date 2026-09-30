import zipfile

import pytest

from topomt.provider_output import ProviderRun


def test_provider_run_preserves_files_after_sources_disappear(tmp_path):
    input_file = tmp_path / 'input.pdb'
    output_dir = tmp_path / 'output'
    nested = output_dir / 'pockets'
    nested.mkdir(parents=True)
    input_file.write_bytes(b'ATOM  original\n')
    (nested / 'pocket1.pqr').write_bytes(b'\x00\xff\n')

    run = ProviderRun.capture(
        'fpocket', 'cli', input_file, output_dir, metadata={'selection': 'all'}
    )
    bundle = tmp_path / 'run.zip'
    run.save(bundle)
    input_file.unlink()
    (nested / 'pocket1.pqr').unlink()

    restored = ProviderRun.load(bundle)
    assert restored.run_id == run.run_id
    assert restored.metadata == {'selection': 'all'}
    assert restored.get_artifact('input/input.pdb') == b'ATOM  original\n'
    assert restored.get_artifact('output/pockets/pocket1.pqr') == b'\x00\xff\n'


def test_provider_run_rejects_changed_artifact(tmp_path):
    input_file = tmp_path / 'input.pdb'
    output_dir = tmp_path / 'output'
    output_dir.mkdir()
    input_file.write_bytes(b'original')
    (output_dir / 'info.txt').write_bytes(b'original output')
    run = ProviderRun.capture('fpocket', 'files', input_file, output_dir)
    bundle = tmp_path / 'run.zip'
    run.save(bundle)

    altered = tmp_path / 'altered.zip'
    with zipfile.ZipFile(bundle) as source, zipfile.ZipFile(altered, 'w') as target:
        for name in source.namelist():
            content = source.read(name)
            target.writestr(name, b'changed' if name == 'output/info.txt' else content)

    with pytest.raises(ValueError, match='checksum'):
        ProviderRun.load(altered)


def test_provider_run_rejects_missing_artifact(tmp_path):
    input_file = tmp_path / 'input.pdb'
    output_dir = tmp_path / 'output'
    output_dir.mkdir()
    input_file.write_bytes(b'original')
    (output_dir / 'info.txt').write_bytes(b'output')
    run = ProviderRun.capture('fpocket', 'files', input_file, output_dir)
    bundle = tmp_path / 'run.zip'
    run.save(bundle)

    incomplete = tmp_path / 'incomplete.zip'
    with zipfile.ZipFile(bundle) as source, zipfile.ZipFile(incomplete, 'w') as target:
        target.writestr('manifest.json', source.read('manifest.json'))
        target.writestr('input/input.pdb', source.read('input/input.pdb'))

    with pytest.raises(ValueError, match='missing'):
        ProviderRun.load(incomplete)


def test_provider_run_preserves_additional_inputs_and_hashes_them(tmp_path):
    receptor = tmp_path / 'input.pdb'
    binder = tmp_path / 'binder.pdb'
    output = tmp_path / 'output'
    output.mkdir()
    receptor.write_bytes(b'receptor')
    binder.write_bytes(b'ligand')
    run = ProviderRun.capture(
        'alphaspace2',
        'library',
        receptor,
        output,
        additional_inputs={'binder/input.pdb': binder},
    )
    bundle = tmp_path / 'bound.zip'
    run.save(bundle)
    binder.write_bytes(b'different ligand')
    changed = ProviderRun.capture(
        'alphaspace2',
        'library',
        receptor,
        output,
        additional_inputs={'binder/input.pdb': binder},
    )
    receptor.unlink()
    binder.unlink()
    restored = ProviderRun.load(bundle)
    assert restored == run
    assert restored.get_artifact('input/input.pdb') == b'receptor'
    assert restored.get_artifact('input/binder/input.pdb') == b'ligand'
    assert changed.run_id != run.run_id


@pytest.mark.parametrize('name', ['../ligand.pdb', '/ligand.pdb', 'input.pdb'])
def test_provider_run_rejects_unsafe_or_duplicate_additional_inputs(tmp_path, name):
    receptor = tmp_path / 'input.pdb'
    output = tmp_path / 'output'
    output.mkdir()
    receptor.write_bytes(b'receptor')
    with pytest.raises(ValueError, match='Unsafe|Duplicate'):
        ProviderRun.capture(
            'alphaspace2',
            'library',
            receptor,
            output,
            additional_inputs={name: receptor},
        )
