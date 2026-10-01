# DFND laboratory

This collection starts a public, reproducible laboratory for learning how DFND
describes molecular topography. Each notebook combines an explained geometric
input, independent reference checks, visual observations and an optional
comparison with original third-party tools. It is the seed of a future benchmark
annex to the TopoMT documentation.

The collection is under development. One minimal control is currently available;
it does not establish general biological accuracy or numerical volume precision.

```{toctree}
:maxdepth: 1

regular_tetrahedron
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

Install original fpocket separately if you want the optional CLI comparison:

```bash
conda install -c conda-forge fpocket
```

TopoMT requires DepDigest >=0.12.0. An older editable sibling checkout can take
precedence over an installed package; verify the version imported by the notebook
kernel. A missing executable is recorded as unavailable. Provider execution
failure remains a failure, even when the native reference checks pass.

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

Only the first notebook is delivered. Later cases will enter the collection
after their input assumptions and independent expectations have been reviewed.
