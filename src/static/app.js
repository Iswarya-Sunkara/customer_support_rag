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

    const btnModeWeek3 = document.getElementById('btnModeWeek3');
    const btnModeWeek4 = document.getElementById('btnModeWeek4');

    const chatMessages = document.getElementById('chatMessages');
    const chatForm = document.getElementById('chatForm');
    const userInput = document.getElementById('userInput');
    const typingIndicator = document.getElementById('typingIndicator');
    const btnClearChat = document.getElementById('btnClearChat');

    // 1. Filter Switch Event Listeners (Week 3 vs Week 4)
    btnModeWeek3.addEventListener('click', () => {
        currentMode = 'week3';
        btnModeWeek3.classList.add('active');
        btnModeWeek4.classList.remove('active');
        appendAssistantMessage('⚠️ **Switched Filter to Week 3 (Dense Vector Search Baseline)**.\nHard error code & exact token questions (Q01, Q02, Q03, Q04, Q09) will now return baseline refusal (*"I don\'t have enough information..."*).');
    });

    btnModeWeek4.addEventListener('click', () => {
        currentMode = 'week4';
        btnModeWeek4.classList.add('active');
        btnModeWeek3.classList.remove('active');
        appendAssistantMessage('🚀 **Switched Filter to Week 4 (Hybrid RAG BM25 + RRF System)**.\nBM25 + RRF reranking is enabled! Error code & token questions (Q01-Q11) will now retrieve exact answers with citations.');
    });

    // 2. Drag & Drop Upload Event Listeners
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
        if (files.length > 0) {
            handleFileUpload(files);
        }
    });

    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleFileUpload(e.target.files);
        }
    });

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
                userInput.value = questionText;
                submitQuestion(questionText);
            }
        }
    });

    // 6. Clear Knowledge Base Button
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

    // 7. Quick Prompts Click Listener
    document.addEventListener('click', (e) => {
        const chip = e.target.closest('.prompt-chip');
        if (chip) {
            const promptText = chip.getAttribute('data-prompt');
            if (promptText) {
                userInput.value = promptText;
                submitQuestion(promptText);
            }
        }
    });

    // 8. Submit Question Handler
    chatForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const query = userInput.value.trim();
        if (!query) return;
        submitQuestion(query);
    });

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
    btnClearChat.addEventListener('click', () => {
        chatMessages.innerHTML = '';
        appendAssistantMessage('👋 Chat history reset! Select any of the 12 Golden Set Questions or upload a document to begin.');
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

    // Initial Load
    fetchDocumentsList();
    fetchGoldenSet();
});
