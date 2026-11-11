# Scientific attribution

Runtime adoption is owned by [#157](https://github.com/uibcdf/topomt/issues/157).
Read the registered [Ackredit consumer guide](../ACKREDIT_GUIDE.md) before
changing these boundaries. The guide's publication is distinct from integration,
and source integration is distinct from installed/public qualification in
[#16](https://github.com/uibcdf/topomt/issues/16).

## User contract

Each reached, successfully completed scientific operation contributes to the
application's current Ackredit session. TopoMT creates bounded captures and
scopes, never an isolated session, import hook, DOI lookup or journal. Completed
empty analyses retain their references. A failed operation earns no completion
credit; genuinely completed child operations remain credited.

`topomt.get_attribution(result)` returns a detached
`topomt.scientific_attribution@1` dictionary. `Topography`, geometric meshes,
`DFNDData`, `ProviderRun` and `ProviderOutput` expose `.attribution` as well.
Raw DFND dictionaries have a separate `scientific_attribution` key; scientific
`raw`, `wet` and `dry` contents retain their definitions. Scalar, tuple and array
helper return types are preserved: use an application-owned Ackredit capture
when keeping the bibliography of a standalone helper result. Copying arrays,
selecting records, inspecting metadata and rendering references earn no new
calculation credit.

The host envelope retains producer/version, explicit bibliographic declarations
with target/roles/context, recording status and an optional portable Ackredit
snapshot. `recorded` means this boundary's recording succeeded; it does not prove
all transitive software is instrumented. `unavailable` retains host declarations
without a recorder. `failed` retains those declarations, any partial provider
snapshot and a catalog-backed `AttributionTrackingWarning`. Warning promotion
does not replace completed science. Unknown legacy attribution is `None`, never
an invented reference to the currently installed producer.

`topomt.cite(result, format='bibtex')` delegates validation/rendering to Ackredit.
It does not register another use. Host declarations remain renderable after an
absent/failed recorder, without changing the original recording status. The
portable snapshot can also include completed contributions from other already
instrumented libraries reached within the capture. Engine internals running in
subprocesses/services are not inferred from imports or automatically observed.

## Method and route inventory

| Boundary | Admission and references | Completion point |
| --- | --- | --- |
| Original fpocket CLI/wrapper | fpocket article and executed original software; adapter-recorded executable fingerprint, unknown version stays unknown | Original files parsed and source-bound Topography accepted in `fpocket/cli.py` |
| Original Pocketeer | Pocketeer software and upstream-requested fpocket article; recorded original version | `pocketeer/library.py` returns accepted Topography |
| Original AlphaSpace2 | AlphaSpace2 software and article; original distribution version | `alphaspace2/library.py` returns accepted Topography |
| Original pyCASTA | pyCAST software/article and CAST construction criterion; original recorded identity | `pycasta/library.py` returns accepted Topography |
| CASTp3 / CASTpFold services | Selected service software/article and CAST criterion, without substituting one service's paper for the other | Selected server adapter obtains and accepts its output; a submission receipt alone is insufficient |
| Original pyKVFinder, GHECOM, CAVER, P2Rank, MOLE, MoloVol, HOLE, POVME, PISA | Selected software/articles and adapter-recorded identity/version; MoloVol/HOLE conditionally credit recognized input data; POVME's compatibility fork retains its own version/URL | Shared `_execution.get_output` returns parsed, validated ProviderOutput; `files` bypasses tracking |
| Native fpocket / TopoMT variant | fpocket scientific criterion and reference implementation; executed TopoMT software | Both direct implementations and their Topography wrappers |
| Native Pocketeer, AlphaSpace2, pyCASTA, CASTp and CASTp3 | Selected method/criterion and reference implementation; executed TopoMT | Direct native functions, wrappers and main dispatcher helpers |
| DFND | Executed TopoMT and actual numerical/geometry children; no invented DFND publication | `dfnd`, `dfnd_to_topography`, direct network queries and derived-data queries |
| Delaunay / regular triangulation | TopoMT construction; Qhull and SciPy only when actually called | Mesh constructor and successful tessellation backend; the weighted four-point shortcut does not cite a fresh Qhull execution |
| Cached mesh use | Original construction records/versions, roles `reused_result` | Successful query using that mesh; no claim of rebuilding it |
| Binomial volume uncertainty | Clopper–Pearson 1934 criterion, executed TopoMT and actually reached SciPy quantiles | Completed conditional interval only; geometric proofs and quadrature bypass the criterion |
| Numerical kernels | NumPy for native array methods; SciPy and Numba at directly reached calls | Successful Python/backend boundary, once per enclosing meaningful operation rather than scalar iteration |
| Native fpocket SASA | Shrake–Rupley criterion and TopoMT implementation | Native surface descriptor computation |
| fpocket druggability | Schmidtke–Barril 2010 criterion, separately from the 2009 detector | Native score call, or an accepted original run reporting the score; no automatic credit in Pocketeer or other detectors |
| Biotite / MDTraj SASA | Selected software/article and Shrake–Rupley criterion | Actual successful SASA call; input reading alone does not earn the SASA article |
| Native AlphaSpace2 probe scoring | AutoDock Vina criterion; executed TopoMT, no claim of executing Vina | `_get_probe_scores` |
| Sphere-union marching cubes | scikit-image and Lewiner method | Actual `marching_cubes` call; an empty input does not credit that backend |
| Optional nearest-neighbor thickness | scikit-learn software/article | Successful neighbor query; explicit neighbor pairs bypass this credit |
| Channel skeleton / experimental graph work | NetworkX software/article when a graph is built; Dijkstra/Brandes only at their reached calculations | Successful graph/path/centrality boundary; experimental scientific status is unchanged |
| Other public geometry/feature helpers | TopoMT and directly used numerical software | Standalone meaningful helper; trivial storage copies and elementary triangle/tetrahedron formulas add no independent literature claim |

Native inspiration/adaptation is not execution of upstream software. Do not add
all catalogue candidates to a workflow bibliography: Zeo++, for example, remains
a study candidate, not an executed TopoMT integration. General Monte Carlo or
quadrature code does not by itself justify citing a particular unrelated
Monte Carlo algorithm. Method claims must follow the inspected implementation.

## Persistence and compatibility

The [specialist checkpoint](specialist_provider_checkpoint.md) records HOLE's
original 1993 citation request and conditional recognized-AMBER 1984 input-data
reference, POVME's requested 2011/2014 papers and executed compatibility-fork
identity, and PISA's 2007/2026 descriptions. Crossref/publisher metadata checked
on 2026-11-11 supplies complete author lists and issue/page identities; the
original HOLE table's page ending is not copied into the corrected bibliography.
Custom HOLE radii earn no invented AMBER reference. Failed original calculations
retain attempted executable/interpreter identity, controls and diagnostics, but
earn no completed-provider reference. Optional failure/absence and fresh engine-
and recorder-free reading have separate controls. The original POVME empty-ROI
failure remains needs_review under #195, not a scientific correction by #193.

MoloVol's [source overview](molovol/overview.md) records verified bibliography,
original element-resource identity and conditional `input_data_reference`
roles. The neutral route credits selected non-overridden Alvarez radii and
referenced natural-element atomic weights from the recognized resource.
All-radii overrides omit the unused radii paper; custom tables retain their
identity without invented citations. An ionic route has not been admitted and
earns no Shannon citation. Original source/table choices remain recoverable.

An attributed `ProviderRun.save` writes a version-2 ZIP envelope around the exact
version-1 scientific manifest plus detached attribution and its SHA-256. The
original run ID, artifact bytes, field provenance and scientific metadata remain
unchanged. Attribution changes do not define another scientific calculation.
Readers validate both planes. These are integrity checks, not authentication of
who actually produced the declarations.

Unattributed runs still write the original version-1 format. New readers accept
both. Older TopoMT readers accepting only version 1 cannot read the new envelope;
do not claim backward readability by those readers. Source-bound reconstruction
preserves the saved attribution without running a provider or registering
another calculation. Raw historical engine files without saved attribution
remain unrecorded; original source metadata alone cannot establish the version
of TopoMT that historically produced them.

## Bibliography and maintenance

`topomt/_bibliography.py` contains offline publication records, complete author
lists and original-work URLs. The initial review checked original articles and
upstream citation requests, then DOI-registered Crossref metadata on 2026-11-08.
Prefer print-issue years when present (GHECOM and Vina are 2010 despite 2009
online-first dates). NetworkX and scikit-learn use their original proceedings/
JMLR records; do not substitute an expanded later preprint author list.
Pocketeer's explicit citation request was consulted in the clean source at
`d5fc4665923fc4c09c47ac3eb7a6a79ec2fe6bcb`.
The fpocket detector and additional druggability citation requests were checked
in `doc/INTRODUCTION.md` at clean source
`4bb0d8447f62fee77e2c3c29f54b5fcaf5e2c066`. The current coefficients may differ
from the original paper; citation acknowledges the criterion and reference
implementation, not coefficient or predictive-performance equivalence.

The method map and software locators in `_ackredit.py` define roles, not a claim
that an arbitrary import executed its full algorithm. Original software versions
come from the accepted run, never the reader's installed distribution. Direct
in-process numerical backends use the observed installed distribution version.
Unreported versions remain null and original fingerprints remain in context.
TopoMT has no released DFND article/DOI to declare; use its software record and
the actual children until a reviewed publication exists.

For every new/changed scientific route:

1. Identify citable methods, adapted implementation/data and executed software;
   verify original bibliography and any upstream acknowledgement instructions.
2. Add offline declarations and the actual completion boundary. Keep optional
   imports deferred and application sessions intact. Cover direct public routes,
   aliases and evaluated-empty results.
3. Preserve detached result references and original versions, including cached
   reuse and saved reading. Do not add citation keys inside scientific descriptor
   mappings or change scalar/tuple APIs to carry metadata.
4. Test using real Ackredit: selected/unselected branches, reused references,
   nested workflows, absence, failures, strict warnings, import laziness,
   persisted reading and mutation independence. Protocol fixtures do not prove
   original-engine scientific accuracy or installed-tool qualification.
5. Update this inventory and user examples. Link an owning issue for any remaining
   gap; do not close broad attribution work after implementing only one provider.

The public portable contract used here starts at Ackredit 0.9.0. This source
development was received with editable Ackredit `0.12.1+10.g4beb850` at clean
source `4beb850c8ba814e6103b4d303128a1a36eb57610`, Python 3.14.10. That evidence
does not qualify every older provider, Python minor, optional engine, wheel or
Conda package. Broader adoption remains under #56 and delivery/support under #16.

## Volume precision criterion — 2026-11-10

The Clopper–Pearson record was checked against the original 1934 paper
([original-paper copy](https://www.barestatistics.nl/uploads/1/1/7/9/11797954/clopper__pearson_1934.pdf))
and [SciPy's primary API reference](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats._result_classes.BinomTestResult.proportion_ci.html).
Offline DOI/title/authors/year/volume/pages identify that interval criterion.
`binomial_interval` credits it only after successful numerical bounds, plus
actually used SciPy. Fixed-order/refined quadrature and geometric full/empty
proofs earn no binomial citation. Structured public measurements retain their
own detached envelope and reused construction references; legacy scalar/tuple
returns preserve the application-owned capture contract.
