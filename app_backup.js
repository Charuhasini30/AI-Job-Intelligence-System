// AI Job Matcher Frontend JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Get DOM elements
    const resumeForm = document.getElementById('resumeForm');
    const uploadBtn = document.getElementById('uploadBtn');
    const findMatchesBtn = document.getElementById('findMatchesBtn');
    const loadingSection = document.getElementById('loadingSection');
    const skillsSection = document.getElementById('skillsSection');
    const resultsSection = document.getElementById('resultsSection');
    const errorAlert = document.getElementById('errorAlert');
    const successAlert = document.getElementById('successAlert');
    const loadingText = document.getElementById('loadingText');

    // Initialize event listeners
    resumeForm.addEventListener('submit', handleResumeUpload);
    findMatchesBtn.addEventListener('click', handleFindMatches);
    
    // Premium features event listeners
    const downloadResumeBtn = document.getElementById('downloadResumeBtn');
    const fixResumeBtn = document.getElementById('fixResumeBtn');
    const resumeBuilderBtn = document.getElementById('resumeBuilderBtn');
    const coverLetterBtn = document.getElementById('coverLetterBtn');
    const pdfEditorBtn = document.getElementById('pdfEditorBtn');
    const careerChatBtn = document.getElementById('careerChatBtn');


  function downloadResumeContent(userName, jobTitle) {
        const resumeText = `Resume for: ${userName}\nJob Title: ${jobTitle}\n\nThis is a sample AI-optimized resume.\n\nSkills:\n- Python\n- Machine Learning\n- FastAPI\n\nExperience:\n- Intern at GenAI Hackathon Project\n`;

        const blob = new Blob([resumeText], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);

        const a = document.createElement('a');
        a.href = url;
        a.download = `${userName.replace(/\s+/g, '_')}_Resume.txt`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }

    document.addEventListener("DOMContentLoaded", function () {
        const button = document.getElementById("downloadResumeBtn");
        button.addEventListener("click", function () {
            const userName = "Charu Hasini"; // Replace this dynamically if needed
            const jobTitle = "AI Developer"; // Replace this dynamically if needed
            downloadResumeContent(userName, jobTitle);
        });
    });

    
    if (downloadResumeBtn) {
        downloadResumeBtn.addEventListener('click', handleDownloadCustomResume);
    }
    
    if (fixResumeBtn) {
        fixResumeBtn.addEventListener('click', handleFixResume);
    }
    
    if (resumeBuilderBtn) {
        resumeBuilderBtn.addEventListener('click', handleResumeBuilder);
    }
    
    if (coverLetterBtn) {
        coverLetterBtn.addEventListener('click', handleCoverLetter);
    }
    
    if (pdfEditorBtn) {
        pdfEditorBtn.addEventListener('click', handlePdfEditor);
    }
    
    if (careerChatBtn) {
        careerChatBtn.addEventListener('click', handleCareerChat);
    }
});

// Handle Resume Builder Assistant
async function handleResumeBuilder() {
    try {
        showPremiumModal('Resume Builder Assistant', 'Loading step-by-step resume builder...');
        
        const response = await fetch('/resume_builder', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                step: 'start',
                data: {}
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            displayResumeBuilderStep(data.response);
        } else {
            showPremiumModal('Resume Builder Error', data.error || 'Failed to load resume builder');
        }
    } catch (error) {
        showPremiumModal('Resume Builder Error', 'Network error occurred');
        console.error('Resume builder error:', error);
    }
}

// Handle AI-Powered Cover Letter Generator
async function handleCoverLetter() {
    try {
        showPremiumModal('AI Cover Letter Generator', 'Generating personalized cover letter...');
        
        const response = await fetch('/cover_letter', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                company_name: '',
                job_title: ''
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            displayCoverLetter(data.cover_letter, data.user_name);
        } else {
            showPremiumModal('Cover Letter Error', data.error || 'Failed to generate cover letter');
        }
    } catch (error) {
        showPremiumModal('Cover Letter Error', 'Network error occurred');
        console.error('Cover letter error:', error);
    }
}

// Handle PDF Resume Editor
async function handlePdfEditor() {
    try {
        showPremiumModal('PDF Resume Editor', 'Loading PDF editor interface...');
        
        const response = await fetch('/pdf_editor', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                action: 'load'
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            displayPdfEditor(data.response);
        } else {
            showPremiumModal('PDF Editor Error', data.error || 'Failed to load PDF editor');
        }
    } catch (error) {
        showPremiumModal('PDF Editor Error', 'Network error occurred');
        console.error('PDF editor error:', error);
    }
}

// Handle Chatbot Career Assistant
async function handleCareerChat() {
    try {
        showCareerChatModal();
    } catch (error) {
        showPremiumModal('Career Assistant Error', 'Failed to load career assistant');
        console.error('Career chat error:', error);
    }
}

// Display Resume Builder Step
function displayResumeBuilderStep(stepData) {
    let content = `
        <div class="resume-builder-step">
            <h4><i class="fas fa-cogs me-2"></i>${stepData.title}</h4>
            <p class="text-muted">${stepData.description}</p>
            
            <form id="resumeBuilderForm">
    `;
    
    if (stepData.fields) {
        stepData.fields.forEach(field => {
            content += `
                <div class="mb-3">
                    <label class="form-label">${field.label} ${field.required ? '<span class="text-danger">*</span>' : ''}</label>
                    ${field.type === 'textarea' ? 
                        `<textarea class="form-control" name="${field.name}" placeholder="${field.placeholder || ''}" ${field.required ? 'required' : ''}>${field.value || ''}</textarea>` :
                        `<input type="${field.type}" class="form-control" name="${field.name}" placeholder="${field.placeholder || ''}" value="${field.value || ''}" ${field.required ? 'required' : ''}>`
                    }
                </div>
            `;
        });
    }
    
    if (stepData.sample) {
        content += `
            <div class="alert alert-info">
                <h6><i class="fas fa-lightbulb me-2"></i>Sample:</h6>
                <p class="mb-0">${stepData.sample}</p>
            </div>
        `;
    }
    
    if (stepData.tips) {
        content += `
            <div class="mt-3">
                <h6><i class="fas fa-tips me-2"></i>Tips:</h6>
                <ul class="list-unstyled">
                    ${stepData.tips.map(tip => `<li><i class="fas fa-check text-success me-2"></i>${tip}</li>`).join('')}
                </ul>
            </div>
        `;
    }
    
    content += `
            <div class="d-flex justify-content-between mt-4">
                <button type="button" class="btn btn-secondary" onclick="previousStep()">Previous</button>
                <button type="submit" class="btn btn-primary">Next Step</button>
            </div>
        </form>
    </div>
    `;
    
    showPremiumModal('Resume Builder Assistant', content);
}

// Display Cover Letter
function displayCoverLetter(coverLetter, userName) {
    const content = `
        <div class="cover-letter-generator">
            <h4><i class="fas fa-envelope me-2"></i>AI-Generated Cover Letter</h4>
            
            <div class="cover-letter-content bg-light p-4 mb-4" style="border-left: 4px solid #007bff;">
                <div class="mb-3">
                    <strong>${coverLetter.header.date}</strong><br>
                    ${coverLetter.header.recipient}<br>
                    <strong>Re: ${coverLetter.header.subject}</strong>
                </div>
                
                <div class="mb-3">
                    ${coverLetter.opening}
                </div>
                
                ${coverLetter.body.map(paragraph => `<div class="mb-3">${paragraph}</div>`).join('')}
                
                <div class="mt-3">
                    ${coverLetter.closing}
                </div>
            </div>
            
            <div class="row">
                <div class="col-md-6">
                    <h6><i class="fas fa-lightbulb me-2"></i>Customization Tips:</h6>
                    <ul class="list-unstyled">
                        ${coverLetter.tips.map(tip => `<li><i class="fas fa-check text-success me-2"></i>${tip}</li>`).join('')}
                    </ul>
                </div>
                <div class="col-md-6">
                    <div class="d-grid">
                        <button class="btn btn-primary mb-2" onclick="customizeCoverLetter()">
                            <i class="fas fa-edit me-2"></i>Customize for Specific Job
                        </button>
                        <button class="btn btn-outline-primary" onclick="downloadCoverLetter()">
                            <i class="fas fa-download me-2"></i>Download as PDF
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    showPremiumModal('AI Cover Letter Generator', content);
}

// Display PDF Editor
function displayPdfEditor(editorData) {
    const content = `
        <div class="pdf-editor">
            <h4><i class="fas fa-edit me-2"></i>${editorData.title}</h4>
            <p class="text-muted">${editorData.description}</p>
            
            <div class="row mb-4">
                <div class="col-md-8">
                    <div class="card">
                        <div class="card-header">
                            <h6><i class="fas fa-file-pdf me-2"></i>Current Resume</h6>
                        </div>
                        <div class="card-body">
                            <div class="d-flex justify-content-between align-items-center">
                                <div>
                                    <strong>${editorData.current_resume.filename}</strong><br>
                                    <small class="text-muted">Uploaded: ${editorData.current_resume.upload_date} • Size: ${editorData.current_resume.file_size}</small>
                                </div>
                                <button class="btn btn-sm btn-outline-primary">
                                    <i class="fas fa-eye me-1"></i>Preview
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="card">
                        <div class="card-header">
                            <h6><i class="fas fa-tools me-2"></i>Editing Tools</h6>
                        </div>
                        <div class="card-body p-2">
                            ${editorData.tools.map(tool => `
                                <button class="btn btn-sm btn-outline-secondary me-2 mb-2" onclick="applyTool('${tool.action}')">
                                    <i class="${tool.icon} me-1"></i>${tool.name}
                                </button>
                            `).join('')}
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="row">
                <div class="col-md-8">
                    <div class="resume-sections">
                        ${editorData.sections.map((section, index) => `
                            <div class="card mb-3">
                                <div class="card-header d-flex justify-content-between align-items-center">
                                    <h6 class="mb-0"><i class="${section.icon} me-2"></i>${section.name}</h6>
                                    ${section.editable ? `<button class="btn btn-sm btn-outline-primary" onclick="editSection(${index})"><i class="fas fa-edit"></i></button>` : ''}
                                </div>
                                <div class="card-body">
                                    <div id="section-${index}" style="white-space: pre-line;">${section.content}</div>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="card">
                        <div class="card-header">
                            <h6><i class="fas fa-palette me-2"></i>Templates</h6>
                        </div>
                        <div class="card-body">
                            ${editorData.templates.map(template => `
                                <div class="template-option mb-2 p-2 border rounded" style="cursor: pointer;" onclick="applyTemplate('${template.name}')">
                                    <strong>${template.name}</strong><br>
                                    <small class="text-muted">${template.preview}</small>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    showPremiumModal('PDF Resume Editor', content, 'xl');
}

// Show Career Chat Modal
function showCareerChatModal() {
    const content = `
        <div class="career-chat">
            <h4><i class="fas fa-robot me-2"></i>Career Assistant</h4>
            <p class="text-muted">Ask me anything about your career, job search, or professional development!</p>
            
            <div id="chatMessages" class="chat-messages mb-3" style="height: 400px; overflow-y: auto; border: 1px solid #dee2e6; border-radius: 0.375rem; padding: 1rem;">
                <div class="message assistant-message mb-3">
                    <div class="d-flex">
                        <div class="avatar me-2">
                            <i class="fas fa-robot text-primary"></i>
                        </div>
                        <div class="message-content">
                            <p class="mb-1"><strong>Career Assistant</strong></p>
                            <p>Hello! I'm your AI career assistant. I can help you with:</p>
                            <ul class="mb-0">
                                <li>Resume and interview advice</li>
                                <li>Salary negotiation tips</li>
                                <li>Career growth strategies</li>
                                <li>Skill development recommendations</li>
                                <li>Job search best practices</li>
                            </ul>
                            <p class="mt-2">What would you like to discuss?</p>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="chat-input">
                <div class="input-group">
                    <input type="text" id="chatInput" class="form-control" placeholder="Type your career question here..." onkeypress="handleChatKeyPress(event)">
                    <button class="btn btn-primary" onclick="sendChatMessage()">
                        <i class="fas fa-paper-plane"></i>
                    </button>
                </div>
            </div>
            
            <div class="mt-3">
                <h6>Quick Questions:</h6>
                <div class="d-flex flex-wrap gap-2">
                    <button class="btn btn-sm btn-outline-secondary" onclick="askQuickQuestion('How can I improve my resume?')">Resume Tips</button>
                    <button class="btn btn-sm btn-outline-secondary" onclick="askQuickQuestion('What salary should I negotiate?')">Salary Advice</button>
                    <button class="btn btn-sm btn-outline-secondary" onclick="askQuickQuestion('How do I prepare for interviews?')">Interview Prep</button>
                    <button class="btn btn-sm btn-outline-secondary" onclick="askQuickQuestion('What skills should I learn next?')">Skill Development</button>
                </div>
            </div>
        </div>
    `;
    
    showPremiumModal('Career Assistant', content, 'lg');
}

// Send chat message
async function sendChatMessage() {
    const input = document.getElementById('chatInput');
    const message = input.value.trim();
    
    if (!message) return;
    
    // Add user message to chat
    addChatMessage(message, 'user');
    input.value = '';
    
    // Show typing indicator
    addTypingIndicator();
    
    try {
        const response = await fetch('/career_chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: message,
                history: getChatHistory()
            })
        });
        
        const data = await response.json();
        
        // Remove typing indicator
        removeTypingIndicator();
        
        if (data.success) {
            addChatMessage(data.response.message, 'assistant', data.response.suggestions);
        } else {
            addChatMessage('Sorry, I encountered an error. Please try again.', 'assistant');
        }
    } catch (error) {
        removeTypingIndicator();
        addChatMessage('Network error occurred. Please check your connection.', 'assistant');
        console.error('Chat error:', error);
    }
}

// Handle chat key press
function handleChatKeyPress(event) {
    if (event.key === 'Enter') {
        sendChatMessage();
    }
}

// Ask quick question
function askQuickQuestion(question) {
    document.getElementById('chatInput').value = question;
    sendChatMessage();
}

// Add chat message
function addChatMessage(message, sender, suggestions = []) {
    const chatMessages = document.getElementById('chatMessages');
    const isUser = sender === 'user';
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${isUser ? 'user-message' : 'assistant-message'} mb-3`;
    
    messageDiv.innerHTML = `
        <div class="d-flex ${isUser ? 'justify-content-end' : ''}">
            ${!isUser ? '<div class="avatar me-2"><i class="fas fa-robot text-primary"></i></div>' : ''}
            <div class="message-content ${isUser ? 'bg-primary text-white' : 'bg-light'}" style="max-width: 80%; padding: 0.75rem; border-radius: 0.5rem;">
                <p class="mb-1"><strong>${isUser ? 'You' : 'Career Assistant'}</strong></p>
                <div style="white-space: pre-line;">${message}</div>
                ${suggestions.length > 0 ? `
                    <div class="mt-2">
                        <small>Suggestions:</small>
                        <ul class="mb-0 mt-1">
                            ${suggestions.map(suggestion => `<li>${suggestion}</li>`).join('')}
                        </ul>
                    </div>
                ` : ''}
            </div>
            ${isUser ? '<div class="avatar ms-2"><i class="fas fa-user text-secondary"></i></div>' : ''}
        </div>
    `;
    
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Add typing indicator
function addTypingIndicator() {
    const chatMessages = document.getElementById('chatMessages');
    const typingDiv = document.createElement('div');
    typingDiv.id = 'typingIndicator';
    typingDiv.className = 'message assistant-message mb-3';
    typingDiv.innerHTML = `
        <div class="d-flex">
            <div class="avatar me-2"><i class="fas fa-robot text-primary"></i></div>
            <div class="message-content bg-light" style="padding: 0.75rem; border-radius: 0.5rem;">
                <div class="typing-animation">
                    <span></span><span></span><span></span>
                </div>
            </div>
        </div>
    `;
    
    chatMessages.appendChild(typingDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Remove typing indicator
function removeTypingIndicator() {
    const typingIndicator = document.getElementById('typingIndicator');
    if (typingIndicator) {
        typingIndicator.remove();
    }
}

// Get chat history
function getChatHistory() {
    const messages = document.querySelectorAll('.message');
    const history = [];
    
    messages.forEach(message => {
        const content = message.querySelector('.message-content div, .message-content p:last-child');
        const isUser = message.classList.contains('user-message');
        if (content && !message.id === 'typingIndicator') {
            history.push({
                role: isUser ? 'user' : 'assistant',
                content: content.textContent.trim()
            });
        }
    });
    
    return history.slice(-10); // Keep last 10 messages for context
}

// Handle resume upload
async function handleResumeUpload(event) {
    event.preventDefault();
    
    const formData = new FormData(resumeForm);
    const fileInput = document.getElementById('resumeFile');
    const nameInput = document.getElementById('userName');
    const emailInput = document.getElementById('userEmail');
    
    // Validate required fields
    if (!nameInput.value.trim()) {
        showError('Please enter your full name.');
        return;
    }
    
    if (!emailInput.value.trim()) {
        showError('Please enter your email address.');
        return;
    }
    
    // Validate email format
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(emailInput.value.trim())) {
        showError('Please enter a valid email address.');
        return;
    }
    
    // Validate file selection
    if (!fileInput.files.length) {
        showError('Please select a resume file to upload.');
        return;
    }

    // Validate file type
    const file = fileInput.files[0];
    const allowedTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
    if (!allowedTypes.includes(file.type) && !file.name.toLowerCase().endsWith('.pdf') && !file.name.toLowerCase().endsWith('.docx')) {
        showError('Please upload a PDF or DOCX file.');
        return;
    }

    // Validate file size (16MB limit)
    const maxSize = 16 * 1024 * 1024; // 16MB in bytes
    if (file.size > maxSize) {
        showError('File too large. Please upload a file smaller than 16MB.');
        return;
    }

    try {
        // Show loading
        showLoading('Uploading and analyzing your resume...');
        hideError();
        hideSuccess();

        // Upload file
        const response = await fetch('/upload_resume', {
            method: 'POST',
            body: formData
        });

        const result = await response.json();

            if (result.success) {
                // Show extracted skills
                displaySkills(result.skills);
                
                // Show notification status if email notifications enabled
                const emailNotifications = document.getElementById('emailNotifications');
                if (emailNotifications && emailNotifications.checked) {
                    showNotificationStatus();
                }
                
                // Show premium features section
                showPremiumFeatures();
                
                showSuccess(result.message + ' Email notifications have been set up for future job matches.');
                hideLoading();
            } else {
                hideLoading();
                showError(result.error || 'Failed to process resume. Please try again.');
            }

        } catch (error) {
            hideLoading();
            console.error('Upload error:', error);
            showError('Network error. Please check your connection and try again.');
        }
    }

    // Handle find matches
    async function handleFindMatches() {
        try {
            // Show loading
            showLoading('Finding the best job matches for you...');
            hideError();
            hideSuccess();

            // Get recommendations
            const response = await fetch('/recommend');
            const result = await response.json();

            if (result.success) {
                // Display job matches
                displayJobMatches(result.recommendations, result.user_skills);
                hideLoading();
                showSuccess(`Found ${result.recommendations.length} job matches for you!`);
            } else {
                hideLoading();
                showError(result.error || 'Failed to get job recommendations. Please try again.');
            }

        } catch (error) {
            hideLoading();
            console.error('Recommendation error:', error);
            showError('Network error. Please check your connection and try again.');
        }
    }

    // Display extracted skills
    function displaySkills(skills) {
        const skillsList = document.getElementById('skillsList');
        
        if (!skills || skills.length === 0) {
            skillsList.innerHTML = '<p class="text-muted">No skills were extracted from your resume.</p>';
            skillsSection.style.display = 'none';
            return;
        }

        // Create skill badges
        const skillBadges = skills.map(skill => 
            `<span class="skill-badge">${escapeHtml(skill)}</span>`
        ).join('');

        skillsList.innerHTML = `
            <p class="mb-3">We found <strong>${skills.length}</strong> technical skills in your resume:</p>
            <div class="skills-container">${skillBadges}</div>
        `;

        // Show skills section with animation
        skillsSection.style.display = 'block';
        skillsSection.classList.add('fade-in');
        
        // Scroll to skills section
        skillsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }

    // Display job matches
    function displayJobMatches(recommendations, userSkills) {
        const jobMatches = document.getElementById('jobMatches');
        
        if (!recommendations || recommendations.length === 0) {
            jobMatches.innerHTML = `
                <div class="text-center p-4">
                    <i class="fas fa-search fa-3x text-muted mb-3"></i>
                    <h5>No job matches found</h5>
                    <p class="text-muted">Try uploading a different resume or check back later for new opportunities.</p>
                </div>
            `;
            resultsSection.style.display = 'block';
            return;
        }

        // Create job match cards
        const jobCards = recommendations.map((job, index) => {
            const matchClass = getMatchClass(job.match_percentage);
            const matchColor = getMatchColor(job.match_percentage);
            
            return `
                <div class="job-match-card card mb-4">
                    <div class="card-body">
                        <div class="row align-items-center">
                            <div class="col-md-8">
                                <h5 class="card-title mb-2">
                                    <i class="fas fa-briefcase me-2"></i>
                                    ${escapeHtml(job.title)}
                                </h5>
                                <div class="company-info mb-3">
                                    <i class="fas fa-building me-1"></i>
                                    ${escapeHtml(job.company)}
                                    ${job.location ? `<span class="ms-3"><i class="fas fa-map-marker-alt me-1"></i>${escapeHtml(job.location)}</span>` : ''}
                                    ${job.experience_level ? `<span class="ms-3"><i class="fas fa-star me-1"></i>${escapeHtml(job.experience_level)}</span>` : ''}
                                </div>
                                ${job.description ? `<p class="card-text text-muted small">${escapeHtml(job.description)}</p>` : ''}
                            </div>
                            <div class="col-md-4 text-center">
                                <div class="match-percentage ${matchClass}">${job.match_percentage}%</div>
                                <div class="progress match-progress mb-2">
                                    <div class="progress-bar bg-${matchColor}" style="width: ${job.match_percentage}%"></div>
                                </div>
                                <small class="text-muted">Match Score</small>
                                
                                <div class="mt-3">
                                    <div class="ats-score badge bg-info fs-6">ATS: ${job.ats_score || 0}/100</div>
                                    <br><small class="text-muted">Resume Compatibility</small>
                                </div>
                            </div>
                        </div>
                        
                        <hr>
                        
                        <div class="row">
                            <div class="col-md-6">
                                <h6 class="mb-2">
                                    <i class="fas fa-check-circle text-success me-1"></i>
                                    Required Skills
                                </h6>
                                <div class="mb-3">
                                    ${job.required_skills.map(skill => 
                                        `<span class="required-skill">${escapeHtml(skill)}</span>`
                                    ).join('')}
                                </div>
                            </div>
                            <div class="col-md-6">
                                <h6 class="mb-2">
                                    <i class="fas fa-exclamation-triangle text-warning me-1"></i>
                                    Skills to Develop (${job.missing_skills.length})
                                </h6>
                                <div class="mb-3">
                                    ${job.missing_skills.length > 0 ? 
                                        job.missing_skills.map(skill => 
                                            `<span class="missing-skill">${escapeHtml(skill)}</span>`
                                        ).join('') : 
                                        '<span class="text-success"><i class="fas fa-star me-1"></i>Perfect match!</span>'
                                    }
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            `;
        }).join('');

        jobMatches.innerHTML = jobCards;

        // Show results section with animation
        resultsSection.style.display = 'block';
        resultsSection.classList.add('fade-in');
        
        // Scroll to results section
        resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }

    // Get match class based on percentage
    function getMatchClass(percentage) {
        if (percentage >= 70) return 'high';
        if (percentage >= 50) return 'medium';
        return 'low';
    }

    // Get match color based on percentage
    function getMatchColor(percentage) {
        if (percentage >= 70) return 'success';
        if (percentage >= 50) return 'warning';
        return 'danger';
    }

    // Show loading section
    function showLoading(text) {
        loadingText.textContent = text;
        loadingSection.style.display = 'block';
        loadingSection.classList.add('fade-in');
        
        // Disable form elements
        uploadBtn.disabled = true;
        if (findMatchesBtn) findMatchesBtn.disabled = true;
    }

    // Hide loading section
    function hideLoading() {
        loadingSection.style.display = 'none';
        
        // Enable form elements
        uploadBtn.disabled = false;
        if (findMatchesBtn) findMatchesBtn.disabled = false;
    }

    // Show error alert
    function showError(message) {
        const errorMessage = document.getElementById('errorMessage');
        errorMessage.textContent = message;
        errorAlert.style.display = 'block';
        errorAlert.classList.add('show');
        
        // Auto-hide after 10 seconds
        setTimeout(() => {
            hideError();
        }, 10000);
    }

    // Hide error alert
    function hideError() {
        errorAlert.style.display = 'none';
        errorAlert.classList.remove('show');
    }

    // Show success alert
    function showSuccess(message) {
        const successMessage = document.getElementById('successMessage');
        successMessage.textContent = message;
        successAlert.style.display = 'block';
        successAlert.classList.add('show');
        
        // Auto-hide after 5 seconds
        setTimeout(() => {
            hideSuccess();
        }, 5000);
    }

    // Hide success alert
    function hideSuccess() {
        successAlert.style.display = 'none';
        successAlert.classList.remove('show');
    }

    // Show notification status
    function showNotificationStatus() {
        const notificationStatus = document.getElementById('notificationStatus');
        if (notificationStatus) {
            notificationStatus.style.display = 'block';
        }
    }

    // Hide notification status
    function hideNotificationStatus() {
        const notificationStatus = document.getElementById('notificationStatus');
        if (notificationStatus) {
            notificationStatus.style.display = 'none';
        }
    }

    // Escape HTML to prevent XSS
    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    // Reset form and sections
    function resetApplication() {
        resumeForm.reset();
        skillsSection.style.display = 'none';
        resultsSection.style.display = 'none';
        hideLoading();
        hideError();
        hideSuccess();
    }

    // Premium feature handlers
    async function handleDownloadCustomResume() {
        try {
            // Show job selection modal or use first job match
            const jobCards = document.querySelectorAll('.job-match-card');
            if (jobCards.length === 0) {
                showError('Please find job matches first before generating a custom resume.');
                return;
            }
            
            // Use the first (highest match) job for simplicity
            const firstJobId = 1; // This would be extracted from the job card data
            
            showLoading('Generating your custom resume...');
            hideError();
            
            const response = await fetch('/download_custom_resume', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ job_id: firstJobId })
            });
            
            const data = await response.json();
            hideLoading();
            
            if (data.success) {
                showCustomResumeModal(data);
            } else {
                showError(data.error || 'Failed to generate custom resume');
            }
            
        } catch (error) {
            hideLoading();
            showError('Error generating custom resume: ' + error.message);
        }
    }
    
    async function handleFixResume() {
        try {
            showLoading('Analyzing your resume for improvements...');
            hideError();
            
            const response = await fetch('/fix_resume', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            });
            
            const data = await response.json();
            hideLoading();
            
            if (data.success) {
                showResumeImprovementsModal(data);
            } else {
                showError(data.error || 'Failed to analyze resume');
            }
            
        } catch (error) {
            hideLoading();
            showError('Error analyzing resume: ' + error.message);
        }
    }
    
    function showCustomResumeModal(data) {
        const modal = document.createElement('div');
        modal.className = 'modal fade';
        modal.innerHTML = `
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header bg-primary text-white">
                        <h5 class="modal-title">
                            <i class="fas fa-download me-2"></i>Custom Resume for ${data.job_title}
                        </h5>
                        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <div class="alert alert-info">
                            <strong>Optimized for:</strong> ${data.job_title} at ${data.company}
                        </div>
                        
                        <div class="card mb-3">
                            <div class="card-header">
                                <h6 class="mb-0">Professional Summary</h6>
                            </div>
                            <div class="card-body">
                                <p>${data.resume_content.summary}</p>
                            </div>
                        </div>
                        
                        <div class="row">
                            <div class="col-md-6">
                                <div class="card mb-3">
                                    <div class="card-header bg-success text-white">
                                        <h6 class="mb-0">Highlighted Skills</h6>
                                    </div>
                                    <div class="card-body">
                                        ${data.resume_content.skills.highlighted.map(skill => 
                                            `<span class="badge bg-success me-1 mb-1">${skill}</span>`
                                        ).join('')}
                                    </div>
                                </div>
                            </div>
                            <div class="col-md-6">
                                <div class="card mb-3">
                                    <div class="card-header bg-warning text-dark">
                                        <h6 class="mb-0">Skills to Add</h6>
                                    </div>
                                    <div class="card-body">
                                        ${data.resume_content.skills.recommendations.map(skill => 
                                            `<span class="badge bg-warning me-1 mb-1">${skill}</span>`
                                        ).join('')}
                                    </div>
                                </div>
                            </div>
                        </div>
                        
                        <div class="card">
                            <div class="card-header">
                                <h6 class="mb-0">Optimization Tips</h6>
                            </div>
                            <div class="card-body">
                                <ul class="list-unstyled">
                                    ${data.resume_content.optimization_tips.map(tip => 
                                        `<li><i class="fas fa-lightbulb text-warning me-2"></i>${tip}</li>`
                                    ).join('')}
                                </ul>
                            </div>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                        <button type="button" class="btn btn-primary" id="downloadResumeBtn">
    <i class="fas fa-download me-2"></i>Download as Text
</button>

                            <i class="fas fa-download me-2"></i>Download as Text
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        const bootstrapModal = new bootstrap.Modal(modal);
        bootstrapModal.show();
        
        modal.addEventListener('hidden.bs.modal', () => {
            document.body.removeChild(modal);
        });
    }
    
    function showResumeImprovementsModal(data) {
        const modal = document.createElement('div');
        modal.className = 'modal fade';
        modal.innerHTML = `
            <div class="modal-dialog modal-xl">
                <div class="modal-content">
                    <div class="modal-header bg-warning text-dark">
                        <h5 class="modal-title">
                            <i class="fas fa-magic me-2"></i>AI Resume Analysis for ${data.user_name}
                        </h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <div class="row mb-4">
                            <div class="col-md-3">
                                <div class="text-center">
                                    <div class="display-4 text-primary">${data.improvements.overall_score}</div>
                                    <div class="text-muted">Overall Score</div>
                                </div>
                            </div>
                            <div class="col-md-9">
                                <div class="progress mb-2" style="height: 20px;">
                                    <div class="progress-bar bg-primary" style="width: ${data.improvements.overall_score}%">
                                        ${data.improvements.overall_score}/100
                                    </div>
                                </div>
                                <small class="text-muted">Based on skills, experience, education, and projects</small>
                            </div>
                        </div>
                        
                        <div class="row">
                            <div class="col-md-6">
                                <div class="card mb-3 border-success">
                                    <div class="card-header bg-success text-white">
                                        <h6 class="mb-0"><i class="fas fa-star me-2"></i>Strengths</h6>
                                    </div>
                                    <div class="card-body">
                                        <ul class="list-unstyled">
                                            ${data.improvements.strengths.map(strength => 
                                                `<li><i class="fas fa-check text-success me-2"></i>${strength}</li>`
                                            ).join('')}
                                        </ul>
                                    </div>
                                </div>
                            </div>
                            
                            <div class="col-md-6">
                                <div class="card mb-3 border-warning">
                                    <div class="card-header bg-warning text-dark">
                                        <h6 class="mb-0"><i class="fas fa-exclamation-triangle me-2"></i>Areas to Improve</h6>
                                    </div>
                                    <div class="card-body">
                                        <ul class="list-unstyled">
                                            ${data.improvements.improvements.slice(0, 5).map(improvement => 
                                                `<li><i class="fas fa-arrow-up text-warning me-2"></i>${improvement}</li>`
                                            ).join('')}
                                        </ul>
                                    </div>
                                </div>
                            </div>
                        </div>
                        
                        <div class="row">
                            <div class="col-md-6">
                                <div class="card mb-3">
                                    <div class="card-header bg-info text-white">
                                        <h6 class="mb-0"><i class="fas fa-plus me-2"></i>Skill Recommendations</h6>
                                    </div>
                                    <div class="card-body">
                                        <ul class="list-unstyled">
                                            ${data.improvements.skill_recommendations.map(rec => 
                                                `<li><i class="fas fa-lightbulb text-info me-2"></i>${rec}</li>`
                                            ).join('')}
                                        </ul>
                                    </div>
                                </div>
                            </div>
                            
                            <div class="col-md-6">
                                <div class="card mb-3">
                                    <div class="card-header bg-secondary text-white">
                                        <h6 class="mb-0"><i class="fas fa-chart-line me-2"></i>Market Insights</h6>
                                    </div>
                                    <div class="card-body">
                                        <ul class="list-unstyled">
                                            ${data.improvements.market_insights.map(insight => 
                                                `<li><i class="fas fa-trending-up text-secondary me-2"></i>${insight}</li>`
                                            ).join('')}
                                        </ul>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                        <button type="button" class="btn btn-warning" onclick="downloadImprovementsReport('${data.user_name}')">
                            <i class="fas fa-download me-2"></i>Download Report
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        const bootstrapModal = new bootstrap.Modal(modal);
        bootstrapModal.show();
        
        modal.addEventListener('hidden.bs.modal', () => {
            document.body.removeChild(modal);
        });
    }
    
    // Show premium features section when user has uploaded resume
    function showPremiumFeatures() {
        const premiumFeatures = document.getElementById('premiumFeatures');
        if (premiumFeatures) {
            premiumFeatures.style.display = 'block';
        }
    }

    // Add file input change listener for better UX
    const fileInput = document.getElementById('resumeFile');
    fileInput.addEventListener('change', function() {
        if (this.files.length > 0) {
            const file = this.files[0];
            const fileName = file.name;
            const fileSize = (file.size / (1024 * 1024)).toFixed(2);
            
            // Update button text to show selected file
            uploadBtn.innerHTML = `
                <i class="fas fa-cloud-upload-alt me-2"></i>
                Upload "${fileName}" (${fileSize} MB)
            `;
        } else {
            // Reset button text
            uploadBtn.innerHTML = `
                <i class="fas fa-cloud-upload-alt me-2"></i>
                Upload & Analyze Resume
            `;
        }
    });
});
