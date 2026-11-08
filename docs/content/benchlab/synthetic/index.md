# Synthetic systems

This collection is the synthetic section of [Topography BenchLab](../index.md).
It provides a public, reproducible laboratory for learning how DFND
describes molecular topography. Each study unit combines an explained geometric
input, independent reference checks, visual observations and eligible
comparisons with original third-party tools. It is the seed of a future benchmark
annex to the TopoMT documentation. It also guides development of DFND through
progressively characterized synthetic systems before molecular benchmarks.

Each system is a named study unit, with versioned inputs and observations.
Scientific groups and reading order can evolve as new systems are added.
The publication target is a collection that can live inside the documentation
or become a standalone study site using the same reviewed case sources.

The collection is under development. Two controls are available: a regular
tetrahedron and a sampled shell with an independently certified wall. They do not
establish general biological accuracy or numerical volume precision. Development
resumed on 2026-11-07, guided by characterization of each synthetic case and its
necessary variants. Protein studies follow completion of that synthetic phase.

```{toctree}
:maxdepth: 1

regular_tetrahedron/index
closed_shell/index
```

## What each study explains

| Case | Scientific question | Reference and study status |
| --- | --- | --- |
| [Regular tetrahedron](regular_tetrahedron/index.md) | How do residence and face transit differ as the probe grows? | Separate executed system, DFND and original-comparison notebooks; atomic-model audit and distinct failure states. |
| [Sampled closed shell](closed_shell/index.ipynb) | Does a certified atomic-ball wall enclose a free central probe region? | Independent wall-coverage certificate and reviewed central-region observations; global cavity count and exact volume remain outside that certificate. |

| Part | What the reader can inspect |
| --- | --- |
| System and question | Geometry, parameters, units, downloadable inputs and the phenomenon being isolated. |
| Independent reference | What is known, how it is justified and which conclusions remain unresolved. |
| DFND observations | Local clearances, regions, access, boundaries, metrics and their interpretation. |
| Original-method comparisons | Versions, settings, submitted inputs, original results and execution status. |
| Comparison and conclusions | Comparable observables, explained differences, limitations and development outcomes. |

Comparison helps identify concrete improvements. Distinguish a geometric error
from an input rejection, a different modeled object or a reporting convention.
Optional methods have different domains; failed or unsupported runs do not mean
zero pockets. The development collection and a later frozen evaluation panel
have different purposes, and synthetic results alone do not establish biological
accuracy.

## Run a case

Use a supported TopoMT installation and the development environment in
`devtools/conda-envs/development_env.yaml`. Notebook tools include JupyterLab,
IPyKernel, NBFormat, NBClient and Matplotlib. These are development/documentation
dependencies, rather than new TopoMT runtime requirements.

Open a notebook from its case directory and execute all cells in order. To execute
the first case from the repository root:

```bash
python -m jupyter nbconvert --to notebook --execute \
    docs/content/benchlab/synthetic/regular_tetrahedron/system.ipynb \
    --output system.executed \
    --output-dir /tmp/topomt-notebook-rerun
```

The tetrahedron's `system.ipynb`, `dfnd.ipynb` and `comparisons.ipynb` run
independently and do not execute original providers. The comparison stage
verifies retained original bundles and reconstructs accepted results without
external engines or requests; see its artifact guide to repeat original execution.
The closed-shell notebook and the tetrahedron's historical combined notebook
retain their earlier optional-provider code. Install original providers
separately if deliberately rerunning those historical comparisons:

```bash
conda install -c conda-forge fpocket
python -m pip install pocketeer==0.4.0 alphaspace2==0.1.2 pycasta==1.0.8
```

The versions above identify the reviewed runs, rather than promise the latest
upstream release. Follow the requirements of
[Pocketeer](https://github.com/cch1999/pocketeer),
[AlphaSpace2](https://github.com/RedesignScience/AlphaSpace2) and
[pyCASTA](https://github.com/giorgioluciano/pycasta). These remain optional.
Set `RUN_PROVIDERS=False` to run native references alone. The tetrahedron's
separate HETATM fpocket check can be disabled with `RUN_FPOCKET=False`.

The historical combined notebooks compare original engines on a synthetic `ATOM` export;
the canonical dummy `HETATM` encoding remains downloadable. Only the record type
changes. Completed provider runs include original evidence bundles. Failures
retain their causes and no invented pocket counts or geometry. CASTp server
evidence is a recorded original attempt; ordinary notebook reruns do not submit
another web job.

The local provider comparisons are recorded. CASTp 3.0 failed during upload;
CASTpFold accepted both aligned HETATM inputs, with results still pending at the
recorded poll. Those attempts do not yet provide CASTp pocket measurements.

TopoMT requires DepDigest >=0.12.0. An older editable sibling checkout can take
precedence over an installed package; verify the version imported by the notebook
kernel. A missing executable is recorded as unavailable. Provider execution
failure remains a failure, even when the native reference checks pass.

These notebooks also use PyUnitWizard's provisional `QuantityRecord` codec
(`qrec/0.3`). Until a published release includes it, use the tested source
revision `23554a7aca31cba144ef248b9771d4668815dd1c` recorded in
`devtools/requirements/controlled_suite_dependencies.txt`. The older controlled
revision lacked that API and failed test collection; the source pin is updated
with these notebook tests.

Each notebook reads versioned input artifacts and displays a new observation
report without overwriting the recorded reference files. Sphinx renders reviewed,
executed outputs; it does not launch optional providers during a documentation
build. Execution and scientific review are separate checks.

## Study sequence

1. **Regular tetrahedron:** residence versus face transit and probe-dependent
   connectivity; independent circumradius formulas.
2. **Sampled closed shell:** atomic-ball wall sealing and volume definitions.
3. **Shell with an opening:** exterior connectivity and mouth interpretation.
4. **Tube:** passage, bottlenecks and the limits of a graph skeleton.
5. **Two chambers with a neck:** residence regions, communication and separation.

The first two controls are available; the tetrahedron now separates its system
reference and native analysis into independently executable notebooks. Later cases enter the collection
after their input assumptions and independent expectations have been reviewed.
