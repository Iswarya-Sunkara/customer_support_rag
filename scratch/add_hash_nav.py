with open('src/static/app.js', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update switchView to update window.location.hash
old_switch_start = """    function switchView(target) {
        closeWeeksPopover();"""

new_switch_start = """    function switchView(target) {
        closeWeeksPopover();
        try {
            if (target && target !== 'chat') {
                history.replaceState(null, null, '#' + target);
            } else {
                history.replaceState(null, null, window.location.pathname);
            }
        } catch (_) {}"""

assert old_switch_start in content, "old_switch_start not found"
content = content.replace(old_switch_start, new_switch_start)

# 2. Add hash restore on load
old_role_check = """    // Role state check on startup
    if (!currentUserRole) {
        openLoginModal(false);
    } else {
        applyRole(currentUserRole, false);
    }"""

new_role_check = """    // Role state check on startup
    if (!currentUserRole) {
        openLoginModal(false);
    } else {
        applyRole(currentUserRole, false);
    }

    // Direct hash navigation (e.g. #week12 or ?tab=week12)
    const initialTarget = (window.location.hash || '').replace('#', '') || new URLSearchParams(window.location.search).get('tab');
    if (initialTarget && ['week3', 'week4', 'week5', 'week6', 'week7', 'week8', 'week9', 'week10', 'week12', 'langfuse'].includes(initialTarget)) {
        setTimeout(() => switchView(initialTarget), 80);
    }"""

assert old_role_check in content, "old_role_check not found"
content = content.replace(old_role_check, new_role_check)

with open('src/static/app.js', 'w', encoding='utf-8') as f:
    f.write(content)

print("Added hash navigation to app.js successfully!")

