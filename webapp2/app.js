// Service Call Analysis Web Application
// Main JavaScript file

// State
let analysisData = null;
let transcriptData = null;

// Initialize on page load
document.addEventListener('DOMContentLoaded', async () => {
    initTabs();
    await loadData();
    renderAllSections();
});

// Tab Navigation
function initTabs() {
    const tabButtons = document.querySelectorAll('.tab-button');
    
    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            const tabName = button.dataset.tab;
            switchTab(tabName);
        });
    });
}

function switchTab(tabName) {
    // Update button states
    document.querySelectorAll('.tab-button').forEach(btn => {
        btn.classList.remove('active');
    });
    document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');
    
    // Update content visibility
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });
    document.getElementById(`tab-${tabName}`).classList.add('active');
}

// Load Analysis Data
async function loadData() {
    try {
        // Load comprehensive analysis
        const analysisResponse = await fetch('../data/comprehensive_analysis.json');
        if (analysisResponse.ok) {
            analysisData = await analysisResponse.json();
        } else {
            console.error('Could not load comprehensive_analysis.json');
            showError('Analysis data not found. Please run the analysis script first.');
            return;
        }
        
        // Load transcript
        const transcriptResponse = await fetch('../data/transcription.json');
        if (transcriptResponse.ok) {
            transcriptData = await transcriptResponse.json();
        } else {
            console.error('Could not load transcription.json');
        }
        
    } catch (error) {
        console.error('Error loading data:', error);
        showError('Error loading data: ' + error.message);
    }
}

function showError(message) {
    document.querySelectorAll('.loading').forEach(el => {
        el.innerHTML = `<p style="color: #ef4444;">⚠️ ${message}</p>`;
    });
}

// Render All Sections
function renderAllSections() {
    if (!analysisData) {
        return;
    }
    
    renderOverallSummary();
    renderComplianceQuestions();
    renderSalesEvaluation();
    renderStructuredAnalysis();
    renderClientInformation();
    renderTranscript();
}

// Tab 1: Overall Summary
function renderOverallSummary() {
    const summaryEl = document.getElementById('overall-summary');
    const summary = analysisData.step1_overall_summary;
    
    if (summary) {
        // Split into paragraphs and render
        const paragraphs = summary.split('\n\n').filter(p => p.trim());
        summaryEl.innerHTML = paragraphs.map(p => `<p>${escapeHtml(p)}</p>`).join('');
    } else {
        summaryEl.innerHTML = '<p>No summary available.</p>';
    }
    
    // Render Overall Critique
    renderOverallCritique();
    
    // Render Client Insights Summary
    renderClientInsightsSummary();
    
    // Update quick stats
    if (analysisData.step2_compliance_analysis?.call_type) {
        const callTypeAnswer = analysisData.step2_compliance_analysis.call_type.answer;
        document.getElementById('quick-call-type').textContent = extractFirstSentence(callTypeAnswer);
    }
    
    if (analysisData.metadata?.total_utterances) {
        document.getElementById('quick-utterances').textContent = analysisData.metadata.total_utterances;
    }
    
    // Calculate duration from transcript
    if (transcriptData?.utterances && transcriptData.utterances.length > 0) {
        const lastUtterance = transcriptData.utterances[transcriptData.utterances.length - 1];
        const durationSeconds = Math.round(lastUtterance.end);
        const minutes = Math.floor(durationSeconds / 60);
        const seconds = durationSeconds % 60;
        document.getElementById('quick-duration').textContent = `${minutes}m ${seconds}s`;
    }
}

function renderOverallCritique() {
    const container = document.getElementById('overall-critique');
    const critique = analysisData.step6_overall_critique;
    
    if (!critique) {
        container.innerHTML = '<p>No overall critique available.</p>';
        return;
    }
    
    let html = `
        <div class="critique-header">
            ${critique.overall_grade ? `<div class="grade-badge grade-${critique.overall_grade}">${critique.overall_grade}</div>` : ''}
            <div class="critique-title">
                <h3>Overall Performance Grade</h3>
            </div>
        </div>
        
        ${critique.compliance_summary ? `
            <div class="critique-section">
                <h4>Compliance Performance${critique.compliance_grade ? ` <span class="inline-grade grade-badge grade-badge-small grade-${critique.compliance_grade}">${critique.compliance_grade}</span>` : ''}</h4>
                <p>${escapeHtml(critique.compliance_summary)}</p>
            </div>
        ` : ''}
        
        ${critique.sales_summary ? `
            <div class="critique-section">
                <h4>Sales & Product Presentation${critique.sales_grade ? ` <span class="inline-grade grade-badge grade-badge-small grade-${critique.sales_grade}">${critique.sales_grade}</span>` : ''}</h4>
                <p>${escapeHtml(critique.sales_summary)}</p>
            </div>
        ` : ''}
        
        ${critique.product_alignment_assessment ? `
            <div class="critique-section">
                <h4>Product-Client Alignment${critique.product_alignment_grade ? ` <span class="inline-grade grade-badge grade-badge-small grade-${critique.product_alignment_grade}">${critique.product_alignment_grade}</span>` : ''}</h4>
                <p>${escapeHtml(critique.product_alignment_assessment)}</p>
            </div>
        ` : ''}
        
        ${critique.strengths && critique.strengths.length > 0 ? `
            <div class="critique-section">
                <h4>✅ Strengths</h4>
                <ul class="strengths-list">
                    ${critique.strengths.map(s => `<li>${escapeHtml(s)}</li>`).join('')}
                </ul>
            </div>
        ` : ''}
        
        ${critique.areas_for_improvement && critique.areas_for_improvement.length > 0 ? `
            <div class="critique-section">
                <h4>📈 Areas for Improvement</h4>
                <ul class="improvements-list">
                    ${critique.areas_for_improvement.map(a => `<li>${escapeHtml(a)}</li>`).join('')}
                </ul>
            </div>
        ` : ''}
        
        ${critique.key_recommendations && critique.key_recommendations.length > 0 ? `
            <div class="critique-section">
                <h4>💡 Key Recommendations</h4>
                <ul class="recommendations-list">
                    ${critique.key_recommendations.map(r => `<li>${escapeHtml(r)}</li>`).join('')}
                </ul>
            </div>
        ` : ''}
        
        ${critique.overall_assessment ? `
            <div class="critique-section overall-assessment">
                <h4>Final Assessment</h4>
                <p>${escapeHtml(critique.overall_assessment)}</p>
            </div>
        ` : ''}
    `;
    
    container.innerHTML = html;
}

function renderClientInsightsSummary() {
    const container = document.getElementById('client-insights-summary');
    const clientSummary = analysisData.executive_summary?.client_insights_summary;
    
    if (!clientSummary || Object.keys(clientSummary).length === 0) {
        container.innerHTML = '<p>No client insights available. Run step 14 to generate.</p>';
        return;
    }
    
    let html = '';
    
    if (clientSummary.client_archetype) {
        html += `
            <div class="insight-section archetype-section">
                <h3>Client Archetype</h3>
                <p class="archetype-text">${escapeHtml(clientSummary.client_archetype)}</p>
            </div>
        `;
    }
    
    if (clientSummary.quick_wins && clientSummary.quick_wins.length > 0) {
        html += `
            <div class="insight-section">
                <h3>⚡ Quick Wins</h3>
                <ul class="quick-wins-list">
                    ${clientSummary.quick_wins.map(w => `<li>${escapeHtml(w)}</li>`).join('')}
                </ul>
            </div>
        `;
    }
    
    html += `
        <div class="insights-grid">
            ${clientSummary.key_pain_points && clientSummary.key_pain_points.length > 0 ? `
                <div class="insight-box">
                    <h4>😓 Key Pain Points</h4>
                    <ul>
                        ${clientSummary.key_pain_points.map(p => `<li>${escapeHtml(p)}</li>`).join('')}
                    </ul>
                </div>
            ` : ''}
            
            ${clientSummary.top_motivations && clientSummary.top_motivations.length > 0 ? `
                <div class="insight-box">
                    <h4>💪 Top Motivations</h4>
                    <ul>
                        ${clientSummary.top_motivations.map(m => `<li>${escapeHtml(m)}</li>`).join('')}
                    </ul>
                </div>
            ` : ''}
            
            ${clientSummary.budget_sensitivity ? `
                <div class="insight-box">
                    <h4>💰 Budget Sensitivity</h4>
                    <p class="sensitivity-${clientSummary.budget_sensitivity}">${escapeHtml(clientSummary.budget_sensitivity).toUpperCase()}</p>
                </div>
            ` : ''}
            
            ${clientSummary.decision_timeline ? `
                <div class="insight-box">
                    <h4>⏰ Decision Timeline</h4>
                    <p>${escapeHtml(clientSummary.decision_timeline)}</p>
                </div>
            ` : ''}
        </div>
    `;
    
    if (clientSummary.recommended_messaging && clientSummary.recommended_messaging.length > 0) {
        html += `
            <div class="insight-section advertising-section">
                <h3>📢 Recommended Messaging</h3>
                <ul class="messaging-list">
                    ${clientSummary.recommended_messaging.map(m => `<li>${escapeHtml(m)}</li>`).join('')}
                </ul>
            </div>
        `;
    }
    
    if (clientSummary.follow_up_strategy && clientSummary.follow_up_strategy.length > 0) {
        html += `
            <div class="insight-section followup-section">
                <h3>📞 Follow-Up Strategy</h3>
                <ul class="followup-list">
                    ${clientSummary.follow_up_strategy.map(f => `<li>${escapeHtml(f)}</li>`).join('')}
                </ul>
            </div>
        `;
    }
    
    container.innerHTML = html;
}

// Tab 2: Compliance Questions
function renderComplianceQuestions() {
    const container = document.getElementById('compliance-questions');
    const compliance = analysisData.step2_compliance_analysis;
    
    if (!compliance) {
        container.innerHTML = '<p>No compliance analysis available.</p>';
        return;
    }
    
    const questionOrder = [
        'introduction',
        'problem_diagnosis',
        'solution_explanation',
        'upsell_attempts',
        'maintenance_plan',
        'closing',
        'call_type',
        'sales_insights'
    ];
    
    let html = '';
    
    questionOrder.forEach(key => {
        const item = compliance[key];
        if (!item) return;
        
        const grade = item.grade || 'N/A';
        const gradeClass = `grade-${grade}`;
        
        html += `
            <div class="compliance-question">
                <div class="question-header">
                    <h3 class="question-title">${escapeHtml(item.question)}</h3>
                    ${grade !== 'N/A' ? `<div class="grade-badge ${gradeClass}">${grade}</div>` : ''}
                </div>
                ${item.grade_explanation ? `<div class="grade-explanation"><strong>Grade Explanation:</strong> ${escapeHtml(item.grade_explanation)}</div>` : ''}
                <div class="answer-text">${escapeHtml(item.answer)}</div>
                ${renderCitations(item.citations)}
            </div>
        `;
    });
    
    container.innerHTML = html;
}

// Tab 3: Sales Evaluation
function renderSalesEvaluation() {
    const salesEval = analysisData.step8_sales_evaluation;
    
    if (!salesEval) {
        document.getElementById('sales-evaluation-questions').innerHTML = '<p>No sales evaluation data available.</p>';
        return;
    }
    
    // Render Sales Questions (includes 70/30 analysis as one of the questions)
    renderSalesQuestions(salesEval);
}

function renderSalesQuestions(salesEval) {
    const container = document.getElementById('sales-evaluation-questions');
    
    const questions = [
        { key: 'building_rapport', title: '🤝 Building Rapport', icon: '🤝' },
        { key: 'handling_objections', title: '💬 Handling Objections', icon: '💬' },
        { key: 'speaking_time_analysis', title: '🗣️ 70/30 Rule Analysis', icon: '🗣️' },
        { key: 'upselling_performance', title: '📈 Upselling Performance', icon: '📈' }
    ];
    
    let html = '<div class="sales-questions-container">';
    
    questions.forEach(q => {
        const data = salesEval[q.key];
        if (!data || data.error) {
            return;
        }
        
        const grade = data.grade || 'N/A';
        const gradeClass = `grade-${grade}`;
        
        html += `
            <div class="compliance-question sales-question">
                <div class="question-header">
                    <h3 class="question-title">${q.icon} ${q.title}</h3>
                    ${grade !== 'N/A' ? `<div class="grade-badge ${gradeClass}">${grade}</div>` : ''}
                </div>
                ${data.grade_explanation ? `
                    <div class="grade-explanation">
                        <strong>Grade Explanation:</strong> ${escapeHtml(data.grade_explanation)}
                    </div>
                ` : ''}
        `;
        
        // Render specific content based on question type
        if (q.key === 'building_rapport') {
            html += renderBuildingRapportContent(data);
        } else if (q.key === 'handling_objections') {
            html += renderHandlingObjectionsContent(data);
        } else if (q.key === 'speaking_time_analysis') {
            html += renderSpeakingTimeContent(data);
        } else if (q.key === 'upselling_performance') {
            html += renderUpsellingContent(data);
        }
        
        html += `</div>`;
    });
    
    html += '</div>';
    container.innerHTML = html;
}

function renderSpeakingTimeContent(data) {
    let html = '';
    
    if (data.speaking_ratio_assessment) {
        html += `<div class="answer-text">${escapeHtml(data.speaking_ratio_assessment)}</div>`;
    }
    
    if (data.time_breakdown) {
        // Extract percentages from the time breakdown descriptions
        const breakdownData = extractTimeBreakdownPercentages(data.time_breakdown);
        
        if (breakdownData.length > 0) {
            html += `
                <div class="time-breakdown-section">
                    <h4>Time Breakdown</h4>
                    <div class="time-breakdown-with-chart">
                        ${renderTimeBreakdownPieChart(breakdownData)}
                        <div class="breakdown-grid">
            `;
            
            for (const [category, description] of Object.entries(data.time_breakdown)) {
                html += `
                    <div class="breakdown-item">
                        <strong>${category.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}:</strong>
                        <span>${escapeHtml(description)}</span>
                    </div>
                `;
            }
            
            html += `
                        </div>
                    </div>
                </div>
            `;
        }
    }
    
    if (data.recommendations && data.recommendations.length > 0) {
        html += `
            <div class="recommendations-section">
                <h4>💡 Recommendations</h4>
                <ul>
                    ${data.recommendations.map(r => `<li>${escapeHtml(r)}</li>`).join('')}
                </ul>
            </div>
        `;
    }
    
    return html;
}

function extractTimeBreakdownPercentages(timeBreakdown) {
    const categories = [];
    const colorMap = {
        'promoting_products': '#f59e0b',
        'listening_to_concerns': '#10b981',
        'technical_explanation': '#3b82f6',
        'rapport_building': '#8b5cf6'
    };
    
    for (const [category, description] of Object.entries(timeBreakdown)) {
        // Extract percentage from description (e.g., "40% - ...")
        const match = description.match(/^(\d+)%/);
        if (match) {
            const percentage = parseInt(match[1]);
            categories.push({
                name: category.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
                percentage: percentage,
                color: colorMap[category] || '#64748b'
            });
        }
    }
    
    return categories;
}

function renderTimeBreakdownPieChart(breakdownData) {
    // Calculate cumulative percentages for conic gradient
    let cumulativePercent = 0;
    const gradientStops = [];
    
    breakdownData.forEach((item, index) => {
        const startPercent = cumulativePercent;
        cumulativePercent += item.percentage;
        const endPercent = cumulativePercent;
        
        gradientStops.push(`${item.color} ${startPercent}% ${endPercent}%`);
    });
    
    const conicGradient = gradientStops.join(', ');
    
    let html = `
        <div class="time-breakdown-pie-chart-container">
            <div class="time-breakdown-pie-chart" style="background: conic-gradient(${conicGradient});">
                <div class="time-breakdown-pie-center">
                    <span class="pie-center-label">Time<br>Breakdown</span>
                </div>
            </div>
            <div class="time-breakdown-legend">
    `;
    
    breakdownData.forEach(item => {
        html += `
            <div class="time-breakdown-legend-item">
                <span class="legend-color-box" style="background-color: ${item.color};"></span>
                <span class="legend-text">${escapeHtml(item.name)}: ${item.percentage}%</span>
            </div>
        `;
    });
    
    html += `
            </div>
        </div>
    `;
    
    return html;
}

function renderBuildingRapportContent(data) {
    let html = '';
    
    if (data.detailed_assessment) {
        html += `<div class="answer-text">${escapeHtml(data.detailed_assessment)}</div>`;
    }
    
    if (data.strengths && data.strengths.length > 0) {
        html += `
            <div class="strengths-section">
                <h4>✅ Strengths</h4>
                <ul>
                    ${data.strengths.map(s => `<li>${escapeHtml(s)}</li>`).join('')}
                </ul>
            </div>
        `;
    }
    
    if (data.weaknesses && data.weaknesses.length > 0) {
        html += `
            <div class="weaknesses-section">
                <h4>⚠️ Areas for Improvement</h4>
                <ul>
                    ${data.weaknesses.map(w => `<li>${escapeHtml(w)}</li>`).join('')}
                </ul>
            </div>
        `;
    }
    
    if (data.supporting_quotes && data.supporting_quotes.length > 0) {
        html += renderSalesQuotes(data.supporting_quotes);
    }
    
    return html;
}

function renderHandlingObjectionsContent(data) {
    let html = '';
    
    if (data.overall_assessment) {
        html += `<div class="answer-text">${escapeHtml(data.overall_assessment)}</div>`;
    }
    
    if (data.objections_identified && data.objections_identified.length > 0) {
        html += `
            <div class="objections-section">
                <h4>Objections Identified & Handled</h4>
        `;
        
        data.objections_identified.forEach(obj => {
            const effectivenessClass = obj.effectiveness === 'high' ? 'effective-high' : 
                                      obj.effectiveness === 'medium' ? 'effective-medium' : 'effective-low';
            
            html += `
                <div class="objection-item">
                    <div class="objection-header">
                        <strong>Objection:</strong> ${escapeHtml(obj.objection)}
                        ${obj.effectiveness ? `<span class="effectiveness-badge ${effectivenessClass}">${obj.effectiveness} effectiveness</span>` : ''}
                    </div>
                    ${obj.how_handled ? `<p><strong>How Handled:</strong> ${escapeHtml(obj.how_handled)}</p>` : ''}
                    ${obj.quote ? `<div class="objection-quote">"${escapeHtml(obj.quote)}"</div>` : ''}
                </div>
            `;
        });
        
        html += `</div>`;
    }
    
    if (data.strengths && data.strengths.length > 0) {
        html += `
            <div class="strengths-section">
                <h4>✅ Strengths</h4>
                <ul>
                    ${data.strengths.map(s => `<li>${escapeHtml(s)}</li>`).join('')}
                </ul>
            </div>
        `;
    }
    
    if (data.areas_for_improvement && data.areas_for_improvement.length > 0) {
        html += `
            <div class="weaknesses-section">
                <h4>📈 Areas for Improvement</h4>
                <ul>
                    ${data.areas_for_improvement.map(a => `<li>${escapeHtml(a)}</li>`).join('')}
                </ul>
            </div>
        `;
    }
    
    return html;
}

function renderUpsellingContent(data) {
    let html = '';
    
    if (data.overall_assessment) {
        html += `<div class="answer-text">${escapeHtml(data.overall_assessment)}</div>`;
    }
    
    // Key metrics
    html += `
        <div class="upsell-metrics">
            <div class="metric-item">
                <span class="metric-label">Upsell Attempted:</span>
                <span class="metric-value ${data.upsell_attempted === 'yes' ? 'value-yes' : 'value-no'}">${data.upsell_attempted || 'N/A'}</span>
            </div>
            <div class="metric-item">
                <span class="metric-label">Upsell Successful:</span>
                <span class="metric-value">${data.upsell_successful || 'N/A'}</span>
            </div>
        </div>
    `;
    
    if (data.products_upsold && data.products_upsold.length > 0) {
        html += `
            <div class="products-upsold-section">
                <h4>Products Upsold</h4>
        `;
        
        data.products_upsold.forEach(product => {
            const successClass = product.success_level === 'high' ? 'success-high' : 
                               product.success_level === 'medium' ? 'success-medium' : 'success-low';
            
            html += `
                <div class="upsold-product-item">
                    <div class="product-name-badge">
                        ${escapeHtml(product.product)}
                        ${product.success_level ? `<span class="success-badge ${successClass}">${product.success_level} success</span>` : ''}
                    </div>
                    ${product.customer_response ? `<p><strong>Customer Response:</strong> ${escapeHtml(product.customer_response)}</p>` : ''}
                    ${product.quote ? `<div class="product-quote">"${escapeHtml(product.quote)}"</div>` : ''}
                </div>
            `;
        });
        
        html += `</div>`;
    }
    
    if (data.objections_faced && data.objections_faced.length > 0) {
        html += `
            <div class="objections-faced-section">
                <h4>Objections Encountered</h4>
        `;
        
        data.objections_faced.forEach(obj => {
            html += `
                <div class="objection-faced-item">
                    <p><strong>Objection:</strong> ${escapeHtml(obj.objection)}</p>
                    <p><strong>Handled Well:</strong> ${escapeHtml(obj.handled_well || 'N/A')}</p>
                    ${obj.outcome ? `<p><strong>Outcome:</strong> ${escapeHtml(obj.outcome)}</p>` : ''}
                </div>
            `;
        });
        
        html += `</div>`;
    }
    
    if (data.missed_opportunities && data.missed_opportunities.length > 0) {
        html += `
            <div class="missed-opportunities-section">
                <h4>⚠️ Missed Opportunities</h4>
                <ul>
                    ${data.missed_opportunities.map(m => `<li>${escapeHtml(m)}</li>`).join('')}
                </ul>
            </div>
        `;
    }
    
    return html;
}

function renderSalesQuotes(quotes) {
    if (!quotes || quotes.length === 0) {
        return '';
    }
    
    let html = '<div class="citations-section">';
    html += '<h4 class="citations-title">Supporting Evidence</h4>';
    
    quotes.forEach(quote => {
        html += `
            <div class="citation">
                <div class="citation-header">
                    ${quote.timestamp ? `<span class="timestamp">${escapeHtml(quote.timestamp)}</span>` : ''}
                </div>
                ${quote.quote ? `<div class="citation-quote">"${escapeHtml(quote.quote)}"</div>` : ''}
                ${quote.context ? `<div class="citation-relevance"><strong>Context:</strong> ${escapeHtml(quote.context)}</div>` : ''}
            </div>
        `;
    });
    
    html += '</div>';
    return html;
}

function renderCitations(citations) {
    if (!citations || citations.length === 0) {
        return '<p style="color: #64748b; font-style: italic;">No specific citations provided.</p>';
    }
    
    let html = '<div class="citations-section">';
    html += '<h4 class="citations-title">Supporting Evidence from Transcript</h4>';
    
    citations.forEach(citation => {
        html += `
            <div class="citation">
                <div class="citation-header">
                    ${citation.timestamp ? `<span class="timestamp">${escapeHtml(citation.timestamp)}</span>` : ''}
                    ${citation.speaker ? `<span class="speaker">${escapeHtml(citation.speaker)}</span>` : ''}
                </div>
                ${citation.quote ? `<div class="citation-quote">"${escapeHtml(citation.quote)}"</div>` : ''}
                ${citation.relevance ? `<div class="citation-relevance"><strong>Relevance:</strong> ${escapeHtml(citation.relevance)}</div>` : ''}
            </div>
        `;
    });
    
    html += '</div>';
    return html;
}

// Tab 3: Structured Analysis
function renderStructuredAnalysis() {
    const structured = analysisData.step3_structured_analysis;
    
    if (!structured) {
        document.getElementById('client-situation').innerHTML = '<p>No structured analysis available.</p>';
        return;
    }
    
    // Render Client Situation
    renderClientSituation(structured.client_situation);
    
    // Render Products and Plans (with integrated interest & research)
    renderEnhancedProducts(structured.products_and_plans);
    
    // Render Alternative Products
    renderAlternativeProducts();
    
    // Render Winner Analysis
    renderWinnerAnalysis();
    
    // Render Overall Outcome
    if (structured.overall_outcome) {
        document.getElementById('overall-outcome').innerHTML = 
            `<p>${escapeHtml(structured.overall_outcome)}</p>`;
    }
}

function renderClientSituation(situation) {
    const container = document.getElementById('client-situation');
    
    if (!situation) {
        container.innerHTML = '<p>No client situation data available.</p>';
        return;
    }
    
    let html = '<div class="situation-grid">';
    
    if (situation.problem_description) {
        html += `
            <div class="situation-item">
                <strong>Problem Description:</strong>
                ${escapeHtml(situation.problem_description)}
            </div>
        `;
    }
    
    if (situation.current_equipment) {
        html += `
            <div class="situation-item">
                <strong>Current Equipment:</strong>
                ${escapeHtml(situation.current_equipment)}
            </div>
        `;
    }
    
    if (situation.other_relevant_details) {
        html += `
            <div class="situation-item">
                <strong>Other Relevant Details:</strong>
                ${escapeHtml(situation.other_relevant_details)}
            </div>
        `;
    }
    
    html += '</div>';
    container.innerHTML = html;
}

function renderEnhancedProducts(products) {
    const container = document.getElementById('products-plans');
    
    if (!products || products.length === 0) {
        container.innerHTML = '<p>No products or plans data available.</p>';
        return;
    }
    
    // Get Perplexity research for mentioned products
    const perplexityResearch = analysisData.step5_perplexity_research?.mentioned_products_research || [];
    
    let html = '<div class="products-grid">';
    
    products.forEach((product, index) => {
        const interestClass = `interest-${product.client_interest_level || 'medium'}`;
        const interestLabel = (product.client_interest_level || 'medium').toUpperCase();
        
        // Find Perplexity research for this product
        const research = perplexityResearch.find(r => r.product_name === product.name);
        
        // Get interest analysis
        const interestAnalysis = product.interest_analysis || {};
        
        html += `
            <div class="product-card enhanced-product-card">
                <div class="product-header">
                    <h4 class="product-name">${escapeHtml(product.name || `Option ${index + 1}`)}</h4>
                    <span class="interest-badge ${interestClass}">${interestLabel} INTEREST</span>
                </div>
                
                ${product.description ? `<div class="product-description">${escapeHtml(product.description)}</div>` : ''}
                
                ${product.features && product.features.length > 0 ? `
                    <div class="product-section">
                        <strong>Key Features:</strong>
                        <ul class="features-list">
                            ${product.features.map(f => `<li>${escapeHtml(f)}</li>`).join('')}
                        </ul>
                    </div>
                ` : ''}
                
                ${product.pricing ? `
                    <div class="product-section">
                        <strong>Pricing:</strong>
                        ${escapeHtml(product.pricing)}
                    </div>
                ` : ''}
                
                ${product.special_terms && product.special_terms.length > 0 ? `
                    <div class="product-section">
                        <strong>Special Terms:</strong>
                        <ul class="special-terms-list">
                            ${product.special_terms.map(t => `<li>${escapeHtml(t)}</li>`).join('')}
                        </ul>
                    </div>
                ` : ''}
                
                ${interestAnalysis.interest_explanation ? `
                    <div class="interest-analysis-section">
                        <h5>💡 Why is the Client Interested?</h5>
                        <p>${escapeHtml(interestAnalysis.interest_explanation)}</p>
                        
                        ${interestAnalysis.supporting_quotes && interestAnalysis.supporting_quotes.length > 0 ? `
                            <div class="interest-quotes-inline">
                                <strong>Supporting Quotes:</strong>
                                ${interestAnalysis.supporting_quotes.map(quote => `
                                    <div class="interest-quote-inline">
                                        ${quote.timestamp ? `<span class="timestamp">${escapeHtml(quote.timestamp)}</span>` : ''}
                                        <span class="indicator indicator-${quote.indicates || 'interest'}">${escapeHtml(quote.indicates || 'interest')}</span>
                                        <p>"${escapeHtml(quote.quote)}"</p>
                                    </div>
                                `).join('')}
                            </div>
                        ` : ''}
                        
                        ${interestAnalysis.hypothesis ? `
                            <div class="interest-hypothesis-inline">
                                <strong>Analysis:</strong> <em>${escapeHtml(interestAnalysis.hypothesis)}</em>
                            </div>
                        ` : ''}
                    </div>
                ` : ''}
                
                ${research ? `
                    <div class="perplexity-research-section">
                        <h5>🔍 Additional Research (Perplexity)</h5>
                        <div class="research-content">
                            ${formatPerplexityContent(research.additional_info)}
                        </div>
                    </div>
                ` : ''}
                
                ${product.client_response ? `
                    <div class="client-response-section">
                        <strong>Client's Response from Call:</strong>
                        <p>${escapeHtml(product.client_response)}</p>
                    </div>
                ` : ''}
            </div>
        `;
    });
    
    html += '</div>';
    container.innerHTML = html;
}

function formatPerplexityContent(content) {
    if (!content) return '';
    
    // Clean up location issues first
    content = cleanText(content);
    
    // First check for ### headings (subsections like "### Alternative Product 1:")
    const hasSubsections = content.includes('###');
    
    // Parse numbered sections (1. Label: content, 2. Label: content, etc.)
    const sectionPattern = /(\d+)\.\s*\*?\*?([^:]+?)\*?\*?\s*:\s*([^\n]*(?:\n(?!\d+\.)[^\n]*)*)/g;
    let formatted = '';
    
    // Split by ### headings first (for things like "### Alternative Product 1:")
    const subsectionPattern = /###\s*(.+?)(?=###|$)/gs;
    const subsections = [...content.matchAll(subsectionPattern)];
    
    if (subsections.length > 0) {
        subsections.forEach(subsection => {
            const title = subsection[1].split('\n')[0].trim();
            const subsectionContent = subsection[1].substring(title.length).trim();
            
            formatted += `<h4 style="margin: 1.5rem 0 1rem 0; color: var(--primary-dark); font-size: 1.1rem;">${escapeHtmlSimple(title)}</h4>`;
            formatted += formatContentWithSections(subsectionContent);
        });
    } else {
        formatted = formatContentWithSections(content);
    }
    
    return formatted;
}

function formatContentWithSections(content) {
    if (!content) return '';
    
    let formatted = '';
    
    // Check for ALL CAPS section headers (like "CUSTOMER NEEDS/CONCERNS ADDRESSED")
    const capsHeaderPattern = /^([A-Z][A-Z\s\/]+[A-Z])$/gm;
    const sections = content.split(capsHeaderPattern);
    
    if (sections.length > 1) {
        // Has section headers
        for (let i = 0; i < sections.length; i++) {
            const part = sections[i].trim();
            if (!part) continue;
            
            // Check if this is a header (all caps)
            if (part.match(/^[A-Z][A-Z\s\/]+[A-Z]$/)) {
                formatted += `
                    <div class="subsection-header">${escapeHtmlSimple(part)}</div>
                `;
            } else {
                // This is content
                formatted += `<div class="subsection-content">${formatBulletPoints(part)}</div>`;
            }
        }
    } else {
        // Try numbered sections
        const sectionPattern = /(\d+)\.\s*\*?\*?([^:]+?)\*?\*?\s*:\s*([^\n]*(?:\n(?!\d+\.)[^\n]*)*)/g;
        const matches = [...content.matchAll(sectionPattern)];
        
        if (matches.length > 0) {
            let lastIndex = 0;
            
            matches.forEach((match) => {
                // Add any text before this match
                if (match.index > lastIndex) {
                    const beforeText = content.substring(lastIndex, match.index).trim();
                    if (beforeText) {
                        formatted += `<div style="margin-bottom: 1rem;">${formatSimpleText(beforeText)}</div>`;
                    }
                }
                
                const label = match[2].trim();
                const sectionContent = match[3].trim();
                
                formatted += `
                    <div class="product-detail-section">
                        <span class="section-label">${escapeHtmlSimple(label)}</span>
                        <div class="section-content">${formatSimpleText(sectionContent)}</div>
                    </div>
                `;
                
                lastIndex = match.index + match[0].length;
            });
            
            // Add any remaining text
            if (lastIndex < content.length) {
                const afterText = content.substring(lastIndex).trim();
                if (afterText) {
                    formatted += `<div style="margin-top: 1rem;">${formatSimpleText(afterText)}</div>`;
                }
            }
        } else {
            // No special formatting needed
            formatted = formatSimpleText(content);
        }
    }
    
    return formatted;
}

function formatBulletPoints(text) {
    if (!text) return '';
    
    // Escape HTML first
    const div = document.createElement('div');
    div.textContent = text;
    let formatted = div.innerHTML;
    
    // Split by bullet points (• or lines starting with •)
    const lines = formatted.split('\n');
    let result = '';
    let inList = false;
    
    lines.forEach(line => {
        line = line.trim();
        if (!line) return;
        
        // Check if line starts with bullet (• or -)
        if (line.match(/^[•\-]\s*/)) {
            if (!inList) {
                result += '<ul class="interest-bullet-list">';
                inList = true;
            }
            // Remove the bullet and trim
            const content = line.replace(/^[•\-]\s*/, '').trim();
            // Make text after colons or ** bold
            let formattedContent = content.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
            // Bold text after colons in bullet points
            formattedContent = formattedContent.replace(/^([^:]+:)/, '<strong>$1</strong>');
            
            result += `<li>${formattedContent}</li>`;
        } else {
            if (inList) {
                result += '</ul>';
                inList = false;
            }
            // Regular paragraph
            let formattedLine = line.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
            result += `<p style="margin: 0.5rem 0;">${formattedLine}</p>`;
        }
    });
    
    if (inList) {
        result += '</ul>';
    }
    
    return result;
}

function formatSimpleText(text) {
    if (!text) return '';
    
    // First escape HTML to prevent XSS
    const div = document.createElement('div');
    div.textContent = text;
    let formatted = div.innerHTML;
    
    // Then apply our safe formatting
    formatted = formatted.replace(/\n/g, '<br>');
    formatted = formatted.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    formatted = formatted.replace(/- /g, '• ');
    
    return formatted;
}

function renderAlternativeProducts() {
    const container = document.getElementById('alternative-products');
    const research = analysisData.step5_perplexity_research;
    
    if (!research || !research.alternative_products_info) {
        container.innerHTML = '<p>No alternative product suggestions available.</p>';
        return;
    }
    
    // Parse the alternative products info into individual products
    const products = parseAlternativeProducts(research.alternative_products_info);
    
    // Parse the interest analysis for each product
    const interestAnalyses = parseInterestAnalysis(research.alternative_interest_analysis);
    
    let html = '<div class="alternative-products-grid">';
    
    // Render each product in its own box
    products.forEach((product, index) => {
        html += `
            <div class="alternative-product-box">
                <div class="alternative-product-header">
                    <h4>${escapeHtml(product.name)}</h4>
                    <span class="alternative-badge">Alternative ${index + 1}</span>
                </div>
                <div class="alternative-product-content">
                    ${formatPerplexityContent(product.content)}
                </div>
        `;
        
        // Add interest analysis if available for this product
        if (interestAnalyses[index]) {
            html += `
                <div class="alternative-interest-section">
                    <h4>💡 Why the Client Might Be Interested</h4>
                    <div class="alternative-interest-content">
                        ${formatPerplexityContent(interestAnalyses[index])}
                    </div>
                </div>
            `;
        }
        
        html += `</div>`;
    });
    
    html += '</div>';
    
    container.innerHTML = html;
}

function parseInterestAnalysis(interestAnalysisText) {
    if (!interestAnalysisText) return [];
    
    // Split by "### Alternative Product X:" markers
    const productPattern = /### Alternative Product \d+:[^\n]*/g;
    const matches = interestAnalysisText.match(productPattern);
    
    if (!matches) return [];
    
    const analyses = [];
    
    // Split the text by these markers
    const parts = interestAnalysisText.split(/### Alternative Product \d+:[^\n]*/);
    
    // Skip the first part (text before first product)
    for (let i = 1; i < parts.length; i++) {
        analyses.push(parts[i].trim());
    }
    
    return analyses;
}

function parseAlternativeProducts(alternativeProductsInfo) {
    if (!alternativeProductsInfo) return [];
    
    // Split by "### Alternative Product" markers
    const productSections = alternativeProductsInfo.split(/### Alternative Product \d+:/);
    
    const products = [];
    
    for (let i = 1; i < productSections.length; i++) {
        const section = productSections[i].trim();
        
        // Try to extract product name from first numbered section or first line
        const firstLineMatch = section.match(/^(.+?)(?:\n|$)/);
        let name = 'Alternative Product ' + i;
        let content = section;
        
        // Check if first line contains "Product name" or is a numbered section
        if (section.match(/^1\.\s*\*?\*?[Pp]roduct name/)) {
            // Extract name from first numbered section
            const nameMatch = section.match(/1\.\s*\*?\*?[Pp]roduct name[^:]*:\s*([^\n]+)/);
            if (nameMatch) {
                name = nameMatch[1].trim();
                // Remove markdown formatting
                name = name.replace(/\*\*/g, '').replace(/\[([^\]]+)\]\([^)]+\)/g, '$1');
            }
        } else if (firstLineMatch) {
            // Use first line as name if it's not a numbered section
            const firstLine = firstLineMatch[1].trim();
            if (!firstLine.match(/^\d+\./)) {
                name = firstLine;
                content = section.substring(firstLine.length).trim();
            }
        }
        
        products.push({
            name: name,
            content: content
        });
    }
    
    return products;
}

function renderWinnerAnalysis() {
    const container = document.getElementById('winner-analysis');
    const winner = analysisData.step7_product_comparison;
    
    if (!winner || !winner.winner_product) {
        container.innerHTML = '<p>No product comparison analysis available.</p>';
        return;
    }
    
    let html = `
        <div class="winner-product-name">
            🏆 ${escapeHtml(winner.winner_product)}
        </div>
        
        <div class="winner-reasoning">
            <h4>Why This Product Wins:</h4>
            <p>${escapeHtml(winner.winner_reasoning)}</p>
        </div>
        
        ${winner.comparison_factors && winner.comparison_factors.length > 0 ? `
            <div class="comparison-factors">
                <h4>Comparison Factors:</h4>
                <ul>
                    ${winner.comparison_factors.map(factor => `
                        <li>${escapeHtml(factor)}</li>
                    `).join('')}
                </ul>
            </div>
        ` : ''}
        
        ${winner.technician_critique ? `
            <div class="technician-critique">
                <h4>Technician Performance Critique:</h4>
                
                <p><strong>Was it the right product?</strong> ${escapeHtml(winner.technician_critique.was_right_product || 'N/A')}</p>
                <p><strong>Upsell Assessment:</strong> ${escapeHtml(winner.technician_critique.upsell_assessment || 'N/A')}</p>
                <p><strong>Customer Budget Flexibility:</strong> ${escapeHtml(winner.technician_critique.customer_budget_flexibility || 'N/A')}</p>
                
                ${winner.technician_critique.critique_bullets && winner.technician_critique.critique_bullets.length > 0 ? `
                    <h5 style="margin-top: 1rem;">Key Points:</h5>
                    <ul class="critique-bullets">
                        ${winner.technician_critique.critique_bullets.map(bullet => `
                            <li>${escapeHtml(bullet)}</li>
                        `).join('')}
                    </ul>
                ` : ''}
                
                ${winner.technician_critique.overall_summary ? `
                    <div class="critique-summary">
                        <strong>Summary:</strong> ${escapeHtml(winner.technician_critique.overall_summary)}
                    </div>
                ` : ''}
            </div>
        ` : ''}
    `;
    
    container.innerHTML = html;
}

// Tab 4: Client Information
function renderClientInformation() {
    const container = document.getElementById('client-information');
    const clientInsights = analysisData.step14_client_insights;
    
    if (!clientInsights || clientInsights.error) {
        container.innerHTML = '<p>No client information available. Run step 14 (Client Insights Extraction) to generate this data.</p>';
        return;
    }
    
    let html = '';
    
    // Demographic Profile
    if (clientInsights.demographic_profile) {
        const demo = clientInsights.demographic_profile;
        html += `
            <div class="card client-info-card">
                <h3>👥 Demographic Profile</h3>
                <div class="info-grid">
                    ${demo.family_status ? `<div class="info-item"><strong>Family Status:</strong> ${escapeHtml(demo.family_status)}</div>` : ''}
                    ${demo.home_details ? `<div class="info-item"><strong>Home Details:</strong> ${escapeHtml(demo.home_details)}</div>` : ''}
                    ${demo.work_situation ? `<div class="info-item"><strong>Work Situation:</strong> ${escapeHtml(demo.work_situation)}</div>` : ''}
                    ${demo.age_indicators ? `<div class="info-item"><strong>Age Indicators:</strong> ${escapeHtml(demo.age_indicators)}</div>` : ''}
                </div>
            </div>
        `;
    }
    
    // Lifestyle & Preferences
    if (clientInsights.lifestyle_preferences) {
        const lifestyle = clientInsights.lifestyle_preferences;
        html += `
            <div class="card client-info-card">
                <h3>🏠 Lifestyle & Preferences</h3>
                <div class="info-grid">
                    ${lifestyle.comfort_needs && lifestyle.comfort_needs.length > 0 ? `
                        <div class="info-item full-width">
                            <strong>Comfort Needs:</strong>
                            <ul>${lifestyle.comfort_needs.map(n => `<li>${escapeHtml(n)}</li>`).join('')}</ul>
                        </div>
                    ` : ''}
                    <div class="info-item"><strong>Environmental Consciousness:</strong> <span class="level-badge ${lifestyle.environmental_consciousness}">${escapeHtml(lifestyle.environmental_consciousness || 'N/A').toUpperCase()}</span></div>
                    <div class="info-item"><strong>Tech Savviness:</strong> <span class="level-badge ${lifestyle.tech_savviness}">${escapeHtml(lifestyle.tech_savviness || 'N/A').toUpperCase()}</span></div>
                    <div class="info-item"><strong>Budget Sensitivity:</strong> <span class="level-badge ${lifestyle.budget_sensitivity}">${escapeHtml(lifestyle.budget_sensitivity || 'N/A').toUpperCase()}</span></div>
                </div>
            </div>
        `;
    }
    
    // Pain Points & Motivations
    html += `<div class="card client-info-card"><h3>💡 Pain Points & Motivations</h3><div class="pain-motivations-grid">`;
    
    if (clientInsights.pain_points && clientInsights.pain_points.length > 0) {
        html += `
            <div class="pain-points-section">
                <h4>😓 Pain Points</h4>
        `;
        clientInsights.pain_points.forEach(pp => {
            html += `
                <div class="pain-point-item severity-${pp.severity}">
                    <div class="pain-header">
                        <span class="pain-text">${escapeHtml(pp.pain_point)}</span>
                        <span class="severity-badge">${escapeHtml(pp.severity || 'medium')}</span>
                    </div>
                    ${pp.supporting_quote ? `<div class="pain-quote">"${escapeHtml(pp.supporting_quote)}"</div>` : ''}
                </div>
            `;
        });
        html += `</div>`;
    }
    
    if (clientInsights.motivations && clientInsights.motivations.length > 0) {
        html += `
            <div class="motivations-section">
                <h4>💪 Motivations</h4>
        `;
        clientInsights.motivations.forEach(mot => {
            html += `
                <div class="motivation-item priority-${mot.priority}">
                    <div class="motivation-header">
                        <span class="motivation-text">${escapeHtml(mot.motivation)}</span>
                        <span class="priority-badge">${escapeHtml(mot.priority || 'medium')}</span>
                    </div>
                    ${mot.supporting_quote ? `<div class="motivation-quote">"${escapeHtml(mot.supporting_quote)}"</div>` : ''}
                </div>
            `;
        });
        html += `</div>`;
    }
    
    html += `</div></div>`;
    
    // Communication & Purchase Behavior
    html += `<div class="card client-info-card"><h3>🗣️ Communication & Purchase Behavior</h3><div class="behavior-grid">`;
    
    if (clientInsights.communication_profile) {
        const comm = clientInsights.communication_profile;
        html += `
            <div class="behavior-section">
                <h4>Communication Profile</h4>
                <div class="info-grid">
                    ${comm.decision_style ? `<div class="info-item"><strong>Decision Style:</strong> ${escapeHtml(comm.decision_style)}</div>` : ''}
                    ${comm.information_preference ? `<div class="info-item"><strong>Info Preference:</strong> ${escapeHtml(comm.information_preference)}</div>` : ''}
                    ${comm.trust_level ? `<div class="info-item"><strong>Trust Level:</strong> <span class="level-badge ${comm.trust_level}">${escapeHtml(comm.trust_level).toUpperCase()}</span></div>` : ''}
                    ${comm.objection_patterns && comm.objection_patterns.length > 0 ? `
                        <div class="info-item full-width">
                            <strong>Objection Patterns:</strong>
                            <ul>${comm.objection_patterns.map(o => `<li>${escapeHtml(o)}</li>`).join('')}</ul>
                        </div>
                    ` : ''}
                </div>
            </div>
        `;
    }
    
    if (clientInsights.purchase_behavior) {
        const purchase = clientInsights.purchase_behavior;
        html += `
            <div class="behavior-section">
                <h4>Purchase Behavior</h4>
                <div class="info-grid">
                    ${purchase.budget_range ? `<div class="info-item"><strong>Budget Range:</strong> ${escapeHtml(purchase.budget_range)}</div>` : ''}
                    ${purchase.financing_interest ? `<div class="info-item"><strong>Financing Interest:</strong> ${escapeHtml(purchase.financing_interest)}</div>` : ''}
                    ${purchase.decision_timeline ? `<div class="info-item"><strong>Decision Timeline:</strong> ${escapeHtml(purchase.decision_timeline)}</div>` : ''}
                    ${purchase.key_influencers && purchase.key_influencers.length > 0 ? `
                        <div class="info-item full-width">
                            <strong>Key Influencers:</strong>
                            <ul>${purchase.key_influencers.map(i => `<li>${escapeHtml(i)}</li>`).join('')}</ul>
                        </div>
                    ` : ''}
                </div>
            </div>
        `;
    }
    
    html += `</div></div>`;
    
    // Advertising Insights
    if (clientInsights.advertising_insights) {
        const ads = clientInsights.advertising_insights;
        html += `
            <div class="card client-info-card advertising-card">
                <h3>📢 Advertising Insights</h3>
                <div class="advertising-grid">
                    ${ads.resonant_messaging && ads.resonant_messaging.length > 0 ? `
                        <div class="ad-section">
                            <h4>Resonant Messaging</h4>
                            <ul>${ads.resonant_messaging.map(m => `<li>${escapeHtml(m)}</li>`).join('')}</ul>
                        </div>
                    ` : ''}
                    ${ads.recommended_channels && ads.recommended_channels.length > 0 ? `
                        <div class="ad-section">
                            <h4>Recommended Channels</h4>
                            <ul>${ads.recommended_channels.map(c => `<li>${escapeHtml(c)}</li>`).join('')}</ul>
                        </div>
                    ` : ''}
                    ${ads.key_value_props && ads.key_value_props.length > 0 ? `
                        <div class="ad-section">
                            <h4>Key Value Props</h4>
                            <ul>${ads.key_value_props.map(v => `<li>${escapeHtml(v)}</li>`).join('')}</ul>
                        </div>
                    ` : ''}
                    ${ads.objections_to_address && ads.objections_to_address.length > 0 ? `
                        <div class="ad-section">
                            <h4>Objections to Address</h4>
                            <ul>${ads.objections_to_address.map(o => `<li>${escapeHtml(o)}</li>`).join('')}</ul>
                        </div>
                    ` : ''}
                </div>
            </div>
        `;
    }
    
    // Sales Strategy
    if (clientInsights.sales_strategy) {
        const strategy = clientInsights.sales_strategy;
        html += `
            <div class="card client-info-card sales-strategy-card">
                <h3>📞 Sales Strategy Recommendations</h3>
                ${strategy.recommended_approach ? `
                    <div class="strategy-section">
                        <h4>Recommended Approach</h4>
                        <p>${escapeHtml(strategy.recommended_approach)}</p>
                    </div>
                ` : ''}
                <div class="strategy-grid">
                    ${strategy.follow_up_emphasis && strategy.follow_up_emphasis.length > 0 ? `
                        <div class="strategy-box">
                            <h4>✅ Follow-Up Emphasis</h4>
                            <ul>${strategy.follow_up_emphasis.map(e => `<li>${escapeHtml(e)}</li>`).join('')}</ul>
                        </div>
                    ` : ''}
                    ${strategy.things_to_avoid && strategy.things_to_avoid.length > 0 ? `
                        <div class="strategy-box">
                            <h4>❌ Things to Avoid</h4>
                            <ul>${strategy.things_to_avoid.map(a => `<li>${escapeHtml(a)}</li>`).join('')}</ul>
                        </div>
                    ` : ''}
                    ${strategy.personalization_opportunities && strategy.personalization_opportunities.length > 0 ? `
                        <div class="strategy-box">
                            <h4>🎯 Personalization Opportunities</h4>
                            <ul>${strategy.personalization_opportunities.map(p => `<li>${escapeHtml(p)}</li>`).join('')}</ul>
                        </div>
                    ` : ''}
                </div>
            </div>
        `;
    }
    
    container.innerHTML = html;
}

// Tab 5: Full Transcript
function renderTranscript() {
    const container = document.getElementById('full-transcript');
    
    if (!transcriptData || !transcriptData.utterances) {
        container.innerHTML = '<p>Transcript not available.</p>';
        return;
    }
    
    const showTimestamps = document.getElementById('show-timestamps');
    
    function render() {
        const showTime = showTimestamps.checked;
        let html = '';
        
        transcriptData.utterances.forEach(utterance => {
            // Map speaker labels
            const speakerMapping = analysisData.metadata?.speaker_mapping || {};
            let displaySpeaker = utterance.speaker;
            
            // Apply mapping if available
            if (speakerMapping[utterance.speaker]) {
                displaySpeaker = speakerMapping[utterance.speaker];
            }
            
            const speakerClass = `speaker-${displaySpeaker.toLowerCase()}`;
            const timestamp = `${formatTime(utterance.start)} - ${formatTime(utterance.end)}`;
            
            html += `
                <div class="utterance ${speakerClass}">
                    <div class="utterance-header">
                        <span class="utterance-speaker">${escapeHtml(displaySpeaker)}</span>
                        ${showTime ? `<span class="utterance-timestamp">${timestamp}</span>` : ''}
                    </div>
                    <div class="utterance-text">${escapeHtml(utterance.text)}</div>
                </div>
            `;
        });
        
        container.innerHTML = html;
    }
    
    render();
    showTimestamps.addEventListener('change', render);
}

// Utility Functions
function cleanText(text) {
    if (!text) return '';
    
    // Clean up "None None" location issues
    text = text.replace(/\bNone None,?\s*/g, '');
    text = text.replace(/\s+,/g, ','); // Clean up extra spaces before commas
    text = text.replace(/,\s+,/g, ','); // Clean up double commas
    text = text.replace(/\bin None None\b/gi, 'in California'); // Specific case
    
    return text;
}

function escapeHtml(text) {
    if (!text) return '';
    text = cleanText(text); // Clean before escaping
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function escapeHtmlSimple(text) {
    // Escape HTML without cleaning text (for use in formatPerplexityContent)
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function formatTime(seconds) {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
}

function extractFirstSentence(text) {
    if (!text) return 'N/A';
    const match = text.match(/^[^.!?]+[.!?]/);
    return match ? match[0].trim() : text.slice(0, 100) + '...';
}

