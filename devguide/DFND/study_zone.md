# Molecular topography study and benchmark area

Date: 2026-11-07. The user selected a growing collection of named system studies
for DFND development and original-method comparison, with synthetic cases before
new molecular benchmarks. Publication may be embedded in TopoMT documentation
or hosted as a separate site. The organization below is a development design,
not a delivered independent deployment or scientific qualification.

## Existing foundation and identity

Maintain `docs/content/benchlab/` as the dedicated public laboratory section.
Its three synthetic units retain frozen inputs, independent references, plots
and native observations. The first two also preserve historical original-provider
evidence. MyST-NB/Sphinx renders stored outputs without running calculations.
Keep the [laboratory checkpoint](notebook_laboratory_checkpoint.md) as the active
case-by-case continuation record.

### Canonical collection layout

```text
docs/content/benchlab/
  index.md
  synthetic/
    index.md
    regular_tetrahedron/
      index.md
      system.ipynb
      dfnd.ipynb
      comparisons.ipynb
      atomic_models.md
      historical.ipynb
      artifacts/regular_tetrahedron_v1/...
      artifacts/native_study_v1/...
      artifacts/comparisons_v1/...
      artifacts/radius_audit_v1/...
    closed_shell/
      index.md
      system.ipynb
      dfnd.ipynb
      historical.ipynb
      artifacts/closed_shell_v1/...
      artifacts/native_study_v1/...
    shell_with_opening/
      index.md
      system.ipynb
      dfnd.ipynb
      artifacts/shell_with_opening_v1/...
  molecular/
    index.md
```

Synthetic systems and Molecular systems are separate collections sharing the
same study-unit contract below. Molecular systems is initially a planned index,
not an assertion that historical protein tests are qualified laboratory cases.
Use the same descriptive case-directory pattern for future molecular studies.
The public reading order is navigation, not a numbered case identity. Indexes
summarize scientific questions, references, review state and available comparisons.

The 2026-11-07 move from Showcase is tracked in
[#133](https://github.com/uibcdf/topomt/issues/133). Existing notebooks retain
scientific code and outputs; versioned artifact bytes are unchanged. Only their
location and navigation prose change. Earlier documentation addresses keep
relocation pages, with no duplicate source notebook or evidence collection.
New cases and input versions enter the collection only after their declared
reference assumptions and evidence have been reviewed.

The maintainer selected a short case overview plus separate `system.ipynb`,
`dfnd.ipynb` and `comparisons.ipynb` stages. The first two stages are delivered
for the tetrahedron under #134; #141 adds the independent comparison notebook,
an atomic-model audit and original local evidence. Its ordinary execution only
verifies/reconstructs stored outputs. Each runs from a clean kernel using frozen inputs and, for DFND, the
committed independent reference rather than another notebook's live variables.
The earlier combined tetrahedron notebook is retained unchanged as historical
evidence. Under #144, the closed shell also has independent system/native
notebooks, with its unchanged combined notebook retained as history. The new
reference adds a separately declared 0.05 Å all-atom escape ray and 5 Å
full-hull exclusion bound on the same frozen input; the old 0.2 Å reference
remains explicitly inconclusive. New stages read committed records in clean
kernels without original-provider execution or server requests.

Under #145, `shell_with_opening` is an exact subset of that frozen wall. It
retains parent atom IDs and introduces no fresh coordinate generation. Its
protocol and independent reference are committed before child native execution.
Separate system/native notebooks inspect the matched 1.4 Å parent/child access
control, larger-probe enclosure/exclusion and mapped exterior contacts. A
comparison stage remains planned; no original provider is run for this unit.

Use descriptive names as permanent case identities, without ordinal codes.
Grouping and study order are editable navigation. Each frozen input retains its
version and checksum; materially changed inputs receive a new version or a
separate variant. The two adopted laboratory controls have different inputs from
similarly named catalog PDBs. The 73-entry catalog also includes a disclosed
historical PDB alias, not 73 independently established geometries or references.

## One system, one study unit

| Part | Required content |
| --- | --- |
| Question | What this case isolates, why it matters and which observations could refute the expected answer. |
| Input | Downloadable coordinates, radii, units, generator/parameters, seed, precision, source identity and version/hash. Record every method-specific export. |
| Independent reference | Analytic value, certificate, controlled witness or justified bounds, with assumptions and tolerances set before native results. Unresolved expectations stay explicit. |
| DFND | Local capacities and witnesses, query policies, raw connectivity/supports, exterior links, dry structures, metrics and public projection. Report uncertainties and maturity. |
| Original comparators | Method/version/source or executable identity, settings, actual received input, original outputs and explicit execution status for each selected comparator. |
| Comparison | Aligned views and metrics for the same declared observable; show incompatible definitions separately. Include seeds, transforms and parameter variants needed to explain behavior. |
| Interpretation | Distinguish input-domain failure, model difference, numerical error, policy/segmentation behavior and unresolved reference. Retain favorable and unfavorable results for every method. |
| Development outcome | Bounded change motivated by evidence, before/after observations, adopted regression guards and remaining questions. Preserve earlier observations. |

A named unit may contain several input versions and variants; it must not merge
their results as if the coordinates/radii were unchanged. The reference model,
DFND carrier-cell regions and a peer's reported region can be different objects.

## Fair and informative comparisons

Original software is the comparator. A TopoMT reproduction remains a separately
identified implementation. Select methods by the question: pocket detection,
empty-volume measurement, channel paths, surface relief and interfaces have
different domains. A ranking score, alpha-space volume, bare-empty volume and
probe-centre accessible region are not interchangeable quantities.

Check parser acceptance, atom selection, radii, coordinate precision, units,
probe controls and required origins before attributing a discrepancy to an
algorithm. Share identical inputs where the interfaces permit it; disclose every
adaptation otherwise. Record default settings and any declared sensitivity study
separately, without tuning only one method to the case.

Retain distinct completed-empty, completed-nonempty, unsupported, unavailable,
failed and pending outcomes. An input rejection has no inferred pocket count.
The absence of an optional comparison does not invalidate an independent native
reference, but it cannot support a comparative-performance conclusion either.

Measure geometry/topology error, support and volume only against references with
matching meaning. A physical-path claim needs a continuous all-atom witness;
neither DFND's graph nor a plausible image alone supplies one. Timing/memory
comparisons need matched scope, hardware, versions, accuracy and cold/warm state.

## Development collection and frozen benchmark

The open laboratory guides implementation. It is not automatically an unbiased
evaluation set after the method has been repeatedly tuned on it. Before a broad
benchmark claim, freeze an evaluation panel and metrics, reserve additional
seeds/parameter regimes or families from tuning, and report the complete panel.
Use synthetic controls to isolate mechanisms, then molecular systems to test
biological relevance and generalization. Synthetic success alone cannot qualify
binding-site ranking, chemistry, conformational effects or biological transport.

Read the original method and its relevant documentation before interpreting a
comparison. A short case-linked literature note can grow with the collection;
an exhaustive survey is not a prerequisite to the next controlled experiment.
Published limitations are hypotheses to reproduce at identified versions, not
automatic defects of every current implementation.

Examples reviewed for this design:

- [CAVER 3.0, 2012](https://doi.org/10.1371/journal.pcbi.1002708), sections 1.1–1.2,
  describes its equal-ball representation of unequal-radius atoms and possible
  passage-radius overestimation near a cutoff. This motivates mixed-radius and
  near-threshold controls; it does not establish an error in DFND or a current
  executable result without measurement.
- [Official fpocket documentation](https://github.com/Discngine/fpocket/blob/master/doc/GETTINGSTARTED.md),
  dpocket advanced, discusses approximate volume estimates and sampling settings.
  This motivates separating volume definitions, accuracy and computational cost.
  The mutable document was read on 2026-11-07; it is not an exact executable pin.
- [CASTp 3.0, 2018](https://pmc.ncbi.nlm.nih.gov/articles/PMC6031066/), biological
  assemblies, illustrates a large biologically artificial pocket from the
  asymmetric unit of 2iwv. This motivates checking system/participant definition;
  an assembly-choice effect is not by itself an algorithmic geometry defect.

The [MOLE comparison](mole_comparison_2026_11_07.md) retains its own exact-source
and prior-art conclusions. The reading above is a bounded starting point, not a
systematic review of all third-party failure modes.

## Publication and next increment

Keep source inputs, numerical evidence and interpretation separate from the
presentation layer. Reuse the same case sources and relative resources for an
embedded documentation collection and a future standalone build, avoiding two
independently edited copies. Static publication reads reviewed outputs and does
not execute engines, contact servers or overwrite frozen reports.

The case index should expose scientific questions, geometry families, available
comparators and study/reference status. Registering a catalog input does not
create a completed benchmark page. Publish studied units progressively, and
retain the unresolved outcomes alongside successful ones.

The staged structure is delivered for the tetrahedron, closed shell and exact
opening variant, preserving earlier evidence. Continue with a tube and the
agreed synthetic sequence. This organization adds no separate hosting deployment
or closure of #75/#76/#16; each new scientific run retains its own protocol.

## Tube continuation and notebook reading — 2026-11-10

The maintainer selects `straight_tube_narrow_dense` after the finite three-case checkpoint.
Its #178 system/native unit has independent path/wall/exclusion references and
retained initial observations. Stay on this input for physical budget #180,
all-atom/public qualification #181 and wider paths #76 before another geometry.
The maintainer subsequently selected `straight_tube_wide_sparse` as its explicit
companion under #183. Its two smaller probes have independently certified end
patches and a clear axis; native 1.4 Å Channel contacts resolve, while 2.5 Å
boundary numerics remain #184. Both tubes' questions remain active; the wider
positive result does not qualify the narrow input.
The initial study is not complete scientific qualification or a provider benchmark.

Present explanations, reference/result tables and figures as the primary web
reading route. Tag long code inputs `hide-input` so MyST-NB offers an expandable
source view while the downloaded notebook keeps executable code. Generated
tables use escaped semantic HTML (for example IPython.display.HTML): rich
text/markdown pipe tables currently render as literal text in this Sphinx route.
Ordinary source Markdown tables retain their existing authoring convention.
Inspect actual notebook and browser outputs, including a mobile viewport;
successful execution and a warning-free build do not prove readable output.
Preserve earlier protocols/observations and refresh the current cell protocol,
fresh-kernel receipts and complete download manifest for a reader change.
