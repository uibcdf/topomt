# DFND Qualitative Domain Snapshot

This report is a qualitative engineering snapshot. It is not a CASTp/fpocket parity report and it does not claim biological correctness.

Probe radius: `1.40 Å`
Selection: `molecule_type in ['protein', 'peptide']`

## System Summary

| system | build_s | query_s | tetra | domains | external_links | dry_components | dry_interfaces | families |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 1crn | 4.87 | 0.15 | 1982 | 4 | 3 | 1 | 276 | pocket_domain:3, void_domain:1 |
| 1rop | 1.82 | 0.17 | 2828 | 1 | 1 | 1 | 506 | pocket_domain:1 |
| 2pk4 | 2.50 | 0.72 | 4008 | 11 | 4 | 1 | 558 | pocket_domain:4, void_domain:7 |
| 2lyz | 4.03 | 1.04 | 6466 | 11 | 1 | 4 | 950 | pocket_domain:1, void_domain:10 |
| 3ptb | 6.81 | 2.91 | 10601 | 30 | 4 | 2 | 1410 | pocket_domain:3, surface_concavity_domain:1, void_domain:26 |

## Largest Resident Domains

### 1crn

| rank | domain_id | family | nodes | resident | connectors | external_links | atoms | volume_solvent_estimate | path_capacity_min | flags |
| ---: | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| 1 | 1 | pocket_domain | 241 | 235 | 6 | 1 | 131 | 1334.415 | 0.001 | contains_transit_connector |
| 2 | 4 | void_domain | 3 | 3 | 0 | 0 | 6 | 28.238 | 0.108 | - |
| 3 | 3 | pocket_domain | 1 | 1 | 0 | 1 | 4 | 1.079 | - | - |
| 4 | 2 | pocket_domain | 1 | 1 | 0 | 1 | 4 | 0.431 | - | - |

### 1rop

| rank | domain_id | family | nodes | resident | connectors | external_links | atoms | volume_solvent_estimate | path_capacity_min | flags |
| ---: | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| 1 | 1 | pocket_domain | 505 | 497 | 8 | 1 | 233 | 3419.159 | 0.003 | contains_transit_connector |

### 2pk4

| rank | domain_id | family | nodes | resident | connectors | external_links | atoms | volume_solvent_estimate | path_capacity_min | flags |
| ---: | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| 1 | 1 | pocket_domain | 511 | 500 | 11 | 1 | 244 | 3227.141 | 0.003 | contains_transit_connector |
| 2 | 6 | void_domain | 4 | 4 | 0 | 0 | 7 | 21.350 | 0.051 | - |
| 3 | 10 | void_domain | 3 | 3 | 0 | 0 | 6 | 16.332 | 0.108 | - |
| 4 | 7 | void_domain | 3 | 3 | 0 | 0 | 6 | 12.200 | 0.012 | - |
| 5 | 5 | void_domain | 2 | 2 | 0 | 0 | 5 | 12.189 | 0.096 | - |

### 2lyz

| rank | domain_id | family | nodes | resident | connectors | external_links | atoms | volume_solvent_estimate | path_capacity_min | flags |
| ---: | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| 1 | 1 | pocket_domain | 864 | 844 | 20 | 1 | 409 | 5923.174 | 0.006 | contains_transit_connector |
| 2 | 4 | void_domain | 14 | 14 | 0 | 0 | 13 | 102.649 | 0.141 | - |
| 3 | 5 | void_domain | 8 | 8 | 0 | 0 | 9 | 56.329 | 0.097 | - |
| 4 | 3 | void_domain | 4 | 4 | 0 | 0 | 7 | 27.489 | 0.049 | - |
| 5 | 7 | void_domain | 5 | 5 | 0 | 0 | 8 | 27.207 | 0.022 | - |

### 3ptb

| rank | domain_id | family | nodes | resident | connectors | external_links | atoms | volume_solvent_estimate | path_capacity_min | flags |
| ---: | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| 1 | 1 | pocket_domain | 1175 | 1159 | 16 | 1 | 565 | 9145.440 | 0.001 | contains_transit_connector |
| 2 | 7 | void_domain | 23 | 23 | 0 | 0 | 19 | 160.886 | 0.023 | - |
| 3 | 6 | void_domain | 18 | 18 | 0 | 0 | 17 | 113.020 | 0.014 | - |
| 4 | 3 | void_domain | 14 | 14 | 0 | 0 | 15 | 92.928 | 0.036 | - |
| 5 | 5 | void_domain | 8 | 8 | 0 | 0 | 10 | 52.138 | 0.081 | - |

## Reading Notes

- The table is sorted by resident solvent-volume estimate, then resident nodes, then total nodes.
- Large numbers of small voids are expected at this stage and should be evaluated later with reporting filters, not by changing the core decomposition.
- `multi_external_link_domain` is still a topological multi-link label; biological channel/tunnel interpretation remains a later morphology step.
