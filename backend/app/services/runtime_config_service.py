from app.config import settings
from app.services.settings_service import get_category


def effective_ldap_config(db):
    cfg = {
        "ldap_enabled": settings.ldap_enabled,
        "ldap_url": settings.ldap_url,
        "ldap_bind_dn": settings.ldap_bind_dn,
        "ldap_bind_password": settings.ldap_bind_password,
        "ldap_base_dn": settings.ldap_base_dn,
        "ldap_user_filter": settings.ldap_user_filter,
        "ldap_admin_group": settings.ldap_admin_group,
        "ldap_signer_group": settings.ldap_signer_group,
        "ldap_viewer_group": settings.ldap_viewer_group,
        "ldap_tls_verify": settings.ldap_tls_verify,
    }
    cfg.update(get_category(db, 'ldap'))
    cfg["ldap_enabled"] = str(cfg.get("ldap_enabled")).lower() in ("1", "true", "yes", "on")
    return cfg


def effective_smtp_config(db):
    cfg = {
        "smtp_enabled": settings.smtp_enabled,
        "smtp_host": settings.smtp_host,
        "smtp_port": settings.smtp_port,
        "smtp_username": settings.smtp_username,
        "smtp_password": settings.smtp_password,
        "smtp_use_tls": settings.smtp_use_tls,
        "smtp_from_email": settings.smtp_from_email,
        "smtp_from_name": settings.smtp_from_name,
        "app_public_url": settings.app_public_url,
    }
    cfg.update(get_category(db, 'smtp'))
    cfg["smtp_enabled"] = str(cfg.get("smtp_enabled")).lower() in ("1", "true", "yes", "on")
    cfg["smtp_use_tls"] = str(cfg.get("smtp_use_tls")).lower() in ("1", "true", "yes", "on")
    return cfg
