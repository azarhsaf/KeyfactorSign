from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "SignPortal"
    secret_key: str = "change_me"
    jwt_expire_minutes: int = 60
    db_url: str = "postgresql+psycopg2://signportal:signportal_pass@db:5432/signportal"
    upload_dir: str = "/app/data/uploads"
    signed_dir: str = "/app/data/signed"
    signserver_base_url: str = ""
    signserver_worker_id: str = ""

    class Config:
        env_file = ".env"


settings = Settings()
