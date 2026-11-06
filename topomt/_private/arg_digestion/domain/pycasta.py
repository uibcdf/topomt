"""Declare execution versus saved pyCASTA options without loading its engine."""

from argdigest import Domain

from ..pycasta_arguments import FILES_PARAMETERS, LIBRARY_PARAMETERS

domain = Domain(
    name='pycasta_options',
    depends_on='backend',
    by_value={
        'library': LIBRARY_PARAMETERS,
        'wrapper': LIBRARY_PARAMETERS,
        'files': FILES_PARAMETERS,
    },
    description='Saved bundles supply their recorded selection, frame and chemistry; native options remain owned by the native route.',
)
