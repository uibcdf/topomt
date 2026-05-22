import json
import tempfile
import time
from io import BytesIO
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from uuid import uuid4
import zipfile

import molsysmt as msm

from topomt import pyunitwizard as puw
from topomt.third_party.castp3.files import load_topography as load_castp_topography
from topomt.topography.Topography import Topography
from topomt.third_party._common import prepare_wrapper_input_pdb


SUBMIT_URL = 'https://cfold.bme.uic.edu/castpfold/submit_calc.php'
DOWNLOAD_URL_TEMPLATE = (
    'https://cfold.bme.uic.edu/castpfold/data/tmppdb/{jobid}/processed/{jobid}.zip'
)


class CastpFoldClient:
    """Minimal client for the CASTpFold CASTp-family server."""

    def __init__(
        self,
        *,
        submit_url: str = SUBMIT_URL,
        download_url_template: str = DOWNLOAD_URL_TEMPLATE,
        timeout: int = 30,
    ) -> None:
        self.submit_url = submit_url
        self.download_url_template = download_url_template
        self.timeout = timeout
        self.headers = {
            'User-Agent': 'TopoMT CASTp provider',
            'Accept': '*/*',
            'X-Requested-With': 'XMLHttpRequest',
            'Origin': 'https://cfold.bme.uic.edu',
            'Referer': 'https://cfold.bme.uic.edu/castpfold/compute',
        }

    def submit(
        self,
        pdb_path: str | Path,
        *,
        probe_radius: float = 1.4,
        email: str = 'N/A',
    ) -> str:
        pdb_path = Path(pdb_path)
        if not pdb_path.exists():
            raise FileNotFoundError(f'PDB file not found: {pdb_path}')

        probe_radius_value = _probe_radius_to_angstroms(probe_radius)
        if not (0.0 <= probe_radius_value <= 5.0):
            raise ValueError('probe_radius must be between 0.0 and 5.0 angstroms.')

        if pdb_path.stat().st_size > 2 * 1024 * 1024:
            raise ValueError('CASTpFold only accepts uploads up to 2 MB.')

        body, boundary = _encode_multipart_form_data(
            fields={
                'probe': str(probe_radius_value),
                'email': email,
            },
            file_field='file',
            file_path=pdb_path,
            content_type='chemical/x-pdb',
        )
        headers = dict(self.headers)
        headers['Content-Type'] = f'multipart/form-data; boundary={boundary}'

        request = Request(
            self.submit_url,
            data=body,
            headers=headers,
            method='POST',
        )
        with urlopen(request, timeout=self.timeout) as response:
            payload = json.loads(response.read().decode('utf-8'))

        jobid = payload.get('jobid', None)
        if not isinstance(jobid, str) or jobid == '':
            raise RuntimeError(f'Invalid CASTpFold submission response: {payload!r}')

        return jobid

    def download_result_zip_bytes(
        self,
        jobid: str,
        *,
        wait: int = 20,
        extra_wait: int = 30,
        retries: int = 1,
    ) -> bytes:
        wait = max(0, int(wait))
        extra_wait = max(0, int(extra_wait))
        retries = max(0, int(retries))

        if wait > 0:
            time.sleep(wait)

        zip_bytes = self._try_download_zip(jobid)
        if zip_bytes is not None:
            return zip_bytes

        for _ in range(retries + 1):
            if extra_wait > 0:
                time.sleep(extra_wait)
            zip_bytes = self._try_download_zip(jobid)
            if zip_bytes is not None:
                return zip_bytes

        raise RuntimeError(f'CASTpFold result ZIP is not ready for job {jobid}.')

    def _try_download_zip(self, jobid: str) -> bytes | None:
        request = Request(
            self.download_url_template.format(jobid=jobid),
            headers=self.headers,
            method='GET',
        )

        try:
            with urlopen(request, timeout=self.timeout) as response:
                payload = response.read()
        except HTTPError as exc:
            if exc.code in {404, 425}:
                return None
            raise
        except URLError:
            return None

        if _is_zip_payload(payload):
            return payload

        return None


def get_topography(
    molecular_system,
    *,
    selection: str = 'all',
    structure_indices: int | list[int] = 0,
    syntax: str = 'MolSysMT',
    probe_radius: float = 1.4,
    email: str = 'N/A',
    wait: int = 20,
    extra_wait: int = 30,
    retries: int = 1,
    timeout: int = 30,
    output_zip_file: str | Path | None = None,
) -> Topography:
    """Submit a structure to CASTpFold and return the resulting Topography."""

    client = CastpFoldClient(timeout=timeout)
    selected_molecular_system = msm.convert(
        molecular_system,
        to_form='molsysmt.MolSys',
        selection=selection,
        structure_indices=structure_indices,
        syntax=syntax,
    )

    with tempfile.TemporaryDirectory(prefix='topomt_castpfold_') as tmpdir_name:
        tmpdir = Path(tmpdir_name)
        input_pdb, _ = prepare_wrapper_input_pdb(
            molecular_system,
            tmpdir=tmpdir,
            selection=selection,
            structure_indices=structure_indices,
            syntax=syntax,
        )
        jobid = client.submit(
            input_pdb,
            probe_radius=probe_radius,
            email=email,
        )
        zip_bytes = client.download_result_zip_bytes(
            jobid,
            wait=wait,
            extra_wait=extra_wait,
            retries=retries,
        )

        if output_zip_file is None:
            zip_path = tmpdir / f'{jobid}.zip'
        else:
            zip_path = Path(output_zip_file).expanduser()
            zip_path.parent.mkdir(parents=True, exist_ok=True)
        zip_path.write_bytes(zip_bytes)

        return load_castp_topography(
            zip_file=zip_path,
            molecular_system=selected_molecular_system,
        )


def _encode_multipart_form_data(
    *,
    fields: dict[str, str],
    file_field: str,
    file_path: Path,
    content_type: str,
) -> tuple[bytes, str]:
    boundary = f'----TopoMTBoundary{uuid4().hex}'
    line_break = b'\r\n'
    body = bytearray()

    for key, value in fields.items():
        body.extend(f'--{boundary}'.encode('utf-8'))
        body.extend(line_break)
        body.extend(f'Content-Disposition: form-data; name="{key}"'.encode('utf-8'))
        body.extend(line_break)
        body.extend(line_break)
        body.extend(str(value).encode('utf-8'))
        body.extend(line_break)

    body.extend(f'--{boundary}'.encode('utf-8'))
    body.extend(line_break)
    body.extend(
        (
            f'Content-Disposition: form-data; name="{file_field}"; '
            f'filename="{file_path.name}"'
        ).encode('utf-8')
    )
    body.extend(line_break)
    body.extend(f'Content-Type: {content_type}'.encode('utf-8'))
    body.extend(line_break)
    body.extend(line_break)
    body.extend(file_path.read_bytes())
    body.extend(line_break)
    body.extend(f'--{boundary}--'.encode('utf-8'))
    body.extend(line_break)

    return bytes(body), boundary


def _is_zip_payload(payload: bytes) -> bool:
    if len(payload) < 4:
        return False

    try:
        return zipfile.is_zipfile(BytesIO(payload))
    except OSError:
        return False


def _probe_radius_to_angstroms(probe_radius) -> float:
    if puw.is_quantity(probe_radius):
        return float(puw.get_value(probe_radius, to_unit='angstroms'))

    return float(probe_radius)
