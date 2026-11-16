| Original case | Probe Å | Regions | Serial cold solve s | Two-worker cold solve s | Shared further serial read s |
| --- | ---: | ---: | ---: | ---: | ---: |
| `regular_tetrahedron` | 1.2 | 1 | 0.317 | 0.520 | 0.217 |
| `regular_tetrahedron` | 1.4 | 1 | 0.268 | 0.521 | 0.217 |
| `regular_tetrahedron` | 1.7 | 0 | 0.218 | 0.217 | 0.167 |
| `closed_shell` | 0.05 | 1 | 108.594 | 92.756 | 98.942 |
| `closed_shell` | 0.2 | 1 | 96.240 | 86.458 | 98.692 |
| `closed_shell` | 1.4 | 1 | 95.185 | 85.248 | 95.336 |
| `closed_shell` | 5 | 0 | 35.624 | 35.384 | 35.524 |
| `shell_with_opening` | 1.4 | 1 | 82.286 | 73.770 | 81.386 |
| `shell_with_opening` | 3 | 1 | 80.836 | 70.645 | 87.290 |
| `shell_with_opening` | 5 | 0 | 30.475 | 29.837 | 29.230 |
| `straight_tube_narrow_dense` | 1.2 | 1 | 87.888 | 74.411 | 86.486 |
| `straight_tube_narrow_dense` | 1.4 | 1 | 80.690 | 68.705 | 79.287 |
| `straight_tube_narrow_dense` | 2.5 | 0 | 22.474 | 22.680 | 22.574 |
| `straight_tube_wide_sparse` | 1.4 | 1 | 95.837 | 83.058 | 95.021 |
| `straight_tube_wide_sparse` | 2.5 | 1 | 92.238 | 80.548 | 92.338 |
| `straight_tube_wide_sparse` | 5 | 0 | 27.474 | 27.286 | 26.924 |
| `dumbbell` | 1.4 | 3 | 139.051 | 124.178 | 147.352 |
| `dumbbell` | 2.2 | 2 | 148.659 | 128.312 | 141.352 |
| `dumbbell` | 6 | 0 | 51.933 | 48.543 | 49.134 |

Solve times include exact reading, independent complete geometry/frontier, all certified arithmetic, saving and bounded launcher overhead. Shared reading is executed once per profile and checks every configuration; it is not duplicated in the aggregate. Only tetrahedron 1.4 Å has three fresh repetitions per mode (table shows medians); all larger entries are single shared-host observations. Exact exclusions do not launch numerical workers. Probe labels are rounded Å display values of unchanged exact nm Models. Serial remains the default.
