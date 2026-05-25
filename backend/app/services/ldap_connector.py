import ldap
from app.config import settings

class LDAPConnector:
    def test_connection(self):
        if not settings.ldap_enabled:
            return {"status": "disabled"}
        try:
            conn = ldap.initialize(settings.ldap_url)
            conn.set_option(ldap.OPT_REFERRALS, 0)
            conn.simple_bind_s(settings.ldap_bind_dn, settings.ldap_bind_password)
            conn.unbind_s()
            return {"status": "ok", "url": settings.ldap_url}
        except Exception as ex:
            return {"status": "error", "error": str(ex), "url": settings.ldap_url}

    def authenticate(self, username: str, password: str):
        conn = ldap.initialize(settings.ldap_url)
        conn.set_option(ldap.OPT_REFERRALS, 0)
        conn.simple_bind_s(settings.ldap_bind_dn, settings.ldap_bind_password)
        filt = settings.ldap_user_filter.replace('{username}', username)
        result = conn.search_s(settings.ldap_base_dn, ldap.SCOPE_SUBTREE, filt, ['distinguishedName', 'memberOf', 'displayName', 'mail'])
        if not result:
            return None
        dn, attrs = result[0]
        user_conn = ldap.initialize(settings.ldap_url)
        user_conn.set_option(ldap.OPT_REFERRALS, 0)
        user_conn.simple_bind_s(dn, password)
        groups = [g.decode() if isinstance(g, bytes) else str(g) for g in attrs.get('memberOf', [])]
        display = attrs.get('displayName', [username])[0]
        if isinstance(display, bytes):
            display = display.decode()
        mail = attrs.get('mail', [f'{username}@ldap.local'])[0]
        if isinstance(mail, bytes):
            mail = mail.decode()
        role = 'viewer'
        groups_l = [g.lower() for g in groups]
        if any(settings.ldap_admin_group.lower() in g for g in groups_l):
            role = 'admin'
        elif any(settings.ldap_signer_group.lower() in g for g in groups_l):
            role = 'signer'
        return {"username": username, "display_name": display, "email": mail, "role": role, "groups": groups}


    def search_users(self, query: str, limit: int = 30):
        if not settings.ldap_enabled:
            return []
        conn = ldap.initialize(settings.ldap_url)
        conn.set_option(ldap.OPT_REFERRALS, 0)
        conn.simple_bind_s(settings.ldap_bind_dn, settings.ldap_bind_password)
        q = query or '*'
        filt = f"(|(sAMAccountName=*{q}*)(displayName=*{q}*)(mail=*{q}*))"
        result = conn.search_s(settings.ldap_base_dn, ldap.SCOPE_SUBTREE, filt, ['sAMAccountName', 'displayName', 'mail', 'distinguishedName', 'memberOf'])
        out = []
        for dn, attrs in result[:limit]:
            username = attrs.get('sAMAccountName', [b''])[0]
            display = attrs.get('displayName', [b''])[0]
            mail = attrs.get('mail', [b''])[0]
            groups = [g.decode() if isinstance(g, bytes) else str(g) for g in attrs.get('memberOf', [])]
            out.append({
                'username': username.decode() if isinstance(username, bytes) else str(username),
                'display_name': display.decode() if isinstance(display, bytes) else str(display),
                'email': mail.decode() if isinstance(mail, bytes) else str(mail),
                'dn': dn,
                'groups': groups,
            })
        conn.unbind_s()
        return out
