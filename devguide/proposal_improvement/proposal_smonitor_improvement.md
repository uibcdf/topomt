**Proposal: Use This Space for smonitor Suggestions**

While implementing TopoMT’s native engines we consistently rely on `smonitor` to emit
signals, warnings, and telemetry. If, during that work, we identify functionality gaps
or helper patterns (e.g., richer diagnostic bundles, catalog entries, or helper APIs)
the right place to propose them is here: record the observation and we will port it to
the shared `smonitor` repo rather than keeping ad hoc local copies.

For example, the new emitter/warnings helpers in TopoMT could be generalized upstream
if other MolSysMT-based projects need the same cataloged diagnostics. This document
reminds contributors to consider whether their local change deserves an upstream issue
before expanding TopoMT’s own subset.

### Report: SASA backend restriction

While implementing the Pocketeer workflow we discovered that `molsysmt.physchem.get_sasa`
cannot be configured with the `polar_probe_radius` that the upstream project uses for
classifying buried alpha spheres. The API simply forwards to MDtraj without exposing the
`probe_radius` argument, so attempting to call `get_sasa(..., probe_radius=1.4)` immediately
raises `NotImplementedMethodError`. Without that knob we cannot reproduce Pocketeer’s SASA
thresholding, and the computed surface areas are not aligned with the hard-coded defaults in
`pocketeer`.

**Reproduce:** run `msm.physchem.get_sasa(receptor, probe_radius=1.4)` against any structure;
the call is rejected before anything is computed because the engine parameter list does not
let the caller override the water probe.

**Current workaround:** we now assemble a Biotite `AtomArray` (copied from `build_heavy_receptor_view`,
with coordinates converted to Å and the usual annotations) and invoke `biotite.structure.sasa`
with a configurable `probe_radius`. The computed tuple is converted back to nm² and fed into
TopoMT’s pipeline. This is sufficient to keep parity with the upstream Pocketeer results, but it
requires duplicating Biotite-specific wiring in TopoMT instead of relying on a shared helper.

**Next steps:** extend `molsysmt.physchem.get_sasa` with an optional `probe_radius` argument, so
clients can tune polar and apolar probes without resorting to custom Biotite calls. When that
builder exists we can drop the local Biotite path from TopoMT and emit a cataloged warning if
its required dependency is missing. Consider also adding a MolSysMT helper that exports the
data necessary to construct a Biotite `AtomArray` so that other projects can avoid reimplementing
the same translation.
