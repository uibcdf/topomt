# PISA availability and licence review — 2026-11-11

Owning integration: uibcdf/topomt#194; assessment #165. The maintainer requested
an extended source/web/history search before any external question. No external
issue has been authorized or published. Original PDBe source remains clean at
`6d6f7d09ea5bf0f3f8a1602dd56fa896e6aca401` in `~/repos@others/pisa`.

## Conclusion for this integration

PISA has documented local research use and a no-payment academic acquisition
route. PDBe's own protocol instructs researchers to clone and compile the
standalone engine for their structures; the repository also supplies an
official Docker route. CCP4 explicitly offers its suite free to academic
institutions. Therefore the absence of a root `LICENSE` is not sufficient to
conclude that PISA is unavailable, requires payment for academic use, or should
be rejected from this integration.

Two questions remain separate: the existence of that documented research-use
route, and a complete standalone grant for modification/redistribution of the
selected engine and runtime resources. This search establishes the former;
it has not recovered the latter. Keep PISA as a selected optional external
executable under #194, document the applicable acquisition route, and continue
adapter/result work without bundling the engine or its runtime data. Do not
label the engine Apache-2.0 by borrowing a wrapper's licence. Original execution
qualification and public delivery remain unfinished work, not consequences of
this documentary review.

## Findings and their exact scope

| Source | Observed evidence | Scope / limit |
| --- | --- | --- |
| [PDBe-KB/pisa](https://github.com/PDBe-KB/pisa/tree/6d6f7d09ea5bf0f3f8a1602dd56fa896e6aca401) | README documents standalone compilation and supplied-assembly `--as-is` analysis. PISA/pisalib headers contain copyright and the executable source requests the original article citation. | No repository-level licence or general redistribution/modification grant found in this source. Documented compilation/use is not an SPDX identification. |
| Full fetched PDBe Git history | 66 commits inspected using `git log --all --no-renames --name-only`; no LICENSE/LICENCE/COPYING/COPYRIGHT/conditions/notice paths, or licence-related commit messages found. | Filename/message review, not a claim to have inspected every historical file's contents or unpublished grants. Checkout scientific files remain unchanged. |
| [Original CCP4/PISA project](https://ccp4forge.rc-harwell.ac.uk/ccp4/pisa/-/tree/main) | Public GitLab API identifies project 14, branch main; metadata licence fields are null. Three recursive tree pages contain 221 entries with no licence/readme/notice-like path. | Official additional source, distinct from the PDBe fork; no explicit standalone licence was recovered there either. HTML browsing failed, but bounded direct API reads succeeded. |
| [PDBe PISA methods protocol](https://doi.org/10.1002/cpz1.70446), Basic Protocol 3 and Commentary | Explicitly teaches local analysis of novel/user structures by cloning and compiling `PDBe-KB/pisa`, or using `pdbegroup/pisa`. Identifies the selected implementation with the PISA distributed in CCP4 9.0. | Strong direct evidence of intended local research use. Its article licence is not a substitute for a software licence; wrapper and subprocess remain distinct. The protocol identifies analysis of specified assemblies, without assembly prediction. |
| [CCP4 commercial-users page](https://www.ccp4.ac.uk/ccp4-commercial-users/) | Explicitly states that the suite is free to academic institutions and commercial organizations should arrange a licence with CCP4. | No-payment academic availability is established. Do not generalize this to every commercial use or impose payment on the separate public-data route. |
| [CCP4 Academic Licence, July 2021](https://www.ccp4.ac.uk/licensing/CCP4_Academic_Software_Licence_UKRI_July_2021.pdf) | Distinguishes academic CCP4 Software, GNU software and third-party software. Academic-use applications are royalty-free under its agreement; application redistribution and permitted use have conditions. | Verifies an academic no-payment acquisition category, not unrestricted open-source licensing or this exact GitHub source's complete grant. A CCP4 installation/acceptance is a separate user/institution matter. |
| [CCP4 9.0.001 distribution conditions](https://ccp4forge.rc-harwell.ac.uk/ccp4/ccp4-base/-/raw/9.0.001/conditions.txt) | States separate commercial and nonprofit/noncommercial routes and requires acceptance/completion of the applicable agreement. The text still contains earlier-version references. | Confirms that no-payment and agreement-free are different. Do not claim that this checkout proves an institutional agreement has been completed, or treat old version wording as a new PISA-specific licence. |
| [CCP4 GNU list](https://www.ccp4.ac.uk/licensing/GPL_and_LGPL_software.html) | Lists CCP4/MMDB libraries as LGPLv3 and MMDB2 as GPLv3; directs users to exact source licences. PISA is not individually listed. | The PDBe checkout's inspected MMDB2/SSM/SRS headers instead state modified LGPLv3; preserve this exact-version distinction rather than assuming every bundled copy has the current general-list terms. |
| [pisa-analysis licence](https://github.com/PDBe-KB/pisa-analysis/blob/main/LICENSE) | Explicit Apache-2.0 for this Python wrapper. | Does not automatically license the original standalone subprocess or its runtime datasets. |
| [pdbe-pisa-json](https://github.com/PDBe-KB/pdbe-pisa-json#license) | Explicit Apache-2.0 for its code and CC-BY-4.0 for its data. | Establishes declared public-result/data reuse terms; not a grant for every PISA engine/resource file. |
| [PDBe/PDBe-KB paper](https://doi.org/10.1002/pro.4439) | Describes a policy of publishing the majority of data pipelines/visualization tools under Apache-2.0. | The stated majority/general policy does not identify this copyright-bearing engine as Apache-2.0. |
| [EMBL-EBI Terms of Use](https://www.ebi.ac.uk/about/terms-of-use/), revised 2026-10-14 | Describes freely available resources, attribution and resource-specific terms. Section “Usage of Data Resources and Tools”, item 6, distinguishes software run from EBI web pages from downloadable software, including third-party repository downloads, which has individual licence agreements. | The general website policy does not supply a blanket Apache or other downloadable-engine grant. Resource-specific terms take precedence. |
| [PISA service disclaimer](https://www.ebi.ac.uk/msd-srv/prot_int/pi_disclaimer.html), [FAQ](https://www.ebi.ac.uk/msd-srv/prot_int/pi_tips.html) and [CLI documentation](https://www.ccp4.ac.uk/html/pisa.html) | Describe service/model limitations, local operation, units and citation. No additional complete standalone licensing statement recovered from these pages. | Scientific documentation and attribution are useful for #194 but do not replace missing distribution terms. No structures were uploaded and no analysis was submitted during this review. |
| [CCP4 source/download documentation](https://www.ccp4.ac.uk/download/) | Supplies program source/build access and academic acquisition routes; original PISA documentation and recent PDBe methods paper identify its CCP4/PDBe relationship. | Availability, article licence and program licence remain distinct. The 10 GB full CCP4 source archive was not downloaded for this metadata question. |

The setup SRS/MolRef/PISA parameter and symmetry data in the selected PDBe
checkout still have no separately identified complete licence statement. The
inspected executable source's citation notice is retained; it does not identify
all modification/redistribution terms. No conclusion that use is prohibited,
paid for every user, or unrestricted open-source use is established by this
search.

## Current disposition and ownership

There is documented local research use, free academic acquisition through CCP4,
and an explicitly licensed public-results/data route. PISA remains selected for
an optional local adapter; this is not a proposal to replace it with the API.
The API serves precomputed structures and cannot replace analysis of a novel
supplied assembly. An installed external executable and an independent reader
can be integrated without publishing a copy of the engine or datasets.

The unresolved standalone engine/resource grant stays visible under assessment
#165, independently of the bounded adapter delivery #194. Broader
interface/PePrMint assessment also remains #165. Do not advertise the unresolved
standalone route as universally open source. Any execution/admission receipt
must identify its acquisition and terms; no installed/public qualification or
institutional licence acceptance is claimed here. Independent parser and adapter
development remains within #194's authorized scope.

The external question is optional and deferred after this extended review.
Revisit it under #165 if a precise standalone grant is needed for redistribution,
a fork, or an acquisition route that the documented terms do not establish.
No new external publication is authorized by the maintainer's search request.

## Reproduction and search limits

Inspect the selected clean source revision before repeating the review. Search
its README, Dockerfile, current program headers and bundled-library notices;
inspect fetched-history path names with rename detection disabled to avoid
fetching large precompiled-header blobs. For the official CCP4 project, inspect
`/api/v4/projects/14?license=true` and all three pages of
`/api/v4/projects/14/repository/tree?ref=main&recursive=true&per_page=100&page=N`.
The CCP4 review covers metadata and filenames, not every file's contents.
Searches of repository issues/commit messages and the primary web sources above
did not produce an additional engine-specific grant. A negative search result
does not establish that no grant exists elsewhere.

Raw bounded search receipts remain in `.cache/hole-povme-pisa/` as
`pisa-history-licence-scan.json`, `pisa-ccp4-project.json`,
`pisa-ccp4-licence-tree.json` and `pisa-official-http.json`. These include a
successful read of CCP4's official `conditions.txt`; old or guessed URLs that
returned 404 are not cited as affirmative licence evidence.

## Retained external question — deferred and unpublished

Destination: https://github.com/PDBe-KB/pisa/issues

Title: Clarify licensing of standalone PISA code and bundled runtime data

We are preparing an optional local PISA adapter for TopoMT, preserving the
original scientific code and using the supplied-assembly `--as-is` route. We
intend to link users to the original program, not redistribute its executable
or runtime data.

Your README and PDBe methods protocol document local compilation/research use,
and CCP4 documents academic acquisition without payment. Our remaining question
is the precise standalone licence, rather than whether local use is intended.
At source `6d6f7d09ea5bf0f3f8a1602dd56fa896e6aca401`, we could not identify a
repository-level LICENSE/COPYING file.
The inspected PISA/pisalib headers contain copyright notices, while the SSM,
MMDB2 and CCP4SRS headers refer to CCP4's modified LGPL v3. The setup directory
also contains SRS, MolRef and PISA parameter/symmetry data.

Could you identify the canonical licence/terms applying to (1) the standalone
PISA/pisalib program in this repository and (2) these bundled runtime datasets,
particularly modification/redistribution permissions? We have kept the Apache
licence of `pisa-analysis`, the CC-BY public data, and the library licences
separate rather than assuming that one covers every component. A canonical
file or link would help integrators preserve those distinctions. Thank you.

## Publication boundary

The common MolSysSuite guide requires prior explicit maintainer permission for
issues outside UIBCDF. This text remains internal. The maintainer requested the
extended search above rather than authorizing publication; do not publish or
treat that response as consent.
Continue HOLE/POVME and interface/parser contracts meanwhile. Do not advertise
unknown standalone licensing as established open-source eligibility or publish
bundled engine/data copies through this adapter.
