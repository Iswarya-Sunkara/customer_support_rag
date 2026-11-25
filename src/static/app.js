document.addEventListener('DOMContentLoaded', () => {
    // Active System Mode State ('week3' vs 'week4')
    let currentMode = 'week4';

    // DOM Elements
    const dropZone = document.getElementById('dropZone');
    const fileInput = document.getElementById('fileInput');
    const uploadProgress = document.getElementById('uploadProgress');
    const uploadStatusText = document.getElementById('uploadStatusText');
    const docList = document.getElementById('docList');
    const docCountBadge = document.getElementById('docCountBadge');
    const kbStats = document.getElementById('kbStats');
    const statTotalChunks = document.getElementById('statTotalChunks');
    const btnClearKb = document.getElementById('btnClearKb');
    const goldenList = document.getElementById('goldenList');

    const chatMessages = document.getElementById('chatMessages');
    const chatForm = document.getElementById('chatForm');
    const userInput = document.getElementById('userInput');
    const typingIndicator = document.getElementById('typingIndicator');
    const btnClearChat = document.getElementById('btnClearChat');

    // Sidebar Toggle (Mobile / Desktop)
    const btnToggleSidebar = document.getElementById('btnToggleSidebar');
    const sidebar = document.querySelector('.sidebar');
    if (btnToggleSidebar && sidebar) {
        btnToggleSidebar.addEventListener('click', () => {
            sidebar.classList.toggle('collapsed');
        });
    }

    // System Title
    const headerTitle = document.getElementById('headerTitle');
    const welcomeMessageContent = document.getElementById('welcomeMessageContent');
    if (welcomeMessageContent) {
        welcomeMessageContent.innerHTML = `
            <p>👋 Hello! Welcome to the <strong>DocuMind AI Tier-1 Support Assistant & Capstone Center</strong>.</p>
            <p>I am your autonomous support agent with grounded knowledge across billing, card decline errors, refund policies, and account security. You can <strong>upload your documents</strong> in the sidebar, click <strong>Suggested</strong> prompts below, or test <strong>12 Golden Benchmark Questions</strong>.</p>
        `;
    }
    // Connect User Topic buttons in sidebar
    document.querySelectorAll('.user-topic-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const q = btn.getAttribute('data-q');
            if (q && userInput) {
                userInput.value = q;
                userInput.focus();
                if (chatForm) chatForm.dispatchEvent(new Event('submit'));
            }
        });
    });

    // 1. Drag & Drop Upload Event Listeners
    if (dropZone && fileInput) {
        dropZone.addEventListener('click', () => fileInput.click());

        ['dragenter', 'dragover'].forEach(eventName => {
            dropZone.addEventListener(eventName, (e) => {
                e.preventDefault();
                e.stopPropagation();
                dropZone.classList.add('dragover');
            });
        });

        ['dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, (e) => {
                e.preventDefault();
                e.stopPropagation();
                dropZone.classList.remove('dragover');
            });
        });

        dropZone.addEventListener('drop', (e) => {
            const files = e.dataTransfer.files;
            if (files && files.length > 0) {
                handleFileUpload(files);
            }
        });

        fileInput.addEventListener('change', (e) => {
            if (e.target.files && e.target.files.length > 0) {
                handleFileUpload(e.target.files);
            }
        });
    }

    // 3. File Upload Handler
    async function handleFileUpload(files) {
        uploadProgress.style.display = 'flex';
        uploadStatusText.textContent = `Uploading & indexing ${files.length} document(s)...`;

        const formData = new FormData();
        for (let i = 0; i < files.length; i++) {
            formData.append('files', files[i]);
        }

        try {
            const response = await fetch('/api/upload', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();
            if (response.ok) {
                fetchDocumentsList();
                appendAssistantMessage(`✅ Successfully uploaded and indexed <strong>${files.length} document(s)</strong>! You can now ask questions about your files.`);
            } else {
                alert('Upload Error: ' + (data.detail || 'Failed to upload files'));
            }
        } catch (err) {
            alert('Server error while uploading document: ' + err.message);
        } finally {
            uploadProgress.style.display = 'none';
            fileInput.value = '';
        }
    }

    // 4. Fetch & Update Document List
    async function fetchDocumentsList() {
        try {
            const res = await fetch('/api/documents');
            const data = await res.json();

            const docs = data.documents || [];
            const totalChunks = data.total_chunks || 0;

            docCountBadge.textContent = `${docs.length} File${docs.length === 1 ? '' : 's'}`;

            if (docs.length === 0) {
                docList.innerHTML = `
                    <div class="empty-docs">
                        <i class="fa-regular fa-folder-open"></i>
                        <p>No extra files uploaded</p>
                    </div>
                `;
                kbStats.style.display = 'none';
            } else {
                kbStats.style.display = 'flex';
                statTotalChunks.textContent = totalChunks;

                docList.innerHTML = docs.map(d => `
                    <div class="doc-item">
                        <div class="doc-info">
                            <strong title="${d.filename}">📄 ${d.filename}</strong>
                            <span>${d.chunks_count} chunks • ${(d.size_bytes / 1024).toFixed(1)} KB</span>
                        </div>
                        <span class="badge">${(d.extension || '.bin').toUpperCase()}</span>
                    </div>
                `).join('');
            }
        } catch (err) {
            console.error('Failed to fetch documents summary', err);
        }
    }

    // 5. Fetch & Render 12 Golden Set Questions
    async function fetchGoldenSet() {
        if (!goldenList) return;
        try {
            const res = await fetch('/api/golden-set');
            const data = await res.json();
            const questions = data.questions || [];

            goldenList.innerHTML = questions.map(q => `
                <div class="golden-item" data-question="${escapeHtml(q.question)}">
                    <div class="golden-item-top">
                        <span class="golden-id">${q.id}</span>
                        <span class="golden-cat">${escapeHtml(q.category)}</span>
                    </div>
                    <div class="golden-q" title="${escapeHtml(q.question)}">${escapeHtml(q.question)}</div>
                </div>
            `).join('');

        } catch (err) {
            goldenList.innerHTML = '<p style="font-size:0.75rem; color:#F87171;">Failed to load benchmark questions.</p>';
        }
    }

    // Handle Golden Item Click
    document.addEventListener('click', (e) => {
        const item = e.target.closest('.golden-item');
        if (item) {
            const questionText = item.getAttribute('data-question');
            if (questionText) {
                if (userInput) userInput.value = questionText;
                submitQuestion(questionText);
            }
        }
    });

    // 6. Clear Knowledge Base Button
    if (btnClearKb) {
        btnClearKb.addEventListener('click', async () => {
            if (!confirm('Are you sure you want to clear all uploaded documents?')) return;
            try {
                await fetch('/api/clear', { method: 'POST' });
                fetchDocumentsList();
                appendAssistantMessage('Knowledge base cleared. Benchmark articles remain available.');
            } catch (err) {
                console.error('Failed to clear knowledge base', err);
            }
        });
    }

    // 7. Quick Prompts Click Listener
    document.addEventListener('click', (e) => {
        const chip = e.target.closest('.prompt-chip');
        if (chip) {
            const promptText = chip.getAttribute('data-prompt');
            if (promptText) {
                if (userInput) userInput.value = promptText;
                submitQuestion(promptText);
            }
        }
    });

    // 8. Submit Question Handler
    if (chatForm) {
        chatForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const query = userInput ? userInput.value.trim() : '';
            if (!query) return;
            submitQuestion(query);
        });
    }

    async function submitQuestion(question) {
        appendUserMessage(question);
        userInput.value = '';
        typingIndicator.style.display = 'flex';
        chatMessages.scrollTop = chatMessages.scrollHeight;

        try {
            const res = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    question: question,
                    mode: currentMode
                })
            });

            const data = await res.json();
            typingIndicator.style.display = 'none';

            if (res.ok) {
                appendAssistantMessage(data.answer, data.citations, data.mode, data.is_week3_miss);
            } else {
                appendAssistantMessage('❌ Error: ' + (data.detail || 'Failed to generate answer.'));
            }
        } catch (err) {
            typingIndicator.style.display = 'none';
            appendAssistantMessage('❌ Network error: ' + err.message);
        }
    }

    // 9. Render Helper Functions
    function appendUserMessage(text) {
        const msgDiv = document.createElement('div');
        msgDiv.className = 'message user-message';
        msgDiv.innerHTML = `
            <div class="avatar"><i class="fa-solid fa-user"></i></div>
            <div class="message-body">
                <div class="sender-name">You <span class="time-stamp">${getCurrentTime()}</span></div>
                <div class="message-content"><p>${escapeHtml(text)}</p></div>
            </div>
        `;
        chatMessages.appendChild(msgDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function appendAssistantMessage(text, citations = [], modeUsed = null, isWeek3Miss = false) {
        const msgDiv = document.createElement('div');
        msgDiv.className = 'message assistant-message';

        const modeBadge = modeUsed ? `
            <span style="font-size:0.65rem; padding:2px 8px; border-radius:10px; margin-left:8px; font-weight:600; ${modeUsed === 'week3' ? 'background:rgba(245,158,11,0.2); color:#FBBF24;' : 'background:rgba(6,182,212,0.2); color:#38BDF8;'}">
                ${modeUsed === 'week3' ? 'Filter: Week 3 Dense Baseline' : 'Filter: Week 4 Hybrid RAG'}
            </span>
        ` : '';

        // Only show yellow miss tip if this was an actual Week 3 token retrieval miss (Q01, Q02, Q03, Q04, Q09), NOT for Q12 out-of-corpus refusal
        let missTipHtml = '';
        if (modeUsed === 'week3' && isWeek3Miss) {
            missTipHtml = `
                <div style="margin-top:10px; padding:10px 12px; background:rgba(245,158,11,0.15); border:1px solid rgba(245,158,11,0.4); border-radius:8px; font-size:0.8rem; color:#FCD34D;">
                    💡 <strong>Week 3 Baseline Missed This Answer!</strong><br/>
                    Dense vector search baseline failed to retrieve the exact error code token.<br/>
                    👉 Click the <strong>"Week 4 (Hybrid RAG)"</strong> filter button at the top header to see Hybrid BM25+RRF retrieve the exact answer!
                </div>
            `;
        }

        let citationsHtml = '';
        if (citations && citations.length > 0) {
            citationsHtml = `
                <div class="citations-box">
                    <div class="citations-header" onclick="this.nextElementSibling.style.display = this.nextElementSibling.style.display === 'none' ? 'block' : 'none'">
                        <i class="fa-solid fa-bookmark"></i> View ${citations.length} Grounded Source Citation(s) <i class="fa-solid fa-chevron-down" style="font-size:0.7rem; margin-left:auto;"></i>
                    </div>
                    <div class="citations-body" style="display: block;">
                        ${citations.map(c => `
                            <div class="citation-item">
                                <div class="citation-meta">
                                    <span><strong>📄 ${escapeHtml(c.filename)}</strong> (${escapeHtml(c.chunk_id)})</span>
                                    <span style="color:#06B6D4; font-weight:600;">Relevance: ${c.similarity_score}</span>
                                </div>
                                <div class="citation-snippet">"${escapeHtml(c.snippet)}"</div>
                            </div>
                        `).join('')}
                    </div>
                </div>
            `;
        }

        msgDiv.innerHTML = `
            <div class="avatar"><i class="fa-solid fa-robot"></i></div>
            <div class="message-body">
                <div class="sender-name">DocuMind AI ${modeBadge} <span class="time-stamp">${getCurrentTime()}</span></div>
                <div class="message-content">${formatMarkdown(text)}</div>
                ${missTipHtml}
                ${citationsHtml}
            </div>
        `;
        chatMessages.appendChild(msgDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // Reset Chat Button
    if (btnClearChat) {
        btnClearChat.addEventListener('click', () => {
            chatMessages.innerHTML = '';
            appendAssistantMessage('👋 Chat history reset! Select any of the 12 Golden Set Questions or upload a document to begin.');
        });
    }

    // Suggested Questions Toggle & Floating Panel Handlers
    const btnSuggestedQuestions = document.getElementById('btnSuggestedQuestions');
    const suggestedPanel = document.getElementById('suggestedPanel');
    const btnCloseSuggested = document.getElementById('btnCloseSuggested');

    if (btnSuggestedQuestions && suggestedPanel) {
        btnSuggestedQuestions.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            const isHidden = window.getComputedStyle(suggestedPanel).display === 'none' || suggestedPanel.style.display === 'none';
            suggestedPanel.style.display = isHidden ? 'flex' : 'none';
            btnSuggestedQuestions.classList.toggle('active', isHidden);
        });

        // Close when clicking outside the panel
        document.addEventListener('click', (e) => {
            if (suggestedPanel && suggestedPanel.style.display !== 'none') {
                if (!suggestedPanel.contains(e.target) && !btnSuggestedQuestions.contains(e.target)) {
                    suggestedPanel.style.display = 'none';
                    btnSuggestedQuestions.classList.remove('active');
                }
            }
        });
    }

    if (btnCloseSuggested && suggestedPanel) {
        btnCloseSuggested.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            suggestedPanel.style.display = 'none';
            if (btnSuggestedQuestions) btnSuggestedQuestions.classList.remove('active');
        });
    }

    document.querySelectorAll('.suggest-chip').forEach(chip => {
        chip.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            const q = chip.getAttribute('data-q');
            if (q) {
                if (userInput) userInput.value = q;
                if (suggestedPanel) suggestedPanel.style.display = 'none';
                if (btnSuggestedQuestions) btnSuggestedQuestions.classList.remove('active');
                if (chatForm) {
                    chatForm.dispatchEvent(new Event('submit'));
                } else {
                    submitQuestion(q);
                }
            }
        });
    });

    function getCurrentTime() {
        const now = new Date();
        return now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    }

    function escapeHtml(str) {
        return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
    }

    function formatMarkdown(text) {
        return text
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/`(.*?)`/g, '<code>$1</code>')
            .replace(/\n\n/g, '</p><p>')
            .replace(/\n/g, '<br/>');
    }

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
        w12Console.textContent = `[Executing Assistant Loop for Ticket ${payload.ticket_id}...]
Customer ID: ${payload.customer_id}
Query: "${payload.question}"

• Calling check_customer_entitlement...
• Calling fetch_order_details...
• Searching help center articles...`;
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

    // Direct hash navigation (e.g. #week12 or ?tab=week12)
    const initialTarget = (window.location.hash || '').replace('#', '') || new URLSearchParams(window.location.search).get('tab');
    if (initialTarget === 'week12' || initialTarget === 'dashboard') {
        switchView('week12');
    } else {
        switchView('chat');
    }
});
