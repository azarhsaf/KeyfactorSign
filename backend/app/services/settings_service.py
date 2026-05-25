import json
from app.models.settings import Setting

SENSITIVE_KEYS = {"ldap_bind_password", "smtp_password", "signserver_password"}


def _serialize(v):
    return json.dumps(v)


def _deserialize(v):
    try:
        return json.loads(v)
    except Exception:
        return v


def get_setting(db, category: str, key: str, default=None):
    row = db.query(Setting).filter(Setting.category == category, Setting.key == key).first()
    if not row:
        return default
    return _deserialize(row.value_encrypted)


def set_setting(db, category: str, key: str, value):
    row = db.query(Setting).filter(Setting.category == category, Setting.key == key).first()
    if not row:
        row = Setting(category=category, key=key, value_encrypted=_serialize(value))
        db.add(row)
    else:
        row.value_encrypted = _serialize(value)
    db.commit()


def get_category(db, category: str):
    rows = db.query(Setting).filter(Setting.category == category).all()
    out = {}
    for r in rows:
        out[r.key] = _deserialize(r.value_encrypted)
    return out


def masked_payload(payload: dict):
    out = {}
    for k, v in payload.items():
        if k in SENSITIVE_KEYS and v:
            out[k] = "********"
        else:
            out[k] = v
    return out
