"""
설정 관리 모듈.
.env 파일에 적힌 값(Supabase 주소, API 키 등)을
파이썬 코드에서 안전하게 꺼내 쓸 수 있게 해주는 곳.

pydantic-settings의 BaseSettings를 쓰면, .env 파일의
SUPABASE_URL 같은 값이 자동으로 Settings 객체의 속성으로 들어온다.

Supabase가 API 키 체계를 새로 바꾸면서(레거시 anon/service_role 키 ->
publishable/secret 키), 이 프로젝트는 새 방식을 기준으로 설정을 읽는다.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    supabase_url: str
    supabase_publishable_key: str
    supabase_secret_key: str
    supabase_jwks_url: str = ""
    supabase_db_password: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


settings = Settings()
