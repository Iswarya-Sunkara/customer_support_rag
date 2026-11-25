with open('src/static/styles.css', 'r', encoding='utf-8') as f:
    css = f.read()

# 1. Update .chat-footer
old_chat_footer = """.chat-footer {
    padding: 16px 24px;
    background: rgba(17, 24, 39, 0.6);
    border-top: 1px solid var(--border-color);
}"""

new_chat_footer = """.chat-footer {
    padding: 16px 24px;
    background: rgba(17, 24, 39, 0.6);
    border-top: 1px solid var(--border-color);
    position: relative;
    z-index: 50;
}"""

assert old_chat_footer in css, "old_chat_footer not found"
css = css.replace(old_chat_footer, new_chat_footer)

# 2. Update .suggested-panel to be firmly anchored above footer
old_suggested_panel = """.suggested-panel {
    background: rgba(15, 23, 42, 0.96);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border: 1px solid rgba(245, 158, 11, 0.35);
    border-radius: 14px;
    padding: 14px 16px;
    margin-bottom: 12px;
    box-shadow: 0 16px 36px -6px rgba(0, 0, 0, 0.8), 0 0 20px rgba(245, 158, 11, 0.15);
    display: flex;
    flex-direction: column;
    gap: 12px;
    animation: fadeInSlideUp 0.25s ease-out;
}"""

new_suggested_panel = """.suggested-panel {
    position: absolute;
    bottom: calc(100% + 10px);
    left: 24px;
    right: 24px;
    max-height: 420px;
    overflow-y: auto;
    z-index: 1000;
    background: rgba(15, 23, 42, 0.98);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border: 1px solid rgba(245, 158, 11, 0.45);
    border-radius: 14px;
    padding: 16px 18px;
    box-shadow: 0 16px 36px -6px rgba(0, 0, 0, 0.9), 0 0 24px rgba(245, 158, 11, 0.2);
    display: flex;
    flex-direction: column;
    gap: 12px;
    animation: fadeInSlideUp 0.2s ease-out;
}"""

assert old_suggested_panel in css, "old_suggested_panel not found"
css = css.replace(old_suggested_panel, new_suggested_panel)

# 3. Clean role-user hiding rules
old_role_rules = """/* User Role: Strictly hide all week-wise curriculum modules, golden benchmarks & evaluation switches */
body.role-user #sidebarGoldenSection,
body.role-user #sidebarCurriculumSection,
body.role-user #weeksPopoverWrapper,
body.role-user #filterSwitchContainer,
body.role-user #btnFullscreenEval {
    display: none !important;
}

body.role-user #sidebarUserSection {
    display: flex !important;
}

body.role-admin #sidebarUserSection {
    display: none !important;
}"""

if old_role_rules in css:
    css = css.replace(old_role_rules, "/* Clean Capstone Layout: No role restrictions */")

with open('src/static/styles.css', 'w', encoding='utf-8') as f:
    f.write(css)

print("Updated src/static/styles.css!")

