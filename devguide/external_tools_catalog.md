# External-tool catalogue and provider stewardship

Organization updated: 2026-11-07; technical assessments retain their stated dates.
This is the maintained index for external integrations, comparison references
and research candidates. Historical intake remains in
[#8](https://github.com/uibcdf/topomt/issues/8); bounded reorganization is
tracked in [#67](https://github.com/uibcdf/topomt/issues/67).

Permanent conversation: [catalogue discussion #68](https://github.com/uibcdf/topomt/discussions/68)
in [Methods and Tools](https://github.com/uibcdf/topomt/discussions/categories/methods-and-tools).
The [resource register](discussion_resources.md) links each canonical resource
conversation, including historical candidates. Read [the contributor instructions](discussions.md)
for category procedures, facets and follow-up. Resource reviews, arguments and
dated conclusions belong in the conversations themselves.

Datasets and validation references have their own
[benchmark catalogue](benchmark_catalog.md) and permanent
[discussion #92](https://github.com/uibcdf/topomt/discussions/92) in Datasets and Benchmarks.

| Integrated provider conversation | Maintained overview |
|---|---|
| [fpocket #69](https://github.com/uibcdf/topomt/discussions/69) | [Overview](fpocket4/overview.md) |
| [Pocketeer #70](https://github.com/uibcdf/topomt/discussions/70) | [Overview](pocketeer/overview.md) |
| [AlphaSpace2 #71](https://github.com/uibcdf/topomt/discussions/71) | [Overview](alphaspace2/overview.md) |
| [pyCASTA #72](https://github.com/uibcdf/topomt/discussions/72) | [Overview](pycasta/overview.md) |
| [CASTp / CASTpFold #73](https://github.com/uibcdf/topomt/discussions/73) | [Overview](castp/overview.md) |
| [pyKVFinder #107](https://github.com/uibcdf/topomt/discussions/107) | [Overview](pykvfinder/overview.md) |
| [GHECOM #109](https://github.com/uibcdf/topomt/discussions/109) | [Overview](ghecom/overview.md) |
| [CAVER #104](https://github.com/uibcdf/topomt/discussions/104) | [Overview](caver/overview.md) |
| [P2Rank #108](https://github.com/uibcdf/topomt/discussions/108) | [Overview](p2rank/overview.md) |

## Ownership and current scope

The maintainer accepted [the expansion plan](external_provider_expansion_plan.md)
on 2026-11-07 under [#135](https://github.com/uibcdf/topomt/issues/135), before
further BenchLab work: pyKVFinder #136, GHECOM #137, CAVER 3.02 CLI #138 and
P2Rank 2.5.1 #139. This is an implementation batch, not an execution certificate.
Eligibility is currently restricted to no-payment routes: locally installable
open source or no-cost services with reviewed terms and automation/disclosure
conditions. Distinguish editions, academic-only permissions and unknown licences.
Paid routes are excluded for now; unreviewed leads remain in the catalogue.

This catalogue and the linked provider overviews are permanent, versioned
navigation records outside the defect/proposal queues. Discussions host resource
descriptions, discovery, reviews, evidence and scientific conversations; their
opening posts also link relevant technical records. Independently closable
bugs, capabilities and validation phases keep their own issues and reports under
the [reporting protocol](reporting_protocol.md).

Original-provider delivery and its viewer consumer are initially implemented.
Exhaustive fidelity and local-method certification remain incomplete. The
historical [implementation pause](provider_pocket_output_checkpoint.md) does not
override later decisions: use [current status](status.md) and the resumed
[synthetic-first DFND checkpoint](DFND/notebook_laboratory_checkpoint.md) for
scheduling. Catalogue membership is not authorization to integrate a candidate.
DFND defines Topography's native semantic direction. External geometry and labels
retain their provenance until separately admitted under that contract.

## Integrated providers

Providers are both optional integrations and comparison references. Availability of
a package or service, original-adapter fidelity, local reproduction and canonical
Topography admission are separate statuses.
The table and dated native receipt below retain their original review scope;
later provider evidence is linked from the current status and individual records.

Shared availability and diagnostics follow the
[MolSysSuite optional-engine contract](https://github.com/uibcdf/molsyssuite/blob/main/devguide/optional_engine_integration.md).
TopoMT's adoption evidence lives in [the ecosystem review](pending_proposals/review_python_ecosystem_policy_adoption.md)
under [#56](https://github.com/uibcdf/topomt/issues/56). The current package
requires DepDigest >=0.12.0; an older editable checkout is not an installed
verification target for the new executable boundary.

| Provider overview | Original routes and result | Original/runtime evidence | Local reproduction |
|---|---|---|---|
| [fpocket](fpocket4/overview.md) | CLI/files; `FpocketOutput` | CLI 4.2.3 and retained fixtures audited on bounded inputs | Historical pinned-build final-pocket parity; explicit `fpocket-topomt` variant |
| [Pocketeer](pocketeer/overview.md) | Python library; `PocketeerOutput` | Installed 0.4.0 plus source fixtures | Selected test passes, but allows extra pockets and large numeric differences |
| [AlphaSpace2](alphaspace2/overview.md) | Python library and captured files; `AlphaSpace2Output` | Installed 0.1.2, including selected receptor/reference contacts | Selected geometry/contact/typed-score tests pass; broader semantics remain |
| [pyCASTA](pycasta/overview.md) | Python library/scripts; `PyCASTAOutput` | Installed 1.0.8; separate original-score correction #35 closed | Native `1a6w` regression [#53](https://github.com/uibcdf/topomt/issues/53) remains open |
| [CASTp / CASTpFold](castp/overview.md) | Servers/files; `CASTpOutput` | Archives and mocked transports; current live availability unverified | Historical CASTp1 closure; experimental CASTp3-like route |
| [pyKVFinder](pykvfinder/overview.md) | Library/files; `PyKVFinderOutput`, cavity grids | Explicit compatibility source 0.9.6+uibcdf.2, NumPy 2.5.4; 266 unit cases and a 12-cavity direct-original/recovery pilot | No native reproduction |
| [GHECOM](ghecom/overview.md) | CLI/files; `GhecomOutput`, P-mode grid pockets | Original 2026/08/17 source pilot: 41 clusters on one retained input | No native reproduction |
| [CAVER](caver/overview.md) | CLI/files; `CaverOutput`, ordered tunnel paths | Original 3.02 + Java 21 source pilot: 47 profiles on one retained input | No native reproduction |
| [P2Rank](p2rank/overview.md) | CLI/files; `P2RankOutput`, predicted sites | Original 2.5.1 + Java 21 source pilot: 5 sites on one retained input | No native reproduction |

The [new-adapter checkpoint](original_provider_expansion_checkpoint.md) records
exact inputs, archives, limits and engine-free recovery. These source pilots do
not qualify public packages or establish scientific agreement between methods.

Installation and user API requirements remain in the
[user guide](../docs/content/user/third_party_engines.md).
[#19](https://github.com/uibcdf/topomt/issues/19) owns exhaustive original
field/route fidelity; descriptor issues #20–#52 are independently closable work.
[#65](https://github.com/uibcdf/topomt/issues/65) and
[#66](https://github.com/uibcdf/topomt/issues/66) record the initial output and
viewer outcomes. Their closure does not close every provider's validation.

Native evidence dated 2026-09-30: the selected Pocketeer, AlphaSpace2 and pyCASTA
parity modules yielded 25 passes and one failure (#53) in 169.95 seconds, on
TopoMT commit `5f2c0f43c8b0ec4b231641e0df58d1474f651785`, Linux/Python 3.13.14.
Those tests use local upstream mirrors, not a universal distribution matrix.
The fpocket and CASTp historical parity batteries were not rerun in that audit.

## Researched candidates and comparison tools

The official sources below were reviewed on 2026-09-30. These are scientific
scope and integration-route assessments, not installation tests or live-service
certificates. Priority is advisory; no new integration is approved by this table.
A comparison reference can also become an optional provider.

| Tool and official source | Capability / relationship | Route to assess | Priority / rationale |
|---|---|---|---|
| [MOLE / MOLEonline](https://moleonline.cz/) | Channel/tunnel/pore candidate and close DFND antecedent | [Engine](https://github.com/sb-ncbr/MOLE), [Webchemistry](https://github.com/sb-ncbr/webchemistry), [web interface](https://github.com/sb-ncbr/moleonline-web); no runtime integration | High: [2026-11-07 source/method review](DFND/mole_comparison_2026_11_07.md) distinguishes operators and bounds originality claims; executable comparison remains pending |
| [PISA](https://github.com/PDBe-KB/pisa) | Interface candidate and comparison | CLI/XML, including `--as-is` assembly-interface analysis | High: supplied-assembly interfaces without assembly prediction |
| [DoGSite3](https://proteins.plus/help/dogsite3_rest) | Pocket/subpocket and descriptor candidate | Documented REST API and retained results | Medium: remote alternative with volumetric output |
| [HOLE](https://www.holeprogram.org/) | Ion-channel pore dimension comparison | Executable/results | Specialized: pore profiles |
| [CHAP](https://github.com/channotation/chap) | Ion-channel structural/functional annotation | Executable/results; trajectory-dependent analyses separately | Specialized: distinguish geometry from hydrophobic/water inference |

Preserve each method's scientific definitions: channel centerlines, grid regions,
surface scores and buried interface areas are different evidence. A predicted
site, an inferred biological assembly or a score does not automatically define a
DFND feature or binding claim. Use provider-specific contracts before shared
consumer access; do not force every output into a pocket-only schema.

## Historical research intake retained from #8

Every distinct reference from the inspected issue comments is retained below
or in the integrated-provider table. Duplicate fpocketR and Pocket-to-Concavity
comments remain in #8's history; POVME 2/3 share a project-family entry here.
These links were imported on 2026-10-01. Their technical scope, release state,
licence and runtime availability have not been newly audited.

| Reference | Current relationship / next review |
|---|---|
| [fpocketR](https://github.com/Weeks-UNC/fpocketR) | RNA-oriented integration reference from #8; assess input/output differences |
| [Scipion fpocket integration](https://github.com/scipion-chem/scipion-chem-fpocket) | Integration example, not an independent detector oracle |
| [Pocket-to-Concavity / P2C](https://github.com/genki-kudo/Pocket-to-Concavity) | fpocket-related analysis reference; assess its added semantics |
| [pfnet-research/pocket_detection](https://github.com/pfnet-research/pocket_detection) | Unassessed candidate |
| [MolModa](https://durrantlab.pitt.edu/molmoda/) | Application/integration example from #8 |
| [PePrMint](https://github.com/reuter-group/peprmint-web) | Unassessed surface/interface-related reference |
| [POVME 3](https://github.com/POVME/POVME3) / [POVME 2](https://durrantlab.pitt.edu/povme2/) | Pocket shape/volume/flexibility comparison; review region-input requirements |
| [AlphaTraj](https://github.com/dooo12332/AlphaTraj) | Unassessed candidate/reference |
| [Pocket2Mol](https://github.com/pengxingang/pocket2mol) | Related project; assess domain ownership before proposing integration |
| [PPD](https://github.com/rdzhao/PPD) | Unassessed candidate/reference |
| [LIGSITE in ENSPARA](https://github.com/bowman-lab/enspara/blob/master/docs/source/pocket-detection.rst) | Detection/comparison reference |
| [CASTpFold source reference](https://github.com/BoweiYe1/CastpFold) / [castp-Script](https://github.com/athulvis/castp-Script) | Auxiliary CASTp references; not guaranteed server internals |
| [PocketSCP](https://pubs.acs.org/doi/10.1021/acs.jcim.5c00728) | Literature intake; implementation and scope to assess |
| [SurfDock](https://github.com/CAODH/SurfDock) | Related project; assess domain ownership before proposing integration |

The existing [POVME 2 discussion](https://github.com/uibcdf/topomt/discussions/10),
[POVME 3 discussion](https://github.com/uibcdf/topomt/discussions/11),
[cryptic-pocket reading](https://github.com/uibcdf/topomt/discussions/12) and
[SARS-CoV-2 reading](https://github.com/uibcdf/topomt/discussions/13) remain in
Literature and Resources. The POVME tool-family conversation is linked from
the [resource register](discussion_resources.md); the two primary-paper threads
retain their distinct reading histories. Literature discussion is not evidence
that a provider is integrated.

## New research intake — 2026-11-07

These additional families expand the discovery catalogue, not the current
implementation batch. Only the official repository/README and licence identity
were reviewed; no local installation or original execution is claimed.
Use the catalogue conversation #68 for initial intake until a dedicated resource
review is opened, then add its canonical thread to the resource register.

| Lead | Official access source | Scientific question and next gate |
| --- | --- | --- |
| [MoloVol](https://github.com/molovol/MoloVol) | MIT; [original method paper](https://journals.iucr.org/j/issues/2022/04/00/yr5079/yr5079.pdf) | Volumes/surfaces of molecules and unit cells; useful probe-center versus probe-occupied volume definitions for synthetic systems. Review exact CLI, radii, region definitions and selected version before admission. |
| [PyVOL](https://github.com/schlessinger-lab/pyvol) | MIT wrapper/library; official README documents an MSMS executable dependency | Pocket/subpocket segmentation and surface/volume representations. Review the entire MSMS acquisition/licence chain and current Python compatibility before deciding whether a no-payment route meets our scope. The wrapper licence alone does not admit its backend. |

## Maintenance rule

- Maintain one catalogue row per project family and one overview per integrated
  provider. Tag capabilities and relationships separately: integrated provider,
  candidate, comparison reference or related project; more than one may apply.
- Record official sources, installation prerequisites, reviewed version/revision,
  review date and evidence scope. Unknown licence/version/availability stays
  unknown until checked; an imported link is not a technical audit.
- Refresh the affected overview when its route, requirements, evidence or issue
  state changes. Keep field matrices and measurements in existing linked records.
- Store pending bugs and proposals under their owning issues/reports. A bounded
  provider validation phase may have an umbrella issue; the permanent overview
  and discussion do not close when that phase finishes.
- Reopen a closed defect for demonstrated recurrence of the same defect. New
  requirements get new issues. Preserve resolved records in the archive.
- Review manually when upstream releases, service failures, scientific findings
  or integration work supply a reason. No scheduled monitoring is implemented
  or claimed by this catalogue.
- Follow [Discussions maintenance](discussions.md) for resource intake, category
  choice, labels and follow-up. Keep substantive reviews and conclusions in the
  conversation, linking technical studies and owning issues for actionable work.
