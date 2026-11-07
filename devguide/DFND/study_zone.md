# Molecular topography study and benchmark area

Date: 2026-11-07. The user selected a growing collection of named system studies
for DFND development and original-method comparison, with synthetic cases before
new molecular benchmarks. Publication may be embedded in TopoMT documentation
or hosted as a separate site. The organization below is a development design,
not a delivered independent deployment or scientific qualification.

## Existing foundation and identity

Extend `docs/content/showcase/dfnd/`: its two notebooks already combine frozen
inputs, independent references, plots, native observations and original-provider
evidence. MyST-NB/Sphinx renders stored outputs without running calculations.
Keep the [laboratory checkpoint](notebook_laboratory_checkpoint.md) as the active
case-by-case continuation record.

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

First apply this structure to the two delivered studies, preserving their
original evidence. Continue with the independently grounded shell-opening case,
then the agreed synthetic sequence. This design adds no new scientific run,
provider integration, hosting deployment or closure of #75/#76/#16.
