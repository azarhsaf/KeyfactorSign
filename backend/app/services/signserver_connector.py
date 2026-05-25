import httpx
from app.config import settings

class SignServerConnector:
    def __init__(self):
        self.base = settings.signserver_base_url.rstrip('/')

    def _auth(self):
        if settings.signserver_auth_type == "basic" and settings.signserver_username:
            return (settings.signserver_username, settings.signserver_password)
        return None

    def _process_url(self) -> str:
        # Accept either full process endpoint (.../signserver/process) or SignServer root (.../signserver)
        if self.base.endswith('/process'):
            return self.base
        return f"{self.base}/process"

    def health_check(self):
        url = self._process_url()
        if not self.base:
            return {"status": "not_configured"}
        try:
            r = httpx.get(url, timeout=settings.signserver_timeout, verify=settings.signserver_tls_verify, auth=self._auth())
            return {"status": "reachable", "code": r.status_code, "url": url}
        except Exception as ex:
            return {"status": "error", "error": str(ex), "url": url}

    def sign_pdf(self, input_pdf_path: str, output_pdf_path: str, metadata: dict):
        cert = (settings.signserver_client_cert, settings.signserver_client_key) if settings.signserver_client_cert and settings.signserver_client_key else None
        url = self._process_url()
        with open(input_pdf_path, "rb") as fh:
            files = {"file": (input_pdf_path.split('/')[-1], fh, "application/pdf")}
            data = {"workerName": settings.signserver_worker_id}
            r = httpx.post(
                url,
                files=files,
                data=data,
                timeout=settings.signserver_timeout,
                verify=settings.signserver_tls_verify,
                auth=self._auth(),
                cert=cert,
            )
        r.raise_for_status()
        with open(output_pdf_path, "wb") as out:
            out.write(r.content)
        return {"ok": True, "status_code": r.status_code, "url": url, "worker": settings.signserver_worker_id}

    def test_signing(self):
        sample = b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 300 100] /Contents 4 0 R >>\nendobj\n4 0 obj\n<< /Length 31 >>\nstream\nBT /F1 12 Tf 20 50 Td (Test) Tj ET\nendstream\nendobj\nxref\n0 5\n0000000000 65535 f \ntrailer\n<< /Root 1 0 R /Size 5 >>\nstartxref\n0\n%%EOF"
        cert = (settings.signserver_client_cert, settings.signserver_client_key) if settings.signserver_client_cert and settings.signserver_client_key else None
        files = {"file": ("test.pdf", sample, "application/pdf")}
        data = {"workerName": settings.signserver_worker_id}
        url = self._process_url()
        r = httpx.post(url, files=files, data=data, timeout=settings.signserver_timeout, verify=settings.signserver_tls_verify, auth=self._auth(), cert=cert)
        return {"status_code": r.status_code, "ok": r.status_code < 400, "url": url}

    def timestamp_pdf(self, input_pdf_path: str, output_pdf_path: str):
        return {"ok": settings.tsa_enabled, "tsa_url": settings.tsa_url}
