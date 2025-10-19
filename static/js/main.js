// QaderiChat - Main JavaScript File

class QaderiChat {
    constructor() {
        this.apiEndpoint = '/api/send-message/';
        this.messagesEndpoint = '/api/get-messages/';
        this.clearEndpoint = '/api/clear-chat/';
        this.isTyping = false;
        this.messageHistory = [];
        
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.setupTheme();
        this.loadChatHistory();
        this.setupAutoResize();
    }
    
    setupEventListeners() {
        // Send message on button click
        const sendButton = document.getElementById('sendButton');
        if (sendButton) {
            sendButton.addEventListener('click', () => this.sendMessage());
        }
        
        // Send message on Enter key (Shift+Enter for new line)
        const chatInput = document.getElementById('chatInput');
        if (chatInput) {
            chatInput.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    this.sendMessage();
                }
            });
            
            // Show typing indicator
            chatInput.addEventListener('input', () => {
                this.updateSendButton();
            });
        }
        
        // Clear chat button
        const clearButton = document.getElementById('clearChat');
        if (clearButton) {
            clearButton.addEventListener('click', () => this.clearChat());
        }
        
        // Theme toggle
        const themeToggle = document.getElementById('themeToggle');
        if (themeToggle) {
            themeToggle.addEventListener('click', () => this.toggleTheme());
        }
    }
    
    setupTheme() {
        const savedTheme = localStorage.getItem('qaderichat-theme') || 'light';
        this.setTheme(savedTheme);
    }
    
    setTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem('qaderichat-theme', theme);
        
        const themeIcon = document.querySelector('#themeToggle i');
        if (themeIcon) {
            themeIcon.className = theme === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
        }
    }
    
    toggleTheme() {
        const currentTheme = document.documentElement.getAttribute('data-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        this.setTheme(newTheme);
    }
    
    setupAutoResize() {
        const chatInput = document.getElementById('chatInput');
        if (chatInput) {
            chatInput.addEventListener('input', function() {
                this.style.height = 'auto';
                this.style.height = Math.min(this.scrollHeight, 120) + 'px';
            });
        }
    }
    
    async loadChatHistory() {
        try {
            const response = await fetch(this.messagesEndpoint);
            const data = await response.json();
            
            if (data.success && data.messages.length > 0) {
                this.hideWelcomeScreen();
                data.messages.forEach(message => {
                    this.displayMessage(message.content, message.type, false);
                });
                this.scrollToBottom();
            }
        } catch (error) {
            console.error('Error loading chat history:', error);
        }
    }
    
    async sendMessage() {
        const chatInput = document.getElementById('chatInput');
        const message = chatInput.value.trim();
        
        if (!message || this.isTyping) return;
        
        // Clear input and hide welcome screen
        chatInput.value = '';
        chatInput.style.height = 'auto';
        this.hideWelcomeScreen();
        this.updateSendButton();
        
        // Display user message
        this.displayMessage(message, 'user');
        
        // Show typing indicator
        this.showTypingIndicator();
        this.isTyping = true;
        
        try {
            const response = await fetch(this.apiEndpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify({ message: message })
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.displayMessage(data.assistant_message.content, 'assistant');
            } else {
                this.displayMessage(
                    data.assistant_message?.content || 'Sorry, I encountered an error. Please try again.',
                    'assistant'
                );
                this.showToast('error', data.error || 'An error occurred');
            }
        } catch (error) {
            console.error('Error sending message:', error);
            this.displayMessage(
                'Sorry, I\'m having trouble connecting. Please check your internet connection and try again.',
                'assistant'
            );
            this.showToast('error', 'Network error occurred');
        } finally {
            this.hideTypingIndicator();
            this.isTyping = false;
            this.updateSendButton();
        }
    }
    
    displayMessage(content, type, animate = true) {
        const messagesContainer = document.getElementById('chatMessages');
        if (!messagesContainer) return;
        
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}`;
        if (animate) {
            messageDiv.style.opacity = '0';
            messageDiv.style.transform = 'translateY(20px)';
        }
        
        const avatar = document.createElement('div');
        avatar.className = 'message-avatar';
        avatar.innerHTML = type === 'user' ? '<i class="fas fa-user"></i>' : '<i class="fas fa-robot"></i>';
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        
        // Process markdown and sanitize HTML
        if (typeof marked !== 'undefined' && typeof DOMPurify !== 'undefined') {
            contentDiv.innerHTML = DOMPurify.sanitize(marked.parse(content));
        } else {
            contentDiv.textContent = content;
        }
        
        const timeDiv = document.createElement('div');
        timeDiv.className = 'message-time';
        timeDiv.textContent = new Date().toLocaleTimeString();
        
        if (type === 'user') {
            messageDiv.appendChild(contentDiv);
            messageDiv.appendChild(avatar);
        } else {
            messageDiv.appendChild(avatar);
            messageDiv.appendChild(contentDiv);
        }
        
        messageDiv.appendChild(timeDiv);
        messagesContainer.appendChild(messageDiv);
        
        if (animate) {
            // Trigger animation
            requestAnimationFrame(() => {
                messageDiv.style.transition = 'all 0.3s ease-out';
                messageDiv.style.opacity = '1';
                messageDiv.style.transform = 'translateY(0)';
            });
        }
        
        this.scrollToBottom();
    }

    showTypingIndicator() {
        const messagesContainer = document.getElementById('chatMessages');
        if (!messagesContainer) return;

        const typingDiv = document.createElement('div');
        typingDiv.className = 'typing-indicator';
        typingDiv.id = 'typingIndicator';

        typingDiv.innerHTML = `
            <div class="message-avatar">
                <i class="fas fa-robot"></i>
            </div>
            <div class="message-content">
                <span>QaderiChat is typing</span>
                <div class="typing-dots">
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                </div>
            </div>
        `;

        messagesContainer.appendChild(typingDiv);
        this.scrollToBottom();
    }

    hideTypingIndicator() {
        const typingIndicator = document.getElementById('typingIndicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }

    hideWelcomeScreen() {
        const welcomeScreen = document.getElementById('welcomeScreen');
        if (welcomeScreen) {
            welcomeScreen.style.display = 'none';
        }
    }

    updateSendButton() {
        const sendButton = document.getElementById('sendButton');
        const chatInput = document.getElementById('chatInput');

        if (sendButton && chatInput) {
            const hasText = chatInput.value.trim().length > 0;
            sendButton.disabled = !hasText || this.isTyping;
        }
    }

    scrollToBottom() {
        const messagesContainer = document.getElementById('chatMessages');
        if (messagesContainer) {
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }
    }

    async clearChat() {
        if (!confirm('Are you sure you want to clear the chat history?')) {
            return;
        }

        try {
            const response = await fetch(this.clearEndpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                }
            });

            const data = await response.json();

            if (data.success) {
                const messagesContainer = document.getElementById('chatMessages');
                if (messagesContainer) {
                    messagesContainer.innerHTML = '';
                }

                const welcomeScreen = document.getElementById('welcomeScreen');
                if (welcomeScreen) {
                    welcomeScreen.style.display = 'flex';
                }

                this.showToast('success', 'Chat history cleared successfully');
            } else {
                this.showToast('error', 'Failed to clear chat history');
            }
        } catch (error) {
            console.error('Error clearing chat:', error);
            this.showToast('error', 'Network error occurred');
        }
    }

    showToast(type, message) {
        const toastId = type === 'error' ? 'errorToast' : 'successToast';
        const bodyId = type === 'error' ? 'errorToastBody' : 'successToastBody';

        const toast = document.getElementById(toastId);
        const toastBody = document.getElementById(bodyId);

        if (toast && toastBody) {
            toastBody.textContent = message;
            const bsToast = new bootstrap.Toast(toast);
            bsToast.show();
        }
    }

    getCSRFToken() {
        // First try to get from window variable
        if (window.csrfToken) {
            return window.csrfToken;
        }

        // Then try cookies
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            const [name, value] = cookie.trim().split('=');
            if (name === 'csrftoken') {
                return value;
            }
        }

        // Fallback: try to get from meta tag
        const csrfMeta = document.querySelector('meta[name="csrf-token"]');
        return csrfMeta ? csrfMeta.getAttribute('content') : '';
    }
}

// Initialize the chat application when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.qaderiChat = new QaderiChat();
});

// Utility functions
function formatTime(date) {
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
