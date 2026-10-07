# Installation

TopoMT is currently reviewed through its source-development route. Its noarch
Conda publisher is configured, but public receiving evidence remains pending in
[uibcdf/topomt#78](https://github.com/uibcdf/topomt/issues/78). On 2026-10-07 the
queried official `uibcdf/topomt` Conda and `topomt` PyPI metadata endpoints returned
404, and the current GitHub release inventory was empty. These bounded
observations do not prove historical absence or installed compatibility.

For this workspace, activate the qualified `molsyssuite@uibcdf_3.14` environment
and install the eligible local clone without changing its dependency closure:

```bash
conda activate molsyssuite@uibcdf_3.14
python -m pip install --no-deps --editable .
```

Run from the intended clone; verify Python 3.14, `pip check` and import origins
before testing. This command assumes an already provisioned environment. It is
not a standalone public install recipe or proof of supported scientific backends.
Optional owner Conda environments use the reviewed
[development commands](../../../devtools/conda-envs/README.md).

A future public Conda install requires an authorized real candidate, successful
exact-source and installed gates, promotion of the same bytes, and clean public
receiving evidence. A guide/publisher pin alone does not supply these prerequisites.
Python 3.11–3.14 qualification and public support remain tracked in
[uibcdf/topomt#16](https://github.com/uibcdf/topomt/issues/16).

Original third-party engines are optional and installed separately. See
[Third-party engines](../user/third_party_engines.md) for supported backends,
requirements, installation commands, and tested versions.
