"""配置加载：环境变量 / .env → Settings 对象。

原则：密钥只从 .env 与环境变量读取，绝不写死在代码里、绝不进 git。
M0 只需要单一上游；M1 起渠道改由 SQLite 的 channels 表管理，
这里保留网关自身配置（对外 key、监听端口等）。
"""
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # 网关对外的自发 key：客户端拿它访问网关（否则任何本机进程都能花你的渠道额度）
    gateway_api_key: str = "dev-local-key"

    # ---- M0：单一测试上游 ----
    upstream_base_url: str = ""
    upstream_api_key: str = ""
    upstream_model: str = ""


@lru_cache
def get_settings() -> Settings:
    """进程内缓存一份配置；改动 .env 后需重启进程生效。"""
    return Settings()
