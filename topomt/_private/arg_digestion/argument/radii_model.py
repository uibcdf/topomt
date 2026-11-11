"""Validate DFND radius-model names within their selected dispatch context."""

from topomt._private.smonitor import ArgumentError


def digest_radii_model(
    radii_model: object,
    method: str | None = None,
    engine: str | None = None,
    caller: str | None = None,
) -> object:
    # Other methods, including CASTp, own different radius-model vocabularies.
    # Follow the dispatcher's engine override after ArgDigest normalizes names.
    selected_method = engine if engine is not None else method
    if selected_method != 'dfnd':
        return radii_model

    if isinstance(radii_model, str) and radii_model in {'vdw', 'protor', 'provided'}:
        return radii_model

    raise ArgumentError(
        arg_name='radii_model',
        value=radii_model,
        caller=caller,
        reason="radii_model must be 'vdw', 'protor', or 'provided'.",
    )
