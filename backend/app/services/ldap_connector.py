from app.config import settings

class LDAPConnector:
    def test_connection(self):
        if not settings.ldap_enabled:
            return {"status": "disabled"}
        return {"status": "placeholder", "url": settings.ldap_url}
