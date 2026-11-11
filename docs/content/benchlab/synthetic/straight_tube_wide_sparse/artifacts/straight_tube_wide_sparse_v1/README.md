# Wide straight-tube evidence and replay

Read [the system notebook](../../system.ipynb), then
[DFND observations](../../dfnd.ipynb). They execute independently from the case
directory. The complete ZIP linked from [the case](../../index.md) includes the
same reference/helper tree and a per-file SHA-256 manifest.

## Fixed scientific identity

- `input.json`: full-precision 77-ball, quantity-aware model, SHA-256
  `77fc6f703dac08084e75398202169c9f8e05fc07e75eec4faf400932a3f2a855`.
- `input.pdb`: original rounded topology, SHA-256
  `73fc166e0c0bd3e06da852774aaeca737c9adf59aff7627273f46f8bb4e17eb1`.
- Argon radius 1.88 Å, source atom IDs 0–76, isolated/nonperiodic conditions.
  Generator `cylinder_tube(20, 6, 3.5, jitter=0.1, seed=0)` gives seven rings
  with eleven atoms each. Both radius and sampling differ from the narrow tube.
- `protocol.json`: probes 1.4, 2.5 and 5 Å, finite atomic-center hull, zero
  physical tolerances, with_connectors/flag_only/dryface and epsilon/boundary
  margin 1e-6 Å; frozen at source `1cd0f18` before reference/native execution.

## Reference, execution and reader chronology

1. `reference_certificate.json`, `reference_verification.json` and
   `reference_receipt.json` retain the independently checked complete axis,
   outward tails and sufficient finite-hull cover. The axis minimum is
   3.9065969808290815 Å. The 5 Å whole-hull distance bound is
   6.594243009499208 Å, versus expanded radius 6.88 Å.
2. `boundary_1.4A_*` and `boundary_2.5A_*` retain separate protocols,
   certificates, verification and measured receipts. Both prove two free end
   patches, with all 68 lateral faces covered. The complete hull has 86 faces.
   Generation/replay uses only independent checkers, not TopoMT/DFND or a
   comparator. The receipts retain that import exclusion.
3. `native_protocol.json` was committed at `fdb253c` before actual native/public
   receiving. `native_attempt_metadata_encoding.json` retains the first
   execution from that source. Its numerical observations are usable history;
   bibliographic strings were misencoded by the study serializer, so it is
   **not accepted as portable saved-attribution evidence** (#185).
4. `native_capture_protocol_v2.json` preserves the failed attempt hash and
   requires unchanged JSON attribution metadata. The development encoder fix
   at `3ad9515` preserves strings before quantity detection. The subsequent
   `native_observations.json` is a new original execution from that committed
   scientific/helper source, with a preserved pre-existing human version-file
   edit identified by hash. No scientific DFND operator changed. The new capture
   checks original-result and completed-operation attribution round trips.
5. `reader_protocol.json` freezes notebook code/Markdown, the accepted original
   observations hash and clean committed source **3ad9515019e722c0ccf4ade7a3024de4166e217e**
   before fresh-kernel execution. `system_receipt.json` and `dfnd_receipt.json`
   record those separate executions. Reviewed outputs are rendered by Sphinx;
   a documentation build does not execute the notebooks or providers.

The original JSON retains actual producer versions and detached Ackredit records.
The clean-source reader has its own producer version; it does not relabel earlier
results. Native support JSON is development evidence, not a versioned public
`Topography` interchange format. Reading/rendering attribution earns no new
calculation credit. No original provider or server is executed here.

## Physical results and their limits

At 1.4 Å the native global count is two. The Channel's two attachments resolve;
ten other attempted component/patch associations remain unknown. At 2.5 Å the
physical result is unresolved because critical-section ordering lies within the
numerical margin (#184). At 5 Å arrangement work exhausts its budget (#180),
while a local OpenConcavity/Mouth survives the independently empty all-atom
finite carrier (#181, needs_review). Local capacities are not all-atom
certificates; the latter observation alone does not diagnose a solver error.

The actual-public physical targets first produced one pass and two failures;
the unresolved 2.5/5 Å targets remain strict expected failures with those owners.
Selected native interior paths are checked against all atoms and every segment;
the native validation flag remains false. Independent axis tails and physical
attachment rays have separate evidence. No optimal bottleneck, exact volume,
aperture area, all three-dimensional region count or biological claim follows.

## Resource and replay scope

References, native receiving and notebook executions are sequential on one CPU
with one numerical thread, a 6 GiB address-space ceiling and 120 CPU seconds per
runner. Preflight found over 50 GiB available of 60.5 GiB RAM, zero memory-pressure
averages and no active sampled swap traffic; no scheduler allocation was usable.
Availability was not treated as a reservation. Each receipt retains measured
elapsed time/RSS; input preparation, reference generation, native execution and
reading are different scopes. Original reference generation took about 0.4 s
for passage and 2–3 s per boundary certificate; these are single-case observations,
not a comparative performance claim.

Acquire the pinned source/environment separately, confirm the printed TopoMT
module origin, then Run All in a fresh kernel for each notebook. Code inputs can
be expanded on the website and remain complete in the download. Neither Run All
nor ZIP verification rewrites retained files. Prior three-case/narrow notebooks,
scientific artifacts and published ZIPs remain unchanged. Source receiving and
a deployed website do not qualify an installed release or Python/platform matrix.
