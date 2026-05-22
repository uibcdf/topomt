# DFND Probe-Radius Sweep

This is an engineering-coherence report, not a cavity-detection quality validation.

Selection: `molecule_type in ['protein', 'peptide']`

## Monotonicity Checks

| system | resident non-increasing | permeable faces non-increasing | resident solvent volume non-increasing |
| --- | --- | --- | --- |
| 1crn | True | True | True |
| 1rop | True | True | True |
| 2lyz | True | True | True |
| 2pk4 | True | True | True |
| 3ptb | True | True | True |

## Sweep Table

| system | probe | build_s | query_s | tetra | resident | connectors | terminal | permeable_faces | domains | external_links | dry_components | dry_interfaces | families | volume_solvent_estimate |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | ---: |
| 1crn | 0.80 | 5.01 | 0.28 | 1982 | 541 | 13 | 151 | 1827 | 14 | 2 | 1 | 606 | pocket_domain:2, void_domain:12 | 1998.721 |
| 1crn | 1.00 | 5.01 | 0.24 | 1982 | 383 | 7 | 136 | 1353 | 9 | 4 | 1 | 450 | pocket_domain:4, void_domain:5 | 1733.372 |
| 1crn | 1.20 | 5.01 | 0.20 | 1982 | 297 | 1 | 120 | 1072 | 6 | 3 | 1 | 340 | pocket_domain:3, void_domain:3 | 1509.994 |
| 1crn | 1.40 | 5.01 | 0.17 | 1982 | 240 | 6 | 98 | 889 | 4 | 3 | 1 | 276 | pocket_domain:3, void_domain:1 | 1364.163 |
| 1crn | 1.80 | 5.01 | 0.39 | 1982 | 160 | 8 | 83 | 623 | 2 | 2 | 1 | 222 | pocket_domain:2 | 1129.975 |
| 1crn | 2.20 | 5.01 | 0.19 | 1982 | 114 | 10 | 57 | 436 | 6 | 6 | 1 | 188 | pocket_domain:6 | 913.692 |
| 1rop | 0.80 | 2.05 | 0.26 | 2828 | 1015 | 11 | 184 | 3426 | 6 | 1 | 5 | 906 | pocket_domain:1, void_domain:5 | 4407.904 |
| 1rop | 1.00 | 2.05 | 0.32 | 2828 | 789 | 8 | 196 | 2726 | 8 | 1 | 2 | 774 | pocket_domain:1, void_domain:7 | 4064.419 |
| 1rop | 1.20 | 2.05 | 0.55 | 2828 | 617 | 15 | 162 | 2176 | 7 | 2 | 2 | 632 | pocket_domain:2, void_domain:5 | 3718.724 |
| 1rop | 1.40 | 2.05 | 0.19 | 2828 | 497 | 8 | 148 | 1769 | 1 | 1 | 1 | 506 | pocket_domain:1 | 3419.159 |
| 1rop | 1.80 | 2.05 | 0.28 | 2828 | 343 | 10 | 120 | 1254 | 6 | 5 | 1 | 382 | pocket_domain:5, void_domain:1 | 2910.298 |
| 1rop | 2.20 | 2.05 | 0.26 | 2828 | 261 | 7 | 109 | 967 | 5 | 5 | 2 | 310 | pocket_domain:5 | 2554.299 |
| 2pk4 | 0.80 | 3.03 | 1.06 | 4008 | 1207 | 13 | 279 | 3973 | 34 | 3 | 4 | 1268 | pocket_domain:3, void_domain:31 | 4710.797 |
| 2pk4 | 1.00 | 3.03 | 0.68 | 4008 | 845 | 14 | 226 | 2888 | 18 | 2 | 1 | 888 | pocket_domain:2, void_domain:16 | 4109.608 |
| 2pk4 | 1.20 | 3.03 | 0.74 | 4008 | 646 | 11 | 190 | 2256 | 10 | 3 | 1 | 688 | pocket_domain:3, void_domain:7 | 3653.947 |
| 2pk4 | 1.40 | 3.03 | 0.51 | 4008 | 519 | 13 | 159 | 1836 | 11 | 4 | 1 | 558 | pocket_domain:4, void_domain:7 | 3320.404 |
| 2pk4 | 1.80 | 3.03 | 0.68 | 4008 | 397 | 14 | 128 | 1415 | 6 | 6 | 2 | 458 | pocket_domain:6 | 2857.595 |
| 2pk4 | 2.20 | 3.03 | 0.50 | 4008 | 294 | 14 | 115 | 1098 | 5 | 5 | 2 | 358 | pocket_domain:5 | 2428.578 |
| 2lyz | 0.80 | 4.48 | 2.20 | 6466 | 2160 | 23 | 430 | 6969 | 39 | 1 | 16 | 2196 | pocket_domain:1, void_domain:38 | 9032.990 |
| 2lyz | 1.00 | 4.48 | 1.89 | 6466 | 1520 | 20 | 357 | 4996 | 36 | 1 | 6 | 1632 | pocket_domain:1, void_domain:35 | 7958.138 |
| 2lyz | 1.20 | 4.48 | 1.45 | 6466 | 1122 | 22 | 291 | 3794 | 20 | 1 | 5 | 1238 | pocket_domain:1, void_domain:19 | 7007.134 |
| 2lyz | 1.40 | 4.48 | 1.09 | 6466 | 887 | 20 | 228 | 3031 | 11 | 1 | 4 | 950 | pocket_domain:1, void_domain:10 | 6216.212 |
| 2lyz | 1.80 | 4.48 | 0.65 | 6466 | 621 | 9 | 206 | 2222 | 6 | 4 | 4 | 672 | pocket_domain:4, void_domain:2 | 5163.208 |
| 2lyz | 2.20 | 4.48 | 1.07 | 6466 | 463 | 7 | 183 | 1672 | 10 | 10 | 3 | 552 | pocket_domain:10 | 4420.943 |
| 3ptb | 0.80 | 7.03 | 8.77 | 10601 | 3408 | 19 | 724 | 10735 | 117 | 4 | 12 | 3714 | pocket_domain:4, void_domain:113 | 14926.144 |
| 3ptb | 1.00 | 7.03 | 6.59 | 10601 | 2274 | 21 | 543 | 7317 | 85 | 3 | 4 | 2578 | pocket_domain:3, void_domain:82 | 12813.225 |
| 3ptb | 1.20 | 7.03 | 3.49 | 10601 | 1635 | 30 | 394 | 5458 | 39 | 4 | 3 | 1844 | pocket_domain:3, surface_concavity_domain:1, void_domain:35 | 11136.891 |
| 3ptb | 1.40 | 7.03 | 2.93 | 10601 | 1272 | 17 | 349 | 4339 | 30 | 4 | 2 | 1410 | pocket_domain:3, surface_concavity_domain:1, void_domain:26 | 9883.590 |
| 3ptb | 1.80 | 7.03 | 1.68 | 10601 | 870 | 22 | 260 | 3061 | 11 | 5 | 1 | 1000 | pocket_domain:5, void_domain:6 | 8109.047 |
| 3ptb | 2.20 | 7.03 | 1.49 | 10601 | 623 | 11 | 221 | 2233 | 8 | 8 | 1 | 744 | pocket_domain:8 | 6775.208 |
