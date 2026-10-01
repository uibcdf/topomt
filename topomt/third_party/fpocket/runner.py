import os
import subprocess
from pathlib import Path
from typing import Sequence

from depdigest import check_dependency

from topomt._depdigest import DOC_URL, LIBRARIES
from topomt._private.smonitor import TopoMTException


class FpocketError(TopoMTException, RuntimeError):
    """Report fpocket availability or execution failures through SMonitor."""

    def __init__(self, message: str | None = None, **kwargs) -> None:
        super().__init__(message, **kwargs)


class _MissingExecutable(ImportError):
    """Distinguish the shared absence result from provider import failures."""


def run_fpocket(
    pdb_file: str | Path,
    *,
    fpocket_cmd: str = 'fpocket',
    workdir: str | Path | None = None,
    extra_args: Sequence[str] | None = None,
) -> Path:
    """Run the configured fpocket command and return its output directory.

    Availability is checked through DepDigest for ``fpocket_cmd`` before
    execution. Missing commands and engine failures raise ``FpocketError``;
    unrelated filesystem and provider errors retain their original identity.
    """
    pdb_file = Path(pdb_file).resolve()
    if workdir is None:
        workdir = pdb_file.parent
    else:
        workdir = Path(workdir).resolve()

    # subprocess resolves relative executable paths after changing to cwd.
    executable = fpocket_cmd
    if os.path.dirname(fpocket_cmd) and not Path(fpocket_cmd).is_absolute():
        executable = str((workdir / fpocket_cmd).resolve())

    dependency = LIBRARIES['fpocket']
    try:
        check_dependency(
            'fpocket',
            kind=dependency['kind'],
            executable=executable,
            pypi_name=dependency['pypi'],
            conda_name=dependency['conda'],
            conda_channel=dependency['channel'],
            doc_url=DOC_URL,
            caller='run_fpocket',
            exception_class=_MissingExecutable,
        )
    except _MissingExecutable as exc:
        raise FpocketError(
            str(exc), code='ExecutableNotFoundError', executable=fpocket_cmd
        ) from exc

    cmd = [fpocket_cmd, '-f', str(pdb_file)]
    if extra_args:
        cmd.extend(extra_args)

    try:
        subprocess.run(
            cmd,
            check=True,
            cwd=workdir,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError as exc:
        raise FpocketError(
            f'fpocket failed with code {exc.returncode}:\n{exc.stderr}'
        ) from exc

    out_dir = workdir / f'{pdb_file.stem}_out'
    if not out_dir.exists():
        raise FpocketError(f'Expected fpocket output dir not found: {out_dir}')

    return out_dir
