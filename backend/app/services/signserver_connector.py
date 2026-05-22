import httpx
from app.config import settings

class SignServerConnector:
    def __init__(self):
        self.base = settings.signserver_base_url.rstrip('/')

    def _auth(self):
        if settings.signserver_auth_type == "basic" and settings.signserver_username:
            return (settings.signserver_username, settings.signserver_password)
        return None

    def health_check(self):
        if not self.base:
            return {"status": "not_configured"}
        url = f"{self.base}/process"
        try:
            r = httpx.get(url, timeout=settings.signserver_timeout, verify=settings.signserver_tls_verify, auth=self._auth())
            return {"status": "reachable", "code": r.status_code}
        except Exception as ex:
            return {"status": "error", "error": str(ex)}

    def sign_pdf(self, input_pdf_path: str, output_pdf_path: str, metadata: dict):
        worker = settings.signserver_worker_id
        url = f"{self.base}/process?workerName={worker}"
        with open(input_pdf_path, "rb") as f:
            data = f.read()
        cert = (settings.signserver_client_cert, settings.signserver_client_key) if settings.signserver_client_cert and settings.signserver_client_key else None
        r = httpx.post(url, content=data, headers={"Content-Type": "application/pdf"}, timeout=settings.signserver_timeout, verify=settings.signserver_tls_verify, auth=self._auth(), cert=cert)
        r.raise_for_status()
        with open(output_pdf_path, "wb") as out:
            out.write(r.content)
        return {"ok": True, "status_code": r.status_code}

    def timestamp_pdf(self, input_pdf_path: str, output_pdf_path: str):
        return {"ok": settings.tsa_enabled, "tsa_url": settings.tsa_url}
