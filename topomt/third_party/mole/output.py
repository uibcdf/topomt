"""Original MOLE feature records and complete detached JSON access."""

from typing import Any

from topomt.third_party._protocol import artifact
from topomt.third_party._saved_json import read_json
from topomt.third_party.output import ProviderOutput


class MoleOutput(ProviderOutput):
    """Original channels and cavities; a MOLE label is not DFND admission."""

    provider = 'mole'

    @property
    def original_data(self) -> dict[str, Any]:
        """Return a detached copy of all original JSON fields.

        This is the original fixed-unit MOLE protocol: coordinates, radii and
        distances are in angstroms; tetrahedral volumes are in angstroms cubed.
        Use record geometries/measurements for quantity-aware access. Includes
        the original surface, origins, configuration, layers and chemistry.

        Returns
        -------
        dict
            Original JSON decoded into independent containers, retaining the
            producer's field definitions and fixed physical units.

        Raises
        ------
        ValueError
            If the original JSON is missing or malformed.

        Examples
        --------
        >>> output.original_data['Version']  # doctest: +SKIP
        '2.5.26.10.26'
        """
        return read_json(artifact(self.run, 'json/data.json'), provider='mole')
