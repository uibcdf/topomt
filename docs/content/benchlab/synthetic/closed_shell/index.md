# Sampled closed shell

Does a wall of discrete atomic balls really enclose a probe, and how does that
answer change with probe size? This unit retains the same **72 balls**, radii
**1.7 Å**, fixed-seed coordinates near a **6 Å** sphere and no periodic boundary.
The construction name is not an independent closure certificate.

| Stage | What it explains | Current status |
| --- | --- | --- |
| [System and independent references](system.ipynb) | Input geometry, an all-atom escape ray, a covered-wall certificate and a full-hull exclusion bound. | Executed in its own fresh kernel, without importing DFND. |
| [DFND experiments](dfnd.ipynb) | Spatially selected raw supports, three justified controls, the original sweep, reporting policy and volume definitions. | Executed in another fresh kernel; declared controls pass. |
| [Historical combined study](historical.ipynb) | Earlier reference, native and original-provider observations. | Preserved byte-for-byte, including its earlier execution code and dates. |

```{toctree}
:maxdepth: 1

system
dfnd
Public Topography receiving <topography>
Stronger enclosure reference at 0.2 Å <closure_at_0p2>
Historical combined record <historical>
```

## What the controls establish

| Probe | Independent evidence | Current native observation |
| --- | --- | --- |
| 0.05 Å | A straight ray from the origin has minimum all-atom clearance 0.095285 Å and reaches the exterior. | The central component has exterior links; DFND labels it `channel`, with 128 resident cells and 10 exterior-link clusters. |
| 1.4 Å | Every hull triangle is covered by probe-expanded balls, while the origin remains free and strictly inside. | A central `void` with 33 resident cells and no exterior link. |
| 5.0 Å | A convex-combination bound proves the whole finite hull covered by probe-expanded balls. | No resident wet component in the finite hull. |

The ray is an independent continuous access witness. It does not qualify all
paths in DFND's graph. The 1.4 Å wall certificate proves at least one bounded
free probe-center region containing the origin; it does not prescribe the exact
global cavity count. Ten native exterior-link clusters do not by themselves
establish ten physical mouths.

The older 0.2 Å control remains visible. Its original conservative wall-coverage
margin is negative and proves neither access nor closure. A
[stronger independent subdivision cover](closure_at_0p2.md) now certifies the
enclosed free origin at that probe, consistent with the native/public `Void`.
The earlier notebooks retain their originally inconclusive sufficient bounds.
Neither certificate establishes an exact physical transition radius.

## Inputs, evidence and reproducibility

Both notebooks read the unchanged
{download}`quantity-aware input <artifacts/closed_shell_v1/input.json>`.
The 0.05 Å query is an explicitly declared reference extension on those same
coordinates; the old 0.2/1.4/5 Å query records remain unchanged. The
{download}`protocol <artifacts/native_study_v1/protocol.json>` and
{download}`independent reference <artifacts/native_study_v1/system_reference.json>`
were frozen before fresh native observation. DFND reads that committed reference,
without requiring another live notebook kernel.

The new {download}`native report <artifacts/native_study_v1/dfnd_observations.json>`
retains actual source/software identities, dimensional values, origin-containing
cell IDs, raw and reported counts, the 49-point sweep and the reporting control.
Reruns display new observations without overwriting the frozen records. The
{download}`execution receipt <artifacts/native_study_v1/execution_receipt.json>`
records the qualified source scope and resource measurements.

Standalone figures: {download}`input geometry <artifacts/native_study_v1/system_geometry.png>`,
{download}`independent certificates <artifacts/native_study_v1/system_certificates.png>`,
{download}`native probe controls <artifacts/native_study_v1/dfnd_probes.png>` and
{download}`native sweep <artifacts/native_study_v1/dfnd_sweep.png>`.

## Interpretation and continuation

The input is a sampled atomic wall, rather than a continuum sphere with an
exact inner radius. Bare free space, free probe-center space and the finite
hull have different volume definitions. DFND's central solvent estimate remains
numerically unqualified under #75; it is not accepted by matching an unrelated
volume or another detector.

The historical notebook retains its original fpocket/Pocketeer/AlphaSpace2/
pyCASTA and CASTp records. This split neither re-executes those providers nor
polls/submits a server job. A new comparison stage can be prepared separately,
with its own atomic-model audit. Earlier failure, empty and pending outcomes
keep their original scope.

The [opening variant](../shell_with_opening/index.md) derives from this same frozen wall,
with atom correspondence and an independent 1.4 Å access witness.
Regenerating jitter after deleting atoms would change more than the opening.
The full synthetic phase, independent panel #76, volume precision and later
protein studies remain separate work.
