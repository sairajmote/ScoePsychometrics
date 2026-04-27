/**
 * feedback.js
 * Controls the one-question-at-a-time survey flow for /feedback.
 * Handles: navigation, progress tracking, validation, submission,
 * and fetching + displaying the live Overall Accuracy Score.
 */

// ─── State ───────────────────────────────────────────────────────────────────
const TOTAL_QUESTIONS = 15;
let currentStep = 0;          // 0 = intro card, 1-15 = question cards
let answers = {};              // { fieldName: numericValue }

// ─── DOM references ──────────────────────────────────────────────────────────
const cards       = () => document.querySelectorAll('.fb-card');
const progressBar = () => document.getElementById('fb-progress-bar');
const progressLbl = () => document.getElementById('fb-progress-label');

// ─── Init ────────────────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
    // Show intro card
    showCard('fb-intro');
    updateProgress(0);

    // Wire up radio buttons for immediate visual feedback
    document.querySelectorAll('input[type="radio"]').forEach(radio => {
        radio.addEventListener('change', e => {
            const field = e.target.name;
            answers[field] = parseInt(e.target.value, 10);
            // Animate the selected option
            highlightSelected(field, e.target.value);
        });
    });

    // Character counter for Q15 textarea
    const tx = document.getElementById('q15_open_text');
    if (tx) {
        tx.addEventListener('input', () => {
            document.getElementById('char-count').textContent = tx.value.length;
        });
    }

    // ── Keyboard Support ──
    window.addEventListener('keydown', e => {
        // Only trigger if a survey question is active and not the text question
        if (currentStep < 1 || currentStep >= TOTAL_QUESTIONS) return;
        
        let num = parseInt(e.key, 10);
        if (e.key === '0') num = 10; // 0 maps to 10 for Likert-10

        if (!isNaN(num) && num >= 1 && num <= 10) {
            const card = getActiveQuestionCard();
            if (!card) return;

            const field = card.dataset.field;
            const radio = document.querySelector(`input[name="${field}"][value="${num}"]`);
            
            if (radio) {
                radio.checked = true;
                answers[field] = num;
                highlightSelected(field, String(num));
                
                // Advance to next question with a small delay for visual feedback
                setTimeout(() => nextQ(), 200);
            }
        }
    });
});

// ─── Navigation ──────────────────────────────────────────────────────────────

/** Called by "Begin Survey" on the intro card. */
function startSurvey() {
    currentStep = 1;
    showCardByStep(currentStep);
    updateProgress(currentStep);
}

/** Move to next question. Validates required fields (Q1-Q14). */
function nextQ() {
    const card = getActiveQuestionCard();
    if (!card) return;

    const field = card.dataset.field;
    const type  = card.dataset.type;

    // Text questions (Q15) are optional — just proceed
    if (type !== 'text') {
        const val = getRadioValue(field);
        if (val === null) {
            showToast('Please select an answer before continuing.');
            return;
        }
        answers[field] = val;
    } else {
        // Capture textarea value
        const tx = document.getElementById('q15_open_text');
        if (tx) answers['q15_open_text'] = tx.value.trim() || null;
    }

    currentStep++;
    showCardByStep(currentStep);
    updateProgress(currentStep);
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

/** Move to previous question. */
function prevQ() {
    if (currentStep <= 1) {
        currentStep = 0;
        showCard('fb-intro');
        updateProgress(0);
    } else {
        currentStep--;
        showCardByStep(currentStep);
        updateProgress(currentStep);
    }
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// ─── Card Display ─────────────────────────────────────────────────────────────

/** Show a card by its element id. */
function showCard(id) {
    cards().forEach(c => c.classList.remove('active'));
    const target = document.getElementById(id);
    if (target) target.classList.add('active');
}

/** Show the card whose data-q matches step. */
function showCardByStep(step) {
    cards().forEach(c => c.classList.remove('active'));
    const target = document.querySelector(`.fb-card[data-q="${step}"]`);
    if (target) {
        target.classList.add('active');
        // Restore previously selected option if user navigated back
        restoreSelection(target);
    }
}

// ─── Progress Bar ─────────────────────────────────────────────────────────────

function updateProgress(step) {
    const pct = step === 0 ? 0 : Math.round((step / TOTAL_QUESTIONS) * 100);
    progressBar().style.width = pct + '%';
    progressLbl().textContent = step === 0
        ? 'Ready to begin'
        : `Question ${step} of ${TOTAL_QUESTIONS}`;
}

// ─── Helpers ──────────────────────────────────────────────────────────────────

/** Get the currently visible question card. */
function getActiveQuestionCard() {
    return document.querySelector('.fb-card.active[data-q]') || null;
}

/** Read a radio group value, returns int or null. */
function getRadioValue(name) {
    const sel = document.querySelector(`input[name="${name}"]:checked`);
    return sel ? parseInt(sel.value, 10) : null;
}

/** Highlight the selected Likert option spans. */
function highlightSelected(field, value) {
    document.querySelectorAll(`input[name="${field}"]`).forEach(radio => {
        const span = radio.nextElementSibling;
        if (!span) return;
        span.classList.toggle('selected', radio.value === value);
    });
}

/** Restore radio selections when navigating back. */
function restoreSelection(card) {
    const field = card.dataset.field;
    if (!field || !(field in answers)) return;
    const val = String(answers[field]);
    const radio = document.querySelector(`input[name="${field}"][value="${val}"]`);
    if (radio) {
        radio.checked = true;
        highlightSelected(field, val);
    }
    // Restore textarea
    if (field === 'q15_open_text') {
        const tx = document.getElementById('q15_open_text');
        if (tx && answers['q15_open_text']) {
            tx.value = answers['q15_open_text'];
            document.getElementById('char-count').textContent = tx.value.length;
        }
    }
}

// ─── Submission ───────────────────────────────────────────────────────────────

/**
 * Build the payload from collected answers, POST to /api/feedback,
 * then navigate to the thank-you card and show the live OAS.
 */
async function submitFeedback() {
    // Capture Q15 textarea one final time
    const tx = document.getElementById('q15_open_text');
    if (tx) answers['q15_open_text'] = tx.value.trim() || null;

    // Disable button to prevent double-submission
    const btn = document.getElementById('btn-submit');
    if (btn) { btn.disabled = true; btn.textContent = 'Submitting…'; }

    // Pull optional linking fields from URL params (set by report page if passed)
    const params = new URLSearchParams(window.location.search);
    const payload = {
        user_id:   params.get('user_id')   ? parseInt(params.get('user_id'), 10)  : null,
        report_id: params.get('report_id') ? params.get('report_id') : null,
        ...answers
    };

    try {
        const res = await fetch('/api/feedback', {
            method:  'POST',
            headers: { 'Content-Type': 'application/json' },
            body:    JSON.stringify(payload)
        });

        if (!res.ok) {
            const err = await res.json().catch(() => ({}));
            throw new Error(err.detail || `Server error ${res.status}`);
        }

        // Navigate to thank-you card
        progressBar().style.width = '100%';
        progressLbl().textContent = 'Survey complete!';
        showCard('fb-thankyou');
        window.scrollTo({ top: 0, behavior: 'smooth' });

        // Fetch live Overall Accuracy Score
        fetchAndShowOAS();

    } catch (err) {
        if (btn) { btn.disabled = false; btn.textContent = 'Submit Feedback ✓'; }
        showToast('Submission failed: ' + err.message);
    }
}

/** Fetch /api/feedback/stats and show OAS in the thank-you card. */
async function fetchAndShowOAS() {
    try {
        const res  = await fetch('/api/feedback/stats');
        if (!res.ok) return;
        const data = await res.json();
        const box  = document.getElementById('fb-oas-box');
        const val  = document.getElementById('fb-oas-value');
        if (box && val) {
            val.textContent = data.overall_accuracy_score.toFixed(1) + '%';
            box.style.display = 'block';
        }
    } catch (_) {
        // Silently fail — OAS box just stays hidden
    }
}

// ─── Toast ────────────────────────────────────────────────────────────────────

let toastTimer = null;

function showToast(msg) {
    let toast = document.getElementById('fb-toast');
    if (!toast) {
        toast = document.createElement('div');
        toast.id = 'fb-toast';
        toast.className = 'fb-toast';
        document.body.appendChild(toast);
    }
    toast.textContent = msg;
    toast.classList.add('show');
    if (toastTimer) clearTimeout(toastTimer);
    toastTimer = setTimeout(() => toast.classList.remove('show'), 3500);
}
