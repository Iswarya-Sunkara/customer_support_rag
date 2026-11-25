with open('src/static/app.js', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Remove role block from lines 35-137
role_start = text.find('    // --- Role-Based Access Control (User vs Admin) ---')
role_end = text.find('    // Connect User Topic buttons in sidebar')
assert role_start != -1 and role_end != -1, "role landmarks not found"

clean_header_init = """    // System Title
    const headerTitle = document.getElementById('headerTitle');
    const welcomeMessageContent = document.getElementById('welcomeMessageContent');
    if (welcomeMessageContent) {
        welcomeMessageContent.innerHTML = `
            <p>👋 Hello! Welcome to the <strong>DocuMind AI Tier-1 Support Assistant & Capstone Center</strong>.</p>
            <p>I am your autonomous support agent with grounded knowledge across billing, card decline errors, refund policies, and account security. You can <strong>upload your documents</strong> in the sidebar, click <strong>Suggested</strong> prompts below, or test <strong>12 Golden Benchmark Questions</strong>.</p>
        `;
    }
"""

text = text[:role_start] + clean_header_init + text[role_end:]
print("1. Removed role modal and RBAC logic from app.js.")

# 2. Improve suggested questions toggle & chips
old_suggest_block = """    // Suggested Questions Toggle & Click-to-Send Handlers
    const btnSuggestedQuestions = document.getElementById('btnSuggestedQuestions');
    const suggestedPanel = document.getElementById('suggestedPanel');
    const btnCloseSuggested = document.getElementById('btnCloseSuggested');

    if (btnSuggestedQuestions && suggestedPanel) {
        btnSuggestedQuestions.addEventListener('click', (e) => {
            e.preventDefault();
            const isHidden = suggestedPanel.style.display === 'none';
            suggestedPanel.style.display = isHidden ? 'flex' : 'none';
            btnSuggestedQuestions.classList.toggle('active', isHidden);
        });
    }

    if (btnCloseSuggested && suggestedPanel) {
        btnCloseSuggested.addEventListener('click', (e) => {
            e.preventDefault();
            suggestedPanel.style.display = 'none';
            if (btnSuggestedQuestions) btnSuggestedQuestions.classList.remove('active');
        });
    }

    document.querySelectorAll('.suggest-chip').forEach(chip => {
        chip.addEventListener('click', (e) => {
            e.preventDefault();
            const q = chip.getAttribute('data-q');
            if (q) {
                userInput.value = q;
                if (suggestedPanel) suggestedPanel.style.display = 'none';
                if (btnSuggestedQuestions) btnSuggestedQuestions.classList.remove('active');
                chatForm.dispatchEvent(new Event('submit'));
            }
        });
    });"""

new_suggest_block = """    // Suggested Questions Toggle & Floating Panel Handlers
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
                userInput.value = q;
                if (suggestedPanel) suggestedPanel.style.display = 'none';
                if (btnSuggestedQuestions) btnSuggestedQuestions.classList.remove('active');
                chatForm.dispatchEvent(new Event('submit'));
            }
        });
    });"""

assert old_suggest_block in text, "old_suggest_block not found"
text = text.replace(old_suggest_block, new_suggest_block)
print("2. Upgraded suggested questions toggle with outside-click detection.")

# 3. Clean up the startup block (remove role check)
old_startup = """    // Check Role state on startup
    if (!currentUserRole) {
        openLoginModal(false);
    } else {
        applyRole(currentUserRole, false);
    }

    // Direct hash navigation (e.g. #week12 or ?tab=week12)
    const initialTarget = (window.location.hash || '').replace('#', '') || new URLSearchParams(window.location.search).get('tab');
    if (initialTarget === 'week12' || initialTarget === 'dashboard') {
        switchView('week12');
    } else {
        switchView('chat');
    }"""

new_startup = """    // Direct hash navigation (e.g. #week12 or ?tab=week12)
    const initialTarget = (window.location.hash || '').replace('#', '') || new URLSearchParams(window.location.search).get('tab');
    if (initialTarget === 'week12' || initialTarget === 'dashboard') {
        switchView('week12');
    } else {
        switchView('chat');
    }"""

assert old_startup in text, "old_startup not found"
text = text.replace(old_startup, new_startup)
print("3. Removed role modal check on startup.")

with open('src/static/app.js', 'w', encoding='utf-8') as f:
    f.write(text)

print("Saved clean app.js!")

