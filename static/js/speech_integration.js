// Speech-to-Text Integration Module with Gemini AI
class SpeechToTextIntegration {
    constructor() {
        this.recognition = null;
        this.isListening = false;
        this.currentTool = null;
        this.debugMode = true;
        this.boundEventListeners = {};
        
        this.init();
        
        // Add window unload handler for cleanup
        window.addEventListener('unload', this.cleanup.bind(this));
    }

    init() {
        // Check for speech recognition support
        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            this.recognition = new SpeechRecognition();
            
            // Configure recognition settings
            this.recognition.continuous = false;
            this.recognition.interimResults = false;
            this.recognition.lang = 'en-US';  // Set primary language
            this.recognition.maxAlternatives = 1;
            
            this.setupEventListeners();
            this.addSpeechButtons();
            this.showSpeechInstructions();
        } else {
            console.warn('Speech recognition not supported in this browser');
            this.showUnsupportedMessage();
        }
    }

    setupEventListeners() {
        this.recognition.onstart = () => {
            this.isListening = true;
            this.updateSpeechStatus('Listening...', 'listening');
            this.log('Speech recognition started');
        };

        this.recognition.onend = () => {
            this.isListening = false;
            this.updateSpeechStatus('Click to speak', 'idle');
            this.log('Speech recognition ended');
        };

        this.recognition.onresult = (event) => {
            try {
                if (event.results && event.results.length > 0) {
                    const transcript = event.results[0][0].transcript;
                    this.log('Speech recognized:', transcript);
                    this.processSpeechInput(transcript);
                } else {
                    throw new Error('No speech detected');
                }
            } catch (error) {
                this.log('Error processing speech:', error);
                this.updateSpeechStatus('Error processing speech. Please try again.', 'error');
            }
        };

        this.recognition.onerror = (event) => {
            this.log('Speech recognition error:', event.error);
            this.updateSpeechStatus('Error occurred. Try again.', 'error');
        };
    }

    addSpeechButtons() {
        // Add global speech control
        this.addGlobalSpeechControl();
        
        // Add speech buttons to specific forms
        this.addFormSpeechButtons();
        
        // Add tool-specific speech shortcuts
        this.addToolShortcuts();
    }

    addGlobalSpeechControl() {
        const globalControl = document.createElement('div');
        globalControl.id = 'global-speech-control';
        globalControl.innerHTML = `
            <div class="speech-control-container">
                <button id="global-speech-btn" class="speech-btn global-speech">
                    <i class="fas fa-microphone"></i>
                    <span class="speech-status">Click to speak</span>
                </button>
                <div class="speech-help">
                    <i class="fas fa-question-circle"></i>
                    <div class="speech-help-popup">
                        <h6>Voice Commands:</h6>
                        <ul>
                            <li>"Create a website for my restaurant"</li>
                            <li>"Analyze this feedback: [your feedback]"</li>
                            <li>"Generate an email for marketing"</li>
                            <li>"Make a poster for grand opening"</li>
                            <li>"Fill the form with [details]"</li>
                        </ul>
                    </div>
                </div>
            </div>
        `;
        
        // Add CSS styles
        const styles = `
            <style>
                #global-speech-control {
                    position: fixed;
                    bottom: 40px;
                    right: 20px;
                    z-index: 1000;
                    background: white;
                    border-radius: 15px;
                    box-shadow: 0 4px 20px rgba(0,0,0,0.1);
                    padding: 15px;
                    border: 2px solid #e9ecef;
                    display: none;
                }
                
                .speech-control-container {
                    display: flex;
                    align-items: center;
                    gap: 10px;
                }
                
                .speech-btn {
                    display: flex;
                    align-items: center;
                    gap: 8px;
                    padding: 12px 20px;
                    border: 2px solid #007bff;
                    background: #007bff;
                    color: white;
                    border-radius: 25px;
                    cursor: pointer;
                    font-weight: 600;
                    transition: all 0.3s ease;
                    font-size: 14px;
                }
                
                .speech-btn:hover {
                    background: #0056b3;
                    transform: translateY(-2px);
                }
                
                .speech-btn.listening {
                    background: #dc3545;
                    border-color: #dc3545;
                    animation: pulse 1.5s infinite;
                }
                
                .speech-btn.processing {
                    background: #ffc107;
                    border-color: #ffc107;
                    color: #000;
                }
                
                .speech-btn.error {
                    background: #6c757d;
                    border-color: #6c757d;
                }
                
                @keyframes pulse {
                    0% { box-shadow: 0 0 0 0 rgba(220, 53, 69, 0.7); }
                    70% { box-shadow: 0 0 0 10px rgba(220, 53, 69, 0); }
                    100% { box-shadow: 0 0 0 0 rgba(220, 53, 69, 0); }
                }
                
                .speech-help {
                    position: relative;
                    cursor: pointer;
                    color: #6c757d;
                    font-size: 16px;
                }
                
                .speech-help-popup {
                    position: absolute;
                    top: 100%;
                    right: 0;
                    background: white;
                    border: 1px solid #ddd;
                    border-radius: 8px;
                    padding: 15px;
                    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
                    min-width: 300px;
                    display: none;
                    z-index: 1001;
                }
                
                .speech-help:hover .speech-help-popup {
                    display: block;
                }
                
                .speech-help-popup h6 {
                    margin: 0 0 10px 0;
                    color: #333;
                }
                
                .speech-help-popup ul {
                    margin: 0;
                    padding-left: 20px;
                    font-size: 12px;
                }
                
                .speech-help-popup li {
                    margin-bottom: 5px;
                    color: #666;
                }
                
                .form-speech-btn {
                    position: absolute;
                    top: 5px;
                    right: 5px;
                    width: 35px;
                    height: 35px;
                    border-radius: 50%;
                    border: 2px solid #28a745;
                    background: #28a745;
                    color: white;
                    cursor: pointer;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-size: 12px;
                    transition: all 0.3s ease;
                }
                
                .form-speech-btn:hover {
                    background: #1e7e34;
                    transform: scale(1.1);
                }
                
                .speech-field-wrapper {
                    position: relative;
                }
                
                .speech-notification {
                    position: fixed;
                    top: 100px;
                    right: 20px;
                    background: #007bff;
                    color: white;
                    padding: 15px 20px;
                    border-radius: 8px;
                    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
                    z-index: 1002;
                    opacity: 0;
                    transform: translateX(100%);
                    transition: all 0.3s ease;
                }
                
                .speech-notification.show {
                    opacity: 1;
                    transform: translateX(0);
                }
                
                .speech-notification.success {
                    background: #28a745;
                }
                
                .speech-notification.error {
                    background: #dc3545;
                }
            </style>
        `;
        
        document.head.insertAdjacentHTML('beforeend', styles);
        document.body.appendChild(globalControl);
        
        // Add event listener
        document.getElementById('global-speech-btn').addEventListener('click', () => {
            this.toggleGlobalListening();
        });
    }

    addFormSpeechButtons() {
        // Add speech buttons to form fields
        const formFields = document.querySelectorAll('input[type="text"], input[type="email"], textarea, select');
        
        formFields.forEach(field => {
            if (!field.closest('.speech-field-wrapper')) {
                this.wrapFieldWithSpeech(field);
            }
        });
    }

    wrapFieldWithSpeech(field) {
        const wrapper = document.createElement('div');
        wrapper.className = 'speech-field-wrapper';
        
        field.parentNode.insertBefore(wrapper, field);
        wrapper.appendChild(field);
        
        const speechBtn = document.createElement('button');
        speechBtn.type = 'button';
        speechBtn.className = 'form-speech-btn';
        speechBtn.innerHTML = '<i class="fas fa-microphone"></i>';
        speechBtn.title = 'Fill with voice';
        
        speechBtn.addEventListener('click', (e) => {
            e.preventDefault();
            this.listenForField(field);
        });
        
        wrapper.appendChild(speechBtn);
    }

    addToolShortcuts() {
        // Add tool-specific voice shortcuts
        const toolShortcuts = document.createElement('div');
        toolShortcuts.id = 'tool-shortcuts';
        toolShortcuts.innerHTML = `
            <div class="tool-shortcuts-container">
                <h6>Quick Voice Commands:</h6>
                <div class="shortcut-grid">
                    <button class="shortcut-btn" data-command="website">
                        <i class="fas fa-globe"></i>
                        "Create website"
                    </button>
                    <button class="shortcut-btn" data-command="email">
                        <i class="fas fa-envelope"></i>
                        "Generate email"
                    </button>
                    <button class="shortcut-btn" data-command="feedback">
                        <i class="fas fa-comments"></i>
                        "Analyze feedback"
                    </button>
                    <button class="shortcut-btn" data-command="poster">
                        <i class="fas fa-image"></i>
                        "Make poster"
                    </button>
                </div>
            </div>
        `;
        
        // Add styles for shortcuts
        const shortcutStyles = `
            <style>
                #tool-shortcuts {
                    position: fixed;
                    bottom: 20px;
                    right: 20px;
                    background: white;
                    border-radius: 15px;
                    box-shadow: 0 4px 20px rgba(0,0,0,0.1);
                    padding: 20px;
                    max-width: 300px;
                    border: 2px solid #e9ecef;
                    z-index: 999;
                }
                
                .tool-shortcuts-container h6 {
                    margin: 0 0 15px 0;
                    color: #333;
                    font-weight: 600;
                }
                
                .shortcut-grid {
                    display: grid;
                    grid-template-columns: 1fr 1fr;
                    gap: 10px;
                }
                
                .shortcut-btn {
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    gap: 5px;
                    padding: 12px 8px;
                    border: 1px solid #ddd;
                    background: #f8f9fa;
                    border-radius: 8px;
                    cursor: pointer;
                    transition: all 0.3s ease;
                    font-size: 11px;
                    text-align: center;
                }
                
                .shortcut-btn:hover {
                    background: #e9ecef;
                    transform: translateY(-2px);
                }
                
                .shortcut-btn i {
                    font-size: 16px;
                    color: #007bff;
                }
            </style>
        `;
        
        document.head.insertAdjacentHTML('beforeend', shortcutStyles);
        
        // Only add shortcuts on dashboard or tool pages
        if (window.location.pathname === '/' || window.location.pathname.includes('/tools/')) {
            document.body.appendChild(toolShortcuts);
            
            // Add event listeners
            document.querySelectorAll('.shortcut-btn').forEach(btn => {
                btn.addEventListener('click', () => {
                    const command = btn.getAttribute('data-command');
                    this.executeToolShortcut(command);
                });
            });
        }
    }

    showSpeechInstructions() {
        // Show initial instructions
        setTimeout(() => {
            this.showNotification('Speech-to-text is ready! Click the microphone to start.', 'success');
        }, 1000);
    }

    toggleGlobalListening() {
        if (this.isListening) {
            this.recognition.stop();
        } else {
            this.currentTool = 'global';
            this.recognition.start();
        }
    }

    listenForField(field) {
        if (this.isListening) {
            this.recognition.stop();
            return;
        }
        
        this.currentField = field;
        this.currentTool = 'field';
        this.recognition.start();
    }

    executeToolShortcut(command) {
        this.currentTool = command;
        this.showNotification(`Say your ${command} requirements...`, 'info');
        this.recognition.start();
    }

    async processSpeechInput(transcript) {
        this.log('Processing speech input:', transcript);
        this.updateSpeechStatus('Processing...', 'processing');
        
        try {
            if (this.currentTool === 'field') {
                await this.fillSingleField(transcript);
            } else {
                await this.processWithGemini(transcript);
            }
        } catch (error) {
            this.log('Error processing speech:', error);
            this.showNotification('Error processing speech. Please try again.', 'error');
        }
        
        this.updateSpeechStatus('Click to speak', 'idle');
    }

    async fillSingleField(transcript) {
        if (this.currentField) {
            // Direct field filling for simple inputs
            if (this.currentField.tagName === 'SELECT') {
                this.fillSelectField(this.currentField, transcript);
            } else {
                this.currentField.value = transcript.trim();
                this.currentField.dispatchEvent(new Event('input', { bubbles: true }));
            }
            
            this.showNotification('Field filled successfully!', 'success');
            this.currentField = null;
        }
    }

    fillSelectField(selectElement, transcript) {
        const options = Array.from(selectElement.options);
        const lowerTranscript = transcript.toLowerCase();
        
        // Find matching option
        const matchedOption = options.find(option => 
            option.text.toLowerCase().includes(lowerTranscript) ||
            option.value.toLowerCase().includes(lowerTranscript)
        );
        
        if (matchedOption) {
            selectElement.value = matchedOption.value;
            selectElement.dispatchEvent(new Event('change', { bubbles: true }));
        }
    }

    async processWithGemini(transcript) {
        const currentPage = this.detectCurrentPage();
        const prompt = this.buildGeminiPrompt(transcript, currentPage);
        
        try {
            const response = await fetch('/api/process-speech', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    transcript,
                    page: currentPage,
                    prompt 
                })
            });
            
            const result = await response.json();
            
            if (result.success) {
                await this.executeGeminiInstructions(result.instructions);
            } else {
                throw new Error(result.error || 'Failed to process speech');
            }
        } catch (error) {
            this.log('Gemini API error:', error);
            // Fallback to local processing
            await this.fallbackProcessing(transcript);
        }
    }

    buildGeminiPrompt(transcript, currentPage) {
        return `
You are an AI assistant for a business toolkit application. The user is on the ${currentPage} page and said: "${transcript}"

Analyze the user's speech and provide instructions to fill out forms or execute actions. Return a JSON response with:
{
    "action": "fill_form" | "navigate" | "execute_tool",
    "page": "${currentPage}",
    "fields": {
        "fieldId": "value to fill"
    },
    "navigation": "url_to_navigate_to",
    "tool_execution": {
        "tool": "website|email|feedback|poster|sales",
        "auto_submit": true|false
    },
    "message": "confirmation message for user"
}

Current page context:
${this.getPageContext(currentPage)}

Examples:
- "Create a website for my restaurant called Pizza Palace" → fill website form with business name, type restaurant
- "Generate a marketing email for new customers" → fill email form with type marketing, recipient new customers
- "Make a poster for grand opening sale" → fill poster form with type promotional, title grand opening
- "Analyze this feedback: the service was terrible" → fill feedback form and analyze

Ensure all field names match the actual form field IDs on the page.
        `;
    }

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

    getPageContext(page) {
        const contexts = {
            website: 'Website builder form with fields: websiteType, businessName, businessDescription, keyServices, targetAudience, colorScheme',
            email: 'Email composer form with fields: emailType, recipientType, emailTone, emailPurpose, emailContext, senderName',
            feedback: 'Feedback analyzer with fields: feedbackText, or feedback selection',
            poster: 'Poster maker form with fields: posterType, posterTitle, posterSubtitle, posterDescription, businessName, colorScheme, posterSize',
            sales: 'Sales analytics tool for uploading CSV files',
            dashboard: 'Main dashboard with navigation to all tools'
        };
        return contexts[page] || 'Unknown page context';
    }

    async executeGeminiInstructions(instructions) {
        this.log('Executing instructions:', instructions);
        
        switch (instructions.action) {
            case 'fill_form':
                await this.fillFormFields(instructions.fields);
                if (instructions.tool_execution?.auto_submit) {
                    await this.submitCurrentForm(instructions.tool_execution.tool);
                }
                break;
                
            case 'navigate':
                if (instructions.navigation) {
                    window.location.href = instructions.navigation;
                }
                break;
                
            case 'execute_tool':
                await this.executeToolDirectly(instructions.tool_execution);
                break;
        }
        
        if (instructions.message) {
            this.showNotification(instructions.message, 'success');
        }
    }

    async fillFormFields(fields) {
        for (const [fieldId, value] of Object.entries(fields)) {
            const element = document.getElementById(fieldId);
            if (element) {
                if (element.tagName === 'SELECT') {
                    this.fillSelectField(element, value);
                } else if (element.type === 'checkbox' || element.type === 'radio') {
                    element.checked = true;
                } else {
                    element.value = value;
                    element.dispatchEvent(new Event('input', { bubbles: true }));
                }
                
                // Add visual feedback
                element.style.background = '#e8f5e9';
                setTimeout(() => {
                    element.style.background = '';
                }, 1000);
            }
        }
    }

    async submitCurrentForm(toolType) {
        const forms = {
            website: '#websiteForm',
            email: '#emailForm',
            feedback: '#feedbackForm',
            poster: '#posterForm'
        };
        
        const formSelector = forms[toolType];
        if (formSelector) {
            const form = document.querySelector(formSelector);
            if (form) {
                // Simulate form submission
                setTimeout(() => {
                    const submitBtn = form.querySelector('button[type="submit"]');
                    if (submitBtn) {
                        submitBtn.click();
                    }
                }, 500);
            }
        }
    }

    async fallbackProcessing(transcript) {
        // Simple keyword-based processing as fallback
        const lowerTranscript = transcript.toLowerCase();
        
        if (lowerTranscript.includes('website') || lowerTranscript.includes('site')) {
            if (window.location.pathname !== '/tools/website') {
                window.location.href = '/tools/website';
                return;
            }
            this.extractWebsiteInfo(transcript);
        } else if (lowerTranscript.includes('email') || lowerTranscript.includes('mail')) {
            if (window.location.pathname !== '/tools/email') {
                window.location.href = '/tools/email';
                return;
            }
            this.extractEmailInfo(transcript);
        } else if (lowerTranscript.includes('feedback') || lowerTranscript.includes('review')) {
            if (window.location.pathname !== '/tools/feedback') {
                window.location.href = '/tools/feedback';
                return;
            }
            this.extractFeedbackInfo(transcript);
        } else if (lowerTranscript.includes('poster') || lowerTranscript.includes('flyer')) {
            if (window.location.pathname !== '/tools/poster') {
                window.location.href = '/tools/poster';
                return;
            }
            this.extractPosterInfo(transcript);
        }
    }

    extractWebsiteInfo(transcript) {
        const fields = {};
        const lowerTranscript = transcript.toLowerCase();
        
        // Extract business name
        const businessNameMatch = transcript.match(/(?:for|called|named)\s+([^,.\n]+)/i);
        if (businessNameMatch) {
            fields.businessName = businessNameMatch[1].trim();
        }
        
        // Extract website type
        if (lowerTranscript.includes('restaurant') || lowerTranscript.includes('food')) {
            fields.websiteType = 'restaurant';
        } else if (lowerTranscript.includes('business') || lowerTranscript.includes('company')) {
            fields.websiteType = 'business';
        } else if (lowerTranscript.includes('portfolio')) {
            fields.websiteType = 'portfolio';
        }
        
        this.fillFormFields(fields);
    }

    extractEmailInfo(transcript) {
        const fields = {};
        const lowerTranscript = transcript.toLowerCase();
        
        // Extract email type
        if (lowerTranscript.includes('marketing')) {
            fields.emailType = 'marketing';
        } else if (lowerTranscript.includes('customer service') || lowerTranscript.includes('support')) {
            fields.emailType = 'customer_service';
        } else if (lowerTranscript.includes('thank you') || lowerTranscript.includes('thanks')) {
            fields.emailType = 'thank_you';
        }
        
        // Extract tone
        if (lowerTranscript.includes('professional')) {
            fields.emailTone = 'professional';
        } else if (lowerTranscript.includes('friendly')) {
            fields.emailTone = 'friendly';
        } else if (lowerTranscript.includes('formal')) {
            fields.emailTone = 'formal';
        }
        
        this.fillFormFields(fields);
    }

    extractFeedbackInfo(transcript) {
        // For feedback, directly fill the feedback text
        const feedbackTextarea = document.getElementById('feedbackText');
        if (feedbackTextarea) {
            feedbackTextarea.value = transcript;
            feedbackTextarea.dispatchEvent(new Event('input', { bubbles: true }));
        }
    }

    extractPosterInfo(transcript) {
        const fields = {};
        const lowerTranscript = transcript.toLowerCase();
        
        // Extract poster type
        if (lowerTranscript.includes('sale') || lowerTranscript.includes('promotion')) {
            fields.posterType = 'promotional';
        } else if (lowerTranscript.includes('event') || lowerTranscript.includes('opening')) {
            fields.posterType = 'event';
        }
        
        // Extract title from speech
        const titleMatch = transcript.match(/(?:for|called|titled)\s+([^,.\n]+)/i);
        if (titleMatch) {
            fields.posterTitle = titleMatch[1].trim();
        } else if (lowerTranscript.includes('grand opening')) {
            fields.posterTitle = 'Grand Opening';
        } else if (lowerTranscript.includes('sale')) {
            fields.posterTitle = 'Big Sale';
        }
        
        this.fillFormFields(fields);
    }

    updateSpeechStatus(status, state) {
        const globalBtn = document.getElementById('global-speech-btn');
        if (globalBtn) {
            const statusSpan = globalBtn.querySelector('.speech-status');
            if (statusSpan) {
                statusSpan.textContent = status;
            }
            
            globalBtn.className = `speech-btn global-speech ${state}`;
        }
    }

    showNotification(message, type = 'info') {
        // Remove existing notification
        const existing = document.querySelector('.speech-notification');
        if (existing) {
            existing.remove();
        }
        
        const notification = document.createElement('div');
        notification.className = `speech-notification ${type}`;
        notification.textContent = message;
        
        document.body.appendChild(notification);
        
        // Show notification
        setTimeout(() => {
            notification.classList.add('show');
        }, 100);
        
        // Hide notification after 4 seconds
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 300);
        }, 4000);
    }

    showUnsupportedMessage() {
        this.showNotification('Speech recognition is not supported in this browser. Please use Chrome, Firefox, or Edge.', 'error');
    }

    log(message, ...args) {
        if (this.debugMode) {
            console.log(`[SpeechToText] ${message}`, ...args);
        }
    }
}

// Initialize speech integration when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.speechIntegration = new SpeechToTextIntegration();
});

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = SpeechToTextIntegration;
}