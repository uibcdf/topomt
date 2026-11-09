# Scientific attribution

TopoMT records the methods a calculation actually reaches when the optional
[Ackredit](https://github.com/uibcdf/ackredit) library is available. Your
application owns the session:

```python
import ackredit
import topomt as tmt

with ackredit.session('pocket study'):
    output = tmt.get_provider_output('protein.pdb', method='fpocket')
    bibliography = ackredit.report(format='bibtex')

# Each result also retains its own references, including reused citations.
records = tmt.get_attribution(output)
result_bibliography = tmt.cite(output, format='bibtex')
```

Direct provider calls and native methods participate too. Original execution
records identify the selected tool and its recorded version or fingerprint.
A native reproduction credits the reference method and implementation alongside
TopoMT. It does not claim that the original program ran. DFND currently credits
TopoMT software and the scientific backends it uses; no DFND publication is
invented.

`output.attribution`, `topography.attribution` and
`topography.dfnd.attribution` return detached metadata. Raw DFND dictionaries
carry a separate `scientific_attribution` entry. To retain references from a
standalone helper that returns a scalar, array or tuple, use `ackredit.capture`
around that call. A completed calculation finding zero features still retains
its references. Reusing a geometric mesh preserves its original construction
references with a reuse role.

## Recording status

`tmt.get_attribution(result)` works without Ackredit. Its `status` distinguishes:

- `recorded`: recording succeeded for this boundary;
- `unavailable`: Ackredit was absent; host bibliography is retained;
- `failed`: recording failed; host bibliography and any partial recording remain,
  and TopoMT emits an `AttributionTrackingWarning`.

Optional recording failures preserve scientific results. These statuses describe
recording, not scientific validity or exhaustive coverage of every dependency
inside an external engine. An uninstrumented legacy result returns `None`.

`tmt.cite(result)` needs Ackredit for formatting. It can render retained host
references after an absent/failed recorder without changing the original status
or adding the old calculation to the current session. Check applicability before
using the bibliography in a publication.

## Saving and reading

```python
output.save('original.zip')
restored = tmt.load_provider_output('original.zip', molecular_system='protein.pdb')
references = tmt.cite(restored)
```

The bundle preserves original references and producer versions. Reading or
formatting it runs no original engine and registers no new calculation. Its
scientific run ID and original artifacts remain unchanged.

Attributed bundles use a new version-2 envelope; readers in older TopoMT versions
supporting only version 1 cannot read it. Current readers accept both versions.
Old files lacking attribution remain explicitly unrecorded, rather than being
assigned the reader's current software version.

The integration uses Ackredit's portable API introduced in 0.9.0. Source receiving
has been checked with editable 0.12.1 and Python 3.14; installed/public TopoMT
qualification remains separate. No engine installation or import alone earns
scientific credit.
