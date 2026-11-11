"""Original PISA result ownership."""

from topomt.provider_output import ExternalMeasurement
from topomt.third_party.output import ProviderOutput


class PisaOutput(ProviderOutput):
    """Preserve original interface results without native feature admission."""

    provider = 'pisa'

    @property
    def assembly_policy(self) -> str:
        """Return the original supplied-assembly policy, without biological inference.

        Returns
        -------
        str
            ``supplied_as_is`` for the qualified original XML protocol.

        Raises
        ------
        ValueError
            If the original XML does not establish the supported policy.
        """
        return self._decoded()['assembly_policy']

    def _decoded(self) -> dict:
        from .parser import decode_reports

        return decode_reports(
            self.run.get_artifact('output/interfaces.txt'),
            self.run.get_artifact('output/assemblies.txt'),
        )

    @property
    def assembly_measurements(self) -> dict[str, ExternalMeasurement]:
        """Return original measures of the supplied assembly in explicit units.

        Returns
        -------
        dict
            Detached original accessible/buried areas and model energy terms.

        Raises
        ------
        ValueError
            If original supplied-assembly XML is incomplete or unsupported.
        """
        from topomt.third_party._protocol import measurement

        from .parser import ASSEMBLY_FIELDS

        return {
            ASSEMBLY_FIELDS[key][0]: measurement(
                self.run,
                value['value'],
                value['unit'],
                f'asu_complex/assembly/{key}',
                'assemblies.txt',
                'Original PISA supplied-assembly summary; not a predicted biological assembly',
            )
            for key, value in self._decoded()['assembly'].items()
        }
