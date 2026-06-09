from pydantic_settings import BaseSettings, SettingsConfigDict

# Production db config
class Settings(BaseSettings):
    # Database
    database_hostname: str
    database_port: str
    database_password: str
    database_name: str
    database_username: str
    resend_api_key: str

    # Test Database
    #test_database_name: str test  config does not belong in  production settings

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


    # extra="ignore" lets .env contain test-only keys (e.g. test_database_name) without crashing
    model_config = SettingsConfigDict(env_file = ".env", extra="ignore")

settings = Settings()

