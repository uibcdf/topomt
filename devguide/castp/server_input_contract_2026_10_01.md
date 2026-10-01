# CASTp server input audit — 2026-10-01

TopoMT already supports both original servers through
`get_provider_output(..., method='castp', backend='server', server=...)`.
`Castp3Client` and `CastpFoldClient` upload the structure, obtain a job identifier,
poll for a ZIP and import the original files. Historical molecular archives and
mocked transports do not establish current service availability or acceptance
of fictitious synthetic atoms. No client or native engine was changed here.

## Official forms versus current clients

The forms and their served JavaScript were inspected on 2026-10-01:

| Requirement | CASTp 3.0 | CASTpFold |
|---|---|---|
| Official form | [Calculation](http://sts.bioe.uic.edu/castp/calculation.html) | [Compute](https://cfold.bme.uic.edu/castpfold/compute) |
| File | `.pdb` | `.pdb`, `.cif` |
| Browser size check | At most 5,000,000 bytes | Strictly below 2,000,000 bytes |
| Probe | 0–10 Å; default 1.4 Å | 0–10 Å; default 1.4 Å |
| Multipart fields | `file`, `probe`, `email`; default email `null` | `file`, `probe`, `email`; default email `N/A` |
| Successful response | String starting with `j_` | JSON with `success` and `jobid` |
| Preprocessing stated by form | Not established by this audit | Nonpolar hydrogens ignored; multiple-model NMR structures disallowed |
| Explicit radius-array upload | No field exposed | No field exposed |

CASTpFold's [current frontend bundle](https://cfold.bme.uic.edu/castpfold/static/js/main.9ed1feb8.js)
also displays `hetatm` and `mostfreq` from the acknowledgement. Their effective
values and retained atom population require returned evidence. The form does
not expose them as user-supplied fields.

The current clients use binary size bounds (`5 * 1024**2` and `2 * 1024**2`).
CASTpFold's client restricts probes to 0–5 Å and checks `jobid` without checking
`success` separately. These are follow-up discrepancies; the small inputs and
1.4 Å probe satisfy both sets of bounds. CASTp 3.0's HTTP endpoint responded;
HTTPS on that host was unavailable during this audit. CASTpFold uses HTTPS.

## Coordinate records and physical model

The [wwPDB specification](https://www.wwpdb.org/documentation/file-format-content/format33/sect9.html)
places coordinates in columns 31–54 in Å, element in columns 77–78 and atom name
in columns 13–16. A one-letter carbon atom name starts at column 14. Nonpolymer
atoms use `HETATM`; `ATOM` describes standard polymer residues. Select one frame
and a consistent alternate-location policy, and retain the exact submitted PDB.

The canonical synthetic writer left-aligns `C` at column 13. Historical inputs
remain unchanged. `input_castp.pdb` corrects only that field to ` C  `, retaining
HETATM, DUM labels, coordinates and elements. Tests enforce those byte-level
invariants. This export correction does not change geometry or repair the
production writer. The local peers' ATOM variant is a reader-compatibility input;
its DUM atoms do not become a biological polymer.

The forms document neither DUM acceptance nor a way to supply our reference
radius array of 1.7 Å. Upload acceptance does not prove all dummy atoms survived
preprocessing or that CASTp used the same radii. Do not add fictitious protein
atoms to obtain a result or describe these inputs as identical physical models.

## Live evidence and recovery

| Frozen case | CASTp 3.0 ATOM upload | CASTpFold aligned HETATM upload |
|---|---|---|
| Regular tetrahedron | `Something wrong with upload! 7`; no job ID | Accepted: `j_6abe78a311665`; result not observed |
| Sampled closed shell | `Something wrong with upload! 7`; no job ID | Accepted: `j_6abe78a074161`; result not observed |

The uploads differ in record type and atom-name alignment, so these attempts do
not isolate server-version effects. The CASTp 3.0 message alone does not prove a
format error, DUM rejection or service filesystem failure. CASTpFold warns that
completion can take minutes to hours. Bounded client polling and later GETs
returned no ZIP. Its recorded state is `submitted_pending`, with job ID, last
poll and the separate client exception. Remote completion or failure is unknown;
neither observation is a completed zero-pocket calculation.

Per-case `castp3_observation.json` and `castpfold_observation.json` retain date,
endpoint, probe and submitted-input checksum. Notebook reruns read that evidence
without creating jobs. Retrieve the existing job IDs before any new submission.
If a ZIP arrives, retain it, inspect processed atoms and radius assumptions,
import through the existing files route and append a reviewed observation.

CASTpFold's [tutorial](https://cfold.bme.uic.edu/castpfold/infos/allabout/tutorial.html)
defines SA area and volume. Its 14-residue minimum describes the precomputed
pocket-similarity dataset, not an established upload minimum. That rule and the
server's volume definitions are not DFND acceptance references.
