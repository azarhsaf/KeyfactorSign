import ldap
from ldap.filter import escape_filter_chars

class LDAPConnector:
    def __init__(self, cfg: dict):
        self.cfg = cfg

    def _connect(self):
        conn = ldap.initialize(self.cfg.get("ldap_url"))
        conn.set_option(ldap.OPT_REFERRALS, 0)
        conn.simple_bind_s(self.cfg.get("ldap_bind_dn"), self.cfg.get("ldap_bind_password"))
        return conn

    def test_connection(self):
        if not self.cfg.get("ldap_enabled"):
            return {"status": "disabled"}
        try:
            conn = self._connect()
            conn.unbind_s()
            return {"status": "ok", "url": self.cfg.get("ldap_url")}
        except Exception as ex:
            return {"status": "error", "error": str(ex), "url": self.cfg.get("ldap_url")}

    def authenticate(self, username: str, password: str):
        conn = self._connect()
        filt = self.cfg.get("ldap_user_filter", "(sAMAccountName={username})").replace('{username}', escape_filter_chars(username))
        result = conn.search_s(self.cfg.get("ldap_base_dn"), ldap.SCOPE_SUBTREE, filt, ['distinguishedName', 'memberOf', 'displayName', 'mail'])
        if not result:
            return None
        dn, attrs = result[0]
        user_conn = ldap.initialize(self.cfg.get("ldap_url"))
        user_conn.set_option(ldap.OPT_REFERRALS, 0)
        user_conn.simple_bind_s(dn, password)
        groups = [g.decode() if isinstance(g, bytes) else str(g) for g in attrs.get('memberOf', [])]
        display = attrs.get('displayName', [username])[0]
        if isinstance(display, bytes): display = display.decode(errors='ignore')
        mail = attrs.get('mail', [f'{username}@ldap.local'])[0]
        if isinstance(mail, bytes): mail = mail.decode(errors='ignore')
        role = 'viewer'
        groups_l = [g.lower() for g in groups]
        if any(str(self.cfg.get("ldap_admin_group", "")).lower() in g for g in groups_l): role = 'admin'
        elif any(str(self.cfg.get("ldap_signer_group", "")).lower() in g for g in groups_l): role = 'signer'
        return {"username": username, "display_name": display, "email": mail, "role": role, "groups": groups}

    def search_users(self, query: str, limit: int = 100):
        if not self.cfg.get("ldap_enabled"):
            return []
        conn = self._connect()
        q = (query or '').strip()
        if q:
            esc = escape_filter_chars(q)
            filt = f"(&(objectCategory=person)(objectClass=user)(|(sAMAccountName=*{esc}*)(displayName=*{esc}*)(mail=*{esc}*)))"
        else:
            filt = "(&(objectCategory=person)(objectClass=user))"
        result = conn.search_s(self.cfg.get("ldap_base_dn"), ldap.SCOPE_SUBTREE, filt, ['sAMAccountName', 'displayName', 'mail', 'distinguishedName', 'memberOf'])
        out = []
        for item in result[:limit]:
            if not item or len(item) != 2:
                continue
            dn, attrs = item
            if dn is None or not isinstance(attrs, dict):
                continue
            username = attrs.get('sAMAccountName', [b''])[0]
            display = attrs.get('displayName', [b''])[0]
            mail = attrs.get('mail', [b''])[0]
            groups = [g.decode(errors='ignore') if isinstance(g, bytes) else str(g) for g in attrs.get('memberOf', [])]
            username = username.decode(errors='ignore') if isinstance(username, bytes) else str(username)
            display = display.decode(errors='ignore') if isinstance(display, bytes) else str(display)
            mail = mail.decode(errors='ignore') if isinstance(mail, bytes) else str(mail)
            if not username:
                continue
            out.append({
                'username': username,
                'display_name': display or username,
                'email': mail,
                'distinguished_name': dn,
                'groups': groups,
            })
        conn.unbind_s()
        return out
