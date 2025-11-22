// Chat functionality
const chatMessages = document.getElementById('chatMessages');
const queryForm = document.getElementById('queryForm');
const queryInput = document.getElementById('queryInput');
const sendButton = document.getElementById('sendButton');

// Fill example query
function fillExample(element) {
    queryInput.value = element.textContent;
    queryInput.focus();
}

// Add message to chat
function addMessage(content, isUser = false) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${isUser ? 'message-user' : 'message-assistant'}`;
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    
    if (isUser) {
        contentDiv.textContent = content;
    } else {
        // Format assistant response with line breaks and lists
        const formattedContent = formatResponse(content);
        contentDiv.innerHTML = formattedContent;
    }
    
    messageDiv.appendChild(contentDiv);
    chatMessages.appendChild(messageDiv);
    
    // Scroll to bottom
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Format response text
function formatResponse(text) {
    // Split by newlines and process
    const lines = text.split('\n');
    let html = '';
    let inList = false;
    
    for (let line of lines) {
        line = line.trim();
        
        if (!line) {
            if (inList) {
                html += '</ul>';
                inList = false;
            }
            html += '<br>';
            continue;
        }
        
        // Check if line starts with dash or bullet
        if (line.startsWith('-') || line.startsWith('•')) {
            if (!inList) {
                html += '<ul>';
                inList = true;
            }
            const itemText = line.substring(1).trim();
            html += `<li>${itemText}</li>`;
        } else {
            if (inList) {
                html += '</ul>';
                inList = false;
            }
            html += `<p>${line}</p>`;
        }
    }
    
    if (inList) {
        html += '</ul>';
    }
    
    return html;
}

// Show loading indicator
function showLoading() {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message message-assistant';
    messageDiv.id = 'loadingMessage';
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content loading';
    
    for (let i = 0; i < 3; i++) {
        const dot = document.createElement('div');
        dot.className = 'loading-dot';
        contentDiv.appendChild(dot);
    }
    
    messageDiv.appendChild(contentDiv);
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Remove loading indicator
function removeLoading() {
    const loadingMessage = document.getElementById('loadingMessage');
    if (loadingMessage) {
        loadingMessage.remove();
    }
}

// Show error message
function showError(message) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    errorDiv.textContent = `Error: ${message}`;
    chatMessages.appendChild(errorDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Handle form submission
queryForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const query = queryInput.value.trim();
    if (!query) return;
    
    console.log('Submitting query:', query);
    
    // Remove welcome message if it exists
    const welcomeMessage = document.querySelector('.welcome-message');
    if (welcomeMessage) {
        welcomeMessage.remove();  // Just remove the welcome message, not its parent
    }
    
    // Add user message
    addMessage(query, true);
    
    // Clear input and disable button
    queryInput.value = '';
    sendButton.disabled = true;
    
    // Show loading
    showLoading();
    
    try {
        // Send request to backend
        console.log('Sending request to /api/query');
        const response = await fetch('/api/query', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ query: query })
        });
        
        console.log('Response status:', response.status);
        const data = await response.json();
        console.log('Response data:', data);
        
        // Remove loading
        removeLoading();
        
        if (data.success) {
            // Add assistant response
            console.log('Adding response:', data.response);
            addMessage(data.response);
        } else {
            // Show error
            console.error('Error from server:', data.error);
            showError(data.error || 'Failed to process your request');
        }
        
    } catch (error) {
        console.error('Fetch error:', error);
        removeLoading();
        showError('Failed to connect to the server. Please try again.');
    } finally {
        // Re-enable button
        sendButton.disabled = false;
        queryInput.focus();
    }
});

// Focus input on load
window.addEventListener('load', () => {
    queryInput.focus();
});

// Keyboard shortcut (Ctrl/Cmd + K to focus input)
document.addEventListener('keydown', (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        queryInput.focus();
    }
});
