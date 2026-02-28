"""
配置管理
"""
import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class Config:
    """应用配置"""
    # 基础配置
    DEBUG: bool = False
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    HOST: str = "127.0.0.1"
    PORT: int = 5000

    # 智谱AI配置
    ZHIPU_API_KEY: str = ""
    MODEL: str = "glm-4"
    TEMPERATURE: float = 0.7
    MAX_TOKENS: int = 2000

    # 对话配置
    MAX_HISTORY_ROUNDS: int = 10
    SYSTEM_PROMPT: str = "你是一个有用的AI助手。"

    # 数据库配置
    DATABASE_PATH: str = "data/assistant.db"

    @classmethod
    def from_env(cls) -> "Config":
        """从环境变量加载配置"""
        return cls(
            DEBUG=os.getenv("DEBUG", "false").lower() == "true",
            SECRET_KEY=os.getenv("SECRET_KEY", cls().SECRET_KEY),
            HOST=os.getenv("HOST", cls().HOST),
            PORT=int(os.getenv("PORT", cls().PORT)),
            ZHIPU_API_KEY=os.getenv("ZHIPU_API_KEY", ""),
            MODEL=os.getenv("MODEL", "glm-4"),
            TEMPERATURE=float(os.getenv("TEMPERATURE", "0.7")),
            MAX_TOKENS=int(os.getenv("MAX_TOKENS", "2000")),
            MAX_HISTORY_ROUNDS=int(os.getenv("MAX_HISTORY_ROUNDS", "10")),
            SYSTEM_PROMPT=os.getenv("SYSTEM_PROMPT", cls().SYSTEM_PROMPT),
            DATABASE_PATH=os.getenv("DATABASE_PATH", cls().DATABASE_PATH),
        )


# 全局配置实例
config = Config.from_env()
