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
    renderStructuredAnalysis();
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
                <h4>Compliance Performance</h4>
                <p>${escapeHtml(critique.compliance_summary)}</p>
            </div>
        ` : ''}
        
        ${critique.sales_summary ? `
            <div class="critique-section">
                <h4>Sales & Product Presentation</h4>
                <p>${escapeHtml(critique.sales_summary)}</p>
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

// Tab 4: Full Transcript
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

