# Scientific attribution

Runtime integration is centralized in `topomt/_ackredit.py`; public result
inspection/rendering lives in `topomt/citation.py`. This private package only
re-exports the readers. It neither imports Ackredit nor records method use.

Read `ACKREDIT_GUIDE.md` and `devguide/attribution.md` before adding a scientific
boundary. The unused Flowcite shim has been retired; decorators without actual
completion-boundary instrumentation do not establish adoption.
