| Original 1.4 A Model | Mode | Remaining numerical tasks s | Recover geometry + two bounds s | Further serial read s | Full bounded elapsed s | Sampled group MiB |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| `regular_tetrahedron` | serial | 0.034 | 0.078 | 0.111 | 0.807 | 2.38 |
| `regular_tetrahedron` | parallel2 | 0.383 | 0.067 | 0.127 | 1.458 | 1.89 |
| `closed_shell` | serial | 34.368 | 50.053 | 96.481 | 257.367 | 46.34 |
| `closed_shell` | parallel2 | 23.458 | 48.425 | 90.922 | 237.898 | 110.39 |
| `dumbbell` | serial | 46.655 | 72.254 | 128.096 | 343.681 | 51.36 |
| `dumbbell` | parallel2 | 31.561 | 76.562 | 127.951 | 335.794 | 116.22 |

The full workflow includes first admission/two pieces/checkpoint, fresh-process recovery, completion/storage/reduction, and a further independent serial read. Each configuration is one observation. The remaining numerical-task phase includes pool/startup/scheduling when selected. Do not infer a universal or causal scaling factor from these shared-host observations. Tetrahedron phases are shorter than the five-second memory sampling period, so displayed sampled RSS does not resolve pool memory; all group values can miss peaks or double-count shared pages.
