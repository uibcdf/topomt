# CASTp Checkpoint 2026-04-17: Feature-Area Reporting

## Purpose

This note records the closing of one explicit reporting gap: feature surface
area for pockets, channels, branched channels, and voids.

## Historical motivation

The 1998 CAST papers describe pockets and cavities in terms of:

- area
- volume
- mouth area
- mouth circumference

The native path already reported:

- volume
- mouth area
- mouth perimeter

but it still lacked a direct feature-level `area` field.

## Native change

The native reporting layer now includes `component_area(...)` in
`castp_core.metrics`, computed as the sum of triangle areas over the feature
boundary triangulation.

That value is now propagated through:

- `build_castp_feature_records()`
- `_native_impl.py`

So native feature records now preserve:

- `area`
- `volume`
- `mouth_area`
- `mouth_perimeter`

for the feature-level geometry contract.

## Scope and interpretation

This closes the old gap where pockets and cavities did not expose an explicit
feature surface area at all.

It does **not** yet prove that every CAST-side derived area measure is fully
reproduced. The remaining open question is narrower:

- whether any additional CAST/MKALF geometric summaries still remain absent
- not whether feature area itself is missing

## Effect on the open-fronts list

After this change, reporting remains open mainly because:

- the public surface is still TopoMT-shaped rather than CAST-shaped
- some derived summaries may still be unaudited
- `_native_impl.py` still normalizes the output contract

But "missing feature area" should no longer be treated as an open canonical
front.
