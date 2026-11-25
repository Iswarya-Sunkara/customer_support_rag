with open('src/static/app.js', 'r', encoding='utf-8') as f:
    full_text = f.read()

# Landmark: keep up to formatMarkdown definition (line 485-492)
landmark = """    function formatMarkdown(text) {
        return text
            .replace(/\\*\\*(.*?)\\*\\*/g, '<strong>$1</strong>')
            .replace(/\\*(.*?)\\*/g, '<em>$1</em>')
            .replace(/`(.*?)`/g, '<code>$1</code>')
            .replace(/\\n\\n/g, '</p><p>')
            .replace(/\\n/g, '<br/>');
    }"""

assert landmark in full_text, "formatMarkdown landmark not found"
head = full_text[:full_text.find(landmark) + len(landmark)]

tail = """

    // =========================================================================
    // Core Navigation & View Switching (Support Assistant vs Capstone Center)
    // =========================================================================
    const tabBtnChat = document.getElementById('tabBtnChat');
    const tabBtnWeek12Header = document.getElementById('tabBtnWeek12Header');
    const sidebarChatBtn = document.getElementById('sidebarChatBtn');
    const sidebarWeek12Btn = document.getElementById('sidebarWeek12Btn');
    const sidebarRunTicket1aBtn = document.getElementById('sidebarRunTicket1aBtn');
    const sidebarRunTicket1bBtn = document.getElementById('sidebarRunTicket1bBtn');

    const viewChat = document.getElementById('viewChat');
    const viewWeek12 = document.getElementById('viewWeek12');

    const btnRunWeek12Ticket1a = document.getElementById('btnRunWeek12Ticket1a');
    const btnRunWeek12Ticket1b = document.getElementById('btnRunWeek12Ticket1b');
    const w12Console = document.getElementById('w12LiveOutputConsole');

    function switchView(target) {
        if (target !== 'week12') {
            target = 'chat';
        }

        try {
            if (target === 'week12') {
                history.replaceState(null, null, '#week12');
            } else {
                history.replaceState(null, null, window.location.pathname);
            }
        } catch (_) {}

        if (target === 'chat') {
            if (tabBtnChat) tabBtnChat.classList.add('active');
            if (tabBtnWeek12Header) tabBtnWeek12Header.classList.remove('active');
            if (sidebarChatBtn) sidebarChatBtn.classList.add('active');
            if (sidebarWeek12Btn) sidebarWeek12Btn.classList.remove('active');

            if (viewChat) {
                viewChat.classList.add('active');
                viewChat.style.display = 'flex';
            }
            if (viewWeek12) {
                viewWeek12.classList.remove('active');
                viewWeek12.style.display = 'none';
            }
        } else {
            if (tabBtnChat) tabBtnChat.classList.remove('active');
            if (tabBtnWeek12Header) tabBtnWeek12Header.classList.add('active');
            if (sidebarChatBtn) sidebarChatBtn.classList.remove('active');
            if (sidebarWeek12Btn) sidebarWeek12Btn.classList.add('active');

            if (viewChat) {
                viewChat.classList.remove('active');
                viewChat.style.display = 'none';
            }
            if (viewWeek12) {
                viewWeek12.classList.add('active');
                viewWeek12.style.display = 'flex';
            }
            fetchWeek12Summary();
        }
    }

    if (tabBtnChat) tabBtnChat.addEventListener('click', () => switchView('chat'));
    if (tabBtnWeek12Header) tabBtnWeek12Header.addEventListener('click', () => switchView('week12'));
    if (sidebarChatBtn) sidebarChatBtn.addEventListener('click', () => switchView('chat'));
    if (sidebarWeek12Btn) sidebarWeek12Btn.addEventListener('click', () => switchView('week12'));

    if (sidebarRunTicket1aBtn) {
        sidebarRunTicket1aBtn.addEventListener('click', () => {
            switchView('week12');
            if (btnRunWeek12Ticket1a) btnRunWeek12Ticket1a.click();
        });
    }

    if (sidebarRunTicket1bBtn) {
        sidebarRunTicket1bBtn.addEventListener('click', () => {
            switchView('week12');
            if (btnRunWeek12Ticket1b) btnRunWeek12Ticket1b.click();
        });
    }

    // =========================================================================
    // Week 12: Production & Capstone Dashboard Execution Engine
    // =========================================================================
    async function fetchWeek12Summary() {
        try {
            const resp = await fetch('/api/week12/summary');
            const data = await resp.json();
            if (data.status === 'success' && w12Console && w12Console.textContent.includes('[Ready]')) {
                w12Console.textContent = `[Connected to Gate M6 System]
Module: ${data.module}
Track: ${data.track}
Status: ${data.gate_status}

Client Volume: ${data.overview.client}
Key Resolution: ${data.overview.solution}

Click "Run Live Ticket 1a" or "Run Escalation Ticket 1b" to execute live.`;
            }
        } catch (e) {
            console.error('Failed to load Week 12 summary:', e);
        }
    }

    async function executeWeek12Ticket(payload) {
        if (!w12Console) return;
        w12Console.textContent = `[Executing Assistant Loop for Ticket ${payload.ticket_id}...]\nCustomer ID: ${payload.customer_id}\nQuery: "${payload.question}"\n\n• Calling check_customer_entitlement...\n• Calling fetch_order_details...\n• Searching help center articles...`;
        try {
            const resp = await fetch('/api/week12/run-ticket', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            const data = await resp.json();
            if (data.status === 'success') {
                const res = data.ticket_result;
                w12Console.textContent = `======================================================================
[LIVE RESOLUTION COMPLETE] Ticket: ${res.ticket_id}
======================================================================
• Resolution Status:    ${res.status}
• Entitlement Checked:  ${res.entitlement_checked} (Applicable Window: ${res.applicable_window_days} days)
• Policy Cited (Slug):  [${res.policy_cited}]
• Unified Trace ID:     ${res.trace_id}
• Total Latency:        ${res.latency_ms.toFixed(2)} ms
• Total Cost:           $${res.cost_usd.toFixed(6)} (${res.tokens} tokens across ${res.spans} spans)

[ASSISTANT FINAL DRAFTED RESPONSE]:
${res.reply}`;
            } else {
                w12Console.textContent = `[Error executing ticket]: ${data.error || 'Unknown error'}`;
            }
        } catch (err) {
            w12Console.textContent = `[Network Error]: ${err.message}`;
        }
    }

    if (btnRunWeek12Ticket1a) {
        btnRunWeek12Ticket1a.addEventListener('click', () => {
            executeWeek12Ticket({
                ticket_id: 'TKT-84920',
                customer_id: 'CUST-401',
                order_id: 'ORD-5001',
                question: 'Hi, I was charged $49 for Cloudflare Pro renewal 8 days ago under ORD-5001. Can I get a full refund to my card?'
            });
        });
    }

    if (btnRunWeek12Ticket1b) {
        btnRunWeek12Ticket1b.addEventListener('click', () => {
            executeWeek12Ticket({
                ticket_id: 'TKT-99120',
                customer_id: 'CUST-408',
                order_id: null,
                question: 'Urgent: I see an unauthorized fraudulent charge and have initiated a bank chargeback dispute. Refund this immediately or I will file an FTC complaint!'
            });
        });
    }

    // Ingest initial state
    fetchDocumentsList();
    fetchGoldenSet();

    // Check Role state on startup
    if (!currentUserRole) {
        openLoginModal(false);
    } else {
        applyRole(currentUserRole, false);
    }

    // Direct hash navigation (e.g. #week12 or ?tab=week12)
    const initialTarget = (window.location.hash || '').replace('#', '') || new URLSearchParams(window.location.search).get('tab');
    if (initialTarget === 'week12' || initialTarget === 'dashboard') {
        setTimeout(() => switchView('week12'), 80);
    } else {
        switchView('chat');
    }
});
"""

clean_js = head + tail
with open('src/static/app.js', 'w', encoding='utf-8') as f:
    f.write(clean_js)

print("Saved clean app.js!")

