"""Recover an original provider result using its verified evidence identity."""

from pathlib import Path
from typing import Any

from ._private.arg_digestion import arg_digest
from ._private.arg_digestion.external_arguments import _error
from ._private.arg_digestion.provider_persistence import (
    LOAD_CALLER,
    LOAD_PIPELINES,
    OPTIONS,
)
from ._private.smonitor import signal
from .get_provider_output import get_provider_output
from .provider_output import ProviderRun
from .third_party.output import ProviderOutput

_SAVED_BACKENDS = {
    'fpocket': {'cli', 'wrapper', 'files'},
    'pocketeer': {'library'},
    'alphaspace2': {'library'},
    'pycasta': {'library'},
    'castp': {'files'},
    'pykvfinder': {'library'},
    'ghecom': {'cli'},
    'caver': {'cli'},
    'p2rank': {'cli'},
}


@signal(tags=['provider', 'files', 'recovery'])
@arg_digest(**OPTIONS, map=LOAD_PIPELINES)
def load_provider_output(
    bundle_file: str | Path,
    *,
    molecular_system: Any,
    binder: Any = None,
) -> ProviderOutput:
    """Recover saved original results without running their scientific engine.

    Parameters
    ----------
    bundle_file : str or pathlib.Path
        Original evidence written by ProviderOutput.save or ProviderRun.save.
        Its manifest, artifact hashes and run ID are verified before dispatch.
    molecular_system : MolSysMT-compatible input
        Full original source, including the recorded identities, coordinate
        frame and reference chemistry. The bundle does not replace this source.
    binder : MolSysMT-compatible input, optional
        Original binder source for bound AlphaSpace2 results. Omit it for other
        providers and for unbound runs. Its context is verified by that reader.

    Returns
    -------
    ProviderOutput
        Provider-specific reconstructed records, retaining the original run,
        backend, metadata and artifact bytes. Available empty output stays empty.

    Raises
    ------
    ArgumentError
        If arguments are invalid, a source is absent, context overrides are
        supplied or binder is supplied for a different provider.
    ValueError
        If integrity, provider/backend identity or saved source context is
        unsupported or disagrees. Bundles without sufficient context are not
        upgraded by inference, including current direct-server CASTp captures.
    OSError
        If the bundle cannot be read.

    Notes
    -----
    Method and backend are read from the verified bundle. Execution settings,
    selections, frame and chemical state are restored by its existing reader;
    they cannot be replaced through this function. Recovering does not contact
    an original server or require its optional engine. Native reproductions
    are not selected. ProviderRun.load remains available for inspecting evidence
    that lacks the context required for source-bound reconstruction.
    CASTp reconstruction currently accepts source-bound files captures. Saving
    a direct-server result preserves its evidence but adds no source context.

    Examples
    --------
    >>> output.save('original.zip')  # doctest: +SKIP
    >>> recovered = load_provider_output(  # doctest: +SKIP
    ...     'original.zip', molecular_system='source.h5msm')
    >>> recovered.run == output.run  # doctest: +SKIP
    True
    """
    original = ProviderRun.load(bundle_file)
    supported = _SAVED_BACKENDS.get(original.provider)
    if supported is None or original.backend not in supported:
        raise ValueError(
            'Unsupported saved original-provider route: '
            f'{original.provider!r}/{original.backend!r}.'
        )
    if binder is not None and original.provider != 'alphaspace2':
        _error(
            'binder',
            binder,
            LOAD_CALLER,
            'binder is only supported for saved AlphaSpace2 results.',
        )
    kwargs = {} if original.provider != 'alphaspace2' else {'binder': binder}
    restored = get_provider_output(
        molecular_system,
        method=original.provider,
        backend='files',
        bundle_file=bundle_file,
        **kwargs,
    )
    if restored.run != original:
        raise ValueError('Recovered output disagrees with the verified original run.')
    return restored
