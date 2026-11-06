# Draft: installed-import inspection of extension-generated modules

Proposed owner: `uibcdf/molsyssuite`, linked to distribution work #45 and consumer
`uibcdf/topomt#78` / #101. Not published.

The `installed_imports.check_installed_imports` helper at SDK source
`b9852d973e96613a68cab7278491ff647bfd0b7d` rejects valid, fileless Biotite 2.0.0
PyO3 modules after original Pocketeer execution. The scientific invocation passes
218 cases but its final origin guard raises `ContractError` for
`biotite.rust.sequence.align`. This is a receiving-tool limitation, not a
scientific failure or evidence that an arbitrary fileless module is trustworthy.

Minimal setup in a source-free installed environment:

```python
import sys
from pathlib import Path
import biotite.sequence.align
from installed_imports import check_installed_imports

check_installed_imports(('biotite',), Path(sys.prefix), Path('/tmp/source-unused'))
```

The observed generated modules are `biotite.rust.sequence`, its `align` and
`phylo` children, `biotite.rust.structure`, its `io` child and the `io.pdb` /
`io.pdbx` children. They have neither `__file__` nor `__spec__`; each is the
actual attribute of its recorded parent. The chain reaches `biotite.rust`, an
ExtensionFileLoader module whose installed shared-object bytes pass RECORD hashes.

The bounded consumer control retains the unchanged checker for regular Biotite
subtrees and other suite packages, checks the Python root/native loader paths,
admits only those seven names, asserts every parent-object binding and verifies
all distribution RECORD hashes before/after the tests. Its earlier fileless
PyUnitWizard compatibility-alias checks also remain explicit. Nothing is deleted,
given a fabricated origin or admitted by a blanket namespace exemption.

Please review a supported declaration/inspection mechanism for generated native
submodules. Keep unknown namespaces, mismatched parent objects, source imports
and altered extension bytes failing closed. The provider owns the supported API
and compatibility decision; this draft requests analysis, not a consumer-chosen
general implementation.

Consumer owner: TopoMT #78. Review by 2026-12-05; remove the additional manual
bindings when a qualified shared checker supports this declared origin route.
The current receipt applies only to the enumerated Biotite 2.0.0 modules and
does not qualify future generated namespaces automatically.
