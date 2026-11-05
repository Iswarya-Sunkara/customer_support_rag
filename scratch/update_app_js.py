from pathlib import Path

root = Path(__file__).resolve().parent.parent
app_path = root / "src" / "static" / "app.js"
js = app_path.read_text(encoding="utf-8")

# 1. Add view element and buttons
needle_decl = "const viewWeek10 = document.getElementById('viewWeek10');"
repl_decl = """const viewWeek10 = document.getElementById('viewWeek10');
    const viewWeek12 = document.getElementById('viewWeek12');
    const tabBtnWeek12 = document.getElementById('tabBtnWeek12');
    const sidebarWeek12Btn = document.getElementById('sidebarWeek12Btn');"""
if needle_decl in js and "viewWeek12" not in js:
    js = js.replace(needle_decl, repl_decl, 1)

# 2. Add to allTabBtns and allViews
needle_arrays = "const allTabBtns = [tabBtnChat, tabBtnWeek3, tabBtnWeek4, tabBtnWeek5, tabBtnWeek6, tabBtnWeek7, tabBtnWeek8, tabBtnWeek9, tabBtnWeek10, tabBtnLangfuse].filter(Boolean);"
needle_views = "const allViews = [viewChat, viewWeek3, viewWeek4, viewWeek5, viewWeek6, viewWeek7, viewWeek8, viewWeek9, viewWeek10, viewLangfuse].filter(Boolean);"

if needle_arrays in js:
    js = js.replace(needle_arrays, "const allTabBtns = [tabBtnChat, tabBtnWeek3, tabBtnWeek4, tabBtnWeek5, tabBtnWeek6, tabBtnWeek7, tabBtnWeek8, tabBtnWeek9, tabBtnWeek10, tabBtnWeek12, tabBtnLangfuse].filter(Boolean);", 1)
if needle_views in js:
    js = js.replace(needle_views, "const allViews = [viewChat, viewWeek3, viewWeek4, viewWeek5, viewWeek6, viewWeek7, viewWeek8, viewWeek9, viewWeek10, viewWeek12, viewLangfuse].filter(Boolean);", 1)

# 3. Add to switchView
needle_switch = "} else if (target === 'langfuse') {"
repl_switch = """} else if (target === 'week12') {
                if (tabBtnWeek12) tabBtnWeek12.classList.add('active');
                if (viewWeek12) {
                    viewWeek12.classList.add('active');
                    viewWeek12.style.display = 'flex';
                }
                fetchWeek12Summary();
            } else if (target === 'langfuse') {"""
if needle_switch in js and "target === 'week12'" not in js:
    js = js.replace(needle_switch, repl_switch, 1)

# 4. Add handlers at bottom
week12_handlers = """
    // =========================================================================
    // Week 12: Production & Capstone Dashboard Interactivity
    // =========================================================================
    if (sidebarWeek12Btn) {
        sidebarWeek12Btn.addEventListener('click', () => switchView('week12'));
    }

    const btnRunWeek12Ticket1a = document.getElementById('btnRunWeek12Ticket1a');
    const btnRunWeek12Ticket1b = document.getElementById('btnRunWeek12Ticket1b');
    const w12Console = document.getElementById('w12LiveOutputConsole');

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
        w12Console.textContent = `[Executing Assistant Loop for Ticket ${payload.ticket_id}...]\\nCustomer ID: ${payload.customer_id}\\nQuery: "${payload.question}"\\n\\n• Calling check_customer_entitlement...\\n• Calling fetch_order_details...\\n• Searching help center articles...`;
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
"""

if "btnRunWeek12Ticket1a" not in js:
    idx = js.rfind("});")
    if idx != -1:
        js = js[:idx] + week12_handlers + "\n" + js[idx:]
        print("Appended week12_handlers to app.js")

app_path.write_text(js, encoding="utf-8")
print("Updated app.js successfully!")
