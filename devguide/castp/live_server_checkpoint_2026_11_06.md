# Original server diagnostic — 2026-11-06 local / 2026-11-07 UTC

Owner: [TopoMT #101](https://github.com/uibcdf/topomt/issues/101); broader fidelity
remains [#19](https://github.com/uibcdf/topomt/issues/19). This is a bounded live
diagnostic from this workspace, separate from the
[source-binding checkpoint](source_binding_checkpoint_2026_11_06.md), service
uptime guarantees, prepared PharmacophoreMT receiving and installed qualification.

## Observed routes

Both public calculation pages returned HTTP 200. CASTp3's HTTP form was reachable;
its HTTPS endpoint refused the connection. CASTpFold served its React entry
page and current JavaScript asset. A page's HTTP response does not establish
functional rendering, PDB-ID search or a completed calculation.

The two historical Fold jobs from the
[October audit](server_input_contract_2026_10_01.md) were retrieved before any
new submission. Both result URLs returned HTTP 200 with the same 713-byte HTML
entry page, not ZIPs. Their remote completion/retention remains unknown. Such a
response must not be read as a successful calculation with zero cavities.

Current deployed Fold JavaScript still uses `submit_calc.php` and the existing
`data/tmppdb/<jobid>/processed/<jobid>.zip` download route. These agree with our
existing client. No replacement local kernel or browser automation was used.

## Controlled public input and actual API calls

Each existing original-server API was called once with the historical processed
`2pk4.pdb` extracted unchanged from the tracked CASTp3 ZIP: 92,340 bytes, 745
atoms, one frame, no MODEL or alternate-location records. It is public reference
data, not a chemically prepared receptor. The input SHA-256 is
`491d6fc18883b7b3f82c8b9c85023129a7390c7120ba94eb16b199801f2ee1c1`.
Multipart captures verify that those exact bytes were sent once per request,
with probe 1.4 angstroms and the provider's default `null`/`N/A` email. No personal
email or other molecular source was sent.

The diagnostic records every POST acknowledgement before polling. A saved
receipt prevents another invocation from repeating the submission. Existing
jobs are resumed by GET; there were no blind retries of a POST.

### CASTp3

The server replied HTTP 200 with `Something wrong with upload! 7`; no job ID was
received. Our existing client rejected the response. This is not evidence of
successful CASTp3 execution, and no alternative method was substituted.

The [public Fold handler](https://github.com/BoweiYe1/CastpFold/blob/766326ec98256d0daf02783500c1eb7f6812a560/public/submit_calc.php#L74)
constructs that exact message from `$_FILES['file']['error']` before creating a
job. PHP defines [error 7](https://www.php.net/manual/en/filesystem.constants.php#constant.upload-err-cant-write)
as failure to write the uploaded file to disk. **Conditional inference:** if the
deployed CASTp3 handler retains that construction, this points to upstream upload
storage, preceding molecular processing. The deployed handler, path, permissions,
capacity and cause were not inspected; the message alone does not prove them.

### CASTpFold

The actual API submission returned `success=true` and job **`j_6aee76eb99748`** at
**2026-11-07 00:55:07 UTC**, confirming filename `2pk4.pdb`, probe `1.4`, email
`N/A`. `hetatm` and `mostfreq` were absent from this acknowledgement and were
not invented. Immediate polling returned HTML; the nonwaiting API call raised
its existing not-ready error while the recorded job remained recoverable.

At **00:58:25 UTC**, retrieval returned a **39,462-byte valid ZIP**, with all CRCs
passing. This bounds observed availability; it is not an exact computation-time
measurement. The public `CastpFoldClient.download_result_zip_bytes` subsequently
returned identical bytes without a new POST. ZIP SHA-256:
`3d607718a4bc40bf85cd779173425642ad8f96620db485cda11043cb7611508b`.

Our files API imported **seven pockets and three mouth aggregates**. All 745
atoms were retained in the result PDB; retained serials supplied an explicit
map back to the submitted source, validated against names, residues, chains,
elements and coordinates. That inventory does not by itself establish which
atoms were active in every upstream calculation stage.

The source-bound result survived bundle and H5MSM source persistence/recovery.
Its run ID remains
`699e8017d111fc4e7eef8e2d1a6cc60b15d7d1f0d82514f47dd9675c6eb39372`.
Pocket and mouth membership/coordinates and every numeric `.pocInfo`/`.mouthInfo`
row match the historical Fold `2pk4` export. Job-specific molecule names were
excluded from that comparison. This establishes repeatability on this input,
not general server fidelity or native-method equivalence.

## Operational limits and continuation

The deployed Fold form explicitly allows minutes to hours for completion.
Acceptance, not-ready polling, a received archive and an imported result are
distinct states. Current client acknowledgement retention, exact retry counts
and transport/HTML/not-ready diagnostics still need their own service-contract
slice. In particular, `retries=0` currently performs two GETs; this diagnostic
recorded that behavior rather than changing it silently.

The conclusion is **partial availability**: Fold calculation, download and local
import succeeded for one public input; CASTp3 upload failed. Website rendering
and PDB-ID search were not qualified. Existing jobs were not treated as zero
results, and another server was not selected on CASTp3's behalf.

The [evidence receipt](evidence/castp_live_2pk4_20261107.json) and
[261,774-byte archive](evidence/castp_live_2pk4_20261107.zip) retain the exact submitted
input, acknowledgements, requests, result ZIP, source/bound bundle, observations
and bounded comparison receipts. All 24 payload hashes and CRCs were verified.
Raw website HTML and third-party JavaScript are excluded; their HTTP observations
and hashes remain. No original provider package was installed.
Prepared-receptor receiving remains under #101; no biological relevance or
chemical-readiness claim follows from this processed-PDB diagnostic.
