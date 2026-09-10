"""
설정 관리 모듈.
.env 파일에 적힌 값(Supabase 주소, API 키 등)을
파이썬 코드에서 안전하게 꺼내 쓸 수 있게 해주는 곳.

pydantic-settings의 BaseSettings를 쓰면, .env 파일의
SUPABASE_URL 같은 값이 자동으로 Settings 객체의 속성으로 들어온다.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    supabase_url: str
    supabase_anon_key: str
    supabase_service_role_key: str
    supabase_db_password: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


settings = Settings()
