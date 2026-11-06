"""Original AlphaSpace2 output contract."""

from topomt.third_party.output import ProviderOutput


def _output_protocol() -> dict:
    """Declare original Snapshot numeric fields without importing the engine."""
    units = {
        name: 'angstroms'
        for name in ('_alpha_xyz', '_alpha_radii', '_beta_xyz', '_pocket_xyz')
    }
    units.update(
        {
            name: 'angstroms**3'
            for name in ('_alpha_space', '_beta_space', '_pocket_space')
        }
    )
    units.update({'_alpha_space_nonpolar_ratio': '1', '_beta_scores': 'unspecified'})
    for group in ('pocket_properties', 'beta_properties'):
        for name in (
            'space',
            'nonpolar_space',
            'occupied_space',
            'occupied_nonpolar_space',
        ):
            units[f'{group}[*].{name}'] = 'angstroms**3'
        for name in ('occupancy', 'occupancy_nonpolar'):
            units[f'{group}[*].{name}'] = '1'
        units[f'{group}[*].score'] = 'unspecified'
    units['beta_properties[*].scores'] = 'unspecified'
    return {
        'schema_version': 1,
        'artifact': 'output/topomt_snapshot.json',
        'units': units,
        'snapshot_settings_units': {
            name: 'angstroms'
            for name in (
                'min_r',
                'max_r',
                'beta_cluster_dist',
                'pocket_cluster_dist',
                'contact_cutoff',
            )
        },
    }


class AlphaSpace2Output(ProviderOutput):
    """AlphaSpace2 pockets with alpha/beta sites and original contact state.

    See ProviderOutput for construction and shared access. Run artifacts retain
    receptor, optional binder, full snapshot and exports. Alpha-space, nonpolar
    contributions and weighted occupancy keep AlphaSpace2's definitions; they
    are not geometric intersections or binding probabilities.
    """

    provider = 'alphaspace2'
