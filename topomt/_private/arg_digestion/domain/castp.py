"""Declare CASTp options while preserving raw archive compatibility."""

from argdigest import Domain

from ..castp_arguments import RAW_PARAMETERS, SAVED_PARAMETERS, SERVER_PARAMETERS

DOMAINS = [
    Domain(
        name='castp_original_options',
        depends_on='backend',
        by_value={
            'server': SERVER_PARAMETERS,
            'castpfold': SERVER_PARAMETERS,
            'files': tuple(dict.fromkeys((*RAW_PARAMETERS, *SAVED_PARAMETERS))),
        },
        description='Original routes own their options; the registered original_backend pipeline narrows saved bundles to source, bundle and server identity.',
    ),
    Domain(name='castp_raw_options', members=RAW_PARAMETERS),
]
