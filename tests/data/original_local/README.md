# Original local provider smoke evidence

Captured 2026-11-07 from original CAVER 3.02, P2Rank 2.5.1 and GHECOM
2026/08/17 executions on the unchanged 1AKD PDB distributed in CAVER's
static-structure example. These are technical original-adapter controls,
not native DFND protein characterization, biological validation or BenchLab
comparisons. Counts differ because the methods report different objects.

The ZIPs retain full original inputs/outputs and TopoMT source context; no
field/geometry is replaced with a native result. See `receipt.json` for exact
file checksums and the linked provider checkpoint for acquisition, commands,
resource bounds and limitations. Original temporary paths in logs no longer
exist; recovery consumes the captured bytes and `source.pdb`.

- CAVER: 47 retained tunnel profiles; requested origin [17.012,24.139,7.790] Å,
  probe 0.6 Å, fixed original seed 1, default remaining admitted settings.
- P2Rank: 5 predicted sites using the original default model.
- GHECOM: 41 P-mode morphological grid clusters, grid width 1 Å, small/large
  probes 1.87/6 Å. Model identifiers, not residue/grid values, identify clusters.

Official sources and licences: CAVER CLI GPLv3
https://www.caver.cz/fil/download/caver30/302/caver_3.0.2.zip ; P2Rank MIT
https://github.com/rdk/p2rank/releases/tag/2.5.1 ; GHECOM LGPLv3 author's source
https://github.com/kawabata-takeshi/ghecom_test/tree/e1950a405323d069673fe2df445ecd3f41e8651e .
CAVER's exported viewer scripts retain their original licence; the distribution
licence is included in `CAVER_LICENSE.txt`. No engine executable is bundled here.
