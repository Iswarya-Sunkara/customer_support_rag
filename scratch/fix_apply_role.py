with open('src/static/app.js', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. In applyRole, remove the unconditional switchView('chat')
old_apply_user = """            // User mode enforces clean chatbot view and week4 hybrid retrieval
            currentMode = 'week4';
            switchView('chat');
        } else {"""

new_apply_user = """            // User mode enforces clean chatbot view and week4 hybrid retrieval
            currentMode = 'week4';
        } else {"""

assert old_apply_user in text, "old_apply_user not found"
text = text.replace(old_apply_user, new_apply_user)

# 2. At bottom, call switchView synchronously
old_nav_block = """    // Direct hash navigation (e.g. #week12 or ?tab=week12)
    const initialTarget = (window.location.hash || '').replace('#', '') || new URLSearchParams(window.location.search).get('tab');
    if (initialTarget === 'week12' || initialTarget === 'dashboard') {
        setTimeout(() => switchView('week12'), 80);
    } else {
        switchView('chat');
    }"""

new_nav_block = """    // Direct hash navigation (e.g. #week12 or ?tab=week12)
    const initialTarget = (window.location.hash || '').replace('#', '') || new URLSearchParams(window.location.search).get('tab');
    if (initialTarget === 'week12' || initialTarget === 'dashboard') {
        switchView('week12');
    } else {
        switchView('chat');
    }"""

assert old_nav_block in text, "old_nav_block not found"
text = text.replace(old_nav_block, new_nav_block)

with open('src/static/app.js', 'w', encoding='utf-8') as f:
    f.write(text)

print("Updated applyRole and switchView in app.js!")

