# When the sampled walls close

Both shell inputs now have a **0.005 Å access-to-enclosure bracket** for their
original origin. These bounds use continuous all-atom geometry, independently
of DFND's graph and catalog.

| Fixed input | Access at lower probe (Å) | Enclosure at upper probe (Å) | Native observation at these endpoints |
| --- | ---: | ---: | --- |
| [Closed shell](closed_shell/index.md) | 0.1696861113 | 0.1746861113 | One physical patch / `Pocket`, then zero patches / `Void`. |
| [Shell with opening](shell_with_opening/index.md) | 2.0097446941 | 2.0147446941 | One physical patch / `Pocket`, then zero patches / `Void`. |

Use the full-precision endpoints in the records when replaying. A positive
path proves access at the lower probe and at every smaller probe. At the upper
probe, expanded balls cover every hull face while the origin remains free:
its component is enclosed. Larger probes cannot restore access in the same
fixed model, although they can also exclude the origin. Patch and component
counts need not vary monotonically.

## How the bounds are checked

The lower certificate contains an origin-to-hull segment and an infinite
outward-normal continuation. Their minimum clearance is evaluated against all
atomic balls; both lower endpoints retain about 1e-5 Å safety margin. Candidate
points are discovered from nearest-center bisectors. This finite search does
not establish global optimality.

The upper certificate partitions **every hull triangle** into midpoint
subtriangles. Each leaf's three vertices lie strictly inside one expanded ball;
convexity covers the entire leaf. The verifier checks complete partitions,
all covering inequalities, input identity, original free origin and protocol.
A failed path search or incomplete cover supplies no accepted bracket.

The closed-shell cover has 1,259 leaves, maximum depth eight; the opened-shell
cover has 218 leaves, maximum depth ten. Independent generation/verification
took 1.649/0.052 s and 0.684/0.021 s respectively, with peak RSS below 80 MiB on
one CPU/thread. These small measurements are budget evidence, not scaling claims.

The opened-shell v1 search stopped at its candidate budget; its unresolved
receipt remains. V2 first replays the existing independent 1.4 Å wall certificate.
Covered faces stay covered at larger probes. Restricting witness discovery to
the remaining face yields the bracket within the original resource limits.

## Reproducible records

| Input | Protocol | Complete certificate | Independent verification | Actual native receiving |
| --- | --- | --- | --- | --- |
| Closed shell | {download}`protocol <closed_shell/artifacts/access_bracket_v1/protocol.json>` | {download}`certificate <closed_shell/artifacts/access_bracket_v1/certificate.json>` | {download}`verification <closed_shell/artifacts/access_bracket_v1/verification.json>` | {download}`public observations <closed_shell/artifacts/access_bracket_v1/native_receiving.json>` |
| Shell with opening | {download}`protocol v2 <shell_with_opening/artifacts/access_bracket_v2/protocol.json>` | {download}`certificate <shell_with_opening/artifacts/access_bracket_v2/certificate.json>` | {download}`verification <shell_with_opening/artifacts/access_bracket_v2/verification.json>` | {download}`public observations <shell_with_opening/artifacts/access_bracket_v2/native_receiving.json>` |

Independent sources are `863d5a7` and `a9e2ad6`; native receiving uses `8bc1a7e`.
Actual native/public counts are resolved and agree with the positive/zero
decisions. Catalog classification is reported separately: `Pocket` at a narrow
endpoint does not redefine physical access or imply ligand transport.

These intervals bound original-origin access on the declared hull. They do not
supply an exact transition, maximum bottleneck, free aperture area, all cavities
or arbitrary native graph paths. Wider work remains owned by
[#76](https://github.com/uibcdf/topomt/issues/76).
