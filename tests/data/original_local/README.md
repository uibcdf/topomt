# Original local provider smoke evidence

Captured 2026-11-07 from original CAVER 3.02, P2Rank 2.5.1, GHECOM
2026/08/17 and the explicit pyKVFinder 0.9.6+uibcdf.2 compatibility source,
on the unchanged 1AKD PDB distributed in CAVER's
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
- pyKVFinder 0.9.6+uibcdf.2: 12 original grid cavities with 1 Å spacing;
  scientific implementation unchanged from upstream 0.9.6, with explicitly
  identified compatibility packaging. NumPy 2.5.4 and tomlkit 0.15.2.

Official sources and licences: CAVER CLI GPLv3
https://www.caver.cz/fil/download/caver30/302/caver_3.0.2.zip ; P2Rank MIT
https://github.com/rdk/p2rank/releases/tag/2.5.1 ; GHECOM LGPLv3 author's source
https://github.com/kawabata-takeshi/ghecom_test/tree/e1950a405323d069673fe2df445ecd3f41e8651e .
CAVER's exported viewer scripts retain their original licence; the distribution
licence is included in `CAVER_LICENSE.txt`. No engine executable is bundled here.
pyKVFinder source and vdW dictionary use GPL-3.0-or-later; its licence is retained
as `PYKVFINDER_LICENSE.txt`. Fork source:
https://github.com/uibcdf/pyKVFinder/tree/uibcdf-compat .
