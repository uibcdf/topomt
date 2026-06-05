# DFND vs CASTp Oracle Validation Inventory

This checkpoint compares the current DFND native decomposition against local CASTp-family oracle files. It is an inventory for choosing inspection order; it is not yet a claim of parity.

Naming convention from this point forward: CASTp means CASTp3.0 unless explicitly stated otherwise. CASTp1 names the legacy compiled/reference line. CASTpFold is treated as equivalent to CASTp for systems where both oracles agree, and as fallback oracle when CASTp3.0 files are not locally available.

Inspection route for the next validation stage: 1crn, 1rop, then 2pk4, 1stp, and only then the remaining systems.

Probe radius: 1.40 A
Selection: molecule_type in ['protein', 'peptide']
Hydrogen policy: exclude
DFND radii model: vdw

## DFND System Summary

| system | source | atoms | tetra | domains | external_links | largest_resident_volume | families | pdb_input |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- | --- |
| 1crn | CASTpFold | 327 | 1982 | 4 | 3 | 1334.415 | pocket_domain:3, void_domain:1 | topomt/data/CASTpFold_server/1crn.zip |
| 1rop | CASTpFold | 447 | 2828 | 1 | 1 | 3419.159 | pocket_domain:1 | topomt/data/CASTpFold_server/1rop.zip |
| 2lyz | CASTpFold | 1001 | 6466 | 11 | 1 | 5923.174 | pocket_domain:1, void_domain:10 | topomt/data/CASTpFold_server/2lyz.zip |
| 2pk4 | CASTp3.0 | 630 | 4008 | 11 | 4 | 3227.141 | pocket_domain:4, void_domain:7 | topomt/data/CASTp_3.0_server/2pk4.zip |
| 2pk4 | CASTpFold | 630 | 4008 | 11 | 4 | 3227.141 | pocket_domain:4, void_domain:7 | topomt/data/CASTpFold_server/2pk4.zip |
| 3ptb | CASTp3.0 | 1629 | 10601 | 30 | 4 | 9145.440 | pocket_domain:3, surface_concavity_domain:1, void_domain:26 | topomt/data/CASTp_3.0_server/3ptb.zip |
| 3ptb | CASTpFold | 1629 | 10601 | 30 | 4 | 9145.440 | pocket_domain:3, surface_concavity_domain:1, void_domain:26 | topomt/data/CASTpFold_server/3ptb.zip |
| 1stp | CASTp3.0 | 901 | 5718 | 9 | 4 | 9872.556 | pocket_domain:4, void_domain:5 | topomt/data/CASTp_3.0_server/1stp.zip |
| 1stp | CASTpFold | 901 | 5718 | 9 | 4 | 9872.556 | pocket_domain:4, void_domain:5 | topomt/data/CASTpFold_server/1stp.zip |
| 1a4j | CASTp3.0 | 6626 | 43859 | 63 | 3 | 160430.418 | pocket_domain:3, void_domain:60 | topomt/data/CASTp_3.0_server/1a4j.zip |
| 1a4j | CASTpFold | 6626 | 43859 | 63 | 3 | 160430.418 | pocket_domain:3, void_domain:60 | topomt/data/CASTpFold_server/1a4j.zip |
| 1hiv | CASTp1 | 1516 | 9810 | 24 | 7 | 10347.880 | pocket_domain:7, void_domain:17 | topomt/data/HIV-1-Protease/CASTp_1hiv/1hiv.pdb |
| 1hiv | CASTp3.0 | 1516 | 9810 | 24 | 7 | 10347.880 | pocket_domain:7, void_domain:17 | topomt/data/CASTp_3.0_server/1hiv.zip |
| 1hiv | CASTpFold | 1516 | 9810 | 24 | 7 | 10347.880 | pocket_domain:7, void_domain:17 | topomt/data/CASTpFold_server/1hiv.zip |
| 1tcd | CASTp1 | 3818 | 25155 | 69 | 4 | 37736.654 | pocket_domain:4, void_domain:65 | topomt/data/TcTIM/CASTp_1tcd/1tcd.pdb |
| 1tcd | CASTp3.0 | 3818 | 25155 | 69 | 4 | 37736.654 | pocket_domain:4, void_domain:65 | topomt/data/CASTp_3.0_server/1tcd.zip |
| 1tcd | CASTpFold | 3818 | 25155 | 69 | 4 | 37736.654 | pocket_domain:4, void_domain:65 | topomt/data/CASTpFold_server/1tcd.zip |

## Oracle Comparison

| system | oracle | feature | oracle_count | dfnd_count | exact_atom_set_matches | oracle_only | dfnd_only |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| 1crn | CASTpFold | pocket | 0 | 3 | 0 | 0 | 3 |
| 1crn | CASTpFold | void | 1 | 1 | 0 | 1 | 1 |
| 1crn | CASTpFold | channel | 0 | 0 | 0 | 0 | 0 |
| 1crn | CASTpFold | mouth | 0 | 3 | 0 | 0 | 3 |
| 1rop | CASTpFold | pocket | 3 | 1 | 0 | 3 | 1 |
| 1rop | CASTpFold | void | 0 | 0 | 0 | 0 | 0 |
| 1rop | CASTpFold | channel | 0 | 0 | 0 | 0 | 0 |
| 1rop | CASTpFold | mouth | 3 | 1 | 0 | 3 | 1 |
| 2lyz | CASTpFold | pocket | 6 | 1 | 0 | 6 | 1 |
| 2lyz | CASTpFold | void | 6 | 10 | 0 | 6 | 10 |
| 2lyz | CASTpFold | channel | 0 | 0 | 0 | 0 | 0 |
| 2lyz | CASTpFold | mouth | 6 | 1 | 0 | 6 | 1 |
| 2pk4 | CASTp3.0 | pocket | 3 | 4 | 0 | 3 | 4 |
| 2pk4 | CASTp3.0 | void | 4 | 7 | 0 | 4 | 7 |
| 2pk4 | CASTp3.0 | channel | 0 | 0 | 0 | 0 | 0 |
| 2pk4 | CASTp3.0 | mouth | 3 | 4 | 0 | 3 | 4 |
| 2pk4 | CASTpFold | pocket | 3 | 4 | 0 | 3 | 4 |
| 2pk4 | CASTpFold | void | 4 | 7 | 0 | 4 | 7 |
| 2pk4 | CASTpFold | channel | 0 | 0 | 0 | 0 | 0 |
| 2pk4 | CASTpFold | mouth | 3 | 4 | 0 | 3 | 4 |
| 3ptb | CASTp3.0 | pocket | 12 | 3 | 0 | 12 | 3 |
| 3ptb | CASTp3.0 | void | 14 | 26 | 1 | 13 | 25 |
| 3ptb | CASTp3.0 | channel | 1 | 0 | 0 | 1 | 0 |
| 3ptb | CASTp3.0 | mouth | 13 | 3 | 0 | 13 | 3 |
| 3ptb | CASTpFold | pocket | 12 | 3 | 0 | 12 | 3 |
| 3ptb | CASTpFold | void | 14 | 26 | 1 | 13 | 25 |
| 3ptb | CASTpFold | channel | 1 | 0 | 0 | 1 | 0 |
| 3ptb | CASTpFold | mouth | 13 | 3 | 0 | 13 | 3 |
| 1stp | CASTp3.0 | pocket | 5 | 4 | 0 | 5 | 4 |
| 1stp | CASTp3.0 | void | 3 | 5 | 1 | 2 | 4 |
| 1stp | CASTp3.0 | channel | 1 | 0 | 0 | 1 | 0 |
| 1stp | CASTp3.0 | mouth | 6 | 4 | 0 | 6 | 4 |
| 1stp | CASTpFold | pocket | 5 | 4 | 0 | 5 | 4 |
| 1stp | CASTpFold | void | 3 | 5 | 1 | 2 | 4 |
| 1stp | CASTpFold | channel | 1 | 0 | 0 | 1 | 0 |
| 1stp | CASTpFold | mouth | 6 | 4 | 0 | 6 | 4 |
| 1a4j | CASTp3.0 | pocket | 55 | 3 | 0 | 55 | 3 |
| 1a4j | CASTp3.0 | void | 39 | 60 | 2 | 37 | 58 |
| 1a4j | CASTp3.0 | channel | 7 | 0 | 0 | 7 | 0 |
| 1a4j | CASTp3.0 | mouth | 62 | 3 | 0 | 62 | 3 |
| 1a4j | CASTpFold | pocket | 55 | 3 | 0 | 55 | 3 |
| 1a4j | CASTpFold | void | 39 | 60 | 2 | 37 | 58 |
| 1a4j | CASTpFold | channel | 7 | 0 | 0 | 7 | 0 |
| 1a4j | CASTpFold | mouth | 62 | 3 | 0 | 62 | 3 |
| 1hiv | CASTp1 | pocket | 13 | 7 | 0 | 13 | 7 |
| 1hiv | CASTp1 | void | 3 | 17 | 0 | 3 | 17 |
| 1hiv | CASTp1 | channel | 1 | 0 | 0 | 1 | 0 |
| 1hiv | CASTp1 | mouth | 14 | 7 | 0 | 14 | 7 |
| 1hiv | CASTp3.0 | pocket | 13 | 7 | 0 | 13 | 7 |
| 1hiv | CASTp3.0 | void | 3 | 17 | 0 | 3 | 17 |
| 1hiv | CASTp3.0 | channel | 1 | 0 | 0 | 1 | 0 |
| 1hiv | CASTp3.0 | mouth | 14 | 7 | 0 | 14 | 7 |
| 1hiv | CASTpFold | pocket | 13 | 7 | 0 | 13 | 7 |
| 1hiv | CASTpFold | void | 3 | 17 | 0 | 3 | 17 |
| 1hiv | CASTpFold | channel | 1 | 0 | 0 | 1 | 0 |
| 1hiv | CASTpFold | mouth | 14 | 7 | 0 | 14 | 7 |
| 1tcd | CASTp1 | pocket | 34 | 4 | 0 | 34 | 4 |
| 1tcd | CASTp1 | void | 36 | 65 | 4 | 32 | 61 |
| 1tcd | CASTp1 | channel | 8 | 0 | 0 | 8 | 0 |
| 1tcd | CASTp1 | mouth | 42 | 4 | 0 | 42 | 4 |
| 1tcd | CASTp3.0 | pocket | 34 | 4 | 0 | 34 | 4 |
| 1tcd | CASTp3.0 | void | 36 | 65 | 4 | 32 | 61 |
| 1tcd | CASTp3.0 | channel | 8 | 0 | 0 | 8 | 0 |
| 1tcd | CASTp3.0 | mouth | 42 | 4 | 0 | 42 | 4 |
| 1tcd | CASTpFold | pocket | 34 | 4 | 0 | 34 | 4 |
| 1tcd | CASTpFold | void | 36 | 65 | 4 | 32 | 61 |
| 1tcd | CASTpFold | channel | 8 | 0 | 0 | 8 | 0 |
| 1tcd | CASTpFold | mouth | 42 | 4 | 0 | 42 | 4 |

## Suggested Inspection Order

| rank | system | rationale |
| ---: | --- | --- |
| 1 | 1crn:CASTpFold | CASTpFold; non-mouth count gap 3; unmatched oracle atom sets 1 |
| 2 | 1rop:CASTpFold | CASTpFold; non-mouth count gap 2; unmatched oracle atom sets 3 |
| 3 | 2pk4:CASTp3.0 | CASTp3.0; non-mouth count gap 4; unmatched oracle atom sets 7 |
| 4 | 2pk4:CASTpFold | CASTpFold; non-mouth count gap 4; unmatched oracle atom sets 7 |
| 5 | 1stp:CASTp3.0 | CASTp3.0; non-mouth count gap 4; unmatched oracle atom sets 8 |
| 6 | 1stp:CASTpFold | CASTpFold; non-mouth count gap 4; unmatched oracle atom sets 8 |
| 7 | 2lyz:CASTpFold | CASTpFold; non-mouth count gap 9; unmatched oracle atom sets 12 |
| 8 | 1hiv:CASTp3.0 | CASTp3.0; non-mouth count gap 21; unmatched oracle atom sets 17 |
| 9 | 1hiv:CASTp1 | CASTp1; non-mouth count gap 21; unmatched oracle atom sets 17 |
| 10 | 1hiv:CASTpFold | CASTpFold; non-mouth count gap 21; unmatched oracle atom sets 17 |
| 11 | 3ptb:CASTp3.0 | CASTp3.0; non-mouth count gap 22; unmatched oracle atom sets 26 |
| 12 | 3ptb:CASTpFold | CASTpFold; non-mouth count gap 22; unmatched oracle atom sets 26 |
| 13 | 1tcd:CASTp3.0 | CASTp3.0; non-mouth count gap 67; unmatched oracle atom sets 74 |
| 14 | 1tcd:CASTp1 | CASTp1; non-mouth count gap 67; unmatched oracle atom sets 74 |
| 15 | 1tcd:CASTpFold | CASTpFold; non-mouth count gap 67; unmatched oracle atom sets 74 |
| 16 | 1a4j:CASTp3.0 | CASTp3.0; non-mouth count gap 80; unmatched oracle atom sets 99 |
| 17 | 1a4j:CASTpFold | CASTpFold; non-mouth count gap 80; unmatched oracle atom sets 99 |

## CASTp3.0 vs CASTpFold Input Equivalence Check

| system | PDB byte-identical in ZIPs | note |
| --- | --- | --- |
| 2pk4 | True | Same PDB payload. |
| 3ptb | True | Same PDB payload. |
| 1stp | True | Same PDB payload. |
| 1a4j | False | PDB payload length differs, but DFND summary is identical at this level. |
| 1hiv | True | Same PDB payload. |
| 1tcd | False | PDB payload length differs, but DFND summary is identical at this level. |

## Reading Notes

- CASTp1, CASTp3.0, and CASTpFold are kept as distinct oracle sources; CASTp3.0 and CASTpFold are not collapsed even when their files agree.
- channel in this report merges CASTp channel and branched_channel because DFND currently exposes channel_domain as the topological channel-compatible family.
- Exact matches compare full feature atom sets using PDB serial numbers. Count agreement without exact matches means the feature inventory is numerically similar but not atom-identical.
- Mouth comparison is provisional because DFND external links are graph-derived geometric apertures, not CASTp alpha-shape mouth triangles.
- This report is intended to select cases for fine inspection before algorithmic changes.
