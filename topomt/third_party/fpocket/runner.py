import subprocess
from pathlib import Path
from typing import Sequence


class FpocketError(RuntimeError):
    pass


def run_fpocket(
    pdb_file: str | Path,
    *,
    fpocket_cmd: str = 'fpocket',
    workdir: str | Path | None = None,
    extra_args: Sequence[str] | None = None,
) -> Path:
    """
    Ejecuta fpocket -f <pdb_file> y devuelve el directorio <stem>_out generado.
    """
    pdb_file = Path(pdb_file).resolve()
    if workdir is None:
        workdir = pdb_file.parent
    else:
        workdir = Path(workdir).resolve()

    cmd = [fpocket_cmd, "-f", str(pdb_file)]
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
            f"fpocket failed with code {exc.returncode}:\n{exc.stderr}"
        ) from exc

    out_dir = workdir / f"{pdb_file.stem}_out"
    if not out_dir.exists():
        raise FpocketError(f"Expected fpocket output dir not found: {out_dir}")

    return out_dir
