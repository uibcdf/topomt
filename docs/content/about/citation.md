# Citation

Use the exact TopoMT version and cite the scientific methods and third-party
software used in your calculation. TopoMT's software record names Diego
Prada-Gracia and Liliana M. Moreno-Vargas and links to the
[repository](https://github.com/uibcdf/topomt). Its automatic records currently
declare no TopoMT release DOI or DFND publication.

[Scientific attribution](../user/scientific_attribution.md) explains how
optional Ackredit collects the reached methods and renders their bibliography:

```python
import topomt as tmt

bibliography = tmt.cite(result, format='bibtex')
records = tmt.get_attribution(result)
```

The records preserve original producer versions and distinguish original
software execution from a native adaptation or methodological criterion.
`get_attribution` works without Ackredit; formatting with `cite` needs it.
Review the retained references and recording status before publication.
