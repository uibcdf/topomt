# Third-party engines

TopoMT supports external engines through Python libraries, a local executable,
web services, and persisted result files. It also provides native implementations
of several algorithms. The external engines are optional: installing TopoMT does
not install them, and importing TopoMT does not import them.

## Supported routes and requirements

| Provider | Original engine route | Installation and runtime requirements | Other TopoMT routes and current limits |
|---|---|---|---|
| [fpocket](https://github.com/Discngine/fpocket) | `third_party.fpocket`, `backend='cli'` | `conda install -c conda-forge fpocket`; executable available on PATH, or supply `fpocket_cmd` | Persisted output loader; native implementation and TopoMT variant. Native equivalence is under validation. |
| [Pocketeer](https://github.com/cch1999/pocketeer) | `third_party.pocketeer`, `backend='library'` | `python -m pip install pocketeer`; upstream installs Biotite, atomview and its other requirements | Native implementation needs Biotite, but does not require Pocketeer. Native equivalence is under validation. |
| [AlphaSpace2](https://github.com/RedesignScience/AlphaSpace2) | `third_party.alphaspace2`, `backend='library'` | `python -m pip install alphaspace2`; upstream requires MDTraj, SciPy, Cython and configargparser | Native implementation; library adapter currently accepts a receptor without a binder. Compatibility adjustments cover NumPy, the MDTraj SASA signature, and missing unbound contact arrays in PyPI 0.1.2. |
| [pyCASTA](https://github.com/giorgioluciano/pycasta) | `third_party.pycasta`, `backend='library'` | `python -m pip install pycasta biopandas colorama`; the published package omits these last two runtime requirements | Native implementation. The original runs in an isolated subprocess using its installed scripts and configuration. Optional PyMOL/FreeSASA functions have their own upstream requirements. |
| CASTp 3.0 | `third_party.castp`, `backend='server', server='castp3'` | Network access to the public server; no CASTp Python package to install | Persisted result loader. Server availability and job completion are independent of local dependencies. Local CASTp methods remain experimental. |
| CASTpFold | `third_party.castp`, `backend='server', server='castpfold'` | Network access to the public server; no CASTpFold Python package to install | Persisted result loader and experimental native CASTp routes. |

The `third_party` namespace contains provider adapters. Select `backend='library'`
explicitly for the original Python engines; those providers default to `native`.
The high-level `topomt.get_topography` API uses `implementation='wrapper'` for
Pocketeer, AlphaSpace2 and pyCASTA. A native route does not imply identical results
to the original engine; the provider comparisons and scientific audits determine
which measurements are equivalent.

The optional extras `topomt[alphaspace2]` and `topomt[pocketeer]` install auxiliary
libraries (MDTraj and Biotite), respectively. `topomt[third-party]` combines those
extras. They do not install the original engine distributions. Use the commands
in the table when choosing an original engine.

## Install and run an original engine

Run installation commands in the environment where TopoMT will execute:

```bash
conda install -c conda-forge fpocket
python -m pip install pocketeer
python -m pip install alphaspace2
python -m pip install pycasta biopandas colorama
```

Choose only the engines you need. Their upstream projects own the full dependency
and platform requirements. The following published distributions have been
checked on Linux with Python 3.13: Pocketeer 0.4.0, AlphaSpace2 0.1.2 and pyCASTA
1.0.8. Installed-engine regression tests compare their results with direct
upstream runs on the same PDB input. These checks do not certify every version,
platform, configuration, or native implementation.

The fpocket CLI route has also been checked against direct fpocket 4.2.3 runs
from conda-forge on Linux with Python 3.13. The executable must be visible in
the environment running TopoMT; installation in a different environment does
not make it available automatically.

```python
import topomt as tmt

pockets = tmt.third_party.pocketeer.get_topography(
    'protein.pdb', backend='library'
)
pockets = tmt.third_party.alphaspace2.get_topography(
    'protein.pdb', backend='library'
)
pockets = tmt.third_party.pycasta.get_topography(
    'protein.pdb', backend='library'
)
pockets = tmt.third_party.fpocket.get_topography(
    'protein.pdb', backend='cli', fpocket_cmd='fpocket'
)
```

The original Python engines are registered as soft dependencies in DepDigest.
Missing engines raise a TopoMT `LibraryNotFoundError` when their library backend
is requested. SMonitor provides the dependency diagnostic. An absent fpocket
command raises `FpocketError` with its Conda installation hint. Transitive import
failures and engine execution failures remain distinct from absence.

Older DepDigest versions may also suggest an inferred Conda installation command
for pip-only engines. Use the commands in the table above. The shared correction
is tracked in [DepDigest #22](https://github.com/uibcdf/depdigest/issues/22).

TopoMT captures submitted input, engine output and execution metadata in
`Topography.provider_runs`. pyCASTA's `version_tag` is an upstream output tag,
not its PyPI distribution version. AlphaSpace2 records whether it initialized
missing unbound contact arrays; this compatibility step supplies zero ligand
contacts without changing calculated geometry or scores.

## Source checkouts and web services

The Python adapters retain `upstream_root` for controlled source-checkout
comparisons. Supply an import root for Pocketeer or AlphaSpace2; pyCASTA accepts
the directory containing `run_analysis.py`, its package directory, or repository
root. Install the upstream runtime requirements even when using a source checkout.
For normal execution, use installed distributions in the current environment.

Web routes submit the selected structure to the external service:

```python
topography = tmt.third_party.castp.get_topography(
    'protein.pdb', backend='server', server='castpfold'
)
```

Live service availability is not established by local unit tests. Server adapters
and persisted result loaders have separate validation; using a saved result does
not require installing or contacting its original engine.
