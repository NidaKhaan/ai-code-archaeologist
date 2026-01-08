// AI Code Archaeologist - Frontend JavaScript

const API_BASE = window.location.origin;

// DOM Elements
const analysisForm = document.getElementById('analysisForm');
const repoUrlInput = document.getElementById('repoUrl');
const apiKeyInput = document.getElementById('apiKey');
const analyzeBtn = document.getElementById('analyzeBtn');
const btnText = analyzeBtn.querySelector('.btn-text');
const btnLoader = analyzeBtn.querySelector('.btn-loader');
const statusBadge = document.getElementById('statusBadge');

const progressSection = document.getElementById('progressSection');
const progressText = document.getElementById('progressText');
const progressPercent = document.getElementById('progressPercent');
const progressFill = document.getElementById('progressFill');

const resultsSection = document.getElementById('resultsSection');
const repoInfo = document.getElementById('repoInfo');
const scoreGrade = document.getElementById('scoreGrade');
const scoreFill = document.getElementById('scoreFill');
const scoreDescription = document.getElementById('scoreDescription');
const statsGrid = document.getElementById('statsGrid');

const downloadMarkdown = document.getElementById('downloadMarkdown');
const downloadJSON = document.getElementById('downloadJSON');
const analyzeAnother = document.getElementById('analyzeAnother');

let currentAnalysisId = null;

// Form Submit Handler
analysisForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const repoUrl = repoUrlInput.value.trim();
    const apiKey = apiKeyInput.value.trim();
    
    if (!repoUrl || !apiKey) {
        showError('Please fill in all fields');
        return;
    }
    
    await analyzeRepository(repoUrl, apiKey);
});

// Analyze Repository
async function analyzeRepository(repoUrl, apiKey) {
    try {
        // Reset UI
        resultsSection.style.display = 'none';
        progressSection.style.display = 'block';
        
        // Update button state
        btnText.style.display = 'none';
        btnLoader.style.display = 'flex';
        analyzeBtn.disabled = true;
        statusBadge.textContent = 'Analyzing...';
        statusBadge.style.background = 'rgba(249, 115, 22, 0.1)';
        statusBadge.style.color = '#f97316';
        
        // Simulate progress steps
        await updateProgress(0, 'Fetching repository information...', 1);
        await sleep(1000);
        
        // Step 1: Get repo info
        const repoInfoData = await fetchRepoInfo(repoUrl, apiKey);
        await updateProgress(25, 'Repository found! Preparing to clone...', 2);
        await sleep(1500);
        
        // Step 2: Full analysis
        await updateProgress(50, 'Cloning repository and analyzing files...', 3);
        const analysisData = await performFullAnalysis(repoUrl, apiKey);
        
        await updateProgress(90, 'Generating insights...', 4);
        await sleep(1000);
        
        // Step 3: Display results
        await updateProgress(100, 'Analysis complete!', 4);
        await sleep(500);
        
        displayResults(analysisData, repoInfoData);
        
        // Update button state
        btnText.style.display = 'block';
        btnLoader.style.display = 'none';
        analyzeBtn.disabled = false;
        statusBadge.textContent = 'Complete';
        statusBadge.style.background = 'rgba(16, 185, 129, 0.1)';
        statusBadge.style.color = '#10b981';
        
    } catch (error) {
        console.error('Analysis error:', error);
        showError(error.message || 'Analysis failed. Please try again.');
        
        // Reset button
        btnText.style.display = 'block';
        btnLoader.style.display = 'none';
        analyzeBtn.disabled = false;
        progressSection.style.display = 'none';
        statusBadge.textContent = 'Error';
        statusBadge.style.background = 'rgba(239, 68, 68, 0.1)';
        statusBadge.style.color = '#ef4444';
    }
}

// Fetch Repository Info
async function fetchRepoInfo(repoUrl, apiKey) {
    const response = await fetch(`${API_BASE}/github/info?repo_url=${encodeURIComponent(repoUrl)}`, {
        headers: {
            'X-API-Key': apiKey
        }
    });
    
    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to fetch repository info');
    }
    
    const data = await response.json();
    return data.repository;
}

// Perform Full Analysis
async function performFullAnalysis(repoUrl, apiKey) {
    const response = await fetch(
        `${API_BASE}/github/analyze-full?repo_url=${encodeURIComponent(repoUrl)}&max_files=10`,
        {
            method: 'POST',
            headers: {
                'X-API-Key': apiKey
            }
        }
    );
    
    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Analysis failed');
    }
    
    const data = await response.json();
    currentAnalysisId = data.analysis_id;
    return data;
}

// Update Progress
async function updateProgress(percent, text, step) {
    progressPercent.textContent = `${percent}%`;
    progressText.textContent = text;
    progressFill.style.width = `${percent}%`;
    
    // Update steps
    document.querySelectorAll('.step').forEach((el, index) => {
        if (index + 1 <= step) {
            el.classList.add('active');
        } else {
            el.classList.remove('active');
        }
    });
}

// Display Results
function displayResults(analysisData, repoInfoData) {
    // Show results section
    progressSection.style.display = 'none';
    resultsSection.style.display = 'block';
    
    // Scroll to results
    resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    
    // Repository Info
    repoInfo.innerHTML = `
        <div class="info-row">
            <span class="info-label">Repository</span>
            <span class="info-value">${repoInfoData.name}</span>
        </div>
        <div class="info-row">
            <span class="info-label">Language</span>
            <span class="info-value">${repoInfoData.language || 'N/A'}</span>
        </div>
        <div class="info-row">
            <span class="info-label">Stars</span>
            <span class="info-value">⭐ ${repoInfoData.stars.toLocaleString()}</span>
        </div>
        <div class="info-row">
            <span class="info-label">Forks</span>
            <span class="info-value">🍴 ${repoInfoData.forks.toLocaleString()}</span>
        </div>
    `;
    
    // Overall Score (placeholder - calculate from summary)
    const maintainability = analysisData.summary?.average_maintainability || 0;
    let grade = 'C';
    if (maintainability >= 80) grade = 'A';
    else if (maintainability >= 60) grade = 'B';
    else if (maintainability >= 40) grade = 'C';
    else if (maintainability >= 20) grade = 'D';
    else grade = 'F';
    
    const descriptions = {
        'A': 'Excellent - Highly maintainable code',
        'B': 'Good - Well-structured and maintainable',
        'C': 'Fair - Acceptable but needs improvement',
        'D': 'Poor - Difficult to maintain',
        'F': 'Critical - Requires significant refactoring'
    };
    
    scoreGrade.textContent = grade;
    scoreFill.style.width = `${maintainability}%`;
    scoreDescription.textContent = descriptions[grade];
    
    // Summary Stats
    const summary = analysisData.summary;
    statsGrid.innerHTML = `
        <div class="stat-card">
            <div class="stat-label">Python Files</div>
            <div class="stat-value">${summary.total_python_files || 0}</div>
        </div>
        <div class="stat-card">
            <div class="stat-label">Files Analyzed</div>
            <div class="stat-value">${summary.files_analyzed || 0}</div>
        </div>
        <div class="stat-card">
            <div class="stat-label">Lines of Code</div>
            <div class="stat-value">${(summary.total_lines_of_code || 0).toLocaleString()}</div>
        </div>
        <div class="stat-card">
            <div class="stat-label">Maintainability</div>
            <div class="stat-value">${Math.round(maintainability)}<span style="font-size: 1.5rem;">/100</span></div>
        </div>
    `;
}

// Download Reports
downloadMarkdown.addEventListener('click', async () => {
    if (!currentAnalysisId) return;
    
    try {
        const apiKey = apiKeyInput.value.trim();
        const response = await fetch(`${API_BASE}/reports/markdown/${currentAnalysisId}`, {
            headers: {
                'X-API-Key': apiKey
            }
        });
        
        if (!response.ok) throw new Error('Failed to download report');
        
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `analysis_report_${currentAnalysisId}.md`;
        a.click();
        window.URL.revokeObjectURL(url);
    } catch (error) {
        showError('Failed to download Markdown report');
    }
});

downloadJSON.addEventListener('click', async () => {
    if (!currentAnalysisId) return;
    
    try {
        const apiKey = apiKeyInput.value.trim();
        const response = await fetch(`${API_BASE}/reports/json/${currentAnalysisId}`, {
            headers: {
                'X-API-Key': apiKey
            }
        });
        
        if (!response.ok) throw new Error('Failed to download report');
        
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `analysis_report_${currentAnalysisId}.json`;
        a.click();
        window.URL.revokeObjectURL(url);
    } catch (error) {
        showError('Failed to download JSON report');
    }
});

analyzeAnother.addEventListener('click', () => {
    resultsSection.style.display = 'none';
    repoUrlInput.value = '';
    repoUrlInput.focus();
    currentAnalysisId = null;
    statusBadge.textContent = 'Ready';
    statusBadge.style.background = 'rgba(16, 185, 129, 0.1)';
    statusBadge.style.color = '#10b981';
    window.scrollTo({ top: 0, behavior: 'smooth' });
});

// Utility Functions
function showError(message) {
    alert(message); // In production, use a nice toast notification
}

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

// Auto-focus on repo URL input
window.addEventListener('load', () => {
    repoUrlInput.focus();
});