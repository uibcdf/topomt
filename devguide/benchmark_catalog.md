# Benchmarks and benchmarking databases

Reviewed: 2026-10-03. Permanent discovery conversation:
[discussion #92](https://github.com/uibcdf/topomt/discussions/92), in Reading List.

This inventory covers datasets and reference collections for molecular surface
topography. The [external-tool catalogue](external_tools_catalog.md) covers
providers and software. Both are permanent navigation documents outside the
defect/proposal queues; concrete work remains in owning issues and reports.

## Inventory and evidence scope

| Collection | Scientific purpose | Availability and current qualification |
|---|---|---|
| PocketPicker, pyCASTa distribution | Historical ligand-site detection/ranking and bound/unbound comparisons | Inspected pairing table: 48 pairs, 96 unique PDB IDs; not a reproduced OpenCASTp ligand-site benchmark |
| COACH420, pyCASTa distribution | Larger ligand-site detection/ranking benchmark | 420 directly stored PDBs and evaluation source inspected; OpenCASTp execution and annotation/metric qualification pending |
| TopoMT archived CASTpFold panel | Modern-server region-membership and analytical-measurement equivalence | 89 archived inputs; cumulative independent OpenCASTp audit passes every currently audited field on 84/89; full equivalence remains unqualified |
| DFND synthetic collection and notebook laboratory | Independent geometric references, controlled parameter changes and public demonstrations | Two independently reviewed notebook controls; other generated constructions require separate reference qualification |

Finding, obtaining, inspecting, executing and validating a collection are distinct
states. Collection size and a green implementation test do not establish
independent ground truth or a validated biological benchmark.

## PocketPicker as distributed with pyCASTa

Sources: [pyCAST article, section 4.1 and result tables](https://pmc.ncbi.nlm.nih.gov/articles/PMC12357058/),
[archived release](https://doi.org/10.5281/zenodo.15130898), and
[upstream data](https://github.com/giorgioluciano/pycasta/tree/f3418f38cd3d3c11e6cdd8c13b11431cc5b91894/src/pycasta/data).

The inspected upstream revision is
`f3418f38cd3d3c11e6cdd8c13b11431cc5b91894`. Its
`src/pycasta/data/tables/correspondence.xlsx` contains 48 bound/unbound pairs,
with 96 unique PDB identifiers. Each directory contains 49 PDB files; directory
membership is not identical to pairing-table membership. The existing
[pyCASTa contract](pycasta/contract.md#paired-benchmark-correspondence) retains
the correspondence and the broader directory inventory.

The article specifies alpha 2.8 Å and a 4 Å ligand threshold; these are the
article's settings, not adopted CASTpFold/OpenCASTp parameters. Its ligand-site
containment and ranking results require their own reproducible evaluator.

The 96 pairing-table IDs overlap 74 of TopoMT's 89 server archive IDs. Both
members are available for 35 pairs; 22 IDs are absent from the server panel:
`1chg`, `1igj`, `1imb`, `1ime`, `1krn`, `1l3f`, `1pts`, `2cba`, `2ctb`,
`2ctc`, `2h4n`, `2sil`, `2sim`, `2tmn`, `3gch`, `3mth`, `3p2p`, `5cpa`,
`5p2p`, `6ins`, `6rsa`, `7rat`.

This is identifier coverage only. Before numerical comparison, freeze exact
files/hashes, models, chains, alternate locations, hydrogens, modified residues,
ligand assignments and radius profiles. The article itself flags changed PDB
versions and superposition problems in some paired cases.

## COACH420 in the current pyCASTa repository

Sources: [PDB directory](https://github.com/giorgioluciano/pycasta/tree/f3418f38cd3d3c11e6cdd8c13b11431cc5b91894/data/coach420/pdbs),
[manifest](https://github.com/giorgioluciano/pycasta/blob/f3418f38cd3d3c11e6cdd8c13b11431cc5b91894/coach420.ds), and
[evaluation script](https://github.com/giorgioluciano/pycasta/blob/f3418f38cd3d3c11e6cdd8c13b11431cc5b91894/src/pycasta/evaluate_coach420.py).

The inspected revision contains 420 direct PDB files, with chain-specific names,
and stored outputs from other methods. None of their four-character PDB IDs
overlaps the current 89 archived server cases. This collection is present in
the current repository; it is not the benchmark described in the cited article.

Before adoption, establish original dataset provenance/version, ligand
annotations, excluded cases, ranking and metric definitions, and reproducibility
of each stored method output. The current evaluator consumes ligand-mesh distances
while labelling a calculation DCA; do not adopt that label as an independently
verified standard metric or reuse its comparison percentages without qualification.

## CASTpFold reference archives and OpenCASTp ownership

TopoMT stores 89 original-result archives under `topomt/data/CASTpFold_server/`.
The independently executed OpenCASTp evidence is maintained in
[its equivalence checkpoint](https://github.com/uibcdf/opencastp/blob/main/devguide/server_equivalence.md)
and [OpenCASTp #6](https://github.com/uibcdf/opencastp/issues/6).

As of this review, separately pinned disjoint cohorts cover all 89 cases:
3729 exact region memberships, 14911/14916 region SA/MS values and
26103/26103 additional aggregate descriptors. Five scalar residuals remain;
individual-mouth geometry, per-atom contributions and exported orthospheres
are not fully qualified. This is not a ligand-site accuracy/ranking benchmark.
TopoMT's own historical reproduction evidence remains separate from OpenCASTp's.

The later [joint precision and individual-mouth checkpoint](https://github.com/uibcdf/opencastp/blob/main/devguide/joint_precision_mouth_controls_2026_10_03.md)
adds bounded checks in seven systems: 203 mouth partitions / 1059 triangles
agree with an independent edge-fan graph on shared geometry and seeds. All
632 individual SA/MS area/perimeter values, rim atom sets and triangle counts
match the server for 158 one-mouth regions. The 20 multi-mouth regions have
matching aggregates but no individual server oracle. Five regional scalar
residuals remain; no tested joint intermediate-precision/export variant
improves the panel. This is OpenCASTp evidence, not a new TopoMT engine run.

The [independent 1MRG geometry and live-server controls](https://github.com/uibcdf/opencastp/blob/main/devguide/1mrg_geometric_server_controls_2026_10_03.md)
support native SA volume and area using a separate planar-section algorithm on
the same prepared spheres and two-tetrahedron domain. Three fresh CASTpFold
jobs preserve all 29 regions, printed measurements and 365 exported orthospheres
under translations, including the unresolved volume discrepancy. These are
replicates of one existing benchmark system, not three additional cases. The
five scalar residuals remain open under OpenCASTp #6; no server defect or exact
equivalence recipe is established. TopoMT's engine is unchanged.

The later [probe and historical assembly controls](https://github.com/uibcdf/opencastp/blob/main/devguide/1mrg_probe_assembly_controls_2026_10_03.md)
add five completed 1MRG parameter replicates: 145 exact regions, 579/580 scalars,
1015 additional descriptors and 1825 exported orthospheres. Archive receipts
and job identity were verified after correcting a private filename collision.
A six-decimal intermediate formatting candidate matches these controls but
worsens the original 89-input corpus. Original C regional assembly retains the
five residuals. This adds no distinct molecular systems or TopoMT engine run;
the complete OpenCASTp equivalence gate remains open.

The [six completed minimal controls](https://github.com/uibcdf/opencastp/blob/main/devguide/minimal_server_controls_2026_10_03.md)
retain the 1MRG discrepancy with only five original atoms and supply a regular-
tetrahedron counterexample to uniform final rounding. All six lining sets,
42 additional descriptors and eight supporting spheres match; 22/24 regional
scalars and all 16 elementary separated-sphere atom measures pass. Both server
and native castp3 report an open hull region for the separated balls. These
are explicitly constructed diagnostic geometries, not six additional proteins,
the original DFND DUM/radius models or a biological binding-site benchmark.

The [partial-precision investigation](https://github.com/uibcdf/opencastp/blob/main/devguide/partial_precision_controls_2026_10_03.md)
uses those six cases to screen forty-one ablations. Two candidate policies
survive nineteen proteins (seven frozen geometries plus twelve freshly
prepared inputs), but two new predeclared four-atom CASTpFold jobs refute
both common policies. Native matches all eight new regional scalars,
fourteen additional descriptors and two supporting spheres. Independent
sections support the explicit new geometries. No TopoMT engine or OpenCASTp
numerical policy changed; the original five residuals/89-input verdict remain
open. These two jobs are diagnostic point clouds, not additional proteins.

## DFND controls

Sources: [synthetic collection](DFND/synthetic_benchmarks.md),
[reference-panel issue #76](https://github.com/uibcdf/topomt/issues/76), and
[notebook checkpoint](DFND/notebook_laboratory_checkpoint.md).

The regular tetrahedron and sampled closed shell have reviewed independent
references and retained provider outcomes. Their notebook sources live under
`docs/content/showcase/dfnd/`. Synthetic construction labels alone are not
oracles. Provider input failures remain failures, not zero detected pockets.
The notebook checkpoint retains the pause boundary and unresolved server jobs.

## Adding and adopting a collection

Record official sources and acquisition route, version/revision and review date,
system counts and molecular scope, annotations/reference type, intended metrics
and units, licence/redistribution terms, overlap, qualification status and owning
work/evidence links. Licence and redistribution conditions for the external
datasets above have not been independently qualified by this inventory; a source
code licence does not establish permission for every bundled dataset.

Use discussion #92 for discovery. Keep the inventory current when evidence
changes; preserve raw inputs and parameter provenance in the owning scientific
records. Acquisition, evaluator implementation and validation phases get bounded
issues when selected. Dataset execution, integration, website publication and
automatic monitoring require separately tracked work and evidence.
