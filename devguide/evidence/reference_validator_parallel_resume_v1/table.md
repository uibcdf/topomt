| Original 1.4 A Model | Workers | Worker wall s | Bounded elapsed s | Parent CPU s | Waited child CPU s | Sampled group RSS MiB |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `regular_tetrahedron` | 1 | 0.781 | 1.204 | 0.296 | 0.343 | 1.82 |
| `regular_tetrahedron` | 2 | 0.718 | 1.103 | 0.304 | 0.645 | 1.54 |
| `closed_shell` | 1 | 516.305 | 516.744 | 155.382 | 360.136 | 77.46 |
| `closed_shell` | 2 | 335.521 | 335.944 | 150.358 | 366.002 | 103.76 |
| `dumbbell` | 1 | 552.690 | 553.134 | 206.383 | 345.548 | 80.84 |
| `dumbbell` | 2 | 394.893 | 395.293 | 209.843 | 368.850 | 106.19 |

Tetrahedron phases are shorter than the five-second sampling period: their
displayed group RSS captures early startup and does **not resolve pool memory**.
Other group values are sampled sums, can double-count shared pages and miss
peaks; kernel peak individual-process RSS is recorded separately in the index.
Elapsed ratios compare the same checkpoint/resume/check/read workflow, with one
observation per configuration. The one-worker workflow uses a spawned pool.
