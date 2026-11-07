"""The original routes' signatures own the admissible fpocket option names."""

from inspect import signature

from argdigest import Domain


def _members() -> tuple[str, ...]:
    from topomt.third_party.fpocket import cli, files

    names = set(signature(cli.get_topography).parameters)
    names.update(signature(files.load_topography).parameters)
    names.update(signature(files.load_output).parameters)
    return tuple(sorted(names - {'molecular_system', 'backend', 'skip_digestion'}))


domain = Domain(
    name='fpocket_options',
    members=_members,
    description='Union of original CLI/files option names; each closed leaf enforces its own signature.',
)


def _file_members() -> tuple[str, ...]:
    from topomt.third_party.fpocket.files import load_topography

    return tuple(
        sorted(
            set(signature(load_topography).parameters)
            - {'molecular_system', 'skip_digestion'}
        )
    )


DOMAINS = [Domain(name='fpocket_file_options', members=_file_members)]
