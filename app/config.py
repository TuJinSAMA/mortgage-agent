from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """应用配置"""
    
    # API 配置
    openai_api_key: str = ""
    openai_base_url: str = "https://api.poe.com/v1"
    model_name: str = "GPT-5"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,  # 不区分大小写
        extra="ignore"  # 忽略额外的环境变量
    )


settings = Settings()