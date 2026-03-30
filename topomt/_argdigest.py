# TopoMT/_argdigest.py

DIGESTION_SOURCE = "topomt._private.arg_digestion.argument"
DIGESTION_STYLE = "package"
STANDARDIZER = "topomt._private.arg_digestion.argument_names_standardization:argument_names_standardization"
STRICTNESS = "warn"
SKIP_PARAM = "skip_digestion"

PIPELINES = {
    "as_float64_array": ["sci.to_float64_array"],
    "as_int64_array": ["sci.to_int64_array"],
    "as_nm_float64_array": [{"rule": "sci.to_quantity_array", "params": {"unit": "nm", "dtype": "float64"}}],
}
