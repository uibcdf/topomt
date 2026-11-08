"""Run the original maintained MOLE CLI with explicit .NET resource controls."""

import xml.etree.ElementTree as ET
from pathlib import Path

from topomt.third_party._execution import (
    ProviderExecutionError,
    executable_command,
    file_identity,
    run_command,
)
from topomt.third_party._saved_json import read_json

from .parser import VERSION

# Write defaults explicitly; the complete original configuration is also captured.
PARAMETERS = {
    'probe_radius': ('Cavity', 'ProbeRadius', 3.0),
    'interior_threshold': ('Cavity', 'InteriorThreshold', 1.25),
    'min_depth': ('Cavity', 'MinDepth', 8),
    'min_depth_length': ('Cavity', 'MinDepthLength', 5.0),
    'ignore_hetatoms': ('Cavity', 'IgnoreHETAtoms', False),
    'ignore_hydrogens': ('Cavity', 'IgnoreHydrogens', False),
    'min_tunnel_length': ('Tunnel', 'MinTunnelLength', 0.0),
    'min_pore_length': ('Tunnel', 'MinPoreLength', 0.0),
    'surface_cover_radius': ('Tunnel', 'SurfaceCoverRadius', 10.0),
    'origin_radius': ('Tunnel', 'OriginRadius', 5.0),
    'bottleneck_radius': ('Tunnel', 'BottleneckRadius', 1.25),
    'bottleneck_tolerance': ('Tunnel', 'BottleneckTolerance', 0.0),
    'auto_origin_cover_radius': ('Tunnel', 'AutoOriginCoverRadius', 10.0),
    'max_auto_origins_per_cavity': ('Tunnel', 'MaxAutoOriginsPerCavity', 5),
    'weight_function': ('Tunnel', 'WeightFunction', 'VoronoiScale'),
}


def ensure_available(options: dict) -> None:
    executable_command('mole', options.get('mole_cmd', 'mole2'))


def run(pdb: Path, output: Path, options: dict) -> tuple[dict, dict]:
    command = executable_command('mole', options.get('mole_cmd', 'mole2'))
    root = ET.Element('Tunnels')
    ET.SubElement(root, 'Input').text = str(pdb)
    ET.SubElement(root, 'WorkingDirectory').text = str(output)
    parameters = ET.SubElement(root, 'Params')
    sections = {name: ET.SubElement(parameters, name) for name in ('Cavity', 'Tunnel')}
    values = {}
    for key, (section, name, default) in PARAMETERS.items():
        value = options.get(key, default)
        values[key] = value
        sections[section].set(
            name, str(int(value)) if type(value) is bool else str(value)
        )
    export = ET.SubElement(root, 'Export')
    ET.SubElement(export, 'Formats', JSON='1', CSV='1')
    ET.SubElement(
        export,
        'Types',
        Cavities='1',
        Tunnels='1',
        PoresAuto=str(int(options.get('compute_pores', False))),
        PoresMerged=str(int(options.get('compute_merged_pores', False))),
    )
    origins = ET.SubElement(root, 'Origins', Auto='0' if 'origin' in options else '1')
    if 'origin' in options:
        ET.SubElement(
            ET.SubElement(origins, 'Origin'),
            'Point',
            dict(zip('XYZ', map(str, options['origin']), strict=True)),
        )
    config = output.parent / 'config.xml'
    ET.ElementTree(root).write(config, encoding='utf-8', xml_declaration=True)
    workers = options.get('workers', 1)
    memory = options.get('memory_mb', 1024)
    argv = [command, str(config)]
    run_command(
        argv,
        output,
        timeout=options.get('timeout', 300),
        workers=workers,
        extra_env={
            'DOTNET_PROCESSOR_COUNT': str(workers),
            'DOTNET_GCHeapHardLimit': hex(memory * 1024 * 1024),
            'DOTNET_CLI_TELEMETRY_OPTOUT': '1',
        },
    )
    stdout = (output / 'stdout.txt').read_text()
    try:
        if (
            not stdout.startswith(f'WebChemistry Tunnels {VERSION},')
            or not any(line.startswith('Done in ') for line in stdout.splitlines())
            or any(
                line.strip() in ('Error:', 'Input Errors:')
                for line in stdout.splitlines()
            )
        ):
            raise ValueError(
                'Original version/completion marker is missing or reports an error'
            )
        for filename, tag in (
            ('tunnels.xml', 'Tunnels'),
            ('pores.xml', 'Pores'),
            ('pores_merged.xml', 'MergedPores'),
            ('paths.xml', 'Paths'),
            ('cavities.xml', 'Cavities'),
            ('startpoints.xml', 'StartPoints'),
        ):
            document = ET.parse(output / 'xml' / filename)
            if (
                document.getroot().tag != tag
                or filename != 'startpoints.xml'
                and document.getroot().attrib.get('Version') != VERSION
                or document.find('.//Exception') is not None
            ):
                raise ValueError(
                    f'Original {filename} reports an incompatible or failed computation'
                )
        data = read_json((output / 'json/data.json').read_bytes(), provider='mole')
        if not isinstance(data, dict) or data.get('Version') != VERSION:
            raise ValueError('Original JSON version disagrees')
    except (ValueError, OSError, ET.ParseError) as error:
        raise ProviderExecutionError(
            provider='mole', reason=f'incomplete original result: {error}'
        ) from error
    home = Path(command).parent
    companions = set(home.glob('*.dll')) | set(home.glob('mole2*.json'))
    distribution = {
        path.name: file_identity(path) for path in sorted(companions) if path.is_file()
    }
    return {
        'version': VERSION,
        'output_protocol_version': VERSION,
        'executable': file_identity(Path(command)),
        'distribution_files': distribution,
        'command': argv,
        'parameters': {
            key: {'value': value, 'unit': 'angstroms'}
            if key
            not in {
                'min_depth',
                'ignore_hetatoms',
                'ignore_hydrogens',
                'max_auto_origins_per_cavity',
                'weight_function',
            }
            else value
            for key, value in values.items()
        },
        'origin': None
        if 'origin' not in options
        else {'value': options['origin'], 'unit': 'angstroms'},
        'origin_policy': 'automatic' if 'origin' not in options else 'explicit_point',
        'compute_pores': options.get('compute_pores', False),
        'compute_merged_pores': options.get('compute_merged_pores', False),
        'original_units': {'length': 'angstroms', 'tetrahedral_volume': 'angstroms**3'},
        'resources': {'workers': workers, 'managed_heap_mib': memory},
    }, {'config.xml': config}
