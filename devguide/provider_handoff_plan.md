# Reproducible original-provider handoff plan

Accepted direction: 2026-11-06, under the user's active long-term development goal.
Owner for the first consumer pilots: [#101](https://github.com/uibcdf/topomt/issues/101).
Provider fidelity remains [#19](https://github.com/uibcdf/topomt/issues/19);
component qualification and full-suite backlog remain #16/#58. This plan is
outside the issue-report queues and does not change their lifecycle or scope.

## Outcome and ownership

Enable a reproducible path from a receptor prepared in MolSysMT, through an
explicit original pocket provider, to attributed pocket records and declared
PharmacophoreMT hypotheses. Integrate all currently registered external methods:
fpocket, Pocketeer, AlphaSpace2, pyCASTA and CASTp/CASTpFold. Native reproductions
retain their independent scientific contracts and are not prerequisites for
original-provider handoff.

MolSysMT owns loading, representation, selections, atom correspondence,
coordinates, chemistry and preparation. TopoMT owns external topography adapters,
their original evidence, source index maps and pocket representations.
PharmacophoreMT owns recognition, feature complementation, projections, matching
tolerances, essentiality, weights and native pharmacophore persistence. ArgDigest,
DepDigest, SMonitor and PyUnitWizard retain their registered responsibilities.
Missing provider capabilities are reported to their owner instead of copied
into TopoMT. Use public tools; respect the sibling contribution route before
changing another component.

## Evidence required for completion

1. Each supported original route has appropriate ArgDigest value/name contracts,
   optional dependency guards and explicit operational errors. Missing engines
   never select a different method silently.
2. Real original execution and persisted recovery agree on pocket order/IDs,
   membership roles, source indices, available geometry, original fields and
   attributed units/definitions. Keep source selection, frame, chemical state,
   versions/options and original bytes; distinguish unknown, empty and invalid.
3. Saved results remain independent of temporary files and later source changes.
   Recovery verifies compatible source evidence and works without the original
   engine. Physical quantities agree under alternate application unit policies.
4. Prepared real receptors pass source persistence, original detection, saved
   recovery and public PharmacophoreMT consumption. Explicit scientific choices
   stay in the consumer; preserve site-to-source context through model roundtrip.
   No affinity, binding-site relevance or exact closed region is inferred from
   provider rank, masks or alpha spheres.
5. Exact installed candidates and dependency origins are verified in clean
   environments. Retain actual wheels/digests, executed guards, skips and limits.
   Current support/matrix/full-suite obligations retain their owning records;
   source checks and old installed wheels cannot qualify changed candidates.

## Current sequence and gaps

| Provider | Current bounded evidence | Next required work |
| --- | --- | --- |
| fpocket | Original CLI/files, reference chemistry, prepared hydrophobic consumer and bounded installed receipts under `fpocket4/`; the current Pocketeer candidate repeats these controls. | Preserve regression coverage; broader fidelity and component gates retain their owners. |
| Pocketeer | Public 0.4.0 original, argument/state and saved-reader controls; prepared public PharmacophoreMT receiving under both unit policies. Exact producer `bb34e67` also passes 311 installed cases without skips and two independent prepared flows in a new prefix. | Preserve the qualified candidate and regression evidence; general fidelity and component gates remain separate. |
| AlphaSpace2 | Original argument/domain contracts at `3e86d1b`; 70 contract cases and eight original receptor/binder cases pass. The 396-case affected source selection preserves fpocket/Pocketeer controls; see its [overview](alphaspace2/overview.md). | Bind receptor/binder reference-state and source evidence; implement saved reconstruction, prepared consumer control and updated installed qualification. |
| pyCASTA | Existing original adapter/output and retained JSON/files; current receiving qualification pending. | Review provider contracts, saved reconstruction and prepared consumer control. |
| CASTp/CASTpFold | Existing server/files adapters and retained archive evidence. | Verify current route/context fidelity and qualify an explicit consumer profile. |

The [prepared consumer checkpoint](pocketeer/pharmacophore_handoff_checkpoint.md)
now also retains the exact installed-candidate receipt and its limits. Continue
with AlphaSpace2's reference-state/source contracts, saved reconstruction and
prepared receiving before qualifying its changed installed candidate. Its
argument handoff is now checked against the pinned original source profile.
Reuse the fpocket developer qualification recorder and PharmacophoreMT's public
tools when extending that pilot; do not introduce a second recognition or model
implementation. Keep the full goal active until the evidence above is complete.
