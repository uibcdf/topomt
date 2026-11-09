# Topography BenchLab

BenchLab is TopoMT's collection of reproducible system studies for developing,
understanding and comparing molecular-topography methods. Each named case asks
a scientific question, explains its reference, shows DFND observations and
records comparisons with original third-party software where appropriate.

[DFND: Theory and Method](../dfnd/index.md) explains the model and algorithm;
BenchLab retains the independently justified systems and their observations.

The [comparative-findings register](https://github.com/uibcdf/topomt/discussions/154)
links scoped advantages and limitations to these reproducible studies. Consult
each maintained card for its current conclusion, tested software profile and
corrections. Pending review and resolved history are shown separately: an old
notebook result does not automatically describe a current limitation.

The collection has two sections:

| Collection | What it investigates | Current scope |
| --- | --- | --- |
| [Synthetic systems](synthetic/index.md) | Controlled geometries that isolate residence, access, openings, constrictions, boundaries, surface relief and interfaces. | Regular tetrahedron, sampled closed shell and its exact opening variant; qualify further cases progressively. |
| [Molecular systems](molecular/index.md) | Real molecular structures and, later, ensembles or trajectories, with explicit preparation and biological context. | Planned. New molecular characterization follows the synthetic phase. |

```{toctree}
:maxdepth: 2

synthetic/index
molecular/index
```

## A study unit for each system

Case names are descriptive and stable. Reading order and thematic grouping can
change as the collection grows without renaming or numbering the systems.
Each case has its own directory, study notebooks and versioned input/evidence
artifacts. The working pattern separates the system/reference, native DFND
analysis and original-method comparisons as those stages are prepared. A short
case overview provides navigation and synthesis. Input versions and variants
retain their separate identities.

| Part | What the study should make clear |
| --- | --- |
| Question and system | What the case isolates; coordinates, radii, units, preparation and exact downloadable inputs. |
| Reference | Independently justified expectations, assumptions, tolerances and unresolved questions. |
| DFND observations | Raw geometry/connectivity, public results, plots, parameter regimes and interpretation. |
| Original-method comparisons | Actual inputs, versions, settings, outputs and execution status for eligible comparators. |
| Conclusions | What the evidence supports, where definitions differ, limitations and any resulting development work. |

Synthetic references and molecular annotations require different scientific
justification. Neither a plausible construction name nor agreement with another
method establishes ground truth. Distinguish geometric accuracy, biological
interpretation, provider equivalence and performance measurements.

Retain completed-empty, completed-nonempty, unsupported, unavailable, failed and
pending outcomes separately. A failed input or service request has no inferred
pocket count. Synthetic results alone do not establish binding-site accuracy or
biological transport.

The open collection guides development. A later evaluation panel and its metrics
must be frozen separately before broad benchmark claims. Documentation renders
reviewed notebook outputs without rerunning engines, contacting servers or
overwriting recorded evidence. The same case sources can support a future
standalone BenchLab site.
