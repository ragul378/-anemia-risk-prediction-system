/**
 * IronHer AI - Top-Right Nutritional Chatbot Copilot Script
 */

document.addEventListener('DOMContentLoaded', () => {
    const chatLauncher = document.getElementById('chatLauncherBtn');
    const navChatBtn = document.getElementById('navChatBtn');
    const chatPanel = document.getElementById('chatPanel');
    const closeChatBtn = document.getElementById('closeChatBtn');
    const minimizeChatBtn = document.getElementById('minimizeChatBtn');
    const chatForm = document.getElementById('chatForm');
    const chatInput = document.getElementById('chatInput');
    const chatMessages = document.getElementById('chatMessages');
    const chatQuickPills = document.querySelectorAll('.chat-quick-pill');

    function openChat() {
        if (chatPanel) {
            chatPanel.classList.remove('d-none');
            chatPanel.classList.add('chat-panel-visible');
            setTimeout(() => {
                if (chatInput) chatInput.focus();
            }, 200);
        }
    }

    function closeChat() {
        if (chatPanel) {
            chatPanel.classList.add('d-none');
            chatPanel.classList.remove('chat-panel-visible');
        }
    }

    if (chatLauncher) {
        chatLauncher.addEventListener('click', () => {
            if (chatPanel.classList.contains('d-none')) {
                openChat();
            } else {
                closeChat();
            }
        });
    }

    if (navChatBtn) {
        navChatBtn.addEventListener('click', (e) => {
            e.preventDefault();
            openChat();
        });
    }

    if (closeChatBtn) {
        closeChatBtn.addEventListener('click', closeChat);
    }

    if (minimizeChatBtn) {
        minimizeChatBtn.addEventListener('click', closeChat);
    }

    // Handle quick suggestion pills
    chatQuickPills.forEach(pill => {
        pill.addEventListener('click', () => {
            const query = pill.getAttribute('data-query');
            if (query && chatInput) {
                chatInput.value = query;
                sendMessage(query);
            }
        });
    });

    // Helper: format basic markdown bold and bullets into clean HTML
    function formatText(text) {
        let formatted = text
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/• (.*)/g, '• $1')
            .replace(/\n\n/g, '<br><br>')
            .replace(/\n/g, '<br>');
        return formatted;
    }

    function appendMessage(sender, text) {
        const msgDiv = document.createElement('div');
        msgDiv.className = sender === 'user' 
            ? 'd-flex justify-content-end mb-3' 
            : 'd-flex justify-content-start mb-3';

        const bubble = document.createElement('div');
        bubble.className = sender === 'user' 
            ? 'p-3 rounded-3 text-white bg-primary-custom shadow-sm user-bubble' 
            : 'p-3 rounded-3 bg-white text-dark border shadow-sm bot-bubble';
        bubble.style.maxWidth = '85%';
        bubble.style.fontSize = '0.88rem';
        bubble.style.lineHeight = '1.45';

        bubble.innerHTML = formatText(text);
        msgDiv.appendChild(bubble);
        chatMessages.appendChild(msgDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function showTyping() {
        const typingDiv = document.createElement('div');
        typingDiv.id = 'chatTypingIndicator';
        typingDiv.className = 'd-flex justify-content-start mb-3';
        typingDiv.innerHTML = `
            <div class="p-2 px-3 rounded-3 bg-light border text-muted small">
                <span class="spinner-grow spinner-grow-sm text-danger me-1" role="status"></span>
                <span>AI Copilot is thinking...</span>
            </div>
        `;
        chatMessages.appendChild(typingDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function removeTyping() {
        const typing = document.getElementById('chatTypingIndicator');
        if (typing) typing.remove();
    }

    function sendMessage(msgText) {
        const text = msgText || (chatInput ? chatInput.value.trim() : '');
        if (!text) return;

        appendMessage('user', text);
        if (chatInput) chatInput.value = '';

        showTyping();

        fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ message: text })
        })
        .then(response => response.json())
        .then(data => {
            removeTyping();
            appendMessage('bot', data.reply || 'Thank you for your question. Please ask about iron sources or enhancers!');
        })
        .catch(err => {
            removeTyping();
            appendMessage('bot', '⚠️ Connection error. Please ensure the Flask server is running and try again.');
            console.error('Chat error:', err);
        });
    }

    if (chatForm) {
        chatForm.addEventListener('submit', (e) => {
            e.preventDefault();
            sendMessage();
        });
    }
});
