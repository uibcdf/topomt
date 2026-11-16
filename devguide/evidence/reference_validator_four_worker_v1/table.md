| Original 1.4 Å profile | Regions | Serial median s (range) | Two-worker median s (range) | Four-worker median s (range) | Four vs two elapsed reduction | Shared further serial read s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `regular_tetrahedron` | 1 | 0.268 (0.267–0.317) | 0.518 (0.471–0.523) | 0.468 (0.467–0.517) | 9.62% | 0.217 |
| `closed_shell` | 1 | 96.288 (95.686–98.442) | 87.453 (85.902–89.921) | 82.919 (78.512–83.191) | 5.18% | 95.838 |
| `dumbbell` | 3 | 131.596 (130.994–136.045) | 119.029 (118.470–120.812) | 107.771 (105.608–108.927) | 9.46% | 130.793 |

Times include the same cold checked solve/saving workflow and bounded launcher overhead. Each mode has three fresh observations in rotated order at lower scheduling priority. Shared reading is executed once per profile and checks all nine configurations; it is outside these solve medians and charged once in the total. These are scoped shared-host observations, not population statistics or general/causal scaling. Tiny inputs can use fewer task workers than requested. Serial remains the default.
