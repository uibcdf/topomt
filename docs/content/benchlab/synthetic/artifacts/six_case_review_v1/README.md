# Six-case review evidence, version 1

This is the retained source review under TopoMT #187 and point diagnosis under
#181. See the [public interpretation](../../six_case_review.md). No native
scientific operator or public promotion rule changed.

- {download}`Protocol <protocol.json>`: 19 profiles, six input identities, 355 original-file
  hashes, declared point/work scope and resources.
- {download}`Compact summary <summary.json>`: actual public families, banks, physical
  availability and point checks by input/probe.
- {download}`Capture receipt <receiving_receipt.json>`: exact producer, dependencies/import
  origins, loaded MolSysMT native-module fingerprint, interpreter, code hashes,
  thread/CPU/memory limits, timings and output identities.
- {download}`Complete capture <receiving.zip>`: exact full JSON observations, receipt and
  protocol, compressed for retention with an internal SHA-256 manifest.

The ZIP is review evidence, rather than a full source/environment study bundle.
Each original case retains its own complete download. The seven original
uncompressed capture files are preserved byte-for-byte inside this archive;
SHA-256 readback was verified before retiring this task's working capture folder.

## Exact source and reproduction

The protocol and helpers were committed at
`1510e007d96da8a3c569f626a1b263fb59a54533` before the full 19-profile capture.
The input collection and preliminary observations were already known: this is
retrospective, case-guided receiving, not a blind evaluation or preregistration.

The routine workspace was the existing Python 3.14.10 environment
`molsyssuite@uibcdf_3.14`. `pip check` passed, imported editable sources were
verified, and the shared prefix was neither modified nor rebuilt. Exact sibling
revisions and native binary identity are in the receipt. The preserved human
version-file change has SHA-256
`d76f39e77bb54929c2d4a02f55ec04d61534ec09df776d2fe89ef731626a88b5`.
This does not qualify a newly installed package or other platform.

From that source and compatible source environment, use a new output directory:

```bash
env OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 \
    NUMBA_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1 \
    taskset -c 0 nice -n 10 timeout 90s python -c \
    'import resource, runpy; resource.setrlimit(resource.RLIMIT_AS, (4*1024**3, 4*1024**3)); runpy.run_module("devtools.benchlab.capture_six_cases", run_name="__main__")' \
    docs/content/benchlab/synthetic/artifacts/six_case_review_v1/protocol.json \
    /tmp/topomt-six-case-receiving
```

Choose one actually allowed logical CPU instead of `0` when necessary and check
available resources before running. The original output directory was the
protocol's sibling `receiving/`; only its verified archive is retained now.
The capturer refuses an existing output directory and checks frozen bytes again
after execution. It makes no original-provider/server request and does not
rediscover references or perform volume sampling.

## Interpretation boundaries

The diagnostic compares each stored resident center with its local four atoms
and all captured atoms. Values have explicit fixed-nm metadata; support weights
are dimensionless. A failed point does not prove its carrier empty, and a clear
point does not certify a path, physical component or catalog morphology.
Connector-only components receive no invented resident-point status.

Point checks preserve input/raw evidence and earn no new originating execution
credit when reading the archive. Actual native executions retain their detached
TopoMT attribution. Original case results and all previous downloads remain
unchanged. #180/#181/#184/#188 and wider #60/#76/#16 retain their own acceptance.
