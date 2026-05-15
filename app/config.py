from pydantic_settings import BaseSettings, SettingsConfigDict

# Production db config
class Settings(BaseSettings):
    # Database
    database_hostname: str
    database_port: str
    database_password: str
    database_name: str
    database_username: str

    # Test Database
    test_database_name: str

    # Auth
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int

    # Stripe
    stripe_secret_key : str
    stripe_webhook_secret : str

    # Redis
    redis_host: str
    redis_port: str

    # Monitoring
    sentry_dsn : str
    
    # Environment
    app_env : str = "development"


    model_config = SettingsConfigDict(env_file = ".env")

settings = Settings()

