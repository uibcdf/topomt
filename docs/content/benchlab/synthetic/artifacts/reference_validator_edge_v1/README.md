---
orphan: true
---

# Certified region-volume receiving capsule

This additive capsule retains the **same nineteen original Models** from the
six-case synthetic panel, complete topology proofs and analytic edge-volume
certificates. All original k=24 absolute and relative requests pass for the
total and every region. The sixteen positive regions remain distinct; six
excluded profiles have exact zero volume. It also retains sixteen boundary
precision controls and nine earlier region-volume controls.

The calculation concerns strict free **probe centers inside the declared finite
domain**. Positions/radii are exact rational nm; volumes are nm³. It does not
qualify native DFND promotion, other numerical Models, proteins or a public
TopoMT detector installation.

[Download receiving.zip](receiving.zip) and extract it into a new directory.
The included source checker needs Python's standard library; receiving is
tested with Python 3.14. Run sequentially with appropriate external CPU/memory/
time limits. The commands below do not impose operating-system resource limits.
Large hull/cell checks can take minutes on one CPU.

```bash
python -m devtools.reference_validator verify models/regular_tetrahedron/profile_1.json volumes/regular_tetrahedron/profile_1.json
python -m devtools.reference_validator verify controls/boundary/near_corner_rational/k32/model.json controls/boundary/near_corner_rational/k32/certificate.json
python -m devtools.reference_validator verify controls/region/asymmetric_three_regions/model.json controls/region/asymmetric_three_regions/certificate.json
```

The checker reconstructs source cells, signed face pieces, exact sphere cuts
and outward numerical bounds. It does not trust saved verification totals or
producer-supplied region assignments. Fresh checking is tested with producer,
DFND, NumPy, SciPy and quantity/attribution imports blocked. No process pool,
Rust backend, original external engine or cached accepted state is needed.

`MANIFEST.json` binds the payload; `bundle_manifest.json` also binds the archive
bytes. These are integrity checks, not producer authentication or a formal
proof of the Python implementation. `DERIVATION.md` preserves the developer
derivation; its repository links are also available in the
[maintained mathematical explanation](https://github.com/uibcdf/topomt/blob/main/devguide/DFND/reference_validator_edge_integration.md).

The original case inputs, notebooks, earlier downloads and earlier coarse
results are preserved with their source scope. Full execution/resource records
and remaining admission work live in
[TopoMT #76](https://github.com/uibcdf/topomt/issues/76). Native physical
qualification remains separately owned by
[#181](https://github.com/uibcdf/topomt/issues/181).
