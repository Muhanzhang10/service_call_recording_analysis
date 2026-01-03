// Service Call Analysis Web Application

let transcriptData = null;
let currentStage = null;

// Stage configuration
const STAGE_CONFIG = {
    'introduction': {
        name: 'Introduction',
        icon: '👋',
        color: '#3b82f6'
    },
    'problem_diagnosis': {
        name: 'Problem Diagnosis',
        icon: '🔍',
        color: '#ec4899'
    },
    'solution_explanation': {
        name: 'Solution',
        icon: '🔧',
        color: '#10b981'
    },
    'upsell_attempts': {
        name: 'Upsell',
        icon: '💼',
        color: '#f59e0b'
    },
    'maintenance_plan': {
        name: 'Maintenance Plan',
        icon: '📋',
        color: '#6366f1'
    },
    'closing': {
        name: 'Closing',
        icon: '👋',
        color: '#8b5cf6'
    }
};

// Initialize app
document.addEventListener('DOMContentLoaded', async () => {
    try {
        await loadTranscript();
        renderHeader();
        renderStageNav();
        renderTranscript();
        renderSalesInsights();
        setupEventListeners();
    } catch (error) {
        console.error('Error initializing app:', error);
        alert('Error loading transcript data. Please ensure annotated_transcript.json is available.');
    }
});

// Load transcript data
async function loadTranscript() {
    try {
        const response = await fetch('./annotated_transcript.json');
        if (!response.ok) {
            throw new Error('Failed to load transcript');
        }
        transcriptData = await response.json();
        console.log('Transcript loaded:', transcriptData);
    } catch (error) {
        console.error('Error loading transcript:', error);
        throw error;
    }
}

// Render header information
function renderHeader() {
    const overallCompliance = transcriptData.overall_compliance || {};
    const score = overallCompliance.score || 0;
    const rating = (overallCompliance.rating || 'N/A').toLowerCase();
    
    document.getElementById('overall-score').textContent = score;
    
    const ratingEl = document.getElementById('overall-rating');
    ratingEl.textContent = overallCompliance.rating || 'N/A';
    ratingEl.className = `overall-rating ${rating}`;
}

// Render stage navigation
function renderStageNav() {
    const stageNav = document.getElementById('stage-nav');
    const stageAnalyses = transcriptData.stage_analyses || {};
    const stageSummary = transcriptData.stage_summary || {};
    
    stageNav.innerHTML = '';
    
    Object.keys(STAGE_CONFIG).forEach(stageKey => {
        const config = STAGE_CONFIG[stageKey];
        const analysis = stageAnalyses[stageKey] || {};
        const summary = stageSummary[stageKey] || {};
        
        const status = analysis.status || 'absent';
        const compliance = analysis.overall_compliance || 'absent';
        
        // Determine status icon
        let statusIcon = '✗';
        if (compliance === 'COMPLIANT') statusIcon = '✓';
        else if (compliance === 'PARTIAL') statusIcon = '⚠';
        else if (status === 'absent') statusIcon = '✗';
        
        const stageItem = document.createElement('a');
        stageItem.href = `#stage-${stageKey}`;
        stageItem.className = 'stage-item';
        stageItem.dataset.stage = stageKey;
        
        stageItem.innerHTML = `
            <span class="stage-icon">${config.icon}</span>
            <span class="stage-name">${config.name}</span>
            <span class="stage-status">${statusIcon}</span>
        `;
        
        stageItem.addEventListener('click', (e) => {
            e.preventDefault();
            selectStage(stageKey);
            // Scroll to stage in transcript
            const stageElement = document.getElementById(`stage-${stageKey}`);
            if (stageElement) {
                stageElement.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        });
        
        stageNav.appendChild(stageItem);
    });
    
    // Render summary cards
    const callType = transcriptData.call_type || {};
    const salesInsights = transcriptData.sales_insights || {};
    
    document.getElementById('call-type').textContent = 
        formatCallType(callType.primary_call_type) || 'Unknown';
    
    document.getElementById('sales-rating').textContent = 
        salesInsights.overall_sales_rating || 'N/A';
    
    const overallCompliance = transcriptData.overall_compliance || {};
    document.getElementById('stages-evaluated').textContent = 
        `${overallCompliance.stages_evaluated || 0}/6`;
}

// Render transcript with annotations
function renderTranscript() {
    const transcriptEl = document.getElementById('transcript');
    const utterances = transcriptData.utterances || [];
    const speakerMap = transcriptData.speaker_identification || {};
    
    transcriptEl.innerHTML = '';
    
    let currentStage = null;
    
    utterances.forEach((utterance, index) => {
        const primaryStage = utterance.primary_stage;
        
        // Add stage divider if new stage
        if (primaryStage && primaryStage !== currentStage && STAGE_CONFIG[primaryStage]) {
            currentStage = primaryStage;
            const analysis = transcriptData.stage_analyses?.[primaryStage] || {};
            const divider = createStageDivider(primaryStage, analysis);
            transcriptEl.appendChild(divider);
        }
        
        // Create utterance element
        const utteranceEl = createUtteranceElement(utterance, speakerMap);
        transcriptEl.appendChild(utteranceEl);
    });
}

// Create stage divider
function createStageDivider(stageKey, analysis) {
    const config = STAGE_CONFIG[stageKey];
    const compliance = analysis.overall_compliance || 'absent';
    
    const divider = document.createElement('div');
    divider.className = 'stage-divider';
    divider.id = `stage-${stageKey}`;
    
    const complianceClass = compliance.toLowerCase().replace('_', '-');
    
    divider.innerHTML = `
        <h3>
            ${config.icon} ${config.name}
            <span class="stage-badge ${complianceClass}">${compliance}</span>
        </h3>
    `;
    
    return divider;
}

// Create utterance element
function createUtteranceElement(utterance, speakerMap) {
    const utteranceEl = document.createElement('div');
    utteranceEl.className = `utterance stage-${utterance.primary_stage || 'other'}`;
    
    const speaker = utterance.speaker;
    const speakerLabel = speakerMap[speaker] || speaker;
    const speakerClass = speakerLabel.toLowerCase();
    
    utteranceEl.innerHTML = `
        <div class="utterance-header">
            <span class="speaker ${speakerClass}">${speakerLabel}</span>
            <span class="timestamp">[${utterance.start.toFixed(2)}s - ${utterance.end.toFixed(2)}s]</span>
        </div>
        <div class="utterance-text">${escapeHtml(utterance.text)}</div>
    `;
    
    // Add annotations if present
    const annotations = utterance.annotations || [];
    if (annotations.length > 0) {
        const annotationsEl = document.createElement('div');
        annotationsEl.className = 'annotations';
        
        annotations.forEach(annotation => {
            const annotationEl = createAnnotationElement(annotation);
            annotationsEl.appendChild(annotationEl);
        });
        
        utteranceEl.appendChild(annotationsEl);
    }
    
    return utteranceEl;
}

// Create annotation element
function createAnnotationElement(annotation) {
    const annotationEl = document.createElement('div');
    annotationEl.className = `annotation ${annotation.type}`;
    
    annotationEl.innerHTML = `
        <span class="annotation-icon">${annotation.icon}</span>
        <div class="annotation-content">
            <div class="annotation-title">${escapeHtml(annotation.title)}</div>
            <div class="annotation-description">${escapeHtml(annotation.description)}</div>
        </div>
    `;
    
    // Add click handler to show modal
    annotationEl.addEventListener('click', () => {
        showAnnotationModal(annotation);
    });
    
    return annotationEl;
}

// Select stage and show analysis
function selectStage(stageKey) {
    currentStage = stageKey;
    
    // Update navigation
    document.querySelectorAll('.stage-item').forEach(item => {
        item.classList.remove('active');
        if (item.dataset.stage === stageKey) {
            item.classList.add('active');
        }
    });
    
    // Show analysis
    const analysis = transcriptData.stage_analyses?.[stageKey];
    if (analysis) {
        renderStageAnalysis(stageKey, analysis);
    }
}

// Render stage analysis panel
function renderStageAnalysis(stageKey, analysis) {
    const config = STAGE_CONFIG[stageKey];
    const title = document.getElementById('analysis-title');
    const content = document.getElementById('analysis-content');
    
    title.textContent = `${config.icon} ${config.name}`;
    
    if (analysis.status === 'absent') {
        content.innerHTML = `
            <div class="analysis-placeholder">
                <p>This stage was not found in the call.</p>
            </div>
        `;
        return;
    }
    
    let html = '';
    
    // Compliance score
    html += `
        <div class="compliance-score">
            <div class="score-circle">${analysis.compliance_score}/100</div>
            <div class="score-label">${analysis.quality_rating}</div>
        </div>
    `;
    
    // Questions
    html += '<div class="questions-list">';
    (analysis.questions || []).forEach(q => {
        const answerClass = q.answer.toLowerCase();
        const answerIcon = q.answer === 'YES' ? '✓' : q.answer === 'PARTIAL' ? '⚠' : '✗';
        
        html += `
            <div class="question-item ${answerClass}">
                <div class="question-header">
                    <span class="question-status">${answerIcon}</span>
                    <span class="question-text">${escapeHtml(q.question)}</span>
                </div>
                <div class="question-score">${q.score}/100</div>
            </div>
        `;
    });
    html += '</div>';
    
    // Key Strengths
    if (analysis.key_strengths && analysis.key_strengths.length > 0) {
        html += '<div class="analysis-section">';
        html += '<h3>✓ Key Strengths</h3>';
        html += '<ul>';
        analysis.key_strengths.forEach(strength => {
            html += `<li>${escapeHtml(strength)}</li>`;
        });
        html += '</ul></div>';
    }
    
    // Critical Gaps
    if (analysis.critical_gaps && analysis.critical_gaps.length > 0) {
        html += '<div class="analysis-section">';
        html += '<h3>⚠ Critical Gaps</h3>';
        html += '<ul>';
        analysis.critical_gaps.forEach(gap => {
            html += `<li>${escapeHtml(gap)}</li>`;
        });
        html += '</ul></div>';
    }
    
    // Recommendations
    if (analysis.recommendations && analysis.recommendations.length > 0) {
        html += '<div class="analysis-section">';
        html += '<h3>💡 Recommendations</h3>';
        html += '<ul>';
        analysis.recommendations.forEach(rec => {
            html += `<li>${escapeHtml(rec)}</li>`;
        });
        html += '</ul></div>';
    }
    
    content.innerHTML = html;
}

// Render sales insights
function renderSalesInsights() {
    const salesEl = document.getElementById('sales-insights');
    const sales = transcriptData.sales_insights || {};
    
    let html = '';
    
    // Opportunities Captured
    if (sales.opportunities_captured && sales.opportunities_captured.length > 0) {
        html += '<div class="sales-card">';
        html += '<h3>✓ Opportunities Captured</h3>';
        html += '<ul>';
        sales.opportunities_captured.forEach(opp => {
            html += `<li><strong>${escapeHtml(opp.opportunity || '')}</strong><br>`;
            html += `<small>${escapeHtml(opp.evidence || '')}</small></li>`;
        });
        html += '</ul></div>';
    }
    
    // Opportunities Missed
    if (sales.opportunities_missed && sales.opportunities_missed.length > 0) {
        html += '<div class="sales-card">';
        html += '<h3>⚠ Opportunities Missed</h3>';
        html += '<ul>';
        sales.opportunities_missed.forEach(opp => {
            html += `<li><strong>${escapeHtml(opp.opportunity || '')}</strong><br>`;
            html += `<small>${escapeHtml(opp.recommendation || '')}</small></li>`;
        });
        html += '</ul></div>';
    }
    
    // Customer Buying Signals
    if (sales.customer_buying_signals && sales.customer_buying_signals.length > 0) {
        html += '<div class="sales-card">';
        html += '<h3>👤 Customer Buying Signals</h3>';
        html += '<ul>';
        sales.customer_buying_signals.forEach(signal => {
            html += `<li><strong>${escapeHtml(signal.signal || '')}</strong><br>`;
            html += `<small>${escapeHtml(signal.response || '')}</small></li>`;
        });
        html += '</ul></div>';
    }
    
    // Sales Strengths
    if (sales.sales_strengths && sales.sales_strengths.length > 0) {
        html += '<div class="sales-card">';
        html += '<h3>💪 Sales Strengths</h3>';
        html += '<ul>';
        sales.sales_strengths.forEach(strength => {
            html += `<li>${escapeHtml(strength)}</li>`;
        });
        html += '</ul></div>';
    }
    
    // Areas for Improvement
    if (sales.areas_for_improvement && sales.areas_for_improvement.length > 0) {
        html += '<div class="sales-card">';
        html += '<h3>📈 Areas for Improvement</h3>';
        html += '<ul>';
        sales.areas_for_improvement.forEach(area => {
            html += `<li>${escapeHtml(area)}</li>`;
        });
        html += '</ul></div>';
    }
    
    salesEl.innerHTML = html;
}

// Show annotation detail modal
function showAnnotationModal(annotation) {
    const modal = document.getElementById('annotation-modal');
    const modalBody = document.getElementById('modal-body');
    
    let html = `
        <h3>${annotation.icon} ${escapeHtml(annotation.title)}</h3>
        <p>${escapeHtml(annotation.description)}</p>
    `;
    
    if (annotation.impact) {
        html += `<strong>Impact:</strong><p>${escapeHtml(annotation.impact)}</p>`;
    }
    
    if (annotation.recommendation) {
        html += `<strong>Recommendation:</strong><p>${escapeHtml(annotation.recommendation)}</p>`;
    }
    
    if (annotation.severity) {
        html += `<strong>Severity:</strong><p>${escapeHtml(annotation.severity)}</p>`;
    }
    
    modalBody.innerHTML = html;
    modal.classList.add('active');
}

// Setup event listeners
function setupEventListeners() {
    // Modal close
    const modal = document.getElementById('annotation-modal');
    const closeBtn = document.getElementById('modal-close');
    
    closeBtn.addEventListener('click', () => {
        modal.classList.remove('active');
    });
    
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.classList.remove('active');
        }
    });
}

// Utility functions
function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function formatCallType(type) {
    if (!type) return 'Unknown';
    return type.split('_').map(word => 
        word.charAt(0).toUpperCase() + word.slice(1)
    ).join(' ');
}

