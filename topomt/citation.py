"""Inspect saved scientific attribution and delegate rendering to Ackredit."""

from typing import Any, Optional

from ._ackredit import attribution_of, backend


def get_attribution(result: Any) -> Optional[dict[str, Any]]:
    """Return detached result bibliography without registering another use.

    Parameters
    ----------
    result : Topography, ProviderOutput, mesh or dict
        A result with TopoMT scientific attribution.

    Returns
    -------
    dict or None
        Original producer, recording status and bibliographic declarations.
        None means that this result has no recorded provenance, as with legacy
        saved results. Ackredit need not be installed to inspect it.

    Examples
    --------
    >>> references = get_attribution(result)  # doctest: +SKIP
    """
    return attribution_of(result)


def cite(result: Any, format: str = 'bibtex') -> str:
    """Render a result's bibliography through Ackredit without new credit.

    Parameters
    ----------
    result : Topography, ProviderOutput, mesh or dict
        Original attributed result, including one recovered from a bundle.
    format : str, default='bibtex'
        An Ackredit report format, for example 'markdown' or 'csl-json'.

    Returns
    -------
    str
        Bibliography rendered by the optional Ackredit provider.

    Raises
    ------
    ValueError
        If attribution is absent, saved records conflict or the format is unsupported.
    ImportError
        If Ackredit is unavailable. get_attribution remains usable without it.

    Notes
    -----
    Host declarations remain renderable after absent/failed recording. That
    does not retrospectively mark the original workflow as successfully tracked.
    No upstream engine, DOI service, registration or scientific calculation runs.

    Examples
    --------
    >>> bibliography = cite(result)  # doctest: +SKIP
    """
    saved = attribution_of(result)
    if saved is None:
        raise ValueError('This result has no recorded scientific attribution.')
    provider = backend()
    if provider is None:
        raise ImportError(
            'Rendering requires Ackredit; use get_attribution for offline records.'
        )
    if saved['status'] == 'recorded' and saved['ackredit'] is not None:
        portable = saved['ackredit']
    else:
        # Construct only the documented public exchange format from our own
        # explicit declarations. Ackredit owns validation and rendering.
        observed = saved['ackredit']
        items = {item['id']: item for item in observed['items']} if observed else {}
        for entry in saved['references']:
            item = entry['item']
            observed_item = items.get(item['id'])
            if observed_item is not None and observed_item != item:
                raise ValueError(
                    f'Conflicting saved bibliography for {item["id"]}. Inspect the original snapshot and host declarations.'
                )
            items[item['id']] = item
        uses = [
            {
                'item_id': entry['item']['id'],
                'used_by': entry['target'],
                'roles': entry['roles'],
                'context': entry['context'],
            }
            for entry in saved['references']
        ]
        if observed:
            uses = [*observed['uses'], *uses]
        portable = {
            'schema': 'ackredit.attribution@1',
            'name': 'TopoMT saved result',
            'context': {
                'producer': saved['producer'],
                'recording_status': saved['status'],
            },
            'items': list(items.values()),
            'uses': uses,
            'usage_tree': observed['usage_tree'] if observed else {},
        }
    return provider.Attribution.from_dict(portable).report(format=format)
