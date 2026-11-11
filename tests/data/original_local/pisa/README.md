# Original PISA supplied-assembly evidence

Owner: uibcdf/topomt#194. Original unchanged source is
`PDBe-KB/pisa@6d6f7d09ea5bf0f3f8a1602dd56fa896e6aca401`, program 2.1.2.
No engine source, executable, SRS/MolRef/PISA resource dataset is redistributed.
See `devguide/pisa/license_review.md` for documented local research use/free
academic acquisition and unresolved standalone redistribution terms under #165.

The synthetic input has 40 atoms in two artificial four-alanine chains, with
canonical TER columns and unique serials. `empty_input.pdb` separates them.
This is a bounded interface-protocol control, not native DFND protein work.
`analysis.txt`, `interfaces.txt`, `assemblies.txt`, `monomers.txt`, their
`empty_` counterparts and receipts retain direct original calls. `--as-is`
is used for analysis/XML, not for the original monomer-list command.

- `pisa.zip`: genuine public-adapter run agrees with the direct reports. One
  interface has 125.73203716 square angstroms, 24 other contacts, 28 reported
  contact atoms and 20 buried-area atoms. Those atom sets remain distinct.
- `pisa-empty.zip`: complete successful zero-interface run; supplied-assembly
  summary remains available despite the original 'Assemblies not calculated'
  wording for the intentionally disabled prediction route.
- `pisa-failed.zip`: deliberately unsupported ZZZ residue identities, rejected
  original analysis. Failed capture retains executable/resource/input evidence
  and no completed-provider attribution.

Each ZIP retains exact submitted PDB/source context, private configuration,
original reports, version and resource fingerprints. Producer paths/timestamps
are historical; saved readers do not reopen them. The special version probe
returns 2 on success; all analysis/extraction commands require 0. Areas are in
square angstroms; model energy terms are in kcal/mol and contact distances in
angstroms. No biological-assembly prediction, energy-accuracy or broad ligand
support claim is established.

`protocol.json` records retained file hashes. Guards are
`tests/test_specialist_original_execution.py`,
`tests/test_specialist_provider_parsers.py` and
`tests/test_specialist_provider_recovery.py`; execution/check scope is in
`devguide/specialist_provider_checkpoint.md`. Saved decoding/replay tests
cannot replace the original source gates or installed/platform qualification.
