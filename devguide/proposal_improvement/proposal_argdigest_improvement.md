**Proposal: Flag argdigest Improvements Here**

During the TopoMT reimplementation effort we are expanding the use of
`argdigest` adapters and digesters. Whenever a new argument-processing
requirement arises (unit-aware arguments, new pipelines, sanitizers), this document
is the spot to note it and propose it for inclusion in the upstream library instead
of layering another local helper.

Record the requirement, the desired API shape, and why the change would benefit other
projects (e.g., a shared `method` digester or normalization pipeline). That way we can
track the request, shape a PR, and keep TopoMT aligned with the central
`argdigest` configuration.
