"""
消息模型
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class Message:
    """消息数据模型"""
    id: int
    conversation_id: int
    role: str
    content: str
    created_at: str

    @classmethod
    def from_dict(cls, data: dict) -> "Message":
        """从字典创建实例"""
        return cls(
            id=data["id"],
            conversation_id=data.get("conversation_id", 0),
            role=data["role"],
            content=data["content"],
            created_at=data["created_at"]
        )

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "id": self.id,
            "conversation_id": self.conversation_id,
            "role": self.role,
            "content": self.content,
            "created_at": self.created_at
        }

    def to_openai_format(self) -> dict:
        """转换为OpenAI格式的消息（用于发送给智谱AI）"""
        return {
            "role": self.role,
            "content": self.content
        }
