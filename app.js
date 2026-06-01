// AI Job Matcher - Enhanced JavaScript with Premium Features
document.addEventListener('DOMContentLoaded', function() {
    // Initialize elements
    const resumeForm = document.getElementById('resumeForm');
    const findMatchesBtn = document.getElementById('findMatchesBtn');
    const skillsSection = document.getElementById('skillsSection');
    const jobMatchesSection = document.getElementById('resultsSection');
    
    // Initialize event listeners only if elements exist
    if (resumeForm) {
        resumeForm.addEventListener('submit', handleResumeUpload);
    } else {
        console.error('Resume form not found');
    }
    
    if (findMatchesBtn) {
        findMatchesBtn.addEventListener('click', handleFindMatches);
    }
    
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
        if (content && message.id !== 'typingIndicator') {
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
    const skillsSection = document.getElementById('skillsSection');
    
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
    const jobMatchesSection = document.getElementById('jobMatchesSection');
    
    if (!recommendations || recommendations.length === 0) {
        jobMatches.innerHTML = `
            <div class="text-center p-4">
                <i class="fas fa-search fa-3x text-muted mb-3"></i>
                <h5>No job matches found</h5>
                <p class="text-muted">Try uploading a different resume or check back later for new opportunities.</p>
            </div>
        `;
        jobMatchesSection.style.display = 'block';
        return;
    }

    // Create job match cards
    const jobCards = recommendations.map(job => `
        <div class="job-match-card card mb-3">
            <div class="card-body">
                <div class="row align-items-center">
                    <div class="col-md-8">
                        <h5 class="card-title mb-2">
                            <i class="fas fa-briefcase me-2"></i>${escapeHtml(job.title)}
                        </h5>
                        <p class="company-info mb-2">
                            <i class="fas fa-building me-2"></i>${escapeHtml(job.company)}
                            <span class="ms-3"><i class="fas fa-map-marker-alt me-1"></i>${escapeHtml(job.location || 'Remote')}</span>
                        </p>
                        <div class="mb-2">
                            <small class="text-muted">Required Skills:</small><br>
                            ${job.required_skills.map(skill => `<span class="required-skill">${escapeHtml(skill)}</span>`).join('')}
                        </div>
                        ${job.missing_skills && job.missing_skills.length > 0 ? `
                            <div class="mb-2">
                                <small class="text-muted">Skills to develop:</small><br>
                                ${job.missing_skills.map(skill => `<span class="missing-skill">${escapeHtml(skill)}</span>`).join('')}
                            </div>
                        ` : ''}
                    </div>
                    <div class="col-md-4 text-center">
                        <div class="match-percentage ${job.match_percentage >= 70 ? '' : job.match_percentage >= 40 ? 'medium' : 'low'}">
                            ${Math.round(job.match_percentage)}%
                        </div>
                        <small class="text-muted">Match Score</small>
                        ${job.ats_score ? `
                            <div class="mt-2">
                                <div class="text-info font-weight-bold">${job.ats_score}/100</div>
                                <small class="text-muted">ATS Score</small>
                            </div>
                        ` : ''}
                        <div class="progress match-progress mt-2">
                            <div class="progress-bar ${job.match_percentage >= 70 ? 'bg-success' : job.match_percentage >= 40 ? 'bg-warning' : 'bg-danger'}" 
                                 style="width: ${job.match_percentage}%"></div>
                        </div>
                        <button class="btn btn-outline-primary btn-sm mt-2" onclick="generateCustomResume(${job.id})">
                            <i class="fas fa-download me-1"></i>Custom Resume
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `).join('');

    jobMatches.innerHTML = `
        <div class="d-flex justify-content-between align-items-center mb-3">
            <h4><i class="fas fa-star me-2"></i>Top Job Matches</h4>
            <small class="text-muted">${recommendations.length} matches found</small>
        </div>
        ${jobCards}
    `;

    // Show job matches section with animation
    jobMatchesSection.style.display = 'block';
    jobMatchesSection.classList.add('fade-in');
    
    // Scroll to job matches section
    jobMatchesSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// Generate custom resume for specific job
async function generateCustomResume(jobId) {
    try {
        showLoading('Generating custom resume for this position...');
        
        const response = await fetch('/download_custom_resume', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                job_id: jobId
            })
        });
        
        const data = await response.json();
        
        hideLoading();
        
        if (data.success) {
            // Display custom resume in modal
            displayCustomResumeModal(data.resume_content, data.job_title, data.company);
        } else {
            showError(data.error || 'Failed to generate custom resume');
        }
    } catch (error) {
        hideLoading();
        console.error('Custom resume generation error:', error);
        showError('Network error occurred');
    }
}

// Display custom resume modal
function displayCustomResumeModal(resumeContent, jobTitle, company) {
    const content = `
        <div class="custom-resume-content">
            <h4><i class="fas fa-file-alt me-2"></i>Custom Resume</h4>
            <p class="text-muted">Optimized for ${jobTitle} at ${company}</p>
            
            <div class="resume-preview bg-light p-4 mb-3" style="border-left: 4px solid #28a745; max-height: 500px; overflow-y: auto;">
                <div class="mb-4">
                    <h5>${resumeContent.header.name}</h5>
                    <p class="mb-1">${resumeContent.header.email}</p>
                    <p class="text-muted">Target: ${resumeContent.header.target_role} at ${resumeContent.header.target_company}</p>
                </div>
                
                <div class="mb-4">
                    <h6>Professional Summary</h6>
                    <p>${resumeContent.summary}</p>
                </div>
                
                <div class="mb-4">
                    <h6>Key Skills</h6>
                    <div class="mb-2">
                        <strong>Highlighted Skills:</strong><br>
                        ${resumeContent.skills.highlighted.map(skill => `<span class="badge bg-success me-1">${skill}</span>`).join('')}
                    </div>
                    ${resumeContent.skills.additional.length > 0 ? `
                        <div class="mb-2">
                            <strong>Additional Skills:</strong><br>
                            ${resumeContent.skills.additional.map(skill => `<span class="badge bg-secondary me-1">${skill}</span>`).join('')}
                        </div>
                    ` : ''}
                </div>
                
                <div class="mb-4">
                    <h6>Match Analysis</h6>
                    <div class="row">
                        <div class="col-md-6">
                            <p><strong>Match Score:</strong> ${resumeContent.match_analysis.score.toFixed(1)}%</p>
                            <p><strong>Matching Skills:</strong> ${resumeContent.match_analysis.matching_skills_count}</p>
                        </div>
                        <div class="col-md-6">
                            <p><strong>Total Requirements:</strong> ${resumeContent.match_analysis.total_requirements}</p>
                            <p><strong>Skills to Develop:</strong> ${resumeContent.match_analysis.missing_skills_count}</p>
                        </div>
                    </div>
                </div>
                
                <div class="mb-4">
                    <h6>Optimization Tips</h6>
                    <ul>
                        ${resumeContent.optimization_tips.map(tip => `<li>${tip}</li>`).join('')}
                    </ul>
                </div>
            </div>
            
            <div class="text-center">
                <button class="btn btn-success me-2" onclick="downloadResumeAsPDF()">
                    <i class="fas fa-download me-2"></i>Download as PDF
                </button>
                <button class="btn btn-outline-primary" onclick="emailCustomResume()">
                    <i class="fas fa-envelope me-2"></i>Email to Me
                </button>
            </div>
        </div>
    `;
    
    showPremiumModal('Custom Resume Generated', content, 'xl');
}

// Premium feature handlers
async function handleDownloadCustomResume() {
    // Get available jobs first to select from
    try {
        const response = await fetch('/jobs');
        const data = await response.json();
        
        if (data.success && data.jobs.length > 0) {
            showJobSelectionModal(data.jobs, 'download_custom_resume');
        } else {
            showError('No jobs available for custom resume generation');
        }
    } catch (error) {
        showError('Failed to load available jobs');
    }
}

async function handleFixResume() {
    try {
        showPremiumModal('Fix My Resume', 'Analyzing your resume for improvements...');
        
        const response = await fetch('/fix_resume', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            displayResumeImprovements(data.improvements, data.user_name);
        } else {
            showPremiumModal('Resume Analysis Error', data.error || 'Failed to analyze resume');
        }
    } catch (error) {
        showPremiumModal('Resume Analysis Error', 'Network error occurred');
        console.error('Resume analysis error:', error);
    }
}

// Display resume improvements
function displayResumeImprovements(improvements, userName) {
    const content = `
        <div class="resume-improvements">
            <h4><i class="fas fa-magic me-2"></i>Resume Analysis Results</h4>
            <p class="text-muted">Comprehensive analysis and improvement suggestions for ${userName}</p>
            
            <div class="row mb-4">
                <div class="col-md-6">
                    <div class="card">
                        <div class="card-body text-center">
                            <h2 class="text-primary">${improvements.overall_score}/100</h2>
                            <p class="mb-0">Overall Resume Score</p>
                        </div>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="card">
                        <div class="card-body">
                            <h6><i class="fas fa-star me-2"></i>Strengths</h6>
                            <ul class="list-unstyled mb-0">
                                ${improvements.strengths.map(strength => `<li><i class="fas fa-check text-success me-2"></i>${strength}</li>`).join('')}
                            </ul>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="row mb-4">
                <div class="col-md-6">
                    <div class="card">
                        <div class="card-header">
                            <h6><i class="fas fa-exclamation-triangle me-2"></i>Areas for Improvement</h6>
                        </div>
                        <div class="card-body">
                            <ul class="list-unstyled mb-0">
                                ${improvements.improvements.map(improvement => `<li class="mb-2"><i class="fas fa-arrow-right text-warning me-2"></i>${improvement}</li>`).join('')}
                            </ul>
                        </div>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="card">
                        <div class="card-header">
                            <h6><i class="fas fa-lightbulb me-2"></i>Skill Recommendations</h6>
                        </div>
                        <div class="card-body">
                            ${improvements.skill_recommendations.map(skill => `
                                <div class="mb-2">
                                    <strong>${skill}</strong>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="row mb-4">
                <div class="col-md-6">
                    <div class="card">
                        <div class="card-header">
                            <h6><i class="fas fa-chart-line me-2"></i>Market Insights</h6>
                        </div>
                        <div class="card-body">
                            <ul class="list-unstyled mb-0">
                                ${improvements.market_insights.map(insight => `<li class="mb-2"><i class="fas fa-info-circle text-info me-2"></i>${insight}</li>`).join('')}
                            </ul>
                        </div>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="card">
                        <div class="card-header">
                            <h6><i class="fas fa-paint-brush me-2"></i>Formatting Tips</h6>
                        </div>
                        <div class="card-body">
                            <ul class="list-unstyled mb-0">
                                ${improvements.formatting_tips.map(tip => `<li class="mb-2"><i class="fas fa-check text-success me-2"></i>${tip}</li>`).join('')}
                            </ul>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    showPremiumModal('Resume Analysis Complete', content, 'xl');
}

// Show job selection modal
function showJobSelectionModal(jobs, action) {
    const content = `
        <div class="job-selection">
            <h4><i class="fas fa-briefcase me-2"></i>Select Target Job</h4>
            <p class="text-muted">Choose a job position to optimize your resume for:</p>
            
            <div class="job-list" style="max-height: 400px; overflow-y: auto;">
                ${jobs.map(job => `
                    <div class="card mb-2 job-selection-card" style="cursor: pointer;" onclick="selectJob(${job.id}, '${action}')">
                        <div class="card-body py-3">
                            <div class="d-flex justify-content-between align-items-center">
                                <div>
                                    <h6 class="mb-1">${escapeHtml(job.title)}</h6>
                                    <small class="text-muted">${escapeHtml(job.company)} • ${escapeHtml(job.location || 'Remote')}</small>
                                </div>
                                <i class="fas fa-chevron-right text-muted"></i>
                            </div>
                        </div>
                    </div>
                `).join('')}
            </div>
        </div>
    `;
    
    showPremiumModal('Select Job Position', content);
}

// Select job for custom resume
function selectJob(jobId, action) {
    if (action === 'download_custom_resume') {
        generateCustomResume(jobId);
    }
}

// Utility functions
function showLoading(message) {
    const loadingSection = document.getElementById('loadingSection');
    const loadingText = document.getElementById('loadingText');
    if (loadingSection && loadingText) {
        loadingText.textContent = message;
        loadingSection.style.display = 'block';
    }
}

function hideLoading() {
    const loadingSection = document.getElementById('loadingSection');
    if (loadingSection) {
        loadingSection.style.display = 'none';
    }
}

function showError(message) {
    const errorAlert = document.getElementById('errorAlert');
    const errorMessage = document.getElementById('errorMessage');
    if (errorAlert && errorMessage) {
        errorMessage.textContent = message;
        errorAlert.style.display = 'block';
        errorAlert.classList.add('show');
        setTimeout(() => {
            errorAlert.style.display = 'none';
            errorAlert.classList.remove('show');
        }, 5000);
    }
}

function hideError() {
    const errorAlert = document.getElementById('errorAlert');
    if (errorAlert) {
        errorAlert.style.display = 'none';
    }
}

function showSuccess(message) {
    const successAlert = document.getElementById('successAlert');
    const successMessage = document.getElementById('successMessage');
    if (successAlert && successMessage) {
        successMessage.textContent = message;
        successAlert.style.display = 'block';
        successAlert.classList.add('show');
        setTimeout(() => {
            successAlert.style.display = 'none';
            successAlert.classList.remove('show');
        }, 5000);
    }
}

function hideSuccess() {
    const successAlert = document.getElementById('successAlert');
    if (successAlert) {
        successAlert.style.display = 'none';
    }
}

function showPremiumFeatures() {
    const premiumSection = document.getElementById('premiumFeatures');
    if (premiumSection) {
        premiumSection.style.display = 'block';
        premiumSection.classList.add('fade-in');
    }
}

function showNotificationStatus() {
    const notificationStatus = document.getElementById('notificationStatus');
    if (notificationStatus) {
        notificationStatus.style.display = 'block';
        notificationStatus.classList.add('fade-in');
    }
}

function showPremiumModal(title, content, size = 'lg') {
    // Create modal if it doesn't exist
    let modal = document.getElementById('premiumModal');
    if (!modal) {
        const modalHTML = `
            <div class="modal fade premium-modal" id="premiumModal" tabindex="-1">
                <div class="modal-dialog modal-${size}">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title" id="premiumModalTitle"></h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body" id="premiumModalBody"></div>
                    </div>
                </div>
            </div>
        `;
        document.body.insertAdjacentHTML('beforeend', modalHTML);
        modal = document.getElementById('premiumModal');
        
        // Initialize Bootstrap modal
        modal.bsModal = new bootstrap.Modal(modal);
    }
    
    // Update modal size if different
    const modalDialog = modal.querySelector('.modal-dialog');
    modalDialog.className = `modal-dialog modal-${size}`;
    
    // Set content
    document.getElementById('premiumModalTitle').textContent = title;
    document.getElementById('premiumModalBody').innerHTML = content;
    
    // Show modal
    modal.bsModal.show();
}

function escapeHtml(unsafe) {
    return unsafe
         .replace(/&/g, "&amp;")
         .replace(/</g, "&lt;")
         .replace(/>/g, "&gt;")
         .replace(/"/g, "&quot;")
         .replace(/'/g, "&#039;");
}

// Placeholder functions for PDF editor and other features
function applyTool(action) {
    console.log('Apply tool:', action);
    // Implementation for PDF editing tools
}

function editSection(index) {
    console.log('Edit section:', index);
    // Implementation for section editing
}

function applyTemplate(templateName) {
    console.log('Apply template:', templateName);
    // Implementation for template application
}

function customizeCoverLetter() {
    console.log('Customize cover letter');
    // Implementation for cover letter customization
}

function downloadCoverLetter() {
    console.log('Download cover letter');
    // Implementation for cover letter download
}

function downloadResumeAsPDF() {
    console.log('Download resume as PDF');
    // Implementation for PDF download
}

function emailCustomResume() {
    console.log('Email custom resume');
    // Implementation for email functionality
}

function previousStep() {
    console.log('Previous step');
    // Implementation for resume builder navigation
}