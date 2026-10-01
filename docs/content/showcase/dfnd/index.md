# DFND laboratory

This collection starts a public, reproducible laboratory for learning how DFND
describes molecular topography. Each notebook combines an explained geometric
input, independent reference checks, visual observations and an optional
comparison with original third-party tools. It is the seed of a future benchmark
annex to the TopoMT documentation.

The collection is under development. Two controls are available: a regular
tetrahedron and a sampled shell with an independently certified wall. They do not
establish general biological accuracy or numerical volume precision. Development
pauses after this two-case tranche for review.

```{toctree}
:maxdepth: 1

regular_tetrahedron
closed_shell
```

## Run a case

Use a supported TopoMT installation and the development environment in
`devtools/conda-envs/development_env.yaml`. Notebook tools include JupyterLab,
IPyKernel, NBFormat, NBClient and Matplotlib. These are development/documentation
dependencies, rather than new TopoMT runtime requirements.

Open a notebook from this directory and execute all cells in order. To execute
the first case from the repository root:

```bash
python -m jupyter nbconvert --to notebook --execute \
    docs/content/showcase/dfnd/regular_tetrahedron.ipynb \
    --output regular_tetrahedron.executed \
    --output-dir /tmp/topomt-notebook-rerun
```

Install original providers separately if you want the optional comparisons:

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

Both notebooks compare original engines on an explicit synthetic `ATOM` export;
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

The notebook reads versioned input artifacts and displays a new observation
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

The first two notebooks are delivered. Later cases will enter the collection
after their input assumptions and independent expectations have been reviewed.
