with open('src/static/app.js', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update WEEK_META to include week12
old_meta = """    const WEEK_META = {
        week3: { short: 'W3: Baseline', icon: 'fa-chart-line', color: '#F59E0B' },
        week4: { short: 'W4: Hybrid', icon: 'fa-bolt', color: '#06B6D4' },
        week5: { short: 'W5: Taxonomy', icon: 'fa-list-check', color: '#A78BFA' },
        week6: { short: 'W6: LLM Judge', icon: 'fa-scale-balanced', color: '#38BDF8' },
        week7: { short: 'W7: Race & Budgets', icon: 'fa-code-compare', color: '#EC4899' },
        week8: { short: 'W8: Trajectory', icon: 'fa-route', color: '#6366F1' },
        week9: { short: 'W9: MCP & Tools', icon: 'fa-network-wired', color: '#A855F7' },
        week10: { short: 'W10: Multi-Agent Race', icon: 'fa-users-gear', color: '#F97316' },
        langfuse: { short: 'Langfuse', icon: 'fa-satellite-dish', color: '#10B981' }
    };"""

new_meta = """    const WEEK_META = {
        week3: { short: 'W3: Baseline', icon: 'fa-chart-line', color: '#F59E0B' },
        week4: { short: 'W4: Hybrid', icon: 'fa-bolt', color: '#06B6D4' },
        week5: { short: 'W5: Taxonomy', icon: 'fa-list-check', color: '#A78BFA' },
        week6: { short: 'W6: LLM Judge', icon: 'fa-scale-balanced', color: '#38BDF8' },
        week7: { short: 'W7: Race & Budgets', icon: 'fa-code-compare', color: '#EC4899' },
        week8: { short: 'W8: Trajectory', icon: 'fa-route', color: '#6366F1' },
        week9: { short: 'W9: MCP & Tools', icon: 'fa-network-wired', color: '#A855F7' },
        week10: { short: 'W10: Multi-Agent Race', icon: 'fa-users-gear', color: '#F97316' },
        week12: { short: 'W12: Capstone', icon: 'fa-trophy', color: '#F59E0B' },
        langfuse: { short: 'Langfuse', icon: 'fa-satellite-dish', color: '#10B981' }
    };"""

assert old_meta in content, "old_meta not found"
content = content.replace(old_meta, new_meta)

# 2. Update declarations & allTabBtns
old_decls = """    const viewWeek8 = document.getElementById('viewWeek8');
    const viewWeek9 = document.getElementById('viewWeek9');
    const viewWeek10 = document.getElementById('viewWeek10');
    const viewWeek12 = document.getElementById('viewWeek12');
    const tabBtnWeek12 = document.getElementById('tabBtnWeek12');
    const tabBtnWeek12Header = document.getElementById('tabBtnWeek12Header');
    const sidebarWeek12Btn = document.getElementById('sidebarWeek12Btn');
    const viewLangfuse = document.getElementById('viewLangfuse');

    const sidebarWeek3Btn = document.getElementById('sidebarWeek3Btn');
    const sidebarWeek4Btn = document.getElementById('sidebarWeek4Btn');
    const sidebarWeek5Btn = document.getElementById('sidebarWeek5Btn');
    const sidebarWeek6Btn = document.getElementById('sidebarWeek6Btn');
    const sidebarWeek7Btn = document.getElementById('sidebarWeek7Btn');
    const sidebarWeek8Btn = document.getElementById('sidebarWeek8Btn');
    const sidebarWeek9Btn = document.getElementById('sidebarWeek9Btn');
    const sidebarWeek10Btn = document.getElementById('sidebarWeek10Btn');
    const sidebarLangfuseBtn = document.getElementById('sidebarLangfuseBtn');
    const btnReloadWeek6Frame = document.getElementById('btnReloadWeek6Frame');
    const week6Iframe = document.getElementById('week6Iframe');

    const filterSwitchContainer = document.getElementById('filterSwitchContainer');

    const allTabBtns = [tabBtnChat, tabBtnWeek3, tabBtnWeek4, tabBtnWeek5, tabBtnWeek6, tabBtnWeek7, tabBtnWeek8, tabBtnWeek9, tabBtnWeek10, tabBtnWeek12, tabBtnLangfuse].filter(Boolean);
    const allViews = [viewChat, viewWeek3, viewWeek4, viewWeek5, viewWeek6, viewWeek7, viewWeek8, viewWeek9, viewWeek10, viewWeek12, viewLangfuse].filter(Boolean);"""

new_decls = """    const viewWeek8 = document.getElementById('viewWeek8');
    const viewWeek9 = document.getElementById('viewWeek9');
    const viewWeek10 = document.getElementById('viewWeek10');
    const viewWeek12 = document.getElementById('viewWeek12');
    const tabBtnWeek12 = document.getElementById('tabBtnWeek12');
    const tabBtnWeek12Header = document.getElementById('tabBtnWeek12Header');
    const sidebarWeek12Btn = document.getElementById('sidebarWeek12Btn');
    const btnRunWeek12Ticket1a = document.getElementById('btnRunWeek12Ticket1a');
    const btnRunWeek12Ticket1b = document.getElementById('btnRunWeek12Ticket1b');
    const w12Console = document.getElementById('w12LiveOutputConsole');
    const viewLangfuse = document.getElementById('viewLangfuse');

    const sidebarWeek3Btn = document.getElementById('sidebarWeek3Btn');
    const sidebarWeek4Btn = document.getElementById('sidebarWeek4Btn');
    const sidebarWeek5Btn = document.getElementById('sidebarWeek5Btn');
    const sidebarWeek6Btn = document.getElementById('sidebarWeek6Btn');
    const sidebarWeek7Btn = document.getElementById('sidebarWeek7Btn');
    const sidebarWeek8Btn = document.getElementById('sidebarWeek8Btn');
    const sidebarWeek9Btn = document.getElementById('sidebarWeek9Btn');
    const sidebarWeek10Btn = document.getElementById('sidebarWeek10Btn');
    const sidebarLangfuseBtn = document.getElementById('sidebarLangfuseBtn');
    const btnReloadWeek6Frame = document.getElementById('btnReloadWeek6Frame');
    const week6Iframe = document.getElementById('week6Iframe');

    const filterSwitchContainer = document.getElementById('filterSwitchContainer');

    const allTabBtns = [tabBtnChat, tabBtnWeek3, tabBtnWeek4, tabBtnWeek5, tabBtnWeek6, tabBtnWeek7, tabBtnWeek8, tabBtnWeek9, tabBtnWeek10, tabBtnWeek12, tabBtnWeek12Header, sidebarWeek12Btn, tabBtnLangfuse].filter(Boolean);
    const allViews = [viewChat, viewWeek3, viewWeek4, viewWeek5, viewWeek6, viewWeek7, viewWeek8, viewWeek9, viewWeek10, viewWeek12, viewLangfuse].filter(Boolean);"""

assert old_decls in content, "old_decls not found"
content = content.replace(old_decls, new_decls)

# 3. Ensure target === 'week12' in switchView
old_w12_switch = """            } else if (target === 'week12') {
                if (tabBtnWeek12) tabBtnWeek12.classList.add('active');
                if (tabBtnWeek12Header) tabBtnWeek12Header.classList.add('active');
                if (viewWeek12) {
                    viewWeek12.classList.add('active');
                    viewWeek12.style.display = 'flex';
                }
                fetchWeek12Summary();
            }"""

new_w12_switch = """            } else if (target === 'week12') {
                if (tabBtnWeek12) tabBtnWeek12.classList.add('active');
                if (tabBtnWeek12Header) tabBtnWeek12Header.classList.add('active');
                if (sidebarWeek12Btn) sidebarWeek12Btn.classList.add('active');
                if (viewWeek12) {
                    viewWeek12.classList.add('active');
                    viewWeek12.style.display = 'flex';
                }
                fetchWeek12Summary();
            }"""

assert old_w12_switch in content, "old_w12_switch not found"
content = content.replace(old_w12_switch, new_w12_switch)

# 4. Attach event listeners
old_listeners = """    if (sidebarWeek10Btn) sidebarWeek10Btn.addEventListener('click', () => switchView('week10'));
    if (sidebarLangfuseBtn) sidebarLangfuseBtn.addEventListener('click', () => switchView('langfuse'));"""

new_listeners = """    if (sidebarWeek10Btn) sidebarWeek10Btn.addEventListener('click', () => switchView('week10'));
    if (sidebarWeek12Btn) sidebarWeek12Btn.addEventListener('click', () => switchView('week12'));
    if (tabBtnWeek12Header) tabBtnWeek12Header.addEventListener('click', () => switchView('week12'));
    if (sidebarLangfuseBtn) sidebarLangfuseBtn.addEventListener('click', () => switchView('langfuse'));"""

assert old_listeners in content, "old_listeners not found"
content = content.replace(old_listeners, new_listeners)

# Clean up duplicate listeners at the bottom
dup_part = """    if (sidebarWeek12Btn) {
        sidebarWeek12Btn.addEventListener('click', () => switchView('week12'));
    }

    const btnRunWeek12Ticket1a = document.getElementById('btnRunWeek12Ticket1a');
    const btnRunWeek12Ticket1b = document.getElementById('btnRunWeek12Ticket1b');
    const w12Console = document.getElementById('w12LiveOutputConsole');"""

clean_part = """    // Week 12 handlers declared above"""

if dup_part in content:
    content = content.replace(dup_part, clean_part)

with open('src/static/app.js', 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated src/static/app.js successfully!")

