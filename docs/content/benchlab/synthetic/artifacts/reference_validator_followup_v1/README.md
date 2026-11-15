---
orphan: true
---

# Reference-validator follow-up capsule

This additive capsule retains all nineteen original finite-hull topology
proofs, their conservative total/per-region volume proofs, sixteen analytic
eight-region precision controls and two native carrier comparisons with separately checked exact actual-vdW Models.
The original BenchLab inputs, notebooks and earlier downloads are unchanged.

All positions/radii are exact encoded rational nm and volumes are nm**3.
Contacts with expanded atomic balls are excluded. Finite-hull connectivity,
valid volume enclosures and requested volume precision have separate states.
Original positive k=24 precision remains unresolved in this receiving. Exact
zero volumes pass for the six excluded profiles. Analytic control precision
does not qualify arbitrary clipped hulls or native public promotion.

Extract into a new directory. The saved checker needs Python's standard
library; source receiving is tested with Python 3.14, without an installed
TopoMT, DFND, NumPy or quantity package. Run checks sequentially under local
CPU/memory/time limits. Full original hull checks can take minutes; these
commands do not impose scheduler or operating-system limits themselves.

From the extracted directory, for a small original example:

```bash
python -m devtools.reference_validator verify models/regular_tetrahedron/profile_1.json topology/regular_tetrahedron/profile_1.json
python -m devtools.reference_validator verify models/regular_tetrahedron/profile_1.json volumes/regular_tetrahedron/profile_1.json
python -m devtools.reference_validator verify controls/near_corner_rational/k32/model.json controls/near_corner_rational/k32/certificate.json
```

The checker recomputes mathematical claims rather than trusting saved check
outputs. `MANIFEST.json` binds every payload member; the external bundle
manifest additionally binds the ZIP itself. These are integrity checks,
not producer authentication or a formal proof of the implementation.

Original producer/kernel identities remain in the retained records and linked
repository receipts. Reading old proofs with this checker is distinct from
same-kernel resume: source/runtime changes require an explicit new run.
This is saved developer evidence, not a production detector installation.

The derivations explain coverage, shared trusted primitives, volume bounds
and the restricted cap/wedge admission. Current issue disposition and full
execution records: https://github.com/uibcdf/topomt/issues/76 ; the first
native qualification consumer remains https://github.com/uibcdf/topomt/issues/181 .
