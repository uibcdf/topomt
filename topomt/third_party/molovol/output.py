"""Provider-owned MoloVol output, separate from native feature admission."""

from typing import Any

from topomt import pyunitwizard as puw
from topomt.provider_output import ExternalMeasurement
from topomt.third_party.output import ProviderOutput


class MoloVolOutput(ProviderOutput):
    """Original MoloVol internal regions and source-bound calculation evidence.

    Attributes
    ----------
    cavities : tuple of ProviderRecord
        Internal rows with original Isolated/Pocket/Tunnel types retained.
        Outside belongs only to the original report and decoded data.

    Examples
    --------
    >>> output.measurements['molecular_volume'].value  # doctest: +SKIP
    >>> output.original_data['probe_mode']  # doctest: +SKIP
    """

    provider = 'molovol'

    @property
    def report_text(self) -> str:
        """Return the complete original report, including the outside region.

        Returns
        -------
        str
            Unmodified original report text.

        Raises
        ------
        ValueError
            If the original report is absent, ambiguous or invalid.
        """
        from .parser import report_data

        return report_data(self.run)[1]

    @property
    def original_data(self) -> dict[str, Any]:
        """Return detached decoded report fields with explicit physical units.

        Returns
        -------
        dict
            Query, effective radii, formula, total measures and region rows.
            Physical packets retain value, unit, source field and printed token.

        Raises
        ------
        ValueError
            If the original report is absent, ambiguous or invalid.
        """
        from .parser import report_data

        return report_data(self.run)[2]

    @property
    def measurements(self) -> dict[str, ExternalMeasurement]:
        """Return original total measures; undefined exterior volumes are absent.

        Returns
        -------
        dict of str to ExternalMeasurement
            Named measures; molecular volume with isolated cavities has its own
            key. Undefined exterior core volume is not replaced by zero.

        Raises
        ------
        ValueError
            If the original report is absent, ambiguous or invalid.
        """
        from .parser import external_measurements, report_data

        filename, _, data = report_data(self.run)
        return external_measurements(self.run, data['measurements'], filename)

    @property
    def element_radii(self) -> dict[str, Any]:
        """Return the effective per-element radii printed in the original report.

        Returns
        -------
        dict
            Detached length quantities in the caller's standard-unit policy.
            The report rounds to six significant digits; exact input radii
            remain in run metadata and the captured effective resource.

        Raises
        ------
        ValueError
            If the original report is absent, ambiguous or invalid.
        """
        from .parser import report_data

        return {
            symbol: puw.quantity(packet['value'], packet['unit'])
            for symbol, packet in report_data(self.run)[2]['element_radii'].items()
        }
