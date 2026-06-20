document.addEventListener('DOMContentLoaded', () => {
    const contactForm = document.getElementById('contact-form');
    const submitBtn = document.getElementById('submit-btn');
    const btnText = document.getElementById('btn-text');
    const terminalBody = document.getElementById('terminal-body');
    
    const totalMessagesEl = document.getElementById('total-messages');
    const sentimentBarsEl = document.getElementById('sentiment-bars');
    const categoryListEl = document.getElementById('category-list');
    const recentMessagesTable = document.getElementById('recent-messages-table');

    function logToTerminal(text, type = 'info') {
        const line = document.createElement('div');
        line.className = 'terminal-line';
        
        let colorClass = 'text-muted';
        if (type === 'success') colorClass = 'text-success';
        if (type === 'warning') colorClass = 'text-warning';
        if (type === 'danger') colorClass = 'text-danger';
        if (type === 'info') colorClass = 'text-info';
        
        line.innerHTML = `<span class="terminal-prompt">eduard.dev $</span> <span class="${colorClass}">${text}</span>`;
        terminalBody.appendChild(line);
        terminalBody.scrollTop = terminalBody.scrollHeight;
    }

    async function fetchMetrics() {
        try {
            const res = await fetch('/api/metrics');
            if (!res.ok) throw new Error('Failed to fetch metrics');
            const data = await res.json();
            updateMetricsUI(data);
        } catch (err) {
            console.error('Error loading metrics:', err);
        }
    }

    function updateMetricsUI(data) {
        totalMessagesEl.textContent = data.total_messages;

        const sentiment = data.sentiment_distribution;
        const total = data.total_messages || 1;
        const posPct = Math.round(((sentiment.positive || 0) / total) * 100);
        const neuPct = Math.round(((sentiment.neutral || 0) / total) * 100);
        const negPct = Math.round(((sentiment.negative || 0) / total) * 100);

        sentimentBarsEl.innerHTML = `
            <div class="sentiment-bar-wrapper">
                <div class="sentiment-bar-label">
                    <span>Положительный (Positive)</span>
                    <span>${posPct}% (${sentiment.positive || 0})</span>
                </div>
                <div class="sentiment-bar-container">
                    <div class="sentiment-bar-fill positive" style="width: ${posPct}%"></div>
                </div>
            </div>
            <div class="sentiment-bar-wrapper">
                <div class="sentiment-bar-label">
                    <span>Нейтральный (Neutral)</span>
                    <span>${neuPct}% (${sentiment.neutral || 0})</span>
                </div>
                <div class="sentiment-bar-container">
                    <div class="sentiment-bar-fill neutral" style="width: ${neuPct}%"></div>
                </div>
            </div>
            <div class="sentiment-bar-wrapper">
                <div class="sentiment-bar-label">
                    <span>Отрицательный (Negative)</span>
                    <span>${negPct}% (${sentiment.negative || 0})</span>
                </div>
                <div class="sentiment-bar-container">
                    <div class="sentiment-bar-fill negative" style="width: ${negPct}%"></div>
                </div>
            </div>
        `;

        const categories = data.category_distribution;
        const catLabels = {
            job_offer: 'Предложение работы',
            partnership: 'Сотрудничество',
            question: 'Вопрос по стеку',
            spam: 'Спам / Реклама',
            other: 'Другое'
        };

        categoryListEl.innerHTML = Object.entries(catLabels).map(([key, label]) => `
            <div class="category-item">
                <span>${label}</span>
                <span class="category-badge">${categories[key] || 0}</span>
            </div>
        `).join('');

        recentMessagesTable.innerHTML = data.recent_messages.map(msg => `
            <tr>
                <td><strong>${escapeHtml(msg.name)}</strong></td>
                <td><span class="badge-category">${translateCategory(msg.category)}</span></td>
                <td><span class="badge-sentiment ${msg.sentiment}">${msg.sentiment.toUpperCase()}</span></td>
                <td><span class="text-secondary">${escapeHtml(msg.message)}</span></td>
                <td><span class="text-success">${escapeHtml(msg.ai_response || '')}</span></td>
            </tr>
        `).join('');
    }

    function translateCategory(cat) {
        const mapping = {
            job_offer: 'Оффер',
            partnership: 'Партнерство',
            question: 'Вопрос',
            spam: 'Спам',
            other: 'Другое'
        };
        return mapping[cat] || cat;
    }

    function escapeHtml(str) {
        if (!str) return '';
        return str.replace(/&/g, '&amp;')
                  .replace(/</g, '&lt;')
                  .replace(/>/g, '&gt;')
                  .replace(/"/g, '&quot;')
                  .replace(/'/g, '&#039;');
    }

    contactForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const payload = {
            name: document.getElementById('name').value,
            email: document.getElementById('email').value,
            phone: document.getElementById('phone').value,
            message: document.getElementById('message').value
        };

        submitBtn.disabled = true;
        btnText.textContent = 'Отправка...';

        logToTerminal(`POST /api/contact - Initiated from ${payload.name} (${payload.email})`, 'info');
        
        await sleep(600);
        logToTerminal('Running payload data schema validation checks...', 'info');
        
        await sleep(500);
        logToTerminal('Connecting to Google Gemini API (model: gemini-1.5-flash)...', 'warning');

        try {
            const res = await fetch('/api/contact', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            if (res.status === 429) {
                logToTerminal('API Error: 429 Too Many Requests (Rate limit exceeded)', 'danger');
                alert('Вы превысили лимит отправки сообщений. Пожалуйста, подождите минуту.');
                submitBtn.disabled = false;
                btnText.textContent = 'Отправить сообщение';
                return;
            }

            if (!res.ok) {
                const errData = await res.json();
                const detail = errData.detail || 'Unknown error';
                throw new Error(detail);
            }

            const data = await res.json();
            
            await sleep(600);
            logToTerminal('AI Analysis Complete!', 'success');
            logToTerminal(`Sentiment detected: ${data.sentiment.toUpperCase()}`, 'success');
            logToTerminal(`Category classified: ${data.category.toUpperCase()}`, 'success');
            logToTerminal(`Suggested reply generated:\n"${data.ai_response}"`, 'success');
            logToTerminal('Dispatching confirmation notification emails to background queue...', 'info');
            
            contactForm.reset();
            fetchMetrics();
        } catch (err) {
            logToTerminal(`System failure: ${err.message}`, 'danger');
            alert(`Ошибка отправки: ${err.message}`);
        } finally {
            submitBtn.disabled = false;
            btnText.textContent = 'Отправить сообщение';
        }
    });

    function sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    // Initial load and polling
    fetchMetrics();
    setInterval(fetchMetrics, 5000);
});
