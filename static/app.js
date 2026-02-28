// ===========================================================================
// HealthAI — Dynamic Multi-Step Wizard Logic
// ===========================================================================

const mainContent = document.getElementById('main-content');
const wizard = document.getElementById('wizard');
const stepContainer = document.getElementById('step-container');
const progressFill = document.getElementById('progress-fill');
const progressSteps = document.getElementById('progress-steps');
const stepIndicator = document.getElementById('step-indicator');
const btnBack = document.getElementById('btn-back');
const btnNext = document.getElementById('btn-next');
const resultsScreen = document.getElementById('results-screen');
const reportContent = document.getElementById('report-content');
const aiStatus = document.getElementById('ai-status');
const statusText = document.getElementById('status-text');
const agentBar = document.getElementById('agent-bar');

// If wizard doesn't exist (user not logged in), skip init
if (!wizard) { fetchStatus(); }

let currentStep = 0;            // 0 = complaint (Step 1), 1+ = dynamic steps
let totalSteps = 1;             // starts with just Step 1, grows after complaint
let formData = {};
let dynamicSteps = [];          // populated by /api/generate-steps
let loadingSteps = false;

// ---- Fetch system status ----
async function fetchStatus() {
    try {
        const res = await fetch('/api/status');
        const data = await res.json();
        if (data.gemini_available) {
            aiStatus.className = 'ai-status online';
            statusText.textContent = 'AI Enhanced';
        } else {
            aiStatus.className = 'ai-status offline';
            statusText.textContent = 'ML Only';
        }
    } catch (e) {
        aiStatus.className = 'ai-status offline';
        statusText.textContent = 'Offline';
    }
}

// ---- Progress ----
function initProgressDots() {
    if (!progressSteps) return;
    progressSteps.innerHTML = '';
    for (let i = 0; i < totalSteps; i++) {
        const dot = document.createElement('div');
        dot.className = 'progress-step-dot' + (i === 0 ? ' active' : '');
        dot.textContent = i + 1;
        progressSteps.appendChild(dot);
    }
}

function updateProgress() {
    const pct = ((currentStep + 1) / totalSteps) * 100;
    if (progressFill) progressFill.style.width = pct + '%';

    const dots = document.querySelectorAll('.progress-step-dot');
    dots.forEach((dot, i) => {
        dot.className = 'progress-step-dot';
        if (i < currentStep) dot.classList.add('done');
        else if (i === currentStep) dot.classList.add('active');
    });

    if (stepIndicator) stepIndicator.textContent = `Step ${currentStep + 1} of ${totalSteps}`;
    if (btnBack) btnBack.disabled = currentStep === 0;

    if (btnNext) {
        if (currentStep === totalSteps - 1) {
            btnNext.innerHTML = '🔬 Analyze <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="9 18 15 12 9 6"/></svg>';
            btnNext.classList.add('analyze-btn');
        } else {
            btnNext.innerHTML = 'Next <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="9 18 15 12 9 6"/></svg>';
            btnNext.classList.remove('analyze-btn');
        }
    }
}

// ===========================================================================
// Render Steps (generic renderer for dynamic step configs)
// ===========================================================================

function renderCurrentStep() {
    stepContainer.innerHTML = '';
    const div = document.createElement('div');
    div.className = 'step';

    if (currentStep === 0) {
        renderComplaintStep(div);
    } else {
        const stepConfig = dynamicSteps[currentStep - 1];
        renderDynamicStep(div, stepConfig);
    }

    stepContainer.appendChild(div);
    stepContainer.scrollTop = 0;
    updateProgress();
}

// Step 0: Primary Complaint (free-text — always first)
function renderComplaintStep(div) {
    div.innerHTML = `
        <div class="step-title">🩺 What's your primary health concern?</div>
        <div class="step-subtitle">Describe your main symptoms or health complaint in your own words. Our AI will generate tailored follow-up questions based on what you describe.</div>
        <textarea class="step-textarea" id="input-complaint" placeholder="e.g. I've been having a persistent cough and fever for the past 3 days, along with body aches...">${formData.complaint || ''}</textarea>
        <div class="complaint-error hidden" id="complaint-error"></div>
    `;
    // Auto-clear error on typing
    const ta = div.querySelector('#input-complaint');
    if (ta) {
        ta.addEventListener('input', () => {
            const err = document.getElementById('complaint-error');
            if (err) { err.classList.add('hidden'); err.textContent = ''; }
        });
    }
}

function showComplaintError(msg) {
    const err = document.getElementById('complaint-error');
    if (err) {
        err.textContent = msg;
        err.classList.remove('hidden');
    }
    // Also shake the textarea
    const ta = document.getElementById('input-complaint');
    if (ta) {
        ta.style.borderColor = 'var(--danger)';
        ta.style.animation = 'none';
        ta.offsetHeight;
        ta.style.animation = 'shake 0.5s';
        setTimeout(() => { ta.style.borderColor = ''; }, 2000);
    }
}

// Generic dynamic step renderer
function renderDynamicStep(div, config) {
    let html = `<div class="step-title">${config.title}</div>`;
    html += `<div class="step-subtitle">${config.subtitle}</div>`;

    switch (config.type) {
        case 'mcq_group':
            html += renderMcqGroup(config);
            break;
        case 'radio':
            html += renderRadio(config);
            break;
        case 'radio_described':
            html += renderRadioDescribed(config);
            break;
        case 'checkbox':
            html += renderCheckbox(config);
            break;
        case 'checkbox_categories':
            html += renderCheckboxCategories(config);
            break;
        case 'lifestyle':
            html += renderLifestyle(config);
            break;
    }

    div.innerHTML = html;

    // Bind interactive elements
    bindRadioCards(div);
    bindCheckboxCards(div);
    bindLifestyleChips(div);
}

// ---- MCQ Group (multiple radio groups in one step) ----
function renderMcqGroup(config) {
    let html = '';
    for (const group of config.groups) {
        const saved = formData[group.key] || '';
        html += `<div style="margin-bottom:18px">
            <div style="font-size:0.82rem;font-weight:600;color:var(--accent);margin-bottom:10px">${group.label}</div>
            <div class="options-grid grid-${group.options.length <= 4 ? '2' : '3'}">
                ${group.options.map(o => `
                    <label class="option-card radio ${saved === o ? 'selected' : ''}" data-key="${group.key}">
                        <input type="radio" name="${group.key}" value="${o}" ${saved === o ? 'checked' : ''}>
                        <span class="option-check"></span>
                        <span class="option-label">${o}</span>
                    </label>
                `).join('')}
            </div>
        </div>`;
    }
    return html;
}

// ---- Simple Radio ----
function renderRadio(config) {
    const saved = formData[config.key] || '';
    return `<div class="options-grid">
        ${config.options.map(o => `
            <label class="option-card radio ${saved === o ? 'selected' : ''}">
                <input type="radio" name="${config.key}" value="${o}" ${saved === o ? 'checked' : ''}>
                <span class="option-check"></span>
                <span class="option-label">${o}</span>
            </label>
        `).join('')}
    </div>`;
}

// ---- Radio with descriptions ----
function renderRadioDescribed(config) {
    const saved = formData[config.key] || '';
    return `<div class="options-grid">
        ${config.options.map(o => `
            <label class="option-card radio ${saved === o.value ? 'selected' : ''}">
                <input type="radio" name="${config.key}" value="${o.value}" ${saved === o.value ? 'checked' : ''}>
                <span class="option-check"></span>
                <div>
                    <div class="option-label">${o.value}</div>
                    <div style="font-size:0.72rem;color:var(--text-muted);margin-top:2px">${o.desc}</div>
                </div>
            </label>
        `).join('')}
    </div>`;
}

// ---- Checkbox (with optional suggested highlights) ----
function renderCheckbox(config) {
    const saved = formData[config.key] || [];
    const suggested = config.suggested || [];
    let html = `<div class="options-grid grid-2">
        ${config.options.map(o => {
        const isSuggested = suggested.includes(o);
        const isSelected = saved.includes(o);
        return `<label class="option-card ${isSelected ? 'selected' : ''}" ${isSuggested ? 'style="border-color:var(--border-glow)"' : ''}>
                <input type="checkbox" name="${config.key}" value="${o}" ${isSelected ? 'checked' : ''}>
                <span class="option-check"></span>
                <span class="option-label">${o}${isSuggested ? ' <span style="font-size:0.65rem;color:var(--accent)">★ relevant</span>' : ''}</span>
            </label>`;
    }).join('')}
    </div>`;
    if (config.has_other) {
        html += `<div class="other-input-wrap" style="margin-top:14px">
            <div style="font-size:0.82rem;font-weight:600;color:var(--accent);margin-bottom:8px">Others — please specify</div>
            <input class="other-input" id="input-${config.other_key}" placeholder="Any others not listed above..." value="${formData[config.other_key] || ''}">
        </div>`;
    }
    return html;
}

// ---- Checkbox with Categories ----
function renderCheckboxCategories(config) {
    const saved = formData.selected_symptoms || [];
    const autoSelected = config.auto_selected || [];
    let html = '';

    for (const [cat, symptoms] of Object.entries(config.categories)) {
        html += `<div class="category-group">
            <div class="category-title">${cat}</div>
            <div class="category-options">
                ${symptoms.map(s => {
            const isAuto = autoSelected.includes(s);
            const isSelected = saved.includes(s) || isAuto;
            return `<label class="option-card ${isSelected ? 'selected' : ''}">
                        <input type="checkbox" name="symptom" value="${s}" ${isSelected ? 'checked' : ''}>
                        <span class="option-check"></span>
                        <span class="option-label">${s.replace(/_/g, ' ')}${isAuto ? ' <span style="font-size:0.6rem;color:var(--success)">✓ detected</span>' : ''}</span>
                    </label>`;
        }).join('')}
            </div>
        </div>`;
    }

    if (config.has_other) {
        html += `<div class="other-input-wrap" style="margin-top:14px">
            <div style="font-size:0.82rem;font-weight:600;color:var(--accent);margin-bottom:8px">Others — please specify</div>
            <input class="other-input" id="input-${config.other_key}" placeholder="Any symptoms not listed above..." value="${formData[config.other_key] || ''}">
        </div>`;
    }
    return html;
}

// ---- Lifestyle ----
function renderLifestyle(config) {
    const saved = formData.lifestyle || {};
    let html = '<div class="lifestyle-grid">';
    for (const [key, opt] of Object.entries(config.options)) {
        html += `<div class="lifestyle-item">
            <div class="lifestyle-label">${opt.label}</div>
            <div class="lifestyle-options" data-key="${key}">
                ${opt.options.map(o => `
                    <button class="lifestyle-chip ${saved[key] === o ? 'selected' : ''}" data-value="${o}" type="button">${o}</button>
                `).join('')}
            </div>
        </div>`;
    }
    html += '</div>';
    return html;
}

// ===========================================================================
// Binding Helpers
// ===========================================================================

function bindRadioCards(container) {
    container.querySelectorAll('.option-card.radio').forEach(card => {
        card.addEventListener('click', () => {
            const inp = card.querySelector('input');
            const name = inp.name;
            container.querySelectorAll(`input[name="${name}"]`).forEach(i => {
                i.closest('.option-card').classList.remove('selected');
            });
            card.classList.add('selected');
            inp.checked = true;
        });
    });
}

function bindCheckboxCards(container) {
    container.querySelectorAll('.option-card:not(.radio)').forEach(card => {
        card.addEventListener('click', (e) => {
            if (e.target.classList.contains('other-input')) return;
            const inp = card.querySelector('input[type="checkbox"]');
            if (!inp) return;
            inp.checked = !inp.checked;
            card.classList.toggle('selected', inp.checked);

            // "None" logic
            if (inp.value === 'None' && inp.checked) {
                container.querySelectorAll('input[type="checkbox"]').forEach(other => {
                    if (other !== inp) {
                        other.checked = false;
                        other.closest('.option-card').classList.remove('selected');
                    }
                });
            } else if (inp.value !== 'None' && inp.checked) {
                const noneInp = container.querySelector('input[value="None"]');
                if (noneInp) {
                    noneInp.checked = false;
                    noneInp.closest('.option-card').classList.remove('selected');
                }
            }
        });
    });
}

function bindLifestyleChips(container) {
    container.querySelectorAll('.lifestyle-options').forEach(group => {
        const key = group.dataset.key;
        group.querySelectorAll('.lifestyle-chip').forEach(chip => {
            chip.addEventListener('click', () => {
                group.querySelectorAll('.lifestyle-chip').forEach(c => c.classList.remove('selected'));
                chip.classList.add('selected');
                if (!formData.lifestyle) formData.lifestyle = {};
                formData.lifestyle[key] = chip.dataset.value;
            });
        });
    });
}

// ===========================================================================
// Save / Collect Step Data
// ===========================================================================

function saveCurrentStep() {
    if (currentStep === 0) {
        const ta = document.getElementById('input-complaint');
        if (ta) formData.complaint = ta.value.trim();
        return;
    }

    const config = dynamicSteps[currentStep - 1];
    if (!config) return;

    switch (config.type) {
        case 'mcq_group':
            for (const group of config.groups) {
                const radio = document.querySelector(`input[name="${group.key}"]:checked`);
                if (radio) formData[group.key] = radio.value;
            }
            break;
        case 'radio':
        case 'radio_described':
            const radio = document.querySelector(`input[name="${config.key}"]:checked`);
            if (radio) formData[config.key] = radio.value;
            break;
        case 'checkbox':
            formData[config.key] = Array.from(
                document.querySelectorAll(`input[name="${config.key}"]:checked`)
            ).map(i => i.value);
            if (config.has_other) {
                const otherInput = document.getElementById(`input-${config.other_key}`);
                if (otherInput) formData[config.other_key] = otherInput.value.trim();
            }
            break;
        case 'checkbox_categories':
            formData.selected_symptoms = Array.from(
                document.querySelectorAll('input[name="symptom"]:checked')
            ).map(i => i.value);
            if (config.has_other) {
                const otherInput = document.getElementById(`input-${config.other_key}`);
                if (otherInput) formData[config.other_key] = otherInput.value.trim();
            }
            break;
        case 'lifestyle':
            // Already saved via click handlers
            break;
    }
}

function validateCurrentStep() {
    if (currentStep === 0) {
        return !!(formData.complaint && formData.complaint.length >= 5);
    }
    const config = dynamicSteps[currentStep - 1];
    if (!config) return true;

    switch (config.type) {
        case 'mcq_group':
            return config.groups.every(g => !!formData[g.key]);
        case 'radio':
        case 'radio_described':
            return !!formData[config.key];
        default:
            return true; // checkboxes are optional
    }
}

// ===========================================================================
// Navigation
// ===========================================================================

async function goNext() {
    saveCurrentStep();

    if (!validateCurrentStep()) {
        btnNext.style.animation = 'none';
        btnNext.offsetHeight;
        btnNext.style.animation = 'shake 0.5s';
        return;
    }

    // After Step 0 (complaint), fetch dynamic follow-up steps
    if (currentStep === 0 && formData.complaint && dynamicSteps.length === 0) {
        loadingSteps = true;
        btnNext.disabled = true;
        btnNext.innerHTML = '<div class="analyzing-spinner" style="width:16px;height:16px;border-width:2px;margin:0"></div> Generating questions...';

        try {
            const res = await fetch('/api/generate-steps', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ complaint: formData.complaint }),
            });
            const data = await res.json();

            // Check if complaint was validated as health-related
            if (!data.valid) {
                loadingSteps = false;
                btnNext.disabled = false;
                btnNext.innerHTML = 'Next <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="9 18 15 12 9 6"/></svg>';
                showComplaintError(data.error || 'Please enter a valid health concern.');
                return;
            }

            dynamicSteps = data.steps || [];
            totalSteps = 1 + dynamicSteps.length;
            initProgressDots();
        } catch (e) {
            console.error('Failed to generate steps:', e);
        }

        loadingSteps = false;
        btnNext.disabled = false;
    }

    if (currentStep < totalSteps - 1) {
        currentStep++;
        renderCurrentStep();
    } else {
        runAnalysis();
    }
}

function goBack() {
    saveCurrentStep();
    if (currentStep > 0) {
        currentStep--;
        renderCurrentStep();
    }
}

// ===========================================================================
// Run Analysis
// ===========================================================================

async function runAnalysis() {
    wizard.style.display = 'none';

    const analyzingHTML = `
        <div class="analyzing-screen" id="analyzing-screen">
            <div class="analyzing-spinner"></div>
            <div class="analyzing-title">Analyzing Your Health Data</div>
            <div class="analyzing-subtitle">Our multi-agent AI system is processing your information...</div>
            <div class="analyzing-steps">
                <div class="analyzing-step active" id="astep-1"><span class="analyzing-step-icon">🩺</span> Extracting symptoms from your data...</div>
                <div class="analyzing-step" id="astep-2"><span class="analyzing-step-icon">🧠</span> Running ML disease prediction model...</div>
                <div class="analyzing-step" id="astep-3"><span class="analyzing-step-icon">🔬</span> AI-enhanced diagnosis analysis...</div>
                <div class="analyzing-step" id="astep-4"><span class="analyzing-step-icon">💊</span> Generating treatment recommendations...</div>
                <div class="analyzing-step" id="astep-5"><span class="analyzing-step-icon">📋</span> Compiling your health report...</div>
            </div>
        </div>
    `;
    mainContent.insertAdjacentHTML('beforeend', analyzingHTML);

    setAgentState('intake', 'done');

    const animateStep = async (stepId, agentName, delay) => {
        await new Promise(r => setTimeout(r, delay));
        const el = document.getElementById(stepId);
        if (el) { el.classList.add('active'); }
        if (agentName) setAgentState(agentName, 'active');
        if (el) {
            const prev = el.previousElementSibling;
            if (prev) { prev.classList.remove('active'); prev.classList.add('done'); }
        }
    };

    const analysisPromise = fetch('/api/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData),
    }).then(r => r.json());

    await animateStep('astep-2', 'diagnosis', 800);
    await animateStep('astep-3', null, 800);
    await animateStep('astep-4', 'recommendation', 800);
    await animateStep('astep-5', 'summary', 800);

    try {
        const result = await analysisPromise;

        document.querySelectorAll('.analyzing-step').forEach(s => {
            s.classList.remove('active'); s.classList.add('done');
        });
        setAgentState('diagnosis', 'done');
        setAgentState('recommendation', 'done');
        setAgentState('summary', 'done');

        await new Promise(r => setTimeout(r, 500));
        document.getElementById('analyzing-screen').remove();
        showResults(result);
    } catch (e) {
        document.getElementById('analyzing-screen').remove();
        wizard.style.display = 'flex';
        alert('An error occurred during analysis. Please try again.');
    }
}

function showResults(result) {
    resultsScreen.classList.remove('hidden');
    reportContent.innerHTML = parseMarkdown(result.report || 'No report generated.');
}

// ===========================================================================
// Agent Bar
// ===========================================================================

function setAgentState(name, state) {
    if (!agentBar) return;
    agentBar.querySelectorAll('.agent-chip').forEach(chip => {
        if (chip.dataset.agent === name) {
            chip.className = `agent-chip ${state}`;
        }
    });
}

// ===========================================================================
// Markdown Parser
// ===========================================================================

function parseMarkdown(text) {
    let html = text
        .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
        .replace(/^#### (.+)$/gm, '<h4>$1</h4>')
        .replace(/^### (.+)$/gm, '<h3>$1</h3>')
        .replace(/^## (.+)$/gm, '<h2>$1</h2>')
        .replace(/^---$/gm, '<hr>')
        .replace(/\*\*\*(.+?)\*\*\*/g, '<strong><em>$1</em></strong>')
        .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.+?)\*/g, '<em>$1</em>')
        .replace(/^&gt; (.+)$/gm, '<blockquote>$1</blockquote>')
        .replace(/^[\-\*] (.+)$/gm, '<li>$1</li>')
        .replace(/^\d+\. (.+)$/gm, '<li>$1</li>')
        .replace(/^\|(.+)\|$/gm, (match, content) => {
            const cells = content.split('|').map(c => c.trim());
            if (cells.every(c => /^[\-:]+$/.test(c))) return '';
            return '<tr>' + cells.map(c => `<td>${c}</td>`).join('') + '</tr>';
        });
    html = html.replace(/((?:<li>.*<\/li>\n?)+)/g, '<ul>$1</ul>');
    html = html.replace(/((?:<tr>.*<\/tr>\n?)+)/g, '<table>$1</table>');
    html = html.replace(/<table>\s*<tr>(.*?)<\/tr>/, (m, row) =>
        '<table><tr>' + row.replace(/<td>/g, '<th>').replace(/<\/td>/g, '</th>') + '</tr>');
    html = html.replace(/\n/g, '<br>');
    html = html.replace(/<br>\s*(<h[234]|<ul|<\/ul|<table|<\/table|<hr|<blockquote)/g, '$1');
    html = html.replace(/(<\/h[234]>|<\/ul>|<\/table>|<\/blockquote>)\s*<br>/g, '$1');
    return html;
}

// ===========================================================================
// Download & New Checkup
// ===========================================================================

const downloadBtn = document.getElementById('download-btn');
const newCheckupBtn = document.getElementById('new-checkup-btn');

if (downloadBtn) {
    downloadBtn.addEventListener('click', () => {
        window.location.href = '/api/download-report';
    });
}

if (newCheckupBtn) {
    newCheckupBtn.addEventListener('click', () => {
        window.location.reload();
    });
}

// ===========================================================================
// Event Listeners
// ===========================================================================

if (btnNext) btnNext.addEventListener('click', goNext);
if (btnBack) btnBack.addEventListener('click', goBack);

document.addEventListener('keydown', (e) => {
    if (!wizard || wizard.style.display === 'none') return;
    if (e.key === 'Enter' && e.target.tagName !== 'TEXTAREA') {
        e.preventDefault();
        goNext();
    }
});

// Shake animation
const shakeStyle = document.createElement('style');
shakeStyle.textContent = '@keyframes shake{0%,100%{transform:translateX(0)}25%{transform:translateX(-5px)}75%{transform:translateX(5px)}}';
document.head.appendChild(shakeStyle);

// ===========================================================================
// Init
// ===========================================================================

async function init() {
    fetchStatus();
    if (wizard) {
        initProgressDots();
        renderCurrentStep();
    }
}

init();
