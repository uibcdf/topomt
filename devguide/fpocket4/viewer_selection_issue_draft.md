# Draft: Active selection fails on bundled pentalanine with unavailable chain indices

Proposed owner: `uibcdf/molsysviewer`. Not published.
Consumer evidence: [TopoMT #101](https://github.com/uibcdf/topomt/issues/101) and
the [complete source-suite checkpoint](full_suite_checkpoint.md).

## Reproduction

Using the installed packages and public MolSysViewer calls:

```python
import molsysviewer as msv

view = msv.MolSysView()
view.load(msv.demo['pentalanine'].molsys)
view.active_selection.set([0, 1, 2])
```

The selection raises:

```text
TypeError: int() argument must be a string, a bytes-like object or a real number, not 'NoneType'
```

In this input, MolSysMT reports `chain_index=[None, None, None]` for the selected
atoms. Group, component, molecule and entity indices are available. The failing
statement in `molsysviewer/active_selection.py:253` converts all per-level parent
indices with `int(value)` without handling the unavailable chain values.

## Observed environment and consumer impact

- Linux x86_64, Python 3.14.7.
- MolSysViewer `0.24.0+188.g73a6f388`, source
  `73a6f388e09146650349dfe83564ae318ba20298`.
- MolSysMT `0.23.0+368.g00abb958f`, source
  `00abb958fb93649131d5ce5fe5e12e90cf4900e9`.
- ArgDigest 0.17.0. The bundled H5MSM 0.4 reader emits its deprecation warning.

This also fails two TopoMT tests:
`test_simplex_menu_selection_sets_native_selection_and_is_inspectable` and
`test_partial_mesh_global_selection_hover_click_boundary`, both in
`tests/test_molsysviewer_topomt_addon.py`.
Both reproduce against TopoMT's pre-ArgDigest source
`edb43579b2a937e1ac5faa7f89876c7ff3c81e5c` with the same package environment.
The standalone reproduction uses no TopoMT operation. Installed addon discovery
can still import TopoMT; this is not a claim that its package was absent.

## Requested analysis

Review active-selection handling of unavailable parent indices and the bundled
demo's topology/legacy schema. Preserve the selected atom indices and the
difference between unavailable and available parent membership. Do not fabricate
a chain index or silently discard the selected atoms. Add a regression for this
public demo workflow and any accepted representation of unavailable metadata.
