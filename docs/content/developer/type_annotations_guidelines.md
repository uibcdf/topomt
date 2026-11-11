# Type annotations (Python 3.11–3.14)

We follow modern type hinting conventions:

- Source must remain compatible with **Python 3.11–3.14**. Routine development
  uses Python 3.14; the oldest supported syntax is Python 3.11.
- Do **not** include `from __future__ import annotations`.
- Write type hints **without quotes**, unless referencing a class not yet defined
  (forward reference).
  ```python
  def ensure_path_exists(path: Path, description: str) -> None:  # ✅ correct
  ```
  ```python
  def connect(self, other: "Feature") -> None:  # ✅ forward reference
  ```
- Use `typing` types in their modern form (`list[int]`, `dict[str, Any]`, etc.),
  not legacy imports (`List`, `Dict`).
- Avoid unnecessary abstraction layers like `TypeAlias` or `Protocol` unless you
  really need structural typing.
- Prefer explicit, concrete types for clarity and readability.

## Checking the public Topography registry

From the repository root, use:

```bash
python -m mypy --config-file devtools/mypy_topography.ini
```

If mypy lives in a separate tool environment, run it there and add
`--python-executable /path/to/scientific/python` to identify the runtime whose
dependencies are being inspected. Do not install or modify scientific packages
just to satisfy this checker.

The configuration checks `topomt/topography/Topography.py` and the positive
consumer examples in `tests/typing/topography_queries.py`, targeting Python 3.11.
It follows imports for type information while reporting errors only in these
explicit targets. Provider-specific entries handle unresolved MolSysMT and
PyUnitWizard typing; local errors are not ignored. A passing result does not
qualify all imported implementations, unannotated method bodies, the whole
package or an installed interpreter/platform matrix.

`get_features()` returns sets. With `as_feature_ids=True` their members are
strings; otherwise they are the registered `BaseFeature` objects. Grouping
returns a dictionary of such sets, with integer dimensionality keys or string
type/shape keys. Literal flags select the corresponding return annotation;
runtime flags require handling the possible return variants.

`info()` returns the `TopographyInfo` typed mapping: `total` is an integer,
`by_dimensionality` maps integers to counts, and `by_type`/`by_shape` map their
names to counts. Annotations describe these existing runtime structures.
Tests in `tests/test_topography_queries.py` preserve identity, empty results,
grouped sets, key types and lookup/error behavior.

---

**Example:**

```python
from pathlib import Path

def ensure_path_exists(path: Path, description: str) -> None:
    if not path.exists():
        raise FileNotFoundError(f"The {description} '{path}' does not exist.")
    if not path.is_file():
        raise ValueError(f"The {description} '{path}' is not a file.")
```
