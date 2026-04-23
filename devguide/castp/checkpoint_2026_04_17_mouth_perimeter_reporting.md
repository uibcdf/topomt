"""Checkpoint for mouth circumference reporting in the native CASTp path."""

# Checkpoint 2026-04-17: Mouth Circumference Reporting

## Purpose

This checkpoint records a canonical reporting improvement in the native CASTp
path.

The goal is to close one explicit gap against the public CAST contract:

- mouth opening circumference

## Historical / paper reference

The 1998 CAST reporting contract explicitly includes:

- mouth area
- mouth circumference

The reporting audit already identified this as a real gap in the native path.

## Native Correction

The native reporting layer now computes and exposes:

- per-mouth `perimeter`
- feature-level `mouth_perimeter` as the sum over all mouths

The perimeter is computed from the boundary edges of the mouth triangulation,
not by summing every triangle edge in the patch.

This is important because the mouth is a triangulated opening, and its
circumference must correspond to the boundary polygon of that opening.

## Implementation Notes

The new helper:

- `mouth_perimeter(...)`

was added in `core/castp_core/metrics.py`.

It:

- counts edges over the mouth-face patch
- keeps only edges that occur once
- sums only those boundary-edge lengths

The result is propagated through:

- `build_castp_feature_records()`
- `_native_impl._component_to_record()`

so the public native records now keep the circumference data.

## Structural Regression

`tests/test_castp_core.py` now includes:

- a direct metric regression proving that a two-triangle square mouth has
  perimeter `4.0`
- a component-builder regression proving that `mouth_perimeter` and per-mouth
  `perimeter` are serialized
- and a native wrapper regression proving `_native_impl.py` preserves the new
  reporting fields

## Status

This does not close the full reporting front:

- `iF/rF/iE/rE/iV/rV` are still not fully exposed
- pocket/cavity surface-area reporting is still incomplete

But it closes one direct and explicit gap against the public CAST output
contract.
