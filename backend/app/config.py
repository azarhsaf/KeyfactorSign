from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "Keyfactor SignPortal"
    secret_key: str = "change_me"
    cors_origins: str = "http://localhost:8081"
    database_url: str = "postgresql+psycopg2://signportal:signportal_pass@db:5432/signportal"
    jwt_expire_minutes: int = 60
    upload_dir: str = "/app/storage/uploads"
    signed_dir: str = "/app/storage/signed"
    max_file_mb: int = 25

    signserver_base_url: str = ""
    signserver_worker_id: str = "PDFSigner"
    signserver_auth_type: str = "none"
    signserver_username: str = ""
    signserver_password: str = ""
    signserver_tls_verify: bool = False
    signserver_client_cert: str = ""
    signserver_client_key: str = ""
    signserver_timeout: int = 60
    signserver_mode: str = "process_servlet"

    tsa_enabled: bool = True
    tsa_url: str = ""
    tsa_worker_name: str = "TimeStampSigner"

    ldap_enabled: bool = False
    ldap_url: str = ""
    ldap_bind_dn: str = ""
    ldap_bind_password: str = ""
    ldap_base_dn: str = ""
    ldap_user_filter: str = "(sAMAccountName={username})"
    ldap_admin_group: str = ""
    ldap_signer_group: str = ""
    ldap_viewer_group: str = ""
    ldap_tls_verify: bool = False

    class Config:
        env_file = ".env"

settings = Settings()
