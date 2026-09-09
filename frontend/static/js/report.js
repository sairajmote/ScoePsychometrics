async function loadReport() {
    const urlParams = new URLSearchParams(window.location.search);
    const reportId = urlParams.get('report_id') || urlParams.get('id');

    // Grab temperament result if passed from the exam submission
    window._temperamentType = urlParams.get('temperament') || '';
    window._temperamentDesc = urlParams.get('temperament_desc') || '';

    if (!reportId) {
        const res = await fetch('/static/data/sample_report_data.json');
        const data = await res.json();
        renderReport(data);
        return;
    }

    try {
        const res = await fetch(`/api/report/${reportId}`);
        if (!res.ok) throw new Error("Report not found");
        const data = await res.json();
        renderReport(data);
    } catch (err) {
        document.getElementById('report-root').innerHTML = `
            <div style="text-align:center;padding:4rem;">
                <h2 style="color:#e74c3c;">Report Not Found</h2>
                <a href="/">Return to Home</a>
            </div>
        `;
    }
}

function formatDuration(seconds) {
    const m = Math.floor(seconds / 60);
    const s = seconds % 60;
    return `${m}m ${s}s`;
}

window.switchTab = function (tabId, event) {
    const btn = event.currentTarget;
    const container = document.querySelector('.results-container');
    const target = document.getElementById(tabId);

    if (!target || !container) return;

    // 1. Calculate transformation origin from the clicked button
    const btnRect = btn.getBoundingClientRect();
    const containerRect = container.getBoundingClientRect();

    const originX = (btnRect.left + btnRect.width / 2) - containerRect.left;
    const originY = (btnRect.top + btnRect.height / 2) - containerRect.top;

    container.style.setProperty('--origin-x', `${originX}px`);
    container.style.setProperty('--origin-y', `${originY}px`);

    // 2. Manage Active States
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');

    document.querySelectorAll('.tab-content').forEach(c => {
        c.classList.remove('active');
        c.style.display = 'none';
    });

    target.style.display = 'block';
    // Force reflow for animation
    void target.offsetWidth;
    target.classList.add('active');

    // 3. Scroll container into view center so the "pop" is visible
    setTimeout(() => {
        container.scrollIntoView({
            behavior: 'smooth',
            block: 'start'
        });
    }, 10);

    // 4. Re-trigger bar animations and charts
    setTimeout(() => {
        document.querySelectorAll('.b5-bar-fill').forEach(bar => {
            const target = bar.getAttribute('data-width');
            if (target) bar.style.width = target + '%';
        });
        document.querySelectorAll('.mi-bar-fill').forEach(bar => {
            const target = bar.getAttribute('data-mi-width');
            if (target) bar.style.width = target + '%';
        });

        if (target.id === 'tab-enneagram' && window.initEnneagramChart) {
            window.initEnneagramChart();
        }
    }, 100);
};

function renderReport(D) {
    const root = document.getElementById('report-root');
    const meta = D.meta;
    const sub = D.subtests;
    const insights = D.composite_insights;

    let html = '';
    let tabsHtml = '';

    // ── COVER ──
    html += `
        <div class="report-cover" id="sec-overview">
            <div class="cover-badge">Psychometric Assessment Report</div>
            <h1 class="cover-title">HI, ${meta.candidate.name.toUpperCase()}</h1>
            
            ${insights.ai_overview ? `
            <div class="ai-summary-box">
                <div class="overview-label" style="font-size:1rem;font-weight:950;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:1rem;color:#000;">Overview</div>
                <div class="ai-summary-text">${insights.ai_overview}</div>
            </div>` : ''}

            <div class="cover-meta">
                <div class="cover-meta-item">
                    <span class="cover-meta-label">Report ID</span>
                    <span class="cover-meta-value">${meta.report_id}</span>
                </div>
                <div class="cover-meta-item">
                    <span class="cover-meta-label">Generated</span>
                    <span class="cover-meta-value">${new Date(meta.generated_at).toLocaleDateString('en-IN', { year: 'numeric', month: 'long', day: 'numeric' })}</span>
                </div>
                <div class="cover-meta-item">
                    <span class="cover-meta-label">Education</span>
                    <span class="cover-meta-value">${meta.candidate.education || 'Not Specified'}</span>
                </div>
            </div>
        </div>`;

    html += `
        <div class="report-tabs">
            ${sub.mbti ? `<button class="tab-btn" onclick="switchTab('tab-mbti', event)">IDENTITY (MBTI)</button>` : ''}
            ${sub.temperament ? `<button class="tab-btn" onclick="switchTab('tab-temperament', event)">CORE TEMPERAMENT</button>` : ''}
            ${sub.big5 ? `<button class="tab-btn" onclick="switchTab('tab-big5', event)">TRAITS (BIG 5)</button>` : ''}
            ${sub.multiple_intelligence ? `<button class="tab-btn" onclick="switchTab('tab-mi', event)">INTELLIGENCE (MI)</button>` : ''}
            ${sub.enneagram ? `<button class="tab-btn" onclick="switchTab('tab-enneagram', event)">MOTIVATIONS (ENNEA)</button>` : ''}
            ${sub.brain_dominance ? `<button class="tab-btn" onclick="switchTab('tab-brain', event)">BRAIN DOMINANCE</button>` : ''}
        </div>
        
        <div class="results-container">`;

    // ── MBTI SECTION ──
    if (sub.mbti) {
        const mbti = sub.mbti;
        const dichRows = Object.values(mbti.dichotomies).map(d => `
            <div class="dichotomy-row">
                <div class="dich-label">${d.dimension_a.label} (${d.dimension_a.code})</div>
                <div class="dich-bar-wrap">
                    <div class="dich-bar-a" style="width:${d.dimension_a.score}%">${Math.round(d.dimension_a.score)}%</div>
                    <div class="dich-bar-b" style="width:${d.dimension_b.score}%">${Math.round(d.dimension_b.score)}%</div>
                </div>
                <div class="dich-label-right">${d.dimension_b.label} (${d.dimension_b.code})</div>
            </div>
        `).join('');

        html += `
        <div id="tab-mbti" class="tab-content">
            <div class="section-block">
                <div class="section-heading">
                    <span class="section-num">01</span>
                    <h2>${mbti.label}</h2>
                </div>
                <div class="section-desc">${mbti.description}</div>
                <div class="section-body">
                    <div class="mbti-type-display">
                        <div class="mbti-type-code">${mbti.result_type}</div>
                        <div class="mbti-type-name">${mbti.type_label}</div>
                    </div>
                    ${dichRows}
                    <div class="interp-box">
                        <strong>Interpretation</strong>
                        ${mbti.interpretation}
                    </div>
                </div>
            </div>
        </div>`;
    }

    // ── TEMPERAMENT SECTION ──
    if (sub.temperament) {
        const temp = sub.temperament;

        // Basic lookup for the short tagline inside the box
        const BASIC_LOOKUP = {
            "Sanguine": "Outgoing, enthusiastic, and sociable.",
            "Choleric": "Ambitious, assertive, and goal-oriented.",
            "Melancholic": "Thoughtful, introspective, and detail-oriented.",
            "Phlegmatic": "Calm, easygoing, and diplomatic."
        };

        // Detailed lookup for the thorough analysis below the box
        const DETAILED_LOOKUP = {
            "Sanguine": "Sanguine individuals are lively, outgoing, and full of energy. They enjoy social interactions, easily connect with others, and often bring enthusiasm and positivity into any environment. They tend to be expressive, spontaneous, and fun-loving, making them great at building relationships. However, their high energy can sometimes lead to impulsiveness, lack of focus, and difficulty sticking to long-term commitments. They thrive in dynamic environments where creativity, communication, and interaction are encouraged.",
            "Choleric": "Choleric individuals are strong-willed, ambitious, and highly goal-driven. They naturally take on leadership roles and are confident in making decisions, especially in challenging situations. Their determination and focus help them achieve results efficiently. However, they may come across as dominant, impatient, or overly controlling when things don’t go according to plan. They prefer structure, control, and clear objectives, and they excel in environments that require leadership, strategy, and quick decision-making.",
            "Melancholic": "Melancholic individuals are thoughtful, analytical, and deeply introspective. They value organization, detail, and precision, often striving for perfection in their work. They tend to be creative and emotionally aware, making them highly empathetic and reflective. However, they may struggle with overthinking, self-criticism, and sensitivity to criticism from others. They thrive in structured environments where they can plan, analyze, and express their creativity in meaningful and purposeful ways.",
            "Phlegmatic": "Phlegmatic individuals are calm, patient, and easygoing. They prefer a peaceful and stable environment and are known for their reliability and supportive nature. They are good listeners, loyal friends, and excellent team players who help maintain harmony in groups. However, they may avoid conflict, resist change, and sometimes lack urgency or motivation in decision-making. They perform well in environments that value consistency, cooperation, and long-term stability."
        };

        const shortTagline = BASIC_LOOKUP[temp.result_type] || temp.interpretation.split('.')[0] + '.';
        const detailedInterp = DETAILED_LOOKUP[temp.result_type] || temp.interpretation;

        html += `
        <div id="tab-temperament" class="tab-content">
            <div class="section-block">
                <div class="section-heading"><span class="section-num">1.5</span><h2>${temp.label}</h2></div>
                <div class="section-body">
                    <div class="temp-result-wrap">
                        <div class="temp-result-box">
                            <div style="font-size:0.8rem; text-transform:uppercase; letter-spacing:0.2em; color:#888; margin-bottom:0.5rem;">Resulting Type</div>
                            <div class="temp-type-label">${temp.result_type.toUpperCase()}</div>
                            <div style="font-size:1.1rem; color:#aaa; margin-top:1rem; font-style:italic;">"${shortTagline}"</div>
                        </div>
                    </div>

                    <div class="temp-detail-wrap">
                        <div class="temp-detail-text">
                            ${detailedInterp}
                        </div>
                    </div>
                </div>
            </div>
        </div>`;
    }

    // ── BIG FIVE SECTION ──
    if (sub.big5) {
        const b5 = sub.big5;
        const descriptorClass = {
            'Very Low': 'desc-very_low', 'Low': 'desc-low', 'Moderate': 'desc-moderate', 'High': 'desc-high', 'Very High': 'desc-very_high'
        };
        const traitOrder = ['openness', 'conscientiousness', 'extraversion', 'agreeableness', 'neuroticism'];
        const traitsHtml = traitOrder.map(key => {
            if (!b5.traits || !b5.traits[key]) return '';
            const t = b5.traits[key];
            const pct = t.score_pct || 0;
            const dc = descriptorClass[t.descriptor] || 'desc-moderate';
            return `
                <div class="b5-trait">
                    <div class="b5-trait-name">${t.label} <span class="b5-descriptor ${dc}">${t.descriptor}</span></div>
                    <div>
                        <div class="b5-bar-wrap"><div class="b5-bar-fill ${key}" data-width="${pct}" style="width:0%"></div></div>
                        <div class="b5-desc-text">${t.description}</div>
                    </div>
                    <div class="b5-pct">${Math.round(pct)}%</div>
                </div>`;
        }).join('');

        html += `
        <div id="tab-big5" class="tab-content">
            <div class="b5-section">
                <div class="section-heading">
                    <span class="section-num">02</span>
                    <h2>${b5.label}</h2>
                </div>
                <div class="section-desc">${b5.description}</div>
                <div class="b5-profile-summary">${b5.profile_summary}</div>
                <div class="b5-trait-list">${traitsHtml}</div>
            </div>
        </div>`;
    }

    // ── MULTIPLE INTELLIGENCE SECTION ──
    if (sub.multiple_intelligence) {
        const mi = sub.multiple_intelligence;
        const icons = { LI: '📚', LMI: '🔢', MI: '🎵', BKI: '🏃', SVI: '🎨', IPI: '🤝', INPI: '🧘', NI: '🌿', EI: '🌌' };
        const intelligenceOrder = ['LI', 'LMI', 'MI', 'BKI', 'SVI', 'IPI', 'INPI', 'NI', 'EI'];
        const dominantIcon = icons[mi.dominant_intelligences[0]] || '🧠';

        const miCards = intelligenceOrder.map(key => {
            if (!mi.intelligences || !mi.intelligences[key]) return '';
            const t = mi.intelligences[key];
            const isDom = mi.dominant_intelligences.includes(key);
            return `
                <div class="mi-card" style="${isDom ? 'border-color:#6C63FF;background:#f5f4ff;' : ''}">
                    <div class="mi-card-top">
                        <span class="mi-card-label">${icons[key] || ''} ${t.label}</span>
                        <span class="mi-card-pct">${Math.round(t.score_pct)}%</span>
                    </div>
                    <div class="mi-bar-wrap"><div class="mi-bar-fill ${key}" data-mi-width="${t.score_pct}" style="width:0%"></div></div>
                    <div class="mi-card-desc">${t.description}</div>
                </div>`;
        }).join('');

        html += `
        <div id="tab-mi" class="tab-content">
            <div class="mi-section">
                <div class="section-heading"><span class="section-num">03</span><h2>${mi.label}</h2></div>
                <div class="section-desc">${mi.description}</div>
                <div class="mi-dominant-banner">
                    <div class="mi-dominant-icon">${dominantIcon}</div>
                    <div class="mi-dominant-text">
                        <h3>Dominant Intelligence: ${mi.dominant_labels.join(' & ')}</h3>
                        <p>${mi.profile_summary}</p>
                    </div>
                </div>
                <div class="mi-grid">${miCards}</div>
            </div>
        </div>`;
    }

    // ── ENNEAGRAM SECTION ──
    if (sub.enneagram) {
        const en = sub.enneagram;
        html += `
        <div id="tab-enneagram" class="tab-content">
            <div class="section-block">
                <div class="section-heading"><span class="section-num">04</span><h2>${en.label}</h2></div>
                <div class="section-desc">${en.description}</div>
                
                <!-- Core Identity Box -->
                <div class="ennea-identity-box">
                    <div class="ennea-bg-num">${en.primary_type.number}</div>
                    
                    <div style="font-size:0.8rem; font-weight:800; text-transform:uppercase; letter-spacing:0.1em; color:#888; margin-bottom:0.5rem;">Primary Pattern</div>
                    <div class="ennea-type-title">Type ${en.primary_type.number}: ${en.primary_type.label}</div>
                    
                    <div style="display:flex; align-items:center; gap:0.8rem; margin-top:1.5rem; flex-wrap:wrap;">
                        <div style="background:var(--c-purple); color:#fff; padding:0.3rem 0.8rem; font-size:0.75rem; font-weight:800; text-transform:uppercase; letter-spacing:0.05em;">Wing ${en.primary_type.wing}</div>
                        <span style="font-size:0.9rem; opacity:0.8;">Influenced by ${en.primary_type.wing_label}</span>
                    </div>
                </div>

                <!-- Intelligence Center -->
                <div class="ennea-center-box enneagram-center-box">
                    <div class="ennea-center-icon">
                        ${en.center.key === 'head' ? '🧠' : en.center.key === 'heart' ? '❤️' : '⚡'}
                    </div>
                    <div>
                        <div style="font-size:0.75rem; font-weight:800; text-transform:uppercase; letter-spacing:0.1em; color:#666; margin-bottom:0.3rem;">Dominant Triad</div>
                        <h3 style="font-size:1.4rem; font-weight:800; margin:0 0 0.5rem 0;">${en.center.label}</h3>
                        <p style="margin:0; font-size:0.95rem; color:#444; line-height:1.5;">You process the world primarily through the ${en.center.key} center, meaning your core drive is <strong>${en.center.core_motivation}</strong>.</p>
                    </div>
                </div>

                <!-- Core Motivation & Interpretation -->
                <div class="interp-box" style="border-left-color:var(--c-purple); margin-bottom:3rem; margin-top:0;">
                    <strong>Analytical Interpretation</strong>
                    <p>${en.interpretation}</p>
                </div>
                
                <!-- 9 Types Breakdown -->
                <h3 style="font-size:1.2rem; font-weight:800; margin-bottom:1.5rem; border-bottom:2px solid #eee; padding-bottom:0.8rem;">FULL ENNEAGRAM PROFILE (LIVE)</h3>
                <div style="display:flex; flex-direction:column; gap:0.5rem; align-items:center;">
                    
                    <!-- Detail Grid (Now on top) -->
                    <div style="width:100%; display:grid; grid-template-columns:repeat(auto-fill, minmax(220px, 1fr)); gap:1rem; align-content:start;">
                        ${en.type_rankings.map(t => {
            let isPrimary = t.type === en.primary_type.number;
            let bg = isPrimary ? '#000' : '#fff';
            let textC = isPrimary ? '#fff' : '#000';
            let descColor = '#888';
            if (t.descriptor === 'moderate') descColor = '#3498db';
            if (t.descriptor === 'strong') descColor = '#1abc9c';
            if (t.descriptor === 'dominant') descColor = '#e74c3c';

            return '<div style="border:1px solid #eee; background:' + bg + '; padding:1rem; display:flex; align-items:center; gap:1rem;">' +
                '<div style="font-size:1.6rem; font-weight:900; color:' + textC + '; width:20px;">' + t.type + '</div>' +
                '<div style="flex:1;">' +
                '<div style="font-size:0.8rem; font-weight:700; color:' + textC + '; line-height:1.2;">' + t.label + '</div>' +
                '<div style="font-size:0.6rem; font-weight:800; text-transform:uppercase; letter-spacing:0.05em; color:' + descColor + '; margin-top:0.3rem;">' + t.score_pct + '% &middot; ' + t.descriptor + '</div>' +
                '</div></div>';
        }).join('')}
                    </div>

                    <!-- Polar Area Chart Container (Upright & Balanced) -->
                    <div style="width:100%; max-width:550px; margin:0 auto 2rem auto; display:flex; justify-content:center; align-items:center; background:#f9f9f9; padding:2rem; border:1px solid #eee;">
                        <div style="position:relative; width:100%; max-width:450px; height:450px;">
                            <canvas id="enneagramChart" style="display:block; width:100%; height:450px;"></canvas>
                        </div>
                    </div>

                </div>
            </div>
        </div>`;
    }

    // ── BRAIN DOMINANCE SECTION ──
    if (sub.brain_dominance) {
        const bd = sub.brain_dominance;
        html += `
        <div id="tab-brain" class="tab-content">
            <div class="section-block">
                <div class="section-heading"><span class="section-num">05</span><h2>${bd.label}</h2></div>
                <div class="section-desc">${bd.description}</div>
                <div class="section-body">
                    <div style="margin-top:2rem;">
                        <div class="brain-label-row">
                            <span>Left Brain (Analytical)</span>
                            <span>Right Brain (Creative)</span>
                        </div>
                        <div style="height:50px; background:#f0f0f0; display:flex; border-radius:4px; overflow:hidden; border:1px solid #eee;">
                            <div style="width:${bd.left.score_pct}%; background:#34495e; display:flex; align-items:center; padding-left:1.5rem; color:#fff; font-weight:800; transition: width 1.5s ease-out;">
                                ${Math.round(bd.left.score_pct)}%
                            </div>
                            <div style="width:${bd.right.score_pct}%; background:var(--c-teal); display:flex; align-items:center; justify-content:flex-end; padding-right:1.5rem; color:#fff; font-weight:800; transition: width 1.5s ease-out;">
                                ${Math.round(bd.right.score_pct)}%
                            </div>
                        </div>
                        <div style="margin-top:2.5rem; padding:2rem; background:#fcfcfc; border-left:4px solid var(--c-teal);">
                            <div style="font-size:0.75rem; font-weight:800; text-transform:uppercase; letter-spacing:0.1em; color:#888; margin-bottom:0.5rem;">Primary Cognitive Style</div>
                            <h3 style="font-size:1.8rem; font-weight:900; color:#000; margin:0 0 1rem 0; letter-spacing:-0.02em;">${bd.dominance.label}</h3>
                            <p style="margin:0; font-size:1.05rem; color:#444; line-height:1.6; max-width:100%; font-style:normal;">
                                ${bd.dominance.description}
                            </p>
                        </div>
                    </div>
                </div>
            </div>
        </div>`;
    }

    html += `</div>`; // Close results-container

    // ── COMPOSITE INSIGHTS ──
    html += `
        <div class="insights-block" id="sec-insights">
            <button class="detailed-report-btn" onclick="toggleDetailedReport()">View</button>
            <h2>Composite Insights</h2>
            
            <div class="insights-preview-wrap">
                <div class="insights-summary">${insights.personality_summary || insights.executive_summary || ""}</div>
                <div class="blur-overlay"></div>
            </div>

            <div class="insights-columns">
                <div class="insight-col strengths">
                    <h3>Top Strengths</h3>
                    <ul>${insights.top_strengths.map(s => `<li>${s}</li>`).join('')}</ul>
                </div>
                <div class="insight-col growth">
                    <h3>Growth Areas</h3>
                    <ul>${insights.growth_areas.map(g => `<li>${g}</li>`).join('')}</ul>
                </div>
            </div>
            
            <div class="insights-detail-header" style="font-size:0.7rem;text-transform:uppercase;letter-spacing:0.12em;font-weight:700;color:#888;margin-top:2.5rem;margin-bottom:1.2rem;">Recommended Career Domains</div>
            <div class="career-paths-grid">
                ${(insights.recommended_career_domains || []).map(c => {
        const name = typeof c === 'object' ? (c.name || 'Undefined') : c;
        const reason = typeof c === 'object' ? (c.reason || '') : '';
        return `
                    <div class="career-path-card">
                        <div class="career-path-name">${name}</div>
                        <div class="career-path-reason">${reason}</div>
                    </div>`;
    }).join('')}
            </div>

            <div class="insights-detail-header" style="font-size:0.7rem;text-transform:uppercase;letter-spacing:0.12em;font-weight:700;color:#888;margin-top:2rem;margin-bottom:0.8rem;">Workplace Compatibility</div>
            <div class="compat-grid">
                <div class="compat-card">
                    <div class="compat-label">Work Environment</div>
                    <div class="compat-value">${insights.compatibility_notes?.work_environment || 'Assessment pending'}</div>
                </div>
                <div class="compat-card">
                    <div class="compat-label">Team Role</div>
                    <div class="compat-value">${insights.compatibility_notes?.team_role || 'Assessment pending'}</div>
                </div>
                <div class="compat-card">
                    <div class="compat-label">Leadership Style</div>
                    <div class="compat-value">${insights.compatibility_notes?.leadership_style || 'Assessment pending'}</div>
                </div>
            </div>
        </div>`;

    // ── FOOTER ──
    html += `
        <div class="report-footer-bar">
            <span>${meta.report_id}</span>
            <span>Psychometric Assessment · ${meta.total_questions_answered} Points</span>
            <button class="print-btn" onclick="window.print()">Save PDF</button>
        </div>`;

    // ── POPULATE MODERN PRINTABLE REPORT (FOR PREMIUM PDF DOWNLOAD) ──
    let p = ''; // printHtml
    const dateStr = new Date(meta.generated_at).toLocaleDateString('en-IN', { year: 'numeric', month: 'long', day: 'numeric' });

    p += `
    <div class="print-section">
        <h1>Psychometric Assessment Report</h1>
        <div style="display:flex; justify-content:space-between; align-items:flex-end;">
            <div>
                <p><strong>Candidate:</strong> ${meta.candidate.name}</p>
                <p><strong>Report ID:</strong> ${meta.report_id}</p>
            </div>
            <div style="text-align:right;">
                <p><strong>Date:</strong> ${dateStr}</p>
                <p><strong>Platform:</strong> ScoePsychometrics</p>
            </div>
        </div>
    </div>

    <div class="print-section">
        <h2>1. Executive Summary</h2>
        <div class="print-card" style="font-style:italic; font-size:1.1rem; border-left:4px solid #1abc9c;">
            ${insights.ai_overview || ""}
        </div>
    </div>

    <div class="print-section">
        <h2>2. Identity Overview</h2>
        <div style="display:grid; grid-template-columns: repeat(3, 1fr); gap: 1rem;">
            <div class="print-card">
                <div style="font-size:0.7rem; font-weight:800; color:#888; text-transform:uppercase;">MBTI Type</div>
                <div style="font-size:1.4rem; font-weight:900;">${sub.mbti?.result_type}</div>
                <div style="font-size:0.75rem; color:#666;">${sub.mbti?.type_label}</div>
            </div>
            <div class="print-card">
                <div style="font-size:0.7rem; font-weight:800; color:#888; text-transform:uppercase;">Temperament</div>
                <div style="font-size:1.4rem; font-weight:900;">${sub.temperament?.result_type}</div>
                <div style="font-size:0.75rem; color:#666;">Core Profile</div>
            </div>
            <div class="print-card" style="border-bottom: 3px solid #1abc9c;">
                <div style="font-size:0.7rem; font-weight:800; color:#888; text-transform:uppercase;">Enneagram</div>
                <div style="font-size:1.4rem; font-weight:900;">Type ${sub.enneagram?.primary_type?.number || '?'}</div>
                <div style="font-size:0.75rem; font-weight:800; color:#1abc9c;">${sub.enneagram?.primary_type?.score_pct || 0}% Dominance</div>
            </div>
        </div>
    </div>

    <div class="print-section">
        <h2>3. Visual Personality Profile (Big Five)</h2>
        <div class="print-card visually-boring-table-replacement">
            ${Object.keys(sub.big5?.traits || {}).map(k => {
        const t = sub.big5.traits[k];
        const val = Math.round(t.score_pct);
        return `
                <div class="b5-print-row">
                    <div class="b5-print-label">
                        <span>${t.label}</span>
                        <span>${val}%</span>
                    </div>
                    <div class="b5-print-track">
                        <div class="b5-print-fill" style="width:${val}%;"></div>
                    </div>
                    <div style="font-size:0.75rem; color:#666; margin-top:0.3rem;">${t.description}</div>
                </div>`;
    }).join('')}
        </div>
    </div>

    <div class="print-section">
        <h2>6. Strengths & Development Areas</h2>
        <div style="display:grid; grid-template-columns: 1fr 1fr; gap: 1.5rem;">
            <div class="print-card" style="border-top:4px solid #1abc9c;">
                <h3 style="color:#1abc9c; text-transform:uppercase; font-size:0.8rem;">Core Strengths</h3>
                <ul style="padding-left:1.2rem; margin:0; font-size:0.9rem;">
                    ${insights.top_strengths.map(s => `<li style="margin-bottom:0.5rem;">${s}</li>`).join('')}
                </ul>
            </div>
            <div class="print-card" style="border-top:4px solid #e74c3c;">
                <h3 style="color:#e74c3c; text-transform:uppercase; font-size:0.8rem;">Growth Areas</h3>
                <ul style="padding-left:1.2rem; margin:0; font-size:0.9rem;">
                    ${insights.growth_areas.map(g => `<li style="margin-bottom:0.5rem;">${g}</li>`).join('')}
                </ul>
            </div>
        </div>
    </div>

    <div class="print-section">
        <h2>7. Career & Work Style</h2>
        <div style="margin-bottom:1.5rem;">
            <h3>Ideal Workspace</h3>
            <p style="font-size:0.9rem;">${insights.compatibility_notes?.work_environment || ""}</p>
        </div>
        <h3>Recommended Roles</h3>
        <div style="display:grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
            ${(insights.recommended_career_domains || []).map(c => {
                const name = typeof c === 'object' ? (c.name || '') : c;
                const reason = typeof c === 'object' ? (c.reason || '') : '';
                return `
                <div class="print-card" style="margin:0; padding:1rem;">
                    <strong>${name}</strong>
                    ${reason ? `<p style="font-size:0.8rem; color:#666; margin:0.3rem 0 0 0;">${reason}</p>` : ''}
                </div>`;
            }).join('')}
        </div>
    </div>

    <div class="print-section">
        <h2>4. Enneagram Analysis</h2>
        <div style="display:grid; grid-template-columns: 300px 1fr; gap: 2rem; align-items:center;">
            <div style="width:300px; height:300px; display:flex; flex-direction:column; align-items:center;">
                <canvas id="enneagramChartPrint" width="300" height="300"></canvas>
                <div style="margin-top:0.75rem; font-weight:900; color:#2c3e50; text-transform:uppercase; font-size:0.75rem; letter-spacing:0.05em; text-align:center; border-top:1px solid #eee; padding-top:0.4rem; width:80%;">
                    Type ${sub.enneagram?.primary_type?.number}: ${sub.enneagram?.primary_type?.label}
                </div>
            </div>
            <div>
                <h3 style="margin-top:0;">Primary Archetype: ${sub.enneagram?.primary_type?.label}</h3>
                <div style="font-size:0.95rem; color:#444;">${sub.enneagram?.interpretation || ""}</div>
            </div>
        </div>
    </div>

    <div class="print-section">
        <h2>5. Cognitive & Temperament Profile</h2>
        <div style="display:grid; grid-template-columns: 1fr 1fr; gap: 1.5rem;">
            <div class="print-card">
                <h3>Brain Dominance</h3>
                <p style="font-size:0.9rem;"><strong>Left (Analytical):</strong> ${Math.round(sub.brain_dominance?.left.score_pct)}%</p>
                <p style="font-size:0.9rem;"><strong>Right (Creative):</strong> ${Math.round(sub.brain_dominance?.right.score_pct)}%</p>
                <hr style="border:0; border-top:1px solid #eee; margin:1rem 0;">
                <p style="font-size:0.85rem; color:#666;">${sub.brain_dominance?.dominance.description}</p>
            </div>
            <div class="print-card">
                <h3>Behavioral Style</h3>
                <p style="font-size:0.9rem;"><strong>Primary Style:</strong> ${sub.temperament?.result_type}</p>
                <hr style="border:0; border-top:1px solid #eee; margin:1rem 0;">
                <p style="font-size:0.85rem; color:#666;">${sub.temperament?.interpretation?.substring(0, 200)}...</p>
            </div>
            ${sub.multiple_intelligence ? `
            <div class="print-card">
                <h3>Multiple Intelligence (MI)</h3>
                <p style="font-size:0.9rem;"><strong>Dominant:</strong> ${sub.multiple_intelligence.dominant_labels.join(', ')}</p>
                <hr style="border:0; border-top:1px solid #eee; margin:1rem 0;">
                <p style="font-size:0.85rem; color:#666;">${sub.multiple_intelligence.profile_summary.substring(0, 200)}...</p>
            </div>` : ''}
        </div>
    </div>

    <div class="print-section">
        <h2>8. Composite Insights (Deep Analysis)</h2>
        <div class="print-card" style="white-space: pre-wrap; font-size:0.95rem; background:#fff;">${insights.personality_summary || ""}</div>
    </div>

    <div class="print-footer">
        <p><strong>RE-PT ID:</strong> ${meta.report_id} | ScoePsychometrics &copy; 2026</p>
        <p><em>Confidential Psychometric Analysis - Intended for Personal Development</em></p>
    </div>
    `;

    document.getElementById('printable-report').innerHTML = p;
    root.innerHTML = html;

    // Animate Big 5 trait bars after DOM render
    setTimeout(() => {
        document.querySelectorAll('.b5-bar-fill').forEach(bar => {
            const target = bar.getAttribute('data-width');
            if (target) bar.style.width = target + '%';
        });
        document.querySelectorAll('.mi-bar-fill').forEach(bar => {
            const target = bar.getAttribute('data-mi-width');
            if (target) bar.style.width = target + '%';
        });

        // Define chart initialization logic for Enneagram
        if (sub.enneagram) {
            window.initEnneagramChart = function () {
                const ctx = document.getElementById('enneagramChart');
                if (!ctx) return;

                if (window.enneagramChartInstance) {
                    window.enneagramChartInstance.destroy();
                }

                const labels = [];
                const data = [];

                const bgColors = [
                    'rgb(247, 172, 83)',   // 1: Orange
                    'rgb(255, 111, 105)',  // 2: Coral/Red
                    'rgb(233, 88, 154)',   // 3: Pink
                    'rgb(167, 101, 166)',  // 4: Purple
                    'rgb(69, 162, 185)',   // 5: Blue
                    'rgb(0, 188, 212)',    // 6: Cyan/Aqua
                    'rgb(58, 181, 133)',   // 7: Green
                    'rgb(144, 225, 122)',  // 8: Lime Green
                    'rgb(252, 208, 89)'    // 9: Yellow
                ];

                for (let i = 1; i <= 9; i++) {
                    const tInfo = sub.enneagram.type_scores[`type_${i}`];
                    labels.push(`Type ${i}: ${tInfo.label}`);

                    let chartVal = tInfo.score_pct || 0;
                    data.push(chartVal);
                }

                try {
                    window.enneagramChartInstance = new Chart(ctx, {
                        type: 'polarArea',
                        data: {
                            labels: labels,
                            datasets: [{
                                data: data,
                                backgroundColor: bgColors,
                                borderWidth: 0,
                                hoverOffset: 4
                            }]
                        },
                        options: {
                            responsive: true,
                            maintainAspectRatio: false,
                            layout: { padding: 20 },
                            scales: {
                                r: {
                                    min: 0,
                                    max: 100,
                                    ticks: { display: false },
                                    grid: { color: 'rgba(0,0,0,0.1)', circular: true, lineWidth: 1 },
                                    angleLines: { color: 'rgba(0,0,0,0.1)', lineWidth: 1 }
                                }
                            },
                            plugins: {
                                legend: { display: false },
                                tooltip: {
                                    callbacks: {
                                        label: function (context) {
                                            return `${context.label}: ${context.raw}%`;
                                        }
                                    }
                                }
                            }
                        }
                    });

                    // Initialize Print Chart
                    const ctxPrint = document.getElementById('enneagramChartPrint');
                    if (ctxPrint) {
                        if (window.enneagramChartPrintInstance) {
                            window.enneagramChartPrintInstance.destroy();
                        }
                        window.enneagramChartPrintInstance = new Chart(ctxPrint, {
                            type: 'polarArea',
                            data: {
                                labels: labels,
                                datasets: [{
                                    data: data,
                                    backgroundColor: bgColors,
                                    borderWidth: 1,
                                    borderColor: '#fff'
                                }]
                            },
                            options: {
                                responsive: true,
                                maintainAspectRatio: false,
                                animation: false,
                                layout: { padding: 10 },
                                scales: {
                                    r: {
                                        min: 0,
                                        max: 100,
                                        ticks: { display: false },
                                        grid: { color: '#eee', circular: true },
                                        angleLines: { color: '#eee' }
                                    }
                                },
                                plugins: {
                                    legend: { display: false },
                                    tooltip: { enabled: false }
                                }
                            },
                            plugins: [{
                                id: 'dominantLabel',
                                afterDatasetsDraw(chart) {
                                    const { ctx, data } = chart;
                                    const ds = data.datasets[0];
                                    const maxVal = Math.max(...ds.data);
                                    const maxIndex = ds.data.indexOf(maxVal);
                                    const meta = chart.getDatasetMeta(0);
                                    const arc = meta.data[maxIndex];

                                    if (arc && maxVal > 0) {
                                        const { x, y, outerRadius, innerRadius, startAngle, endAngle } = arc;
                                        const midAngle = (startAngle + endAngle) / 2;
                                        // Position it slightly outward from the center of the arc
                                        const textRadius = innerRadius + (outerRadius - innerRadius) * 0.6;
                                        const tx = x + Math.cos(midAngle) * textRadius;
                                        const ty = y + Math.sin(midAngle) * textRadius;

                                        ctx.save();
                                        ctx.font = '700 13px "Outfit", "Inter", sans-serif';
                                        ctx.fillStyle = '#000000';
                                        ctx.textAlign = 'center';
                                        ctx.textBaseline = 'middle';
                                        // Minimal light shadow for readability on dark colors
                                        ctx.shadowColor = 'rgba(255, 255, 255, 0.6)';
                                        ctx.shadowBlur = 3;
                                        ctx.fillText(maxVal + '%', tx, ty);
                                        ctx.restore();
                                    }
                                }
                            }]
                        });
                    }
                } catch (err) {
                    console.error("Chart Render Error:", err);
                }
            };

            // Always try to initialize immediately. With explicit canvas height, Chart.js can draw even if display:none.
            setTimeout(() => window.initEnneagramChart(), 10);
        }
    }, 100);
}

loadReport();

// Report Lookup Modal Logic
function openReportModal(e) {
    e.preventDefault();
    document.getElementById('reportModal').classList.add('active');
    document.getElementById('lookupEmail').value = '';
    document.getElementById('lookupPassword').value = '';
    document.getElementById('lookupResults').innerHTML = '';
    setTimeout(() => document.getElementById('lookupEmail').focus(), 100);
}

/**
 * Toggles the blurred Composite Insights section between collapsed and expanded states.
 */
function toggleDetailedReport() {
    const block = document.getElementById('sec-insights');
    const btn = document.querySelector('.detailed-report-btn');

    if (!block || !btn) return;

    const isExpanded = block.classList.toggle('expanded');

    btn.innerText = isExpanded ? 'View Less' : 'View';

    if (!isExpanded) {
        block.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
}

function closeReportModal() {
    document.getElementById('reportModal').classList.remove('active');
}

/**
 * Fired after Google authentication for report lookup.
 * Fills the email field and prompts for password.
 */
async function handleGoogleLookup(response) {
    try {
        const verifyRes = await fetch('/auth/google-verify', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ credential: response.credential })
        });
        const userData = await verifyRes.json();

        if (userData.status === 'success') {
            // Fill email and move to password field
            document.getElementById('lookupEmail').value = userData.email;
            document.getElementById('lookupPassword').focus();

            // Clear any previous results
            document.getElementById('lookupResults').innerHTML = '<p style="color:#2ecc71; font-size:0.9rem;">Email verified via Google. Please enter your password to continue.</p>';
        }
    } catch (err) {
        console.error("Google Lookup Error:", err);
    }
}

/**
 * Standard password-based report lookup.
 */
async function lookupReports() {
    const email = document.getElementById('lookupEmail').value.trim();
    const password = document.getElementById('lookupPassword').value.trim();
    const resDiv = document.getElementById('lookupResults');

    if (!email) {
        resDiv.innerHTML = '<p style="color:red; font-size:0.9rem;">Please enter an email.</p>';
        return;
    }
    if (!password) {
        resDiv.innerHTML = '<p style="color:red; font-size:0.9rem;">Please enter your password.</p>';
        return;
    }

    resDiv.innerHTML = '<p style="color:#666; font-size:0.9rem;">Searching...</p>';

    try {
        const res = await fetch('/api/reports/user/' + encodeURIComponent(email) + '?password=' + encodeURIComponent(password));

        if (res.status === 401) {
            resDiv.innerHTML = '<p style="color:red; font-size:0.9rem;">Invalid password.</p>';
            return;
        }

        const data = await res.json();

        if (!data || data.length === 0) {
            resDiv.innerHTML = '<p style="color:#666; font-size:0.9rem; font-style:italic;">No reports found. Make sure you entered the correct email used during the assessment.</p>';
            return;
        }

        let html = '';
        data.forEach(r => {
            const d = new Date(r.created_at);
            html += `
                <a href="/report?report_id=${r.report_id}" class="report-item">
                    <div>
                        <div class="ri-id">${r.report_id}</div>
                        <div class="ri-date">${d.toLocaleDateString('en-IN', { year: 'numeric', month: 'long', day: 'numeric' })} &middot; ${r.candidate_name}</div>
                    </div>
                    <span style="font-weight:700;">&rarr;</span>
                </a>
            `;
        });
        resDiv.innerHTML = html;
    } catch (err) {
        resDiv.innerHTML = '<p style="color:red; font-size:0.9rem;">Error connecting to server. Please try again.</p>';
    }
}
