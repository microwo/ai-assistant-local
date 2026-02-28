"""
智谱AI服务
"""
from zhipuai import ZhipuAI
from typing import List, Dict, Optional


class ZhipuService:
    """智谱AI服务"""

    def __init__(self, api_key: str, model: str = "glm-4"):
        self.client = ZhipuAI(api_key=api_key)
        self.model = model

    def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        stream: bool = False
    ) -> Dict:
        """
        发起聊天请求

        Args:
            messages: 消息列表，格式为 [{"role": "user", "content": "..."}]
            temperature: 温度参数，0-1之间
            max_tokens: 最大token数
            stream: 是否使用流式响应

        Returns:
            响应结果
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=stream
            )

            if stream:
                # 流式响应需要特殊处理，这里暂时不实现
                return {"error": "Streaming not implemented yet"}

            # 提取回复内容
            return {
                "content": response.choices[0].message.content,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                },
                "model": response.model,
                "finish_reason": response.choices[0].finish_reason
            }

        except Exception as e:
            return {
                "error": str(e),
                "content": None
            }

    def chat_with_history(
        self,
        user_message: str,
        history: List[Dict[str, str]],
        system_prompt: str = "你是一个有用的AI助手。",
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> Dict:
        """
        使用历史记录进行聊天

        Args:
            user_message: 用户消息
            history: 历史消息列表
            system_prompt: 系统提示词
            temperature: 温度参数
            max_tokens: 最大token数

        Returns:
            响应结果
        """
        # 构建消息列表
        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(history)
        messages.append({"role": "user", "content": user_message})

        return self.chat(messages, temperature, max_tokens)

    def validate_api_key(self) -> bool:
        """验证API Key是否有效"""
        try:
            response = self.chat(
                messages=[{"role": "user", "content": "测试"}],
                max_tokens=10
            )
            return "error" not in response
        except Exception:
            return False
