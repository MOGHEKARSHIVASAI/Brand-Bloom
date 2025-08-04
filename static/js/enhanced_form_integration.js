// Enhanced form integration for speech-to-text
// Add this to your existing form JavaScript files

class EnhancedFormSpeechIntegration {
    constructor() {
        this.currentForm = null;
        this.speechMetadata = {};
        this.init();
    }

    init() {
        this.enhanceExistingForms();
        this.setupSpeechEventHandlers();
        this.addFormSpecificFeatures();
    }

    enhanceExistingForms() {
        // Website Builder Form Enhancement
        if (document.getElementById('websiteForm')) {
            this.enhanceWebsiteForm();
        }

        // Email Drafter Form Enhancement
        if (document.getElementById('emailForm')) {
            this.enhanceEmailForm();
        }

        // Feedback Form Enhancement
        if (document.getElementById('feedbackForm')) {
            this.enhanceFeedbackForm();
        }

        // Poster Form Enhancement
        if (document.getElementById('posterForm')) {
            this.enhancePosterForm();
        }
    }

    enhanceWebsiteForm() {
        const form = document.getElementById('websiteForm');
        const originalSubmit = form.onsubmit;

        // Add speech-specific submission handler
        form.onsubmit = async (e) => {
            e.preventDefault();
            
            const formData = {
                websiteType: document.getElementById('websiteType').value,
                businessName: document.getElementById('businessName').value,
                businessDescription: document.getElementById('businessDescription').value,
                keyServices: document.getElementById('keyServices').value,
                targetAudience: document.getElementById('targetAudience').value,
                colorScheme: document.getElementById('colorScheme').value
            };

            // Add speech metadata if available
            if (this.speechMetadata.fromSpeech) {
                formData.speech_metadata = this.speechMetadata;
            }

            await this.submitWithSpeechTracking('/api/generate-website', formData, 'website');
        };

        // Add intelligent form completion
        this.addIntelligentCompletion('websiteForm', {
            'businessName': (value) => {
                // Auto-suggest website type based on business name
                const nameValue = value.toLowerCase();
                const typeField = document.getElementById('websiteType');
                
                if (!typeField.value) {
                    if (nameValue.includes('restaurant') || nameValue.includes('cafe') || nameValue.includes('pizza')) {
                        typeField.value = 'restaurant';
                    } else if (nameValue.includes('shop') || nameValue.includes('store')) {
                        typeField.value = 'ecommerce';
                    } else if (nameValue.includes('consulting') || nameValue.includes('services')) {
                        typeField.value = 'services';
                    }
                    this.triggerFieldUpdate(typeField);
                }
            },
            'websiteType': (value) => {
                // Auto-suggest color scheme based on website type
                const colorField = document.getElementById('colorScheme');
                
                if (!colorField.value || colorField.value === 'professional') {
                    const suggestions = {
                        'restaurant': 'warm',
                        'creative': 'creative',
                        'business': 'professional',
                        'portfolio': 'modern',
                        'ecommerce': 'modern'
                    };
                    
                    if (suggestions[value]) {
                        colorField.value = suggestions[value];
                        this.triggerFieldUpdate(colorField);
                    }
                }
            }
        });
    }

    enhanceEmailForm() {
        const form = document.getElementById('emailForm');
        
        form.onsubmit = async (e) => {
            e.preventDefault();
            
            const formData = {
                emailType: document.getElementById('emailType').value,
                recipientType: document.getElementById('recipientType').value,
                tone: document.getElementById('emailTone').value,
                purpose: document.getElementById('emailPurpose').value,
                context: document.getElementById('emailContext').value,
                senderName: document.getElementById('senderName').value
            };

            if (this.speechMetadata.fromSpeech) {
                formData.speech_metadata = this.speechMetadata;
            }

            await this.submitWithSpeechTracking('/api/draft-email', formData, 'email');
        };

        // Add intelligent suggestions
        this.addIntelligentCompletion('emailForm', {
            'emailType': (value) => {
                const toneField = document.getElementById('emailTone');
                const suggestions = {
                    'marketing': 'friendly',
                    'customer_service': 'professional',
                    'thank_you': 'friendly',
                    'announcement': 'professional'
                };
                
                if (suggestions[value] && !toneField.value) {
                    toneField.value = suggestions[value];
                    this.triggerFieldUpdate(toneField);
                }
            }
        });
    }

    enhanceFeedbackForm() {
        const form = document.getElementById('feedbackForm');
        
        // Handle both manual and stored feedback forms
        if (form) {
            form.onsubmit = async (e) => {
                e.preventDefault();
                
                const feedbackText = document.getElementById('feedbackText').value;
                
                if (!feedbackText.trim()) {
                    alert('Please enter feedback text to analyze.');
                    return;
                }

                const requestData = { feedback: feedbackText };
                
                if (this.speechMetadata.fromSpeech) {
                    requestData.speech_metadata = this.speechMetadata;
                }

                await this.submitWithSpeechTracking('/api/analyze-feedback', requestData, 'feedback');
            };
        }

        // Handle direct speech feedback submission
        this.setupDirectFeedbackAnalysis();
    }

    enhancePosterForm() {
        const form = document.getElementById('posterForm');
        
        form.onsubmit = async (e) => {
            e.preventDefault();
            
            const formData = {
                poster_type: document.getElementById('posterType').value,
                title: document.getElementById('posterTitle').value,
                subtitle: document.getElementById('posterSubtitle').value,
                description: document.getElementById('posterDescription').value,
                business_name: document.getElementById('businessName').value,
                color_scheme: document.getElementById('colorScheme').value,
                size: document.getElementById('posterSize').value
            };

            if (this.speechMetadata.fromSpeech) {
                formData.speech_metadata = this.speechMetadata;
            }

            await this.submitWithSpeechTracking('/api/create-poster', formData, 'poster');
        };

        // Add intelligent completion for posters
        this.addIntelligentCompletion('posterForm', {
            'posterType': (value) => {
                const colorField = document.getElementById('colorScheme');
                const suggestions = {
                    'promotional': 'vibrant',
                    'event': 'professional',
                    'product': 'modern',
                    'announcement': 'professional'
                };
                
                if (suggestions[value] && !colorField.value) {
                    colorField.value = suggestions[value];
                    this.triggerFieldUpdate(colorField);
                }
            }
        });
    }

    setupSpeechEventHandlers() {
        // Listen for speech processing results
        document.addEventListener('speechProcessed', (event) => {
            const { instructions, transcript } = event.detail;
            this.handleSpeechInstructions(instructions, transcript);
        });

        // Listen for speech form filling
        document.addEventListener('speechFormFilled', (event) => {
            const { fields, metadata } = event.detail;
            this.speechMetadata = {
                fromSpeech: true,
                originalTranscript: metadata.transcript,
                processedAt: new Date().toISOString(),
                fieldsCount: Object.keys(fields).length
            };
        });
    }

    async handleSpeechInstructions(instructions, transcript) {
        this.speechMetadata = {
            fromSpeech: true,
            originalTranscript: transcript,
            processedAt: new Date().toISOString()
        };

        switch (instructions.action) {
            case 'fill_form':
                await this.fillFormWithSpeech(instructions.fields);
                if (instructions.tool_execution?.auto_submit) {
                    await this.autoSubmitForm(instructions.tool_execution.tool);
                }
                break;
                
            case 'navigate':
                this.navigateWithSpeech(instructions.navigation);
                break;
                
            case 'execute_tool':
                await this.executeToolWithSpeech(instructions.tool_execution);
                break;
        }

        if (instructions.message) {
            this.showSpeechFeedback(instructions.message, 'success');
        }
    }

    async fillFormWithSpeech(fields) {
        let filledCount = 0;
        
        for (const [fieldId, value] of Object.entries(fields)) {
            const element = document.getElementById(fieldId);
            if (element) {
                await this.animatedFieldFill(element, value);
                filledCount++;
            }
        }

        if (filledCount > 0) {
            this.showSpeechFeedback(`Filled ${filledCount} field(s) from your speech!`, 'success');
        }
    }

    async animatedFieldFill(element, value) {
        // Add visual feedback
        element.style.transform = 'scale(1.05)';
        element.style.transition = 'all 0.3s ease';
        
        // Fill the field
        if (element.tagName === 'SELECT') {
            this.fillSelectWithSpeech(element, value);
        } else if (element.type === 'checkbox' || element.type === 'radio') {
            element.checked = true;
        } else {
            // Simulate typing for better UX
            await this.typeText(element, value);
        }

        // Mark as speech-filled
        this.markFieldAsSpeechFilled(element);
        
        // Reset visual effect
        setTimeout(() => {
            element.style.transform = '';
        }, 300);
    }

    async typeText(element, text) {
        element.value = '';
        element.focus();
        
        for (let i = 0; i < text.length; i++) {
            element.value += text[i];
            element.dispatchEvent(new Event('input', { bubbles: true }));
            await new Promise(resolve => setTimeout(resolve, 30)); // Typing speed
        }
    }

    fillSelectWithSpeech(selectElement, value) {
        const options = Array.from(selectElement.options);
        const lowerValue = value.toLowerCase();
        
        // Try exact match first
        let matchedOption = options.find(option => 
            option.value.toLowerCase() === lowerValue ||
            option.text.toLowerCase() === lowerValue
        );
        
        // Try partial match
        if (!matchedOption) {
            matchedOption = options.find(option => 
                option.text.toLowerCase().includes(lowerValue) ||
                option.value.toLowerCase().includes(lowerValue)
            );
        }
        
        if (matchedOption) {
            selectElement.value = matchedOption.value;
            selectElement.dispatchEvent(new Event('change', { bubbles: true }));
            return true;
        }
        
        return false;
    }

    markFieldAsSpeechFilled(element) {
        element.classList.add('speech-filled');
        
        // Add speech indicator icon
        if (!element.parentNode.querySelector('.speech-indicator')) {
            const indicator = document.createElement('div');
            indicator.className = 'speech-indicator';
            indicator.innerHTML = '<i class="fas fa-microphone text-primary"></i>';
            indicator.style.cssText = `
                position: absolute;
                right: 8px;
                top: 50%;
                transform: translateY(-50%);
                z-index: 10;
                pointer-events: none;
                opacity: 0;
                animation: fadeInScale 0.5s ease forwards;
            `;
            
            const wrapper = element.parentNode;
            if (wrapper.style.position !== 'relative') {
                wrapper.style.position = 'relative';
            }
            wrapper.appendChild(indicator);
        }
    }

    async autoSubmitForm(toolType) {
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
                this.showSpeechFeedback('Auto-submitting form...', 'info');
                
                // Wait a moment for user to see the filled form
                setTimeout(() => {
                    const submitBtn = form.querySelector('button[type="submit"]');
                    if (submitBtn) {
                        submitBtn.click();
                    }
                }, 1500);
            }
        }
    }

    navigateWithSpeech(url) {
        this.showSpeechFeedback('Navigating...', 'info');
        setTimeout(() => {
            window.location.href = url;
        }, 1000);
    }

    async executeToolWithSpeech(toolExecution) {
        this.showSpeechFeedback(`Executing ${toolExecution.tool} tool...`, 'info');
        
        // Tool-specific execution logic
        switch (toolExecution.tool) {
            case 'feedback':
                await this.executeFeedbackAnalysis();
                break;
            case 'website':
                await this.executeWebsiteGeneration();
                break;
            case 'email':
                await this.executeEmailGeneration();
                break;
            case 'poster':
                await this.executePosterCreation();
                break;
        }
    }

    async submitWithSpeechTracking(endpoint, data, toolType) {
        const submitBtn = document.querySelector(`#${toolType}Form button[type="submit"]`);
        
        if (submitBtn) {
            // Show loading state
            const originalText = submitBtn.textContent;
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Processing...';
            
            if (this.speechMetadata.fromSpeech) {
                submitBtn.innerHTML = '<i class="fas fa-microphone fa-spin me-1"></i>Processing Speech...';
            }
        }

        try {
            const response = await fetch(endpoint, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });

            const result = await response.json();
            
            if (result.error) {
                throw new Error(result.error);
            }

            // Handle tool-specific success
            this.handleToolSuccess(toolType, result);

            // Show speech-specific success message
            if (this.speechMetadata.fromSpeech && result.speech_message) {
                this.showSpeechFeedback(result.speech_message, 'success');
            }

        } catch (error) {
            console.error(`${toolType} error:`, error);
            this.showSpeechFeedback(`Error: ${error.message}`, 'error');
        } finally {
            if (submitBtn) {
                submitBtn.disabled = false;
                submitBtn.innerHTML = originalText;
            }
            
            // Reset speech metadata
            this.speechMetadata = {};
        }
    }

    handleToolSuccess(toolType, result) {
        switch (toolType) {
            case 'website':
                this.handleWebsiteSuccess(result);
                break;
            case 'email':
                this.handleEmailSuccess(result);
                break;
            case 'feedback':
                this.handleFeedbackSuccess(result);
                break;
            case 'poster':
                this.handlePosterSuccess(result);
                break;
        }
    }

    handleWebsiteSuccess(result) {
        if (result.html) {
            const preview = document.getElementById('websitePreview');
            if (preview) {
                preview.innerHTML = '';
                
                // Show success message if speech-generated
                if (result.speech_success) {
                    const successDiv = document.createElement('div');
                    successDiv.className = 'alert alert-success mb-3';
                    successDiv.innerHTML = `
                        <h5><i class="fas fa-microphone me-2"></i>Speech Command Successful!</h5>
                        <p class="mb-2">${result.speech_message}</p>
                        <p><strong>Website ID:</strong> ${result.website_id}</p>
                    `;
                    preview.appendChild(successDiv);
                }
                
                const iframe = document.createElement('iframe');
                iframe.setAttribute('sandbox', 'allow-same-origin allow-scripts allow-forms');
                iframe.srcdoc = result.html;
                iframe.style.cssText = 'width: 100%; height: 500px; border: 1px solid #ddd; border-radius: 4px;';
                preview.appendChild(iframe);
            }
        }
    }

    handleEmailSuccess(result) {
        if (result.email || result.generated_at) {
            this.displayGeneratedEmail(result);
            
            // Show copy and download buttons
            document.getElementById('copyEmailBtn').style.display = 'inline-block';
            document.getElementById('downloadBtn').style.display = 'inline-block';
        }
    }

    handleFeedbackSuccess(result) {
        if (result.status === 'success' && result.analysis) {
            // Use existing feedback display function
            if (typeof displayResults === 'function') {
                displayResults(result.analysis);
            }
        }
    }

    handlePosterSuccess(result) {
        if (result.status === 'success' && result.poster) {
            // Use existing poster display function
            if (typeof displayPoster === 'function') {
                displayPoster(result.poster);
            }
            
            // Show download buttons
            document.getElementById('downloadPNGBtn').style.display = 'inline-block';
            document.getElementById('downloadPDFBtn').style.display = 'inline-block';
        }
    }

    addIntelligentCompletion(formId, completionRules) {
        const form = document.getElementById(formId);
        if (!form) return;

        Object.keys(completionRules).forEach(fieldId => {
            const field = document.getElementById(fieldId);
            if (field) {
                field.addEventListener('change', () => {
                    if (field.value) {
                        completionRules[fieldId](field.value);
                    }
                });
            }
        });
    }

    triggerFieldUpdate(field) {
        // Add visual feedback for auto-completed fields
        field.style.background = '#e3f2fd';
        field.dispatchEvent(new Event('change', { bubbles: true }));
        
        setTimeout(() => {
            field.style.background = '';
        }, 2000);
    }

    setupDirectFeedbackAnalysis() {
        // Allow direct speech input for feedback analysis
        if (window.speechIntegration) {
            window.speechIntegration.addCustomHandler('feedback_direct', (transcript) => {
                const feedbackField = document.getElementById('feedbackText');
                if (feedbackField) {
                    feedbackField.value = transcript;
                    
                    // Auto-analyze if it's clearly feedback
                    if (this.isFeedbackText(transcript)) {
                        setTimeout(() => {
                            const form = document.getElementById('feedbackForm');
                            if (form) {
                                form.dispatchEvent(new Event('submit'));
                            }
                        }, 1000);
                    }
                }
            });
        }
    }

    isFeedbackText(text) {
        const feedbackIndicators = [
            'service', 'product', 'experience', 'staff', 'quality',
            'good', 'bad', 'excellent', 'terrible', 'satisfied',
            'disappointed', 'recommend', 'complaint'
        ];
        
        const lowerText = text.toLowerCase();
        return feedbackIndicators.some(indicator => lowerText.includes(indicator));
    }

    showSpeechFeedback(message, type = 'info') {
        // Remove existing notifications
        const existingNotification = document.querySelector('.speech-notification-enhanced');
        if (existingNotification) {
            existingNotification.remove();
        }

        const notification = document.createElement('div');
        notification.className = `speech-notification-enhanced ${type}`;
        
        const iconMap = {
            'success': 'fas fa-check-circle',
            'error': 'fas fa-exclamation-circle',
            'info': 'fas fa-info-circle',
            'warning': 'fas fa-exclamation-triangle'
        };
        
        notification.innerHTML = `
            <i class="${iconMap[type]} me-2"></i>
            <span>${message}</span>
        `;
        
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: ${this.getNotificationColor(type)};
            color: white;
            padding: 15px 20px;
            border-radius: 8px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
            z-index: 2000;
            transform: translateX(100%);
            transition: transform 0.3s ease;
            max-width: 400px;
            font-weight: 500;
        `;
        
        document.body.appendChild(notification);
        
        // Animate in
        setTimeout(() => {
            notification.style.transform = 'translateX(0)';
        }, 100);
        
        // Auto-hide
        setTimeout(() => {
            notification.style.transform = 'translateX(100%)';
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 300);
        }, type === 'error' ? 6000 : 4000);
    }

    getNotificationColor(type) {
        const colors = {
            'success': '#28a745',
            'error': '#dc3545',
            'info': '#17a2b8',
            'warning': '#ffc107'
        };
        return colors[type] || colors.info;
    }

    addFormValidationEnhancement() {
        // Enhanced validation for speech-filled forms
        const forms = document.querySelectorAll('form');
        
        forms.forEach(form => {
            form.addEventListener('submit', (e) => {
                const speechFilledFields = form.querySelectorAll('.speech-filled');
                
                if (speechFilledFields.length > 0) {
                    // Add confidence indicator for speech-filled forms
                    const confidence = this.calculateFormConfidence(speechFilledFields);
                    
                    if (confidence < 0.7) {
                        const proceed = confirm(
                            'Some fields were filled via speech. Please review them before submitting. Continue?'
                        );
                        
                        if (!proceed) {
                            e.preventDefault();
                            return false;
                        }
                    }
                }
            });
        });
    }

    calculateFormConfidence(speechFields) {
        // Simple confidence calculation based on field types and content
        let totalConfidence = 0;
        
        speechFields.forEach(field => {
            let fieldConfidence = 0.8; // Base confidence
            
            // Adjust based on field type
            if (field.tagName === 'SELECT') {
                fieldConfidence = 0.9; // Higher confidence for dropdowns
            } else if (field.type === 'email') {
                // Check email format
                fieldConfidence = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(field.value) ? 0.95 : 0.5;
            } else if (field.value.length < 3) {
                fieldConfidence = 0.6; // Lower confidence for very short text
            }
            
            totalConfidence += fieldConfidence;
        });
        
        return totalConfidence / speechFields.length;
    }

    // Add CSS animations
    addSpeechAnimations() {
        const style = document.createElement('style');
        style.textContent = `
            @keyframes fadeInScale {
                from {
                    opacity: 0;
                    transform: translateY(-50%) scale(0.8);
                }
                to {
                    opacity: 1;
                    transform: translateY(-50%) scale(1);
                }
            }
            
            @keyframes speechFieldPulse {
                0% { background-color: rgba(40, 167, 69, 0.1); }
                50% { background-color: rgba(40, 167, 69, 0.3); }
                100% { background-color: rgba(40, 167, 69, 0.1); }
            }
            
            .speech-filled {
                animation: speechFieldPulse 0.8s ease-in-out;
            }
        `;
        document.head.appendChild(style);
    }
}

// Initialize enhanced form integration
document.addEventListener('DOMContentLoaded', function() {
    window.enhancedFormSpeech = new EnhancedFormSpeechIntegration();
    console.log('Enhanced form speech integration initialized');
});

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = EnhancedFormSpeechIntegration;
}