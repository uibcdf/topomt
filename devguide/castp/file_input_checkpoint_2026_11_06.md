# CASTp original file-input checkpoint — 2026-11-06

Owner: [TopoMT #101](https://github.com/uibcdf/topomt/issues/101) for original
provider receiving; exhaustive fidelity remains under
[#19](https://github.com/uibcdf/topomt/issues/19). This is a source-reader
checkpoint, separate from native CASTp research, live service availability,
prepared-receptor consumption and installed-package qualification.

## Result and public behavior

ZIP and directory inputs now select one coherent family of original result
files recursively. Result files must share their parent directory and filename
stem. The ZIP's external name does not select that family: 71 retained Fold
exports use internal server job identifiers instead of the ZIP's PDB ID.
The matching PDB supplies atom ownership; auxiliary PDBs without corresponding
result files remain original evidence and do not compete with it. This preserves
the packaged TcTIM directory that also contains fpocket output. Explicit
individual-file arguments still allow deliberately selected custom names.

All files remain byte-for-byte in `ProviderRun`, including README, atom
contributions, bulb JSON and auxiliary files. Feature and measurement source
links use the actual relative path, including nested directories. The original
ZIP remains an input artifact; server imports retain their submitted PDB and
untouched downloaded ZIP through the existing server route.

Input routes are mutually exclusive. Ambiguous result families and unmatched
PDB associations fail explicitly. ZIP admission rejects duplicate entries,
noncanonical or truncated names, symbolic links and case aliases in path
components. Extraction preserves names without `extractall` normalization and
creates files exclusively; failures clean their temporary directory. This
prevents an overwritten or renamed member from becoming apparently original
evidence. It does not qualify a new operating-system support lane.

A measurement-only directory now retains its run while leaving atom membership
and geometry unknown. A header-only measurement table remains a known empty
table. Missing result files or a measurement table without any header are
invalid. Empty atom-membership files remain valid: the real Fold `1crn.zip`
contains one closed cavity, a zero-mouth row and a zero-byte `.mouth` file.

## Executed evidence

The new `tests/methods/castp/test_castp_artifact_inputs.py` supplies 60 cases.
Positive layout tests wrap unchanged CASTp3 `1tcd` and Fold job-named `1psn`
payloads, in both member orders and through ZIP/directory routes. These are
explicit packaging transformations, not new server calculations. They compare
records, source indices, membership roles, geometry, original fields and units,
resolve every source-artifact link and verify the portable evidence round trip.
Other controls exercise partial/empty input, explicit custom names, ambiguity,
archive identities, the mixed-provider demo and the real empty-mouth export.

Test-first evidence retains the initial nested-ZIP failure (zero pockets instead
of 78), four accepted zero-byte-table failures and two accepted case-alias
failures. Review also caught the initial recursive-discovery regression in the
mixed-provider demo; its two failed existing guards and subsequent green result
remain in the evidence. The final affected source selection passes **146 cases**,
with **four pre-existing skips for unavailable optional engines** in the common
provider-output module. None of the 60 new CASTp cases skips. Distribution and
reporting contracts separately pass **20 cases**. Ruff checks all 472 Python
files; local mypy passes for `topomt/io/load_CASTp.py` and report indexes agree.
The complete headless HTML build succeeds with 11 existing warnings in unchanged
documentation. All 56 local links in the affected documents resolve.

An independent raw-archive inventory covers all **95 tracked ZIPs**: six CASTp3
and 89 Fold, with one five-file core family in each. All atom labels in `.poc`
and `.mouth` belong to the corresponding archived PDB. A complete source-reader
pass reproduces the independently counted **3,968 pocket rows** and **2,102
positive mouth aggregates**, verifies every original artifact byte and resolves
all feature/measurement artifact links. The receipt records the exact reader
hash and elapsed time; this is not a comparative performance benchmark.

The [evidence receipt](evidence/castp_file_inputs_20261106.json) and its
[84,457-byte archive](evidence/castp_file_inputs_20261106.zip) retain input/member hashes,
the scientific verifier, source/test snapshots, receipts and bounded logs.
Its manifest and SHA-256 sidecar permit verification without depending on the
ignored `.cache/castp-handoff/` working directory.

## Remaining receiving boundary

These checks associate original records with the PDB inside their export.
They do not establish correspondence with an independently prepared receptor,
full source/reference-chemical-state validation, reconstruction of `CASTpOutput`
from a saved `ProviderRun` without recapture, or PharmacophoreMT receiving.
The corpus contains no CASTp export of the prepared eralpha handoff source.
No live job was submitted or retrieved here, no new working-environment package
was installed, and no external-provider or native fallback was substituted.

The current development environment reports unavailable legacy OpenMM PDB bond
inference and retains declared edges. Atom/geometry file reading passes; complete
chemistry and preparation are not qualified by those reads. The next slice
must retain an explicit public MolSysMT atom correspondence, full source frame
and reference-state context before progressing to a declared prepared consumer.
General qualification/full-suite backlog remains #16/#58; #101 and #19 stay open.
