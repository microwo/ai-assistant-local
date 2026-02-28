"""
AI助手本地服务 - Flask主应用
"""
from flask import Flask, request, jsonify, render_template
from config import config
from services.db_service import DatabaseService
from services.zhipu_service import ZhipuService
import os

# 初始化Flask应用
app = Flask(__name__)
app.secret_key = config.SECRET_KEY

# 初始化服务
db = DatabaseService(config.DATABASE_PATH)
zhipu_service = None


def get_zhipu_service():
    """获取智谱AI服务实例"""
    global zhipu_service

    # 从数据库获取API Key
    api_key = db.get_config("zhipu_api_key")

    # 如果数据库中没有，尝试从配置获取
    if not api_key:
        api_key = config.ZHIPU_API_KEY

    if not api_key:
        return None

    # 如果服务不存在或API Key变了，重新创建
    if zhipu_service is None or zhipu_service.client.api_key != api_key:
        model = db.get_config("model") or config.MODEL
        zhipu_service = ZhipuService(api_key=api_key, model=model)

    return zhipu_service


# ===== 路由 =====

@app.route("/")
def index():
    """首页"""
    return render_template("index.html")


# ===== API路由 =====

# 对话相关
@app.route("/api/conversations", methods=["GET", "POST"])
def conversations():
    """获取或创建对话"""
    if request.method == "GET":
        conversations = db.get_conversations()
        return jsonify({"conversations": conversations})

    elif request.method == "POST":
        data = request.get_json()
        title = data.get("title", "新对话")
        conversation_id = db.create_conversation(title)
        conversation = db.get_conversation(conversation_id)
        return jsonify(conversation), 201


@app.route("/api/conversations/<int:conversation_id>", methods=["DELETE", "PUT"])
def conversation_detail(conversation_id: int):
    """删除或更新对话"""
    if request.method == "DELETE":
        success = db.delete_conversation(conversation_id)
        if success:
            return jsonify({"success": True})
        else:
            return jsonify({"error": "Conversation not found"}), 404

    elif request.method == "PUT":
        data = request.get_json()
        title = data.get("title")
        if title:
            success = db.update_conversation_title(conversation_id, title)
            if success:
                conversation = db.get_conversation(conversation_id)
                return jsonify(conversation)
            else:
                return jsonify({"error": "Conversation not found"}), 404
        else:
            return jsonify({"error": "Title is required"}), 400


@app.route("/api/conversations/<int:conversation_id>/messages", methods=["GET"])
def conversation_messages(conversation_id: int):
    """获取对话的消息"""
    messages = db.get_messages(conversation_id)
    return jsonify({"messages": messages})


# 消息相关
@app.route("/api/conversations/<int:conversation_id>/messages", methods=["POST"])
def send_message(conversation_id: int):
    """发送消息"""
    data = request.get_json()
    content = data.get("content", "").strip()

    if not content:
        return jsonify({"error": "Content is required"}), 400

    # 验证对话是否存在
    conversation = db.get_conversation(conversation_id)
    if not conversation:
        return jsonify({"error": "Conversation not found"}), 404

    # 获取智谱AI服务
    zhipu = get_zhipu_service()
    if not zhipu:
        return jsonify({"error": "Zhipu AI API key not configured"}), 500

    # 保存用户消息
    db.create_message(conversation_id, "user", content)

    # 获取历史消息
    max_rounds = int(db.get_config("max_history_rounds") or config.MAX_HISTORY_ROUNDS)
    history_messages = db.get_recent_messages(conversation_id, max_rounds)

    # 转换为OpenAI格式（去除AI尚未回复的最新用户消息）
    history = [msg["role"] for msg in history_messages]
    openai_history = [
        {"role": msg["role"], "content": msg["content"]}
        for msg in history_messages
        if msg["role"] != "user" or msg != history_messages[-1]  # 去除刚刚保存的用户消息
    ]

    # 获取系统提示词
    system_prompt = db.get_config("system_prompt") or config.SYSTEM_PROMPT

    # 获取温度和最大token数
    temperature = float(db.get_config("temperature") or config.TEMPERATURE)
    max_tokens = int(db.get_config("max_tokens") or config.MAX_TOKENS)

    # 调用智谱AI
    response = zhipu.chat_with_history(
        user_message=content,
        history=openai_history,
        system_prompt=system_prompt,
        temperature=temperature,
        max_tokens=max_tokens
    )

    if "error" in response:
        return jsonify({"error": response["error"]}), 500

    # 保存AI回复
    ai_content = response["content"]
    db.create_message(conversation_id, "assistant", ai_content)

    return jsonify({
        "message": {
            "role": "assistant",
            "content": ai_content
        },
        "usage": response.get("usage", {})
    })


# 配置相关
@app.route("/api/config", methods=["GET", "POST"])
def config_api():
    """获取或更新配置"""
    if request.method == "GET":
        all_config = db.get_all_config()

        # 返回配置，敏感信息隐藏
        safe_config = {}
        for key, value in all_config.items():
            if "api_key" in key.lower():
                safe_config[key] = "***已配置***" if value else ""
            else:
                safe_config[key] = value

        # 添加默认值
        if "model" not in safe_config:
            safe_config["model"] = config.MODEL
        if "temperature" not in safe_config:
            safe_config["temperature"] = config.TEMPERATURE
        if "max_tokens" not in safe_config:
            safe_config["max_tokens"] = config.MAX_TOKENS
        if "max_history_rounds" not in safe_config:
            safe_config["max_history_rounds"] = config.MAX_HISTORY_ROUNDS
        if "system_prompt" not in safe_config:
            safe_config["system_prompt"] = config.SYSTEM_PROMPT

        return jsonify(safe_config)

    elif request.method == "POST":
        data = request.get_json()

        # 验证API Key
        if "zhipu_api_key" in data:
            api_key = data["zhipu_api_key"]
            if api_key and api_key != "***已配置***":
                # 测试API Key是否有效
                test_service = ZhipuService(api_key=api_key)
                if test_service.validate_api_key():
                    db.set_config("zhipu_api_key", api_key)
                else:
                    return jsonify({"error": "Invalid API key"}), 400

        # 保存其他配置
        if "model" in data:
            db.set_config("model", data["model"])
        if "temperature" in data:
            db.set_config("temperature", str(data["temperature"]))
        if "max_tokens" in data:
            db.set_config("max_tokens", str(data["max_tokens"]))
        if "max_history_rounds" in data:
            db.set_config("max_history_rounds", str(data["max_history_rounds"]))
        if "system_prompt" in data:
            db.set_config("system_prompt", data["system_prompt"])

        return jsonify({"success": True})


@app.route("/api/config/validate", methods=["POST"])
def validate_config():
    """验证配置是否有效"""
    zhipu = get_zhipu_service()
    if not zhipu:
        return jsonify({"valid": False, "error": "API key not configured"})

    valid = zhipu.validate_api_key()
    return jsonify({"valid": valid})


# 错误处理
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Not found"}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500


if __name__ == "__main__":
    # 确保data目录存在
    os.makedirs("data", exist_ok=True)

    # 运行应用
    app.run(
        host=config.HOST,
        port=config.PORT,
        debug=config.DEBUG
    )
