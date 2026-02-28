"""
数据库服务
"""
import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Optional
import json


class DatabaseService:
    """数据库服务"""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self._ensure_database()

    def _get_connection(self) -> sqlite3.Connection:
        """获取数据库连接"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _ensure_database(self):
        """确保数据库和表存在"""
        conn = self._get_connection()
        cursor = conn.cursor()

        # 创建对话表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL DEFAULT '新对话',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 创建消息表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id INTEGER NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
            )
        """)

        # 创建配置表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS config (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.commit()
        conn.close()

    # 对话相关操作
    def create_conversation(self, title: str = "新对话") -> int:
        """创建新对话"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO conversations (title) VALUES (?)",
            (title,)
        )
        conversation_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return conversation_id

    def get_conversations(self) -> List[Dict]:
        """获取所有对话"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, title, created_at, updated_at
            FROM conversations
            ORDER BY updated_at DESC
        """)
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def get_conversation(self, conversation_id: int) -> Optional[Dict]:
        """获取单个对话"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, title, created_at, updated_at FROM conversations WHERE id = ?",
            (conversation_id,)
        )
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    def delete_conversation(self, conversation_id: int) -> bool:
        """删除对话"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM conversations WHERE id = ?",
            (conversation_id,)
        )
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return success

    def update_conversation_title(self, conversation_id: int, title: str) -> bool:
        """更新对话标题"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE conversations SET title = ?, updated_at = ? WHERE id = ?",
            (title, datetime.now().isoformat(), conversation_id)
        )
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return success

    # 消息相关操作
    def create_message(self, conversation_id: int, role: str, content: str) -> int:
        """创建消息"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO messages (conversation_id, role, content) VALUES (?, ?, ?)",
            (conversation_id, role, content)
        )
        message_id = cursor.lastrowid

        # 更新对话的更新时间
        cursor.execute(
            "UPDATE conversations SET updated_at = ? WHERE id = ?",
            (datetime.now().isoformat(), conversation_id)
        )

        conn.commit()
        conn.close()
        return message_id

    def get_messages(self, conversation_id: int, limit: Optional[int] = None) -> List[Dict]:
        """获取对话的消息"""
        conn = self._get_connection()
        cursor = conn.cursor()

        if limit:
            cursor.execute("""
                SELECT id, role, content, created_at
                FROM messages
                WHERE conversation_id = ?
                ORDER BY created_at ASC
                LIMIT ?
            """, (conversation_id, limit))
        else:
            cursor.execute("""
                SELECT id, role, content, created_at
                FROM messages
                WHERE conversation_id = ?
                ORDER BY created_at ASC
            """, (conversation_id,))

        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def get_recent_messages(self, conversation_id: int, rounds: int) -> List[Dict]:
        """获取最近N轮对话（每轮包括user和assistant）"""
        messages = self.get_messages(conversation_id)
        # 每轮对话包含一条user消息和一条assistant回复
        # 取最后rounds轮的消息
        return messages[-(rounds * 2):] if len(messages) > (rounds * 2) else messages

    # 配置相关操作
    def set_config(self, key: str, value: str):
        """设置配置"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO config (key, value, updated_at)
            VALUES (?, ?, ?)
        """, (key, value, datetime.now().isoformat()))
        conn.commit()
        conn.close()

    def get_config(self, key: str) -> Optional[str]:
        """获取配置"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM config WHERE key = ?", (key,))
        row = cursor.fetchone()
        conn.close()
        return row["value"] if row else None

    def get_all_config(self) -> Dict[str, str]:
        """获取所有配置"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT key, value FROM config")
        rows = cursor.fetchall()
        conn.close()
        return {row["key"]: row["value"] for row in rows}
