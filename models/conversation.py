"""
对话模型
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Conversation:
    """对话数据模型"""
    id: int
    title: str
    created_at: str
    updated_at: str

    @classmethod
    def from_dict(cls, data: dict) -> "Conversation":
        """从字典创建实例"""
        return cls(
            id=data["id"],
            title=data["title"],
            created_at=data["created_at"],
            updated_at=data["updated_at"]
        )

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "id": self.id,
            "title": self.title,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
