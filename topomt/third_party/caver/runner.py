"""Run CAVER 3.02 CLI with explicit origin, Java limits and original config."""

from pathlib import Path

from topomt.third_party._execution import file_identity, java_setup, run_command


def ensure_available(options: dict) -> None:
    java_setup('caver', options, 'caver.jar')


def run(pdb: Path, output: Path, options: dict) -> tuple[dict, dict]:
    home, java, command = java_setup('caver', options, 'caver.jar')
    origin = options['origin']
    values = {
        key: options.get(key, default)
        for key, default in [
            ('probe_radius', 0.9),
            ('shell_radius', 3.0),
            ('shell_depth', 4.0),
        ]
    }
    config = output.parent / 'config.txt'
    config.write_text(
        'starting_point_coordinates '
        + ' '.join(map(str, origin))
        + '\n'
        + ''.join(f'{key} {value}\n' for key, value in values.items())
        + 'seed 1\ngenerate_tunnel_profiles yes\ngenerate_summary yes\ngenerate_histograms no\ngenerate_bottleneck_heat_map no\ngenerate_profile_heat_map no\nsave_dynamics_visualization no\n'
    )
    inputs = output.parent / 'structures'
    inputs.mkdir()
    import shutil

    shutil.copyfile(pdb, inputs / 'input.pdb')
    command += [
        '-jar',
        str(home / 'caver.jar'),
        '-home',
        str(home),
        '-pdb',
        str(inputs),
        '-conf',
        str(config),
        '-out',
        str(output),
    ]
    run_command(
        command,
        output,
        timeout=options.get('timeout', 300),
        workers=options.get('workers', 1),
    )
    identities = {
        str(path.relative_to(home)): file_identity(path)
        for path in sorted((home / 'bin').rglob('*'))
        if path.is_file()
    }
    return {
        'version': '3.02'
        if file_identity(home / 'caver.jar')['sha256']
        == '6ed4d88fa1a364cc77934534a2917c6ec0089e5b413e235f4bad1a0b30c3609a'
        else None,
        'output_protocol_version': '3.02',
        'engine_jar': file_identity(home / 'caver.jar'),
        'java': file_identity(Path(java)),
        'support_files': identities,
        'command': command,
        'origin': {'value': origin, 'unit': 'angstroms'},
        'parameters': {
            key: {'value': value, 'unit': 'angstroms'} for key, value in values.items()
        },
        'resources': {
            'workers': options.get('workers', 1),
            'java_heap_mib': options.get('memory_mb', 1024),
        },
    }, {'config.txt': config}
