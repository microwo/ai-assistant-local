// 当前对话ID
let currentConversationId = null;

// 初始化
document.addEventListener('DOMContentLoaded', () => {
    loadConversations();
});

// 加载对话列表
async function loadConversations() {
    try {
        const response = await fetch('/api/conversations');
        const data = await response.json();

        const conversationsList = document.getElementById('conversationsList');
        conversationsList.innerHTML = '';

        data.conversations.forEach(conversation => {
            const item = document.createElement('div');
            item.className = 'conversation-item';
            item.dataset.id = conversation.id;
            item.innerHTML = `
                <div class="conversation-item-title">${escapeHtml(conversation.title)}</div>
                <div class="conversation-item-time">${formatTime(conversation.updated_at)}</div>
            `;
            item.onclick = () => loadConversation(conversation.id);
            conversationsList.appendChild(item);
        });
    } catch (error) {
        console.error('加载对话列表失败:', error);
    }
}

// 加载对话
async function loadConversation(conversationId) {
    currentConversationId = conversationId;

    // 更新侧边栏高亮
    document.querySelectorAll('.conversation-item').forEach(item => {
        item.classList.toggle('active', parseInt(item.dataset.id) === conversationId);
    });

    // 加载消息
    try {
        const response = await fetch(`/api/conversations/${conversationId}/messages`);
        const data = await response.json();

        const chatMessages = document.getElementById('chatMessages');
        chatMessages.innerHTML = '';

        if (data.messages.length === 0) {
            chatMessages.innerHTML = `
                <div class="empty-state">
                    <p>开始新的对话吧</p>
                </div>
            `;
        } else {
            data.messages.forEach(message => {
                appendMessage(message.role, message.content);
            });
        }

        // 滚动到底部
        scrollToBottom();
    } catch (error) {
        console.error('加载对话失败:', error);
    }
}

// 创建新对话
async function createNewConversation() {
    try {
        const response = await fetch('/api/conversations', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ title: '新对话' })
        });

        const conversation = await response.json();

        // 重新加载对话列表
        await loadConversations();

        // 加载新对话
        await loadConversation(conversation.id);

        // 清空输入框
        document.getElementById('messageInput').value = '';
    } catch (error) {
        console.error('创建对话失败:', error);
        alert('创建对话失败');
    }
}

// 发送消息
async function sendMessage() {
    const input = document.getElementById('messageInput');
    const content = input.value.trim();

    if (!content) return;

    if (!currentConversationId) {
        alert('请先选择或创建一个对话');
        return;
    }

    // 清空输入框
    input.value = '';

    // 显示用户消息
    appendMessage('user', content);
    scrollToBottom();

    // 显示加载状态
    const loadingDiv = document.createElement('div');
    loadingDiv.className = 'message assistant loading';
    loadingDiv.id = 'loadingMessage';
    loadingDiv.innerHTML = '<div class="message-content">AI正在思考</div>';
    document.getElementById('chatMessages').appendChild(loadingDiv);
    scrollToBottom();

    try {
        const response = await fetch(`/api/conversations/${currentConversationId}/messages`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ content })
        });

        // 移除加载状态
        document.getElementById('loadingMessage').remove();

        if (response.ok) {
            const data = await response.json();

            // 显示AI回复
            appendMessage('assistant', data.message.content);
            scrollToBottom();

            // 刷新对话列表（更新时间）
            await loadConversations();
        } else {
            const error = await response.json();
            appendMessage('assistant', `错误: ${error.error}`);
            scrollToBottom();
        }
    } catch (error) {
        document.getElementById('loadingMessage').remove();
        console.error('发送消息失败:', error);
        appendMessage('assistant', '发送消息失败，请检查网络连接');
        scrollToBottom();
    }
}

// 添加消息到界面
function appendMessage(role, content) {
    const chatMessages = document.getElementById('chatMessages');

    // 移除空状态
    const emptyState = chatMessages.querySelector('.empty-state');
    if (emptyState) {
        emptyState.remove();
    }

    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}`;
    messageDiv.innerHTML = `
        <div class="message-role">${role === 'user' ? '你' : 'AI'}</div>
        <div class="message-content">${escapeHtml(content)}</div>
    `;

    chatMessages.appendChild(messageDiv);
}

// 滚动到底部
function scrollToBottom() {
    const chatMessages = document.getElementById('chatMessages');
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// 显示配置
async function showConfig() {
    const modal = document.getElementById('configModal');

    // 加载配置
    try {
        const response = await fetch('/api/config');
        const config = await response.json();

        document.getElementById('apiKeyInput').value = config.zhipu_api_key || '';
        document.getElementById('modelSelect').value = config.model || 'glm-4';
        document.getElementById('temperatureInput').value = config.temperature || 0.7;
        document.getElementById('maxTokensInput').value = config.max_tokens || 2000;
        document.getElementById('maxHistoryRoundsInput').value = config.max_history_rounds || 10;
        document.getElementById('systemPromptInput').value = config.system_prompt || '你是一个有用的AI助手。';
    } catch (error) {
        console.error('加载配置失败:', error);
    }

    modal.style.display = 'flex';
}

// 隐藏配置
function hideConfig() {
    document.getElementById('configModal').style.display = 'none';
}

// 保存配置
async function saveConfig() {
    const config = {
        zhipu_api_key: document.getElementById('apiKeyInput').value,
        model: document.getElementById('modelSelect').value,
        temperature: parseFloat(document.getElementById('temperatureInput').value),
        max_tokens: parseInt(document.getElementById('maxTokensInput').value),
        max_history_rounds: parseInt(document.getElementById('maxHistoryRoundsInput').value),
        system_prompt: document.getElementById('systemPromptInput').value
    };

    try {
        const response = await fetch('/api/config', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(config)
        });

        if (response.ok) {
            alert('配置保存成功');
            hideConfig();
        } else {
            const error = await response.json();
            alert(`保存失败: ${error.error}`);
        }
    } catch (error) {
        console.error('保存配置失败:', error);
        alert('保存配置失败');
    }
}

// 处理键盘事件
function handleKeyDown(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        sendMessage();
    }
}

// HTML转义
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// 格式化时间
function formatTime(isoString) {
    const date = new Date(isoString);
    const now = new Date();
    const diff = now - date;

    const oneMinute = 60 * 1000;
    const oneHour = 60 * oneMinute;
    const oneDay = 24 * oneHour;

    if (diff < oneMinute) {
        return '刚刚';
    } else if (diff < oneHour) {
        return `${Math.floor(diff / oneMinute)}分钟前`;
    } else if (diff < oneDay) {
        return `${Math.floor(diff / oneHour)}小时前`;
    } else {
        return date.toLocaleDateString('zh-CN');
    }
}

// 点击模态框外部关闭
document.getElementById('configModal').addEventListener('click', (e) => {
    if (e.target.id === 'configModal') {
        hideConfig();
    }
});
