# Provider output viewer checkpoint

Updated: 2026-09-30. Owner: [#66](https://github.com/uibcdf/topomt/issues/66).
Current priority: **original-provider results in the TopoMT-owned MolSysViewer addon**.

Workstream: **paused at the user's request after initial provider/viewer delivery**.
Do not start the resume sequence without a new instruction to continue.

## Decision and scope

The user explicitly resumed viewer addon adoption after #65. Concrete DockingMT
and PharmacophoreMT adoption remains deferred. DFND and the full public
Topography runtime gates #60–#63 retain their own acceptance criteria.
This checkpoint supersedes earlier wording that postpones viewer adoption;
the [provider output checkpoint](provider_pocket_output_checkpoint.md) still
defines the scientific result contract. The older
[addon scaffold checkpoint](molsysviewer_topomt_checkpoint.md) is historical.

## Implemented boundary

`attach_provider_output(view, output)` retains the original object under
`view.addons.topomt.provider_outputs[output.run.run_id]` and makes that run active
for the panels. It does not replace `view.topography` or assign canonical DFND
feature labels. Different runs/providers coexist. Attaching a Topography makes
the canonical source active without discarding original provider evidence.

`show_provider_pockets` accepts all pockets or explicit original `pocket_ids`.
`representation='auto'` uses the first nonempty available `alpha_spheres`,
`beta_sites`, `member_atoms` or `lining_atoms`. Explicit requests are supported.
Present empty geometry and unavailable geometry remain distinct in RenderResult;
absence produces an explicit warning. Reported radii remain original radii;
point-only evidence uses a declared display-marker radius. The final boundary
uses existing MolSysViewer sphere primitives and explicit length quantities.
No blob surface, closed region, occupied volume, receptor alignment or affinity
is inferred. The molecular scene, if loaded, must use the source coordinate frame.

`clear_provider_pockets` removes one run's display group, preserving evidence and
unrelated shapes. Direct replacement uses public `shapes.get`/`shapes.clear`
and object identity, rather than the private scene-registry key format.
Provider/run/source identities and geometry definitions remain in RenderResult
details and namespaced tags.

The pocket and summary panels list original reported pocket rows, show all or
one pocket and clear the active run. CASTp mouth aggregates remain auxiliary.
Provider identity is displayed; DFND controls are disabled for provider state.
An addon-owned `topomt.state` query refreshes after frontend mounting. Mounted
widgets are tracked weakly and refreshed after attachment changes.

## Evidence and remaining gates

`tests/test_provider_output_viewer.py` guards real fpocket/CASTp evidence,
units, identities, independent overlays, selections, empty/missing geometry,
repeated rendering, tag reuse, partial failure cleanup and panel state/actions.
It also exercises original fpocket CLI and installed original Python engines.
The first red run reproduced missing entry points and duplicate tags. Legacy
addon tests now capture transport calls in a test-owned list while preserving
real managers/send behavior; they no longer inspect `_message_history`.
Final scoped and exact hosted evidence belongs in #66. These checks do not
certify browser rendering or a green full scientific matrix.

Final installed-original-engine and consumer checks passed 33 tests, including
the loaded-receptor/CLI path, with six upstream AlphaSpace2 undefined-ratio
warnings preserved. Complete Ruff lint/format and six-file scoped mypy passed.
The changed guides render with warnings treated as errors; public HTML retains
the 11 pre-existing diagnostics in #64. The final shared guard, provider-output,
complete addon and import selector passed **229 tests with six optional-engine
skips** and two legacy H5MSM warnings. Resolution is retained in
[the archived report](archive/provider_output_viewer_adoption.md); exact
publication and hosted evidence are recorded in #66.

The private pilot still leaves receptor/model choice to scientists. Public
bundled fixtures establish infrastructure evidence without selecting or
publishing a confidential asset or claiming scientific pilot success.

## Resume sequence

1. Exercise the documented notebook flow with the scientifically selected
   receptor/frame, inspecting the scene and original geometry together.
2. Continue field/route fidelity under #19, saved-library-output reconstruction
   and live CASTp validation. Its exhaustive denominator stays 20/100; this
   viewer slice does not advance it.
3. Assess richer provider/run controls against actual needs. Keep concrete
   DockingMT/PharmacophoreMT adoption deferred.
4. Use retained results for future DFND comparisons and canonical admission.
