import smtplib
from email.mime.text import MIMEText
from app.config import settings
from app.models.settings import EmailLog
from app.services.runtime_config_service import effective_smtp_config

class EmailService:
    def settings_dict(self, db=None):
        if db is not None:
            return effective_smtp_config(db)
        return {
            "smtp_enabled": getattr(settings, 'smtp_enabled', False),
            "smtp_host": getattr(settings, 'smtp_host', ''),
            "smtp_port": getattr(settings, 'smtp_port', 587),
            "smtp_username": getattr(settings, 'smtp_username', ''),
            "smtp_password": getattr(settings, 'smtp_password', ''),
            "smtp_use_tls": getattr(settings, 'smtp_use_tls', True),
            "smtp_from_email": getattr(settings, 'smtp_from_email', ''),
            "smtp_from_name": getattr(settings, 'smtp_from_name', 'Keyfactor SignPortal'),
            "app_public_url": getattr(settings, 'app_public_url', 'http://localhost:8081'),
        }

    def send(self, db, to_email: str, subject: str, body: str, document_id=None):
        cfg = self.settings_dict(db)
        log = EmailLog(document_id=document_id, recipient=to_email, subject=subject, status='queued')
        db.add(log); db.commit(); db.refresh(log)
        if not cfg['smtp_enabled']:
            log.status = 'failed'; log.error = 'SMTP disabled'; db.commit()
            return {"ok": False, "error": "SMTP disabled"}
        try:
            msg = MIMEText(body, 'html')
            msg['Subject'] = subject
            msg['From'] = f"{cfg['smtp_from_name']} <{cfg['smtp_from_email']}>"
            msg['To'] = to_email
            with smtplib.SMTP(cfg['smtp_host'], int(cfg['smtp_port']), timeout=15) as s:
                if cfg['smtp_use_tls']:
                    s.starttls()
                if cfg['smtp_username']:
                    s.login(cfg['smtp_username'], cfg.get('smtp_password',''))
                s.sendmail(cfg['smtp_from_email'], [to_email], msg.as_string())
            log.status = 'sent'; db.commit()
            return {"ok": True}
        except Exception as ex:
            log.status = 'failed'; log.error = str(ex); db.commit()
            return {"ok": False, "error": str(ex)}
