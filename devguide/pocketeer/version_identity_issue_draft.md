# Draft: Pocketeer 0.4.0 distribution reports __version__ 0.3.0

Destination: `cch1999/pocketeer`. Not published; external disclosure requires
explicit human permission under the common contribution policy.

The public `pocketeer-0.4.0-py3-none-any.whl` identifies its distribution as 0.4.0,
while the installed package's `__version__` is the literal string `0.3.0`.

```python
from importlib.metadata import version
import pocketeer

print(version('pocketeer'))  # 0.4.0
print(pocketeer.__version__)  # 0.3.0
```

Observed on Linux x86_64/Python 3.14.7. All 14 Python runtime files in the wheel
match `v0.4.0`, commit `f59cd12fbe175ebf4c34d70405c4c41476d4cc03`, including
the version declaration. Please align the module version with the distribution,
or clarify whether the two identifiers intentionally have different meanings.

TopoMT records both identities and the executing API-file digest for provenance.
Its bounded original-library structural comparison passes; no geometry, ranking
or numerical defect is inferred from this version discrepancy.
