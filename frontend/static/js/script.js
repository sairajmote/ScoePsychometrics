document.addEventListener('DOMContentLoaded', () => {
    const reveals = document.querySelectorAll('.reveal');

    const revealOnScroll = () => {
        const windowHeight = window.innerHeight;
        reveals.forEach(element => {
            const elementTop = element.getBoundingClientRect().top;
            const elementVisible = 150;
            if (elementTop < windowHeight - elementVisible) {
                element.classList.add('active');
            }
        });
    };

    window.addEventListener('scroll', revealOnScroll);

    // Initial check
    revealOnScroll();

    // Fetch and display live accuracy score
    fetchLiveAccuracy();

    // Button hover effects - adding a little "magnetic" feel or simple logs
    const buttons = document.querySelectorAll('.btn');
    buttons.forEach(btn => {
        btn.addEventListener('mouseenter', () => {
            console.log('Interaction: Button Hovered');
        });
    });
});

/**
 * Fetches live feedback stats from /api/feedback/stats
 * and updates the hero section badge.
 */
async function fetchLiveAccuracy() {
    const badge = document.getElementById('live-accuracy-badge');
    const valueDisp = document.getElementById('accuracy-value');
    
    if (!badge || !valueDisp) return;

    try {
        const res = await fetch('/api/feedback/stats');
        if (!res.ok) return;
        
        const data = await res.json();
        
        // Only show if we have actual responses
        if (data.total_responses > 0 && data.overall_accuracy_score > 0) {
            valueDisp.textContent = data.overall_accuracy_score.toFixed(1) + '%';
            badge.style.display = 'inline-flex';
        }
    } catch (err) {
        console.error('Error fetching live accuracy:', err);
    }
}
