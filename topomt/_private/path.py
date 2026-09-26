from os import PathLike
from pathlib import Path


def ensure_path_exists_and_is_file(path: PathLike[str]) -> None:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"The path '{path}' does not exist.")
    if not path.is_file():
        raise ValueError(f"The path '{path}' is not a file.")


def ensure_path_exists_and_is_dir(path: PathLike[str]) -> None:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"The path '{path}' does not exist.")
    if not path.is_dir():
        raise ValueError(f"The path '{path}' is not a directory.")
