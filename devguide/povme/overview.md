# Original external POVME

Owner: [#193](https://github.com/uibcdf/topomt/issues/193); broader family/PyVOL
assessment stays [#159](https://github.com/uibcdf/topomt/issues/159).
Read the [user contract](../../docs/content/user/povme.md) and
[exact source/execution checkpoint](../specialist_provider_checkpoint.md).

TopoMT's worker imports public `PocketVolumeConfig`/`PocketVolume` operations
from the selected external source/interpreter. It verifies import origins,
single-frame results, dependency versions and module fingerprints. The separate
compatibility fork changes packaging/Ray bootstrap, preserving the scientific
modules and original serial task methods. No POVME algorithm is copied into
TopoMT and no parallel runtime is started.

Explicit inclusion regions define the analysis domain. Exclusion/seed regions,
grid spacing, atom-surface distance cutoff and hull/connectivity controls retain
their original semantics. Conservative preflight estimates cover every mesh and
worst-case neighbor storage before launching the worker. The result's `regions`
collection contains the measured frame/ROI, including zero; it does not assert
that a closed cavity or unknown binding site was detected.

Original CSV and returned volumes must agree. When a retained-point PDB exists,
its row count times spacing cubed must agree too. The initial NPY grid header
and payload are validated before creating an array view, without pickle loading
or trusting a claimed allocation size. Error-level original frame fallbacks are
refused. A successful original early return without exported retained points is
`not_written_by_original`, not an empty point cloud.

The captured fully excluded initial-region control raises the original
zero-size minimum-reduction/frame error. Its needs_review finding is owned by
[#195](https://github.com/uibcdf/topomt/issues/195) and
[UIBCDF/POVME#1](https://github.com/uibcdf/POVME/issues/1); see
[the report](../pending_bugs/povme_empty_initial_roi.md). Adapter rejection is
not a provider correction or evidence of geometric inferiority.

Saved reading validates configuration/input fingerprints and explicit units
without POVME, pymolecule, Pydantic, Loguru, Ray or original-machine paths. The
completed original-method citation and actual fork/version survive persistence;
the reader earns no fresh calculation credit. The original README's GPLv3-or-later
grant and contradictory Apache metadata remain documented; the compatibility
fork follows the explicit grant. PyPI/Conda artifacts, Pixi solving, Ray,
trajectories and other historical implementations remain separate qualification.
