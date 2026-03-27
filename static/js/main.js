/**
 * Sign Language App - Frontend JavaScript
 * Handles UI interactions and API communication
 */

// ==========================================
// Global Variables
// ==========================================
let updateInterval = null;
let historyUpdateInterval = null;
let lastPrediction = '?';
let lastConfidence = 0;
let autoAdd = true;
let soundEnabled = true;

// ==========================================
// Initialization
// ==========================================
document.addEventListener('DOMContentLoaded', function() {
    console.log('[INFO] Initializing Sign Language App...');
    
    // Check app health
    checkAppHealth();
    
    // Start updating prediction display
    startPredictionUpdates();
    
    // Start updating history
    startHistoryUpdates();
    
    // Setup event listeners
    setupEventListeners();
    
    // Load user preferences
    loadPreferences();
    
    console.log('[SUCCESS] App initialized!');
});

// ==========================================
// API Functions
// ==========================================

/**
 * Check if the app is running correctly
 */
function checkAppHealth() {
    fetch('/api/health')
        .then(response => response.json())
        .then(data => {
            const statusDot = document.getElementById('statusDot');
            const statusText = document.getElementById('statusText');
            
            if (data.status === 'healthy' && data.model_loaded) {
                statusDot.classList.add('active');
                statusDot.classList.remove('error');
                statusText.textContent = 'Connected';
                console.log('[SUCCESS] App is healthy');
            } else {
                statusDot.classList.add('error');
                statusDot.classList.remove('active');
                statusText.textContent = 'Error';
                console.error('[ERROR] App health check failed');
            }
        })
        .catch(error => {
            console.error('[ERROR] Health check failed:', error);
            document.getElementById('statusDot').classList.add('error');
            document.getElementById('statusText').textContent = 'Disconnected';
        });
}

/**
 * Fetch current prediction from server
 */
function getPrediction() {
    fetch('/api/prediction')
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                updatePredictionDisplay(data.character, data.confidence);
            }
        })
        .catch(error => console.error('[ERROR] Failed to get prediction:', error));
}

/**
 * Fetch prediction history from server
 */
function getHistory() {
    fetch('/api/history')
        .then(response => response.json())
        .then(data => {
            if (data && data.history) {
                updateHistoryDisplay(data.history);
                document.getElementById('predictionCount').textContent = data.count;
            }
        })
        .catch(error => console.error('[ERROR] Failed to get history:', error));
}

/**
 * Get current detected text
 */
function getDetectedText() {
    return fetch('/api/detected_text')
        .then(response => response.json())
        .then(data => data.text)
        .catch(error => {
            console.error('[ERROR] Failed to get text:', error);
            return '';
        });
}

/**
 * Update detected text on server
 */
function updateDetectedText(action, char = null) {
    const payload = { action };
    if (char) {
        payload.char = char;
    }
    
    return fetch('/api/detected_text', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            document.getElementById('displayedText').textContent = data.text;
            return data.text;
        }
    })
    .catch(error => console.error('[ERROR] Failed to update text:', error));
}

// ==========================================
// Display Update Functions
// ==========================================

/**
 * Update prediction display
 */
function updatePredictionDisplay(character, confidence) {
    // Extract character from display format (e.g., "'A'" -> "A")
    const cleanChar = character.replace(/'/g, '');
    
    document.getElementById('predictedChar').textContent = cleanChar;
    
    const confidencePercent = Math.round(confidence);
    document.getElementById('confidenceFill').style.width = confidence + '%';
    document.getElementById('confidenceText').textContent = confidencePercent + '%';
    
    // Update last updated time
    const now = new Date();
    const timeStr = now.toLocaleTimeString();
    document.getElementById('lastUpdated').textContent = timeStr;
    
    // Auto-add high confidence predictions
    if (autoAdd && confidence > 80 && cleanChar !== '?' && cleanChar !== lastPrediction) {
        playSound('success');
        addCharToText(cleanChar);
    }
    
    lastPrediction = cleanChar;
    lastConfidence = confidence;
}

/**
 * Update history display
 */
function updateHistoryDisplay(history) {
    const container = document.getElementById('historyContainer');
    
    if (history.length === 0) {
        container.innerHTML = '<p class="empty-state">No predictions yet. Start using the app!</p>';
        return;
    }
    
    container.innerHTML = '';
    
    // Show last 30 in reverse order (newest first)
    history.slice().reverse().forEach(item => {
        const element = document.createElement('div');
        element.className = 'history-item';
        element.innerHTML = `
            <div class="history-char">${item.character.replace(/'/g, '')}</div>
            <div class="history-confidence">${Math.round(item.confidence)}%</div>
        `;
        container.appendChild(element);
    });
}

// ==========================================
// User Interaction Functions
// ==========================================

/**
 * Add current prediction to text
 */
function addCurrentPrediction() {
    if (lastPrediction && lastPrediction !== '?') {
        addCharToText(lastPrediction);
    }
}

/**
 * Add character to text display
 */
function addCharToText(char) {
    updateDetectedText('append', char);
    playSound('add');
}

/**
 * Clear all text
 */
function clearText() {
    if (confirm('Clear all text?')) {
        updateDetectedText('clear');
        playSound('clear');
    }
}

/**
 * Remove last character
 */
function removeLastChar() {
    updateDetectedText('backspace');
    playSound('backspace');
}

/**
 * Copy text to clipboard
 */
function copyToClipboard() {
    getDetectedText().then(text => {
        if (text) {
            navigator.clipboard.writeText(text)
                .then(() => {
                    showNotification('✓ Copied to clipboard!', 'success');
                    playSound('success');
                })
                .catch(err => {
                    console.error('[ERROR] Copy failed:', err);
                    showNotification('✗ Copy failed', 'error');
                });
        } else {
            showNotification('No text to copy', 'warning');
        }
    });
}

/**
 * Read text using browser's speech synthesis
 */
function speakText() {
    getDetectedText().then(text => {
        if (text) {
            if ('speechSynthesis' in window) {
                // Cancel any ongoing speech
                window.speechSynthesis.cancel();
                
                const utterance = new SpeechSynthesisUtterance(text);
                utterance.rate = 0.9;
                utterance.pitch = 1;
                utterance.volume = 1;
                
                window.speechSynthesis.speak(utterance);
                showNotification('🔊 Speaking...', 'success');
            } else {
                showNotification('Speech synthesis not supported', 'error');
            }
        } else {
            showNotification('No text to read', 'warning');
        }
    });
}

/**
 * Toggle webcam (placeholder)
 */
function toggleWebcam() {
    const btn = event.target.closest('button');
    const icon = btn.querySelector('.btn-icon');
    
    if (btn.classList.contains('active')) {
        btn.classList.remove('active');
        btn.textContent = '📹 Camera On';
        showNotification('Camera turned off', 'warning');
    } else {
        btn.classList.add('active');
        btn.innerHTML = '<span class="btn-icon">⏹️</span> Camera Off';
        showNotification('Camera turned on', 'success');
    }
}

/**
 * Capture snapshot from video feed (placeholder)
 */
function captureSnapshot() {
    showNotification('📸 Snapshot captured!', 'success');
    playSound('capture');
}

// ==========================================
// Update Loops
// ==========================================

/**
 * Start periodic prediction updates
 */
function startPredictionUpdates() {
    getPrediction();
    updateInterval = setInterval(() => {
        getPrediction();
    }, 500);
}

/**
 * Start periodic history updates
 */
function startHistoryUpdates() {
    getHistory();
    historyUpdateInterval = setInterval(() => {
        getHistory();
    }, 1000);
}

// ==========================================
// Event Listeners
// ==========================================

/**
 * Setup all event listeners
 */
function setupEventListeners() {
    // Settings checkboxes
    document.getElementById('autoAddCheckbox').addEventListener('change', (e) => {
        autoAdd = e.target.checked;
        savePreference('autoAdd', autoAdd);
    });
    
    document.getElementById('soundCheckbox').addEventListener('change', (e) => {
        soundEnabled = e.target.checked;
        savePreference('soundEnabled', soundEnabled);
    });
    
    // Keyboard shortcuts
    document.addEventListener('keydown', (e) => {
        if (e.code === 'Space') {
            e.preventDefault();
            addCurrentPrediction();
        } else if (e.code === 'Backspace') {
            e.preventDefault();
            removeLastChar();
        } else if (e.code === 'Delete') {
            e.preventDefault();
            clearText();
        }
    });
}

// ==========================================
// Utility Functions
// ==========================================

/**
 * Play sound effect
 */
function playSound(type = 'default') {
    if (!soundEnabled) return;
    
    const audioContext = new (window.AudioContext || window.webkitAudioContext)();
    const oscillator = audioContext.createOscillator();
    const gainNode = audioContext.createGain();
    
    oscillator.connect(gainNode);
    gainNode.connect(audioContext.destination);
    
    const now = audioContext.currentTime;
    gainNode.gain.setValueAtTime(0.1, now);
    gainNode.gain.exponentialRampToValueAtTime(0.01, now + 0.3);
    
    switch(type) {
        case 'success':
            oscillator.frequency.value = 800;
            oscillator.start(now);
            oscillator.stop(now + 0.2);
            break;
        case 'add':
            oscillator.frequency.value = 600;
            oscillator.start(now);
            oscillator.stop(now + 0.15);
            break;
        case 'backspace':
            oscillator.frequency.value = 400;
            oscillator.start(now);
            oscillator.stop(now + 0.1);
            break;
        case 'clear':
            oscillator.frequency.value = 300;
            oscillator.start(now);
            oscillator.stop(now + 0.2);
            break;
        case 'capture':
            oscillator.frequency.value = 1000;
            oscillator.start(now);
            oscillator.stop(now + 0.1);
            break;
        default:
            oscillator.frequency.value = 500;
            oscillator.start(now);
            oscillator.stop(now + 0.1);
    }
}

/**
 * Show notification to user
 */
function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 80px;
        right: 20px;
        background-color: var(--dark-surface);
        color: white;
        padding: 15px 20px;
        border-radius: 6px;
        border-left: 4px solid;
        border-color: ${type === 'success' ? '#4CAF50' : type === 'error' ? '#f44336' : '#ff9800'};
        z-index: 1000;
        animation: slideIn 0.3s ease;
        max-width: 300px;
        word-wrap: break-word;
    `;
    
    document.body.appendChild(notification);
    
    // Remove after 3 seconds
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

/**
 * Save user preference to localStorage
 */
function savePreference(key, value) {
    try {
        localStorage.setItem(`signlang_${key}`, JSON.stringify(value));
    } catch (error) {
        console.error('[ERROR] Failed to save preference:', error);
    }
}

/**
 * Load user preferences from localStorage
 */
function loadPreferences() {
    try {
        const savedAutoAdd = localStorage.getItem('signlang_autoAdd');
        const savedSound = localStorage.getItem('signlang_soundEnabled');
        
        if (savedAutoAdd !== null) {
            autoAdd = JSON.parse(savedAutoAdd);
            document.getElementById('autoAddCheckbox').checked = autoAdd;
        }
        
        if (savedSound !== null) {
            soundEnabled = JSON.parse(savedSound);
            document.getElementById('soundCheckbox').checked = soundEnabled;
        }
    } catch (error) {
        console.error('[ERROR] Failed to load preferences:', error);
    }
}

/**
 * Cleanup on page unload
 */
window.addEventListener('beforeunload', () => {
    if (updateInterval) clearInterval(updateInterval);
    if (historyUpdateInterval) clearInterval(historyUpdateInterval);
});

// ==========================================
// CSS Animation for Notifications
// ==========================================
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(400px);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(400px);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);

console.log('[INFO] JavaScript initialization complete');
