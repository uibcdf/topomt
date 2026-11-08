# Shell with an opening

What changes when we remove six atoms from the [sampled closed shell](../closed_shell/index.md)?
This unit keeps the remaining **66 atomic balls**, their **1.7 Å** radii and
their parent atom identities unchanged. A strict **35° cap around +Y** defines
the deletion. The geometry is nonperiodic and no coordinates are regenerated.

| Stage | Question | Status |
| --- | --- | --- |
| [System and independent references](system.ipynb) | Does the deletion permit a continuous escape path, and which larger probes remain enclosed or excluded? | Executed in a fresh kernel without importing DFND; reference committed before native observation. |
| [DFND experiments](dfnd.ipynb) | How do raw supports, exterior contacts and public reporting change? | Executed in another fresh kernel; declared controls pass. |
| Original-method comparisons | How do eligible original tools describe the same declared atomic model? | Planned separately; no provider or server execution in these notebooks. |

```{toctree}
:maxdepth: 1

system
dfnd
```

## Independent controls and native observations

| Input / probe | Independent evidence | Current DFND observation |
| --- | --- | --- |
| Closed parent / 1.4 Å | Its expanded vertex balls cover every hull triangle; the origin remains free and strictly inside. | Central `void`, 33 resident cells, no exterior link. |
| Opened child / 1.4 Å | The +Y ray has minimum all-atom clearance **1.819726 Å**, above the probe radius. A conservative cap bound also exceeds 1.4 Å. | Central `pocket`, 35 resident cells, one exterior-link cluster. |
| Opened child / 3 Å | The larger expanded balls cover the child hull boundary while the origin remains free. | Central `void`, nine resident cells, no exterior link. |
| Opened child / 5 Å | An enclosing-ball/convex-combination bound covers the whole finite hull with expanded atomic balls. | No resident wet component in the finite hull. |

Deleting the cap isolates a change in access at the **same 1.4 Å probe**.
The references establish origin access/enclosure and finite-hull exclusion,
rather than an exact global cavity count or a physical mouth count. A failed
sufficient bound leaves the corresponding question unresolved.

## Contact location and interpretation

At 1.4 Å, every unchanged parent hull triangle remains covered by its retained
vertex balls. Any genuine free exterior contact on the child hull must therefore
lie on a newly exposed triangle. DFND's single contact cluster uses parent atom
IDs **[6, 7, 8]** (zero-based), one of those new triangles. Its native gate
radius is **2.010131 Å**; its geometric triangle area is **16.148008 Å²**.
That area is not a measured free aperture area.

This agrees with the independent contact-location constraint. One deleted cap,
one continuous ray and one native contact cluster still do not prove exactly
one physical mouth. Likewise, the 49-point sweep's native change between 2.0
and 2.1 Å is an observation, not an independently established exact physical
transition. Unresolved intervals remain visible in the report.

The constructor's public `atom_indices` mapping keeps the original parent atom
IDs in raw output; local array offsets remain separate. Parent and child
tetrahedron IDs cannot be equated after retriangulation. At `min_size=36`, the
reported child pocket disappears while its raw support and physical result key
remain unchanged. This reporting operation does not close the opening.

## Downloadable input and evidence

The {download}`quantity-aware input <artifacts/shell_with_opening_v1/input.json>`
contains full-precision coordinates, explicit radii, the cap rule and atom mapping.
The {download}`PDB exchange subset <artifacts/shell_with_opening_v1/input.pdb>`
retains the parent rows and serial/residue numbers 7–72. Its rounded coordinates
and dummy atom names do not encode the full JSON ball model or biological chemistry.

The {download}`protocol <artifacts/shell_with_opening_v1/protocol.json>` was
committed at `b6fe6e2`, and the
{download}`independent reference <artifacts/shell_with_opening_v1/system_reference.json>`
at `2ca133d`, before the first child DFND execution. The
{download}`native observations <artifacts/shell_with_opening_v1/dfnd_observations.json>`
retain source/software identities, dimensional measurements, raw/public counts,
mapped contacts, the sweep and reporting control. The
{download}`execution receipt <artifacts/shell_with_opening_v1/execution_receipt.json>`
records notebook/artifact hashes and bounded resource measurements.

Standalone figures: {download}`matched input geometry <artifacts/shell_with_opening_v1/system_geometry.png>`,
{download}`independent probe bounds <artifacts/shell_with_opening_v1/system_certificates.png>`,
{download}`native supports and contacts <artifacts/shell_with_opening_v1/dfnd_contacts.png>`
and {download}`native sweep <artifacts/shell_with_opening_v1/dfnd_sweep.png>`.
Ordinary notebook reruns display recomputed records without overwriting artifacts.
All parent scientific artifacts and notebook bytes remain unchanged.

## What follows

No DFND kernel change was needed for these controls. Solvent-volume precision,
general continuous validity of graph paths, exact physical mouth counts, the
full synthetic inventory and molecular characterization retain their own gates.
The next geometric question is a tube with independently controlled passage
and bottlenecks. Original-method comparisons can be added separately, after
reviewing each tool's input model and the observable being compared.
