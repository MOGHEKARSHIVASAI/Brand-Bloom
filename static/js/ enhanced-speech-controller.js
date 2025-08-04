// Enhanced Centralized Speech Controller for Brand Bloom
class EnhancedSpeechController {
    constructor() {
        this.recognition = null;
        this.isListening = false;
        this.isInitialized = false;
        this.currentPage = this.detectCurrentPage();
        this.activeField = null;
        this.speechMetadata = {};
        this.debugMode = true;
        
        // Speech configuration
        this.config = {
            language: 'en-US',
            continuous: false,
            interimResults: false,
            maxAlternatives: 3,
            autoRestart: true,
            confidenceThreshold: 0.7
        };
        
        // Initialize immediately
        this.initialize();
    }

    initialize() {
        if (this.isInitialized) return;
        
        this.log('Initializing Enhanced Speech Controller...');
        
        // Check browser support
        if (!this.checkBrowserSupport()) {
            this.showNotification('Speech recognition is not supported in this browser. Please use Chrome, Firefox, or Edge.', 'error');
            return;
        }
        
        this.setupSpeechRecognition();
        this.createSpeechUI();
        this.setupEventListeners();
        this.addKeyboardShortcuts();
        this.enhanceExistingForms();
        
        this.isInitialized = true;
        this.log('Speech Controller initialized successfully');
        
        // Show welcome message
        setTimeout(() => {
            this.showNotification('🎤 Speech control is ready! Press Ctrl+Space or click the microphone to start.', 'success');
        }, 1000);
    }

    checkBrowserSupport() {
        return 'webkitSpeechRecognition' in window || 'SpeechRecognition' in window;
    }

    setupSpeechRecognition() {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        this.recognition = new SpeechRecognition();
        
        // Configure recognition
        Object.assign(this.recognition, this.config);
        
        // Event handlers
        this.recognition.onstart = () => this.handleSpeechStart();
        this.recognition.onend = () => this.handleSpeechEnd();
        this.recognition.onresult = (event) => this.handleSpeechResult(event);
        this.recognition.onerror = (event) => this.handleSpeechError(event);
        this.recognition.onnomatch = () => this.handleNoMatch();
    }

    createSpeechUI() {
        // Remove existing UI if any
        const existingUI = document.getElementById('enhanced-speech-ui');
        if (existingUI) existingUI.remove();
        
        // Create main speech UI container
        const speechUI = document.createElement('div');
        speechUI.id = 'enhanced-speech-ui';
        speechUI.innerHTML = this.getSpeechUIHTML();
        document.body.appendChild(speechUI);
        
        // Add CSS styles
        this.addSpeechStyles();
        
        // Setup UI event handlers
        this.setupUIEventHandlers();
    }

    getSpeechUIHTML() {
        return `
            <!-- Global Speech Control Button -->
            <div id="global-speech-control" class="speech-control-widget">
                <button id="global-speech-btn" class="speech-main-btn" title="Voice Control (Ctrl+Space)">
                    <div class="speech-btn-content">
                        <i class="fas fa-microphone speech-icon"></i>
                        <div class="speech-pulse-ring"></div>
                    </div>
                    <span class="speech-status">Click to speak</span>
                </button>
                
                <div class="speech-controls-panel">
                    <button id="speech-help-btn" class="speech-control-btn" title="Voice Commands Help">
                        <i class="fas fa-question-circle"></i>
                    </button>
                    <button id="speech-settings-btn" class="speech-control-btn" title="Speech Settings">
                        <i class="fas fa-cog"></i>
                    </button>
                </div>
            </div>

            <!-- Speech Listening Overlay -->
            <div id="speech-listening-overlay" class="speech-overlay">
                <div class="speech-overlay-content">
                    <div class="speech-visual-indicator">
                        <div class="speech-mic-icon">
                            <i class="fas fa-microphone"></i>
                        </div>
                        <div class="speech-sound-waves">
                            <div class="wave"></div>
                            <div class="wave"></div>
                            <div class="wave"></div>
                            <div class="wave"></div>
                        </div>
                    </div>
                    <h3 class="speech-overlay-title">Listening...</h3>
                    <p class="speech-overlay-subtitle" id="speech-interim-result">Say something...</p>
                    <div class="speech-overlay-actions">
                        <button id="speech-cancel-btn" class="speech-action-btn cancel">
                            <i class="fas fa-times"></i> Cancel
                        </button>
                    </div>
                </div>
            </div>

            <!-- Speech Help Panel -->
            <div id="speech-help-panel" class="speech-panel">
                <div class="speech-panel-header">
                    <h4><i class="fas fa-microphone me-2"></i>Voice Commands</h4>
                    <button id="close-help-btn" class="speech-close-btn">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
                <div class="speech-panel-content">
                    <div class="speech-help-section">
                        <h5>Navigation Commands</h5>
                        <div class="speech-commands">
                            <div class="speech-command">
                                <span class="command">"Go to website builder"</span>
                                <span class="description">Navigate to website tool</span>
                            </div>
                            <div class="speech-command">
                                <span class="command">"Open email tool"</span>
                                <span class="description">Navigate to email composer</span>
                            </div>
                            <div class="speech-command">
                                <span class="command">"Show feedback analyzer"</span>
                                <span class="description">Navigate to feedback tool</span>
                            </div>
                        </div>
                    </div>
                    
                    <div class="speech-help-section">
                        <h5>Form Filling Commands</h5>
                        <div class="speech-commands">
                            <div class="speech-command">
                                <span class="command">"Create website for my restaurant"</span>
                                <span class="description">Auto-fill website form</span>
                            </div>
                            <div class="speech-command">
                                <span class="command">"Generate marketing email"</span>
                                <span class="description">Auto-fill email form</span>
                            </div>
                            <div class="speech-command">
                                <span class="command">"Make promotional poster"</span>
                                <span class="description">Auto-fill poster form</span>
                            </div>
                        </div>
                    </div>
                    
                    <div class="speech-help-section">
                        <h5>Direct Actions</h5>
                        <div class="speech-commands">
                            <div class="speech-command">
                                <span class="command">"Analyze this feedback: [text]"</span>
                                <span class="description">Direct feedback analysis</span>
                            </div>
                            <div class="speech-command">
                                <span class="command">"Fill name with John Smith"</span>
                                <span class="description">Fill specific field</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Speech Settings Panel -->
            <div id="speech-settings-panel" class="speech-panel">
                <div class="speech-panel-header">
                    <h4><i class="fas fa-cog me-2"></i>Speech Settings</h4>
                    <button id="close-settings-btn" class="speech-close-btn">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
                <div class="speech-panel-content">
                    <div class="speech-setting">
                        <label for="speech-language">Language</label>
                        <select id="speech-language" class="speech-select">
                            <option value="en-US">English (US)</option>
                            <option value="en-GB">English (UK)</option>
                            <option value="hi-IN">Hindi</option>
                            <option value="te-IN">Telugu</option>
                        </select>
                    </div>
                    
                    <div class="speech-setting">
                        <label for="speech-confidence">Confidence Threshold</label>
                        <input type="range" id="speech-confidence" min="0.1" max="1" step="0.1" value="0.7" class="speech-range">
                        <span id="confidence-value">70%</span>
                    </div>
                    
                    <div class="speech-setting">
                        <label class="speech-checkbox">
                            <input type="checkbox" id="speech-auto-submit" checked>
                            <span class="checkmark"></span>
                            Auto-submit forms when confident
                        </label>
                    </div>
                    
                    <div class="speech-setting">
                        <label class="speech-checkbox">
                            <input type="checkbox" id="speech-notifications" checked>
                            <span class="checkmark"></span>
                            Show speech notifications
                        </label>
                    </div>
                    
                    <div class="speech-setting">
                        <button id="test-speech-btn" class="speech-test-btn">
                            <i class="fas fa-volume-up me-2"></i>Test Speech Recognition
                        </button>
                    </div>
                </div>
            </div>

            <!-- Speech Notification Container -->
            <div id="speech-notifications" class="speech-notifications-container"></div>
        `;
    }

    addSpeechStyles() {
        if (document.getElementById('enhanced-speech-styles')) return;
        
        const style = document.createElement('style');
        style.id = 'enhanced-speech-styles';
        style.textContent = `
            /* Enhanced Speech UI Styles */
            .speech-control-widget {
                position: fixed;
                bottom: 30px;
                right: 30px;
                z-index: 9999;
                display: flex;
                flex-direction: column;
                align-items: center;
                gap: 10px;
            }
            
            .speech-main-btn {
                position: relative;
                width: 70px;
                height: 70px;
                border-radius: 50%;
                border: none;
                background: linear-gradient(135deg, #DC2626, #EF4444);
                color: white;
                cursor: pointer;
                transition: all 0.3s ease;
                box-shadow: 0 4px 20px rgba(220, 38, 38, 0.3);
                overflow: hidden;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
            }
            
            .speech-main-btn:hover {
                transform: translateY(-3px);
                box-shadow: 0 6px 25px rgba(220, 38, 38, 0.4);
            }
            
            .speech-main-btn.listening {
                background: linear-gradient(135deg, #059669, #10B981);
                animation: speechPulse 1.5s infinite;
            }
            
            .speech-main-btn.processing {
                background: linear-gradient(135deg, #F59E0B, #FBBF24);
            }
            
            .speech-main-btn.error {
                background: linear-gradient(135deg, #DC2626, #EF4444);
                animation: speechShake 0.5s ease-in-out;
            }
            
            .speech-btn-content {
                position: relative;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            
            .speech-icon {
                font-size: 24px;
                z-index: 2;
            }
            
            .speech-pulse-ring {
                position: absolute;
                width: 100%;
                height: 100%;
                border: 2px solid rgba(255, 255, 255, 0.5);
                border-radius: 50%;
                opacity: 0;
                transform: scale(1);
            }
            
            .speech-main-btn.listening .speech-pulse-ring {
                animation: speechRingPulse 1.5s infinite;
            }
            
            .speech-status {
                font-size: 10px;
                font-weight: 600;
                margin-top: 2px;
                text-align: center;
                white-space: nowrap;
            }
            
            .speech-controls-panel {
                display: flex;
                gap: 5px;
                opacity: 0;
                transform: translateY(10px);
                transition: all 0.3s ease;
            }
            
            .speech-control-widget:hover .speech-controls-panel {
                opacity: 1;
                transform: translateY(0);
            }
            
            .speech-control-btn {
                width: 40px;
                height: 40px;
                border-radius: 50%;
                border: none;
                background: rgba(255, 255, 255, 0.9);
                color: #374151;
                cursor: pointer;
                transition: all 0.3s ease;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 14px;
                box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
            }
            
            .speech-control-btn:hover {
                background: white;
                transform: scale(1.1);
                box-shadow: 0 4px 15px rgba(0, 0, 0, 0.15);
            }
            
            /* Speech Overlay */
            .speech-overlay {
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: rgba(0, 0, 0, 0.8);
                backdrop-filter: blur(10px);
                z-index: 10000;
                display: none;
                align-items: center;
                justify-content: center;
                animation: fadeIn 0.3s ease;
            }
            
            .speech-overlay.active {
                display: flex;
            }
            
            .speech-overlay-content {
                background: white;
                border-radius: 20px;
                padding: 40px;
                text-align: center;
                max-width: 400px;
                width: 90%;
                box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
            }
            
            .speech-visual-indicator {
                position: relative;
                margin-bottom: 30px;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            
            .speech-mic-icon {
                width: 80px;
                height: 80px;
                border-radius: 50%;
                background: linear-gradient(135deg, #059669, #10B981);
                color: white;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 30px;
                z-index: 2;
                position: relative;
            }
            
            .speech-sound-waves {
                position: absolute;
                width: 100%;
                height: 100%;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            
            .wave {
                position: absolute;
                width: 80px;
                height: 80px;
                border: 2px solid #059669;
                border-radius: 50%;
                opacity: 0;
                animation: waveAnimation 2s infinite;
            }
            
            .wave:nth-child(2) { animation-delay: 0.5s; }
            .wave:nth-child(3) { animation-delay: 1s; }
            .wave:nth-child(4) { animation-delay: 1.5s; }
            
            .speech-overlay-title {
                font-size: 24px;
                font-weight: 700;
                color: #374151;
                margin-bottom: 10px;
            }
            
            .speech-overlay-subtitle {
                color: #6B7280;
                margin-bottom: 30px;
                min-height: 24px;
                font-style: italic;
            }
            
            .speech-overlay-actions {
                display: flex;
                justify-content: center;
                gap: 15px;
            }
            
            .speech-action-btn {
                padding: 12px 24px;
                border: none;
                border-radius: 12px;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s ease;
                display: flex;
                align-items: center;
                gap: 8px;
            }
            
            .speech-action-btn.cancel {
                background: #F3F4F6;
                color: #374151;
            }
            
            .speech-action-btn.cancel:hover {
                background: #E5E7EB;
            }
            
            /* Speech Panels */
            .speech-panel {
                position: fixed;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%) scale(0.9);
                background: white;
                border-radius: 16px;
                box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
                z-index: 10001;
                max-width: 500px;
                width: 90%;
                max-height: 80vh;
                overflow: hidden;
                opacity: 0;
                visibility: hidden;
                transition: all 0.3s ease;
            }
            
            .speech-panel.active {
                opacity: 1;
                visibility: visible;
                transform: translate(-50%, -50%) scale(1);
            }
            
            .speech-panel-header {
                background: linear-gradient(135deg, #DC2626, #EF4444);
                color: white;
                padding: 20px 25px;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            
            .speech-panel-header h4 {
                margin: 0;
                font-size: 18px;
                font-weight: 600;
            }
            
            .speech-close-btn {
                background: none;
                border: none;
                color: white;
                font-size: 18px;
                cursor: pointer;
                padding: 5px;
                border-radius: 50%;
                transition: all 0.3s ease;
            }
            
            .speech-close-btn:hover {
                background: rgba(255, 255, 255, 0.2);
            }
            
            .speech-panel-content {
                padding: 25px;
                max-height: calc(80vh - 80px);
                overflow-y: auto;
            }
            
            /* Help Panel Styles */
            .speech-help-section {
                margin-bottom: 25px;
            }
            
            .speech-help-section h5 {
                color: #DC2626;
                font-size: 16px;
                font-weight: 600;
                margin-bottom: 15px;
                padding-bottom: 8px;
                border-bottom: 2px solid #FEE2E2;
            }
            
            .speech-commands {
                display: flex;
                flex-direction: column;
                gap: 12px;
            }
            
            .speech-command {
                background: #F9FAFB;
                border-radius: 8px;
                padding: 15px;
                border-left: 4px solid #DC2626;
            }
            
            .speech-command .command {
                display: block;
                font-weight: 600;
                color: #374151;
                margin-bottom: 5px;
                font-family: 'Courier New', monospace;
                background: #E5E7EB;
                padding: 4px 8px;
                border-radius: 4px;
                font-size: 14px;
            }
            
            .speech-command .description {
                color: #6B7280;
                font-size: 14px;
            }
            
            /* Settings Panel Styles */
            .speech-setting {
                margin-bottom: 20px;
            }
            
            .speech-setting label {
                display: block;
                font-weight: 600;
                color: #374151;
                margin-bottom: 8px;
            }
            
            .speech-select {
                width: 100%;
                padding: 10px 15px;
                border: 2px solid #E5E7EB;
                border-radius: 8px;
                background: white;
                font-size: 14px;
                transition: all 0.3s ease;
            }
            
            .speech-select:focus {
                border-color: #DC2626;
                outline: none;
                box-shadow: 0 0 0 3px rgba(220, 38, 38, 0.1);
            }
            
            .speech-range {
                width: 100%;
                height: 6px;
                border-radius: 3px;
                background: #E5E7EB;
                outline: none;
                -webkit-appearance: none;
            }
            
            .speech-range::-webkit-slider-thumb {
                -webkit-appearance: none;
                width: 20px;
                height: 20px;
                border-radius: 50%;
                background: #DC2626;
                cursor: pointer;
                box-shadow: 0 2px 8px rgba(220, 38, 38, 0.3);
            }
            
            .speech-checkbox {
                display: flex;
                align-items: center;
                cursor: pointer;
                font-weight: 500;
                color: #374151;
            }
            
            .speech-checkbox input[type="checkbox"] {
                opacity: 0;
                position: absolute;
                width: 0;
                height: 0;
            }
            
            .checkmark {
                width: 20px;
                height: 20px;
                background: #F3F4F6;
                border: 2px solid #E5E7EB;
                border-radius: 4px;
                margin-right: 12px;
                position: relative;
                transition: all 0.3s ease;
            }
            
            .speech-checkbox input:checked + .checkmark {
                background: #DC2626;
                border-color: #DC2626;
            }
            
            .speech-checkbox input:checked + .checkmark::after {
                content: "✓";
                position: absolute;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                color: white;
                font-weight: bold;
                font-size: 12px;
            }
            
            .speech-test-btn {
                width: 100%;
                padding: 12px 20px;
                background: linear-gradient(135deg, #059669, #10B981);
                color: white;
                border: none;
                border-radius: 8px;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s ease;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            
            .speech-test-btn:hover {
                background: linear-gradient(135deg, #047857, #059669);
                transform: translateY(-1px);
                box-shadow: 0 4px 12px rgba(5, 150, 105, 0.3);
            }
            
            /* Notifications */
            .speech-notifications-container {
                position: fixed;
                top: 20px;
                right: 20px;
                z-index: 10002;
                display: flex;
                flex-direction: column;
                gap: 10px;
                max-width: 400px;
            }
            
            .speech-notification {
                background: white;
                border-radius: 12px;
                padding: 16px 20px;
                box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
                border-left: 4px solid #DC2626;
                transform: translateX(100%);
                transition: all 0.3s ease;
                display: flex;
                align-items: center;
                gap: 12px;
            }
            
            .speech-notification.show {
                transform: translateX(0);
            }
            
            .speech-notification.success {
                border-left-color: #059669;
            }
            
            .speech-notification.error {
                border-left-color: #DC2626;
            }
            
            .speech-notification.info {
                border-left-color: #3B82F6;
            }
            
            .speech-notification .notification-icon {
                font-size: 20px;
            }
            
            .speech-notification.success .notification-icon {
                color: #059669;
            }
            
            .speech-notification.error .notification-icon {
                color: #DC2626;
            }
            
            .speech-notification.info .notification-icon {
                color: #3B82F6;
            }
            
            .speech-notification .notification-content {
                flex: 1;
            }
            
            .speech-notification .notification-title {
                font-weight: 600;
                color: #374151;
                margin-bottom: 2px;
            }
            
            .speech-notification .notification-message {
                color: #6B7280;
                font-size: 14px;
            }
            
            /* Form Enhancement Styles */
            .speech-enhanced-field {
                position: relative;
            }
            
            .speech-field-btn {
                position: absolute;
                top: 50%;
                right: 10px;
                transform: translateY(-50%);
                width: 32px;
                height: 32px;
                border: none;
                border-radius: 50%;
                background: #FEE2E2;
                color: #DC2626;
                cursor: pointer;
                transition: all 0.3s ease;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 12px;
                z-index: 10;
            }
            
            .speech-field-btn:hover {
                background: #DC2626;
                color: white;
                transform: translateY(-50%) scale(1.1);
            }
            
            .speech-filled {
                border-color: #059669 !important;
                box-shadow: 0 0 0 3px rgba(5, 150, 105, 0.1) !important;
                background: rgba(5, 150, 105, 0.05) !important;
            }
            
            .speech-filled-indicator {
                position: absolute;
                top: 50%;
                right: 45px;
                transform: translateY(-50%);
                color: #059669;
                font-size: 14px;
                pointer-events: none;
                z-index: 10;
            }
            
            /* Animations */
            @keyframes speechPulse {
                0%, 100% { transform: scale(1); }
                50% { transform: scale(1.05); }
            }
            
            @keyframes speechRingPulse {
                0% { opacity: 0; transform: scale(1); }
                50% { opacity: 0.7; transform: scale(1.2); }
                100% { opacity: 0; transform: scale(1.4); }
            }
            
            @keyframes speechShake {
                0%, 100% { transform: translateX(0); }
                25% { transform: translateX(-5px); }
                75% { transform: translateX(5px); }
            }
            
            @keyframes waveAnimation {
                0% { opacity: 0; transform: scale(1); }
                50% { opacity: 0.7; }
                100% { opacity: 0; transform: scale(1.5); }
            }
            
            @keyframes fadeIn {
                from { opacity: 0; }
                to { opacity: 1; }
            }
            
            /* Mobile Responsiveness */
            @media (max-width: 768px) {
                .speech-control-widget {
                    bottom: 20px;
                    right: 20px;
                }
                
                .speech-main-btn {
                    width: 60px;
                    height: 60px;
                }
                
                .speech-icon {
                    font-size: 20px;
                }
                
                .speech-panel {
                    width: 95%;
                    max-height: 85vh;
                }
                
                .speech-overlay-content {
                    padding: 30px 20px;
                }
                
                .speech-notifications-container {
                    left: 20px;
                    right: 20px;
                    max-width: none;
                }
                
                .speech-field-btn {
                    width: 28px;
                    height: 28px;
                    font-size: 10px;
                }
            }
        `;
        
        document.head.appendChild(style);
    }

    setupUIEventHandlers() {
        // Main speech button
        document.getElementById('global-speech-btn').addEventListener('click', () => {
            this.toggleListening();
        });
        
        // Help button
        document.getElementById('speech-help-btn').addEventListener('click', () => {
            this.showPanel('speech-help-panel');
        });
        
        // Settings button
        document.getElementById('speech-settings-btn').addEventListener('click', () => {
            this.showPanel('speech-settings-panel');
        });
        
        // Close buttons
        document.getElementById('close-help-btn').addEventListener('click', () => {
            this.hidePanel('speech-help-panel');
        });
        
        document.getElementById('close-settings-btn').addEventListener('click', () => {
            this.hidePanel('speech-settings-panel');
        });
        
        // Cancel button in overlay
        document.getElementById('speech-cancel-btn').addEventListener('click', () => {
            this.stopListening();
        });
        
        // Settings event handlers
        document.getElementById('speech-language').addEventListener('change', (e) => {
            this.config.language = e.target.value;
            this.recognition.lang = e.target.value;
            this.showNotification(`Language changed to ${e.target.options[e.target.selectedIndex].text}`, 'success');
        });
        
        document.getElementById('speech-confidence').addEventListener('input', (e) => {
            this.config.confidenceThreshold = parseFloat(e.target.value);
            document.getElementById('confidence-value').textContent = Math.round(e.target.value * 100) + '%';
        });
        
        // Test speech button
        document.getElementById('test-speech-btn').addEventListener('click', () => {
            this.testSpeechRecognition();
        });
        
        // Click outside to close panels
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('speech-panel')) {
                this.hideAllPanels();
            }
        });
    }

    setupEventListeners() {
        // Form submission interceptors
        document.addEventListener('submit', (e) => {
            if (this.speechMetadata.fromSpeech) {
                this.handleSpeechFormSubmission(e);
            }
        });
        
        // Dynamic form field enhancement
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                mutation.addedNodes.forEach((node) => {
                    if (node.nodeType === 1) {
                        this.enhanceNewElements(node);
                    }
                });
            });
        });
        
        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
    }

    addKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            // Ctrl+Space or Cmd+Space for speech toggle
            if ((e.ctrlKey || e.metaKey) && e.code === 'Space') {
                e.preventDefault();
                this.toggleListening();
            }
            
            // Escape to cancel speech
            if (e.key === 'Escape' && this.isListening) {
                e.preventDefault();
                this.stopListening();
            }
            
            // Alt+H for help
            if (e.altKey && e.key === 'h') {
                e.preventDefault();
                this.showPanel('speech-help-panel');
            }
        });
    }

    enhanceExistingForms() {
        // Enhanced all input fields
        const fields = document.querySelectorAll('input[type="text"], input[type="email"], input[type="password"], textarea, select');
        fields.forEach(field => this.enhanceFormField(field));
        
        // Add form-level speech controls
        const forms = document.querySelectorAll('form');
        forms.forEach(form => this.enhanceForm(form));
    }

    enhanceNewElements(element) {
        // Enhance new form fields
        const fields = element.querySelectorAll ? element.querySelectorAll('input[type="text"], input[type="email"], input[type="password"], textarea, select') : [];
        fields.forEach(field => this.enhanceFormField(field));
        
        // Enhance new forms
        const forms = element.querySelectorAll ? element.querySelectorAll('form') : [];
        forms.forEach(form => this.enhanceForm(form));
    }

    enhanceFormField(field) {
        if (field.closest('.speech-enhanced-field') || field.type === 'hidden') return;
        
        // Wrap field
        const wrapper = document.createElement('div');
        wrapper.className = 'speech-enhanced-field';
        field.parentNode.insertBefore(wrapper, field);
        wrapper.appendChild(field);
        
        // Add speech button
        const speechBtn = document.createElement('button');
        speechBtn.type = 'button';
        speechBtn.className = 'speech-field-btn';
        speechBtn.innerHTML = '<i class="fas fa-microphone"></i>';
        speechBtn.title = 'Fill with voice';
        
        speechBtn.addEventListener('click', (e) => {
            e.preventDefault();
            this.listenForField(field);
        });
        
        wrapper.appendChild(speechBtn);
    }

    enhanceForm(form) {
        if (form.hasAttribute('data-speech-enhanced')) return;
        
        form.setAttribute('data-speech-enhanced', 'true');
        
        // Add form-level speech button
        const formHeader = form.querySelector('.card-header, .form-header, h1, h2, h3, h4, h5');
        if (formHeader && !formHeader.querySelector('.form-speech-btn')) {
            const formSpeechBtn = document.createElement('button');
            formSpeechBtn.type = 'button';
            formSpeechBtn.className = 'btn btn-outline-primary btn-sm form-speech-btn ms-2';
            formSpeechBtn.innerHTML = '<i class="fas fa-microphone me-1"></i>Fill Form';
            formSpeechBtn.title = 'Fill entire form with voice';
            
            formSpeechBtn.addEventListener('click', () => {
                this.listenForForm(form);
            });
            
            formHeader.appendChild(formSpeechBtn);
        }
    }

    // Speech Recognition Event Handlers
    handleSpeechStart() {
        this.isListening = true;
        this.updateSpeechButton('listening');
        this.showListeningOverlay();
        this.log('Speech recognition started');
    }

    handleSpeechEnd() {
        this.isListening = false;
        this.updateSpeechButton('idle');
        this.hideListeningOverlay();
        this.log('Speech recognition ended');
    }

    handleSpeechResult(event) {
        const results = Array.from(event.results);
        const transcript = results.map(result => result[0].transcript).join(' ');
        const confidence = results[0][0].confidence;
        
        this.log('Speech result:', { transcript, confidence });
        
        // Update interim result display
        document.getElementById('speech-interim-result').textContent = transcript;
        
        if (event.results[0].isFinal) {
            this.processSpeechResult(transcript, confidence);
        }
    }

    handleSpeechError(event) {
        this.log('Speech error:', event.error);
        this.updateSpeechButton('error');
        
        let errorMessage = 'Speech recognition failed. ';
        switch (event.error) {
            case 'network':
                errorMessage += 'Check your internet connection.';
                break;
            case 'not-allowed':
                errorMessage += 'Microphone access denied. Please allow microphone access.';
                break;
            case 'no-speech':
                errorMessage += 'No speech detected. Try again.';
                break;
            default:
                errorMessage += 'Please try again.';
        }
        
        this.showNotification(errorMessage, 'error');
        this.hideListeningOverlay();
    }

    handleNoMatch() {
        this.log('No speech match found');
        this.showNotification('Could not understand speech. Please try again.', 'error');
    }

    // Core Speech Processing Methods
    async processSpeechResult(transcript, confidence) {
        this.updateSpeechButton('processing');
        this.hideListeningOverlay();
        
        try {
            if (confidence < this.config.confidenceThreshold) {
                this.showNotification(`Low confidence (${Math.round(confidence * 100)}%). Please speak more clearly.`, 'error');
                return;
            }
            
            const result = await this.processWithAPI(transcript);
            
            if (result.success) {
                await this.executeInstructions(result.instructions, transcript);
                this.showNotification(result.instructions.message || 'Speech command processed successfully!', 'success');
            } else {
                // Fallback to local processing
                const fallbackResult = this.processLocally(transcript);
                await this.executeInstructions(fallbackResult, transcript);
                this.showNotification('Speech processed with basic matching.', 'info');
            }
            
        } catch (error) {
            this.log('Error processing speech:', error);
            this.showNotification('Failed to process speech command.', 'error');
        } finally {
            this.updateSpeechButton('idle');
        }
    }

    async processWithAPI(transcript) {
        try {
            const response = await fetch('/api/process-speech', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    transcript: transcript,
                    page: this.currentPage,
                    context: this.getPageContext()
                })
            });
            
            return await response.json();
        } catch (error) {
            this.log('API processing failed:', error);
            return { success: false };
        }
    }

    processLocally(transcript) {
        const transcriptLower = transcript.toLowerCase();
        
        // Navigation commands
        if (this.isNavigationCommand(transcriptLower)) {
            return this.processNavigationCommand(transcriptLower);
        }
        
        // Form filling commands
        if (this.isFormCommand(transcriptLower)) {
            return this.processFormCommand(transcript, transcriptLower);
        }
        
        // Direct action commands
        if (this.isActionCommand(transcriptLower)) {
            return this.processActionCommand(transcript, transcriptLower);
        }
        
        // Field-specific commands
        if (this.activeField) {
            return this.processFieldCommand(transcript);
        }
        
        // Default: try to fill current form
        return this.processGenericFormFill(transcript);
    }

    isNavigationCommand(transcript) {
        const navKeywords = ['go to', 'open', 'show', 'navigate to', 'switch to'];
        return navKeywords.some(keyword => transcript.includes(keyword));
    }

    processNavigationCommand(transcript) {
        const routes = {
            'website': '/tools/website',
            'email': '/tools/email',
            'feedback': '/tools/feedback',
            'poster': '/tools/poster',
            'sales': '/tools/sales',
            'dashboard': '/dashboard',
            'profile': '/profile'
        };
        
        for (const [tool, route] of Object.entries(routes)) {
            if (transcript.includes(tool)) {
                return {
                    action: 'navigate',
                    navigation: route,
                    message: `Navigating to ${tool} page...`
                };
            }
        }
        
        return {
            action: 'error',
            message: 'Could not determine where to navigate.'
        };
    }

    isFormCommand(transcript) {
        const formKeywords = ['create', 'make', 'generate', 'build', 'design'];
        return formKeywords.some(keyword => transcript.includes(keyword));
    }

    processFormCommand(transcript, transcriptLower) {
        const fields = {};
        
        // Extract business name
        const businessMatch = transcript.match(/(?:for|called|named)\s+([^,.\n]+)/i);
        if (businessMatch) {
            const businessName = businessMatch[1].trim();
            fields.businessName = businessName;
            fields.senderName = businessName;
            fields.posterTitle = businessName;
        }
        
        // Determine form type and fill appropriate fields
        if (transcriptLower.includes('website') || transcriptLower.includes('site')) {
            return this.processWebsiteCommand(transcript, fields);
        } else if (transcriptLower.includes('email')) {
            return this.processEmailCommand(transcript, fields);
        } else if (transcriptLower.includes('poster') || transcriptLower.includes('flyer')) {
            return this.processPosterCommand(transcript, fields);
        }
        
        return {
            action: 'fill_form',
            fields: fields,
            message: 'Filled available fields from speech.'
        };
    }

    processWebsiteCommand(transcript, baseFields) {
        const transcriptLower = transcript.toLowerCase();
        const fields = { ...baseFields };
        
        // Website type detection
        const typeMapping = {
            restaurant: ['restaurant', 'cafe', 'food', 'dining'],
            business: ['business', 'company', 'corporate'],
            portfolio: ['portfolio', 'personal', 'showcase'],
            ecommerce: ['store', 'shop', 'ecommerce'],
            services: ['services', 'consulting']
        };
        
        for (const [type, keywords] of Object.entries(typeMapping)) {
            if (keywords.some(keyword => transcriptLower.includes(keyword))) {
                fields.websiteType = type;
                break;
            }
        }
        
        // Extract description
        const descMatch = transcript.match(/(?:that|which|is|does|provides)\s+([^,.]+)/i);
        if (descMatch) {
            fields.businessDescription = descMatch[1].trim();
        }
        
        // Color scheme detection
        if (transcriptLower.includes('professional')) fields.colorScheme = 'professional';
        else if (transcriptLower.includes('modern')) fields.colorScheme = 'modern';
        else if (transcriptLower.includes('creative')) fields.colorScheme = 'creative';
        
        return {
            action: 'fill_form',
            fields: fields,
            tool_execution: { tool: 'website', auto_submit: false },
            message: `Website form filled for ${fields.businessName || 'your business'}.`
        };
    }

    processEmailCommand(transcript, baseFields) {
        const transcriptLower = transcript.toLowerCase();
        const fields = { ...baseFields };
        
        // Email type detection
        const typeMapping = {
            marketing: ['marketing', 'promotional', 'promotion'],
            customer_service: ['support', 'service', 'help'],
            thank_you: ['thank', 'thanks', 'appreciation'],
            announcement: ['announcement', 'news', 'update']
        };
        
        for (const [type, keywords] of Object.entries(typeMapping)) {
            if (keywords.some(keyword => transcriptLower.includes(keyword))) {
                fields.emailType = type;
                break;
            }
        }
        
        // Tone detection
        if (transcriptLower.includes('professional')) fields.emailTone = 'professional';
        else if (transcriptLower.includes('friendly')) fields.emailTone = 'friendly';
        else if (transcriptLower.includes('formal')) fields.emailTone = 'formal';
        
        // Recipient detection
        if (transcriptLower.includes('customer')) fields.recipientType = 'customer';
        else if (transcriptLower.includes('prospect')) fields.recipientType = 'prospect';
        
        return {
            action: 'fill_form',
            fields: fields,
            tool_execution: { tool: 'email', auto_submit: false },
            message: `Email form configured for ${fields.emailType || 'general'} email.`
        };
    }

    processPosterCommand(transcript, baseFields) {
        const transcriptLower = transcript.toLowerCase();
        const fields = { ...baseFields };
        
        // Poster type detection
        if (transcriptLower.includes('sale') || transcriptLower.includes('promotion')) {
            fields.posterType = 'promotional';
            if (!fields.posterTitle) fields.posterTitle = 'Special Sale';
        } else if (transcriptLower.includes('event') || transcriptLower.includes('opening')) {
            fields.posterType = 'event';
            if (!fields.posterTitle) fields.posterTitle = 'Special Event';
        }
        
        // Extract specific titles
        if (transcriptLower.includes('grand opening')) {
            fields.posterTitle = 'Grand Opening';
            fields.posterType = 'event';
        }
        
        return {
            action: 'fill_form',
            fields: fields,
            tool_execution: { tool: 'poster', auto_submit: false },
            message: `Poster form configured for ${fields.posterTitle || 'your poster'}.`
        };
    }

    isActionCommand(transcript) {
        const actionKeywords = ['analyze', 'send', 'upload', 'submit'];
        return actionKeywords.some(keyword => transcript.includes(keyword));
    }

    processActionCommand(transcript, transcriptLower) {
        if (transcriptLower.includes('analyze') && transcriptLower.includes('feedback')) {
            const feedbackMatch = transcript.match(/feedback[:\s]+(.+)/i);
            if (feedbackMatch) {
                return {
                    action: 'fill_form',
                    fields: { feedbackText: feedbackMatch[1].trim() },
                    tool_execution: { tool: 'feedback', auto_submit: true },
                    message: 'Analyzing feedback...'
                };
            }
        }
        
        return {
            action: 'error',
            message: 'Could not understand the action command.'
        };
    }

    processFieldCommand(transcript) {
        return {
            action: 'fill_field',
            field: this.activeField,
            value: transcript,
            message: 'Field filled with speech input.'
        };
    }

    processGenericFormFill(transcript) {
        // Try to intelligently fill current form
        const currentForm = document.querySelector('form:not([data-speech-processed])');
        if (!currentForm) {
            return {
                action: 'error',
                message: 'No form found to fill.'
            };
        }
        
        const fields = {};
        const nameFields = currentForm.querySelectorAll('[id*="name"], [name*="name"]');
        const emailFields = currentForm.querySelectorAll('[type="email"]');
        const textFields = currentForm.querySelectorAll('textarea, [type="text"]:not([id*="name"])');
        
        // Try to extract name
        const nameMatch = transcript.match(/(?:my name is|I am|called)\s+([^,.]+)/i);
        if (nameMatch && nameFields.length > 0) {
            fields[nameFields[0].id || nameFields[0].name] = nameMatch[1].trim();
        }
        
        // Fill first textarea with full transcript if no specific extraction
        if (textFields.length > 0 && Object.keys(fields).length === 0) {
            fields[textFields[0].id || textFields[0].name] = transcript;
        }
        
        return {
            action: 'fill_form',
            fields: fields,
            message: 'Form filled with speech input.'
        };
    }

    async executeInstructions(instructions, originalTranscript) {
        this.speechMetadata = {
            fromSpeech: true,
            originalTranscript: originalTranscript,
            processedAt: new Date().toISOString(),
            instructions: instructions
        };
        
        switch (instructions.action) {
            case 'navigate':
                this.handleNavigation(instructions.navigation);
                break;
                
            case 'fill_form':
                await this.handleFormFilling(instructions.fields, instructions.tool_execution);
                break;
                
            case 'fill_field':
                this.handleFieldFilling(instructions.field, instructions.value);
                break;
                
            case 'execute_tool':
                await this.handleToolExecution(instructions.tool_execution);
                break;
                
            default:
                this.log('Unknown instruction action:', instructions.action);
        }
    }

    handleNavigation(url) {
        this.showNotification('Navigating...', 'info');
        setTimeout(() => {
            window.location.href = url;
        }, 1000);
    }

    async handleFormFilling(fields, toolExecution) {
        if (!fields || Object.keys(fields).length === 0) {
            this.showNotification('No fields to fill.', 'error');
            return;
        }
        
        let filledCount = 0;
        
        for (const [fieldId, value] of Object.entries(fields)) {
            const field = document.getElementById(fieldId) || document.querySelector(`[name="${fieldId}"]`);
            if (field) {
                await this.fillFieldWithAnimation(field, value);
                filledCount++;
            }
        }
        
        if (filledCount > 0) {
            this.showNotification(`Filled ${filledCount} field(s) from speech!`, 'success');
            
            // Auto-submit if configured
            if (toolExecution?.auto_submit && document.getElementById('speech-auto-submit')?.checked) {
                setTimeout(() => {
                    this.submitCurrentForm();
                }, 2000);
            }
        } else {
            this.showNotification('No matching fields found to fill.', 'error');
        }
    }

    async fillFieldWithAnimation(field, value) {
        // Add visual feedback
        field.classList.add('speech-filled');
        
        // Add speech indicator
        this.addSpeechIndicator(field);
        
        // Fill field based on type
        if (field.tagName === 'SELECT') {
            this.fillSelectField(field, value);
        } else if (field.type === 'checkbox' || field.type === 'radio') {
            field.checked = true;
        } else {
            // Animate typing for better UX
            await this.typeInField(field, value);
        }
        
        // Trigger change event
        field.dispatchEvent(new Event('input', { bubbles: true }));
        field.dispatchEvent(new Event('change', { bubbles: true }));
    }

    async typeInField(field, text) {
        field.focus();
        field.value = '';
        
        for (let i = 0; i < text.length; i++) {
            field.value += text[i];
            field.dispatchEvent(new Event('input', { bubbles: true }));
            await new Promise(resolve => setTimeout(resolve, 50));
        }
    }

    fillSelectField(select, value) {
        const options = Array.from(select.options);
        const lowerValue = value.toLowerCase();
        
        // Try exact match first
        let option = options.find(opt => 
            opt.value.toLowerCase() === lowerValue || 
            opt.text.toLowerCase() === lowerValue
        );
        
        // Try partial match
        if (!option) {
            option = options.find(opt => 
                opt.text.toLowerCase().includes(lowerValue) ||
                opt.value.toLowerCase().includes(lowerValue)
            );
        }
        
        if (option) {
            select.value = option.value;
            return true;
        }
        
        return false;
    }

    addSpeechIndicator(field) {
        const wrapper = field.closest('.speech-enhanced-field');
        if (wrapper && !wrapper.querySelector('.speech-filled-indicator')) {
            const indicator = document.createElement('div');
            indicator.className = 'speech-filled-indicator';
            indicator.innerHTML = '<i class="fas fa-microphone" title="Filled via speech"></i>';
            wrapper.appendChild(indicator);
        }
    }

    handleFieldFilling(field, value) {
        if (field) {
            this.fillFieldWithAnimation(field, value);
            this.activeField = null;
        }
    }

    async handleToolExecution(toolExecution) {
        if (toolExecution?.auto_submit) {
            this.submitCurrentForm();
        }
    }

    submitCurrentForm() {
        const form = document.querySelector('form:not([data-speech-processed])');
        if (form) {
            const submitBtn = form.querySelector('button[type="submit"], input[type="submit"]');
            if (submitBtn) {
                this.showNotification('Auto-submitting form...', 'info');
                setTimeout(() => {
                    submitBtn.click();
                }, 1500);
            }
        }
    }

    // Speech Control Methods
    toggleListening() {
        if (this.isListening) {
            this.stopListening();
        } else {
            this.startListening();
        }
    }

    startListening() {
        if (!this.recognition) {
            this.showNotification('Speech recognition not available.', 'error');
            return;
        }
        
        try {
            this.recognition.start();
        } catch (error) {
            this.log('Error starting speech recognition:', error);
            this.showNotification('Failed to start speech recognition.', 'error');
        }
    }

    stopListening() {
        if (this.recognition && this.isListening) {
            this.recognition.stop();
        }
    }

    listenForField(field) {
        this.activeField = field;
        this.startListening();
    }

    listenForForm(form) {
        this.activeForm = form;
        this.startListening();
    }

    testSpeechRecognition() {
        this.showNotification('Say something to test speech recognition...', 'info');
        this.startListening();
    }

    // UI Update Methods
    updateSpeechButton(state) {
        const btn = document.getElementById('global-speech-btn');
        const statusEl = btn.querySelector('.speech-status');
        
        btn.className = `speech-main-btn ${state}`;
        
        switch (state) {
            case 'listening':
                statusEl.textContent = 'Listening...';
                break;
            case 'processing':
                statusEl.textContent = 'Processing...';
                break;
            case 'error':
                statusEl.textContent = 'Try again';
                break;
            default:
                statusEl.textContent = 'Click to speak';
        }
    }

    showListeningOverlay() {
        const overlay = document.getElementById('speech-listening-overlay');
        overlay.classList.add('active');
    }

    hideListeningOverlay() {
        const overlay = document.getElementById('speech-listening-overlay');
        overlay.classList.remove('active');
    }

    showPanel(panelId) {
        this.hideAllPanels();
        const panel = document.getElementById(panelId);
        if (panel) {
            panel.classList.add('active');
        }
    }

    hidePanel(panelId) {
        const panel = document.getElementById(panelId);
        if (panel) {
            panel.classList.remove('active');
        }
    }

    hideAllPanels() {
        const panels = document.querySelectorAll('.speech-panel');
        panels.forEach(panel => panel.classList.remove('active'));
    }

    showNotification(message, type = 'info', duration = 4000) {
        if (!document.getElementById('speech-notifications')?.checked && type !== 'error') {
            return;
        }
        
        const container = document.getElementById('speech-notifications');
        const notification = document.createElement('div');
        notification.className = `speech-notification ${type}`;
        
        const icons = {
            success: 'fa-check-circle',
            error: 'fa-exclamation-triangle',
            info: 'fa-info-circle'
        };
        
        notification.innerHTML = `
            <i class="fas ${icons[type]} notification-icon"></i>
            <div class="notification-content">
                <div class="notification-title">${type.charAt(0).toUpperCase() + type.slice(1)}</div>
                <div class="notification-message">${message}</div>
            </div>
        `;
        
        container.appendChild(notification);
        
        // Show notification
        setTimeout(() => notification.classList.add('show'), 100);
        
        // Auto-hide
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 300);
        }, duration);
    }

    // Utility Methods
    detectCurrentPage() {
        const path = window.location.pathname;
        if (path.includes('/tools/website')) return 'website';
        if (path.includes('/tools/email')) return 'email';
        if (path.includes('/tools/feedback')) return 'feedback';
        if (path.includes('/tools/poster')) return 'poster';
        if (path.includes('/tools/sales')) return 'sales';
        if (path === '/' || path.includes('dashboard')) return 'dashboard';
        return 'unknown';
    }

    getPageContext() {
        return {
            url: window.location.href,
            title: document.title,
            forms: document.querySelectorAll('form').length,
            fields: document.querySelectorAll('input, textarea, select').length
        };
    }

    handleSpeechFormSubmission(event) {
        // Add speech metadata to form submission
        const form = event.target;
        if (this.speechMetadata.fromSpeech) {
            // You can add hidden fields or modify the submission here
            this.log('Form submitted via speech:', this.speechMetadata);
        }
    }

    log(message, ...args) {
        if (this.debugMode) {
            console.log(`[EnhancedSpeechController] ${message}`, ...args);
        }
    }

    // Public API Methods
    destroy() {
        if (this.recognition) {
            this.recognition.stop();
            this.recognition = null;
        }
        
        const ui = document.getElementById('enhanced-speech-ui');
        if (ui) ui.remove();
        
        const styles = document.getElementById('enhanced-speech-styles');
        if (styles) styles.remove();
        
        this.isInitialized = false;
    }

    getStatus() {
        return {
            initialized: this.isInitialized,
            listening: this.isListening,
            supported: this.checkBrowserSupport(),
            currentPage: this.currentPage,
            config: this.config
        };
    }
}

// Auto-initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    // Only initialize if not already done
    if (!window.enhancedSpeechController) {
        window.enhancedSpeechController = new EnhancedSpeechController();
        console.log('Enhanced Speech Controller initialized successfully!');
    }
});

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = EnhancedSpeechController;
}