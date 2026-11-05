"""
Enhance Week 12 Capstone UI with top-level navigation tab, KPI cards, and cache-busting.
"""

from pathlib import Path

root = Path(__file__).resolve().parent.parent
index_path = root / "src" / "static" / "index.html"
app_path = root / "src" / "static" / "app.js"

html = index_path.read_text(encoding="utf-8")

# 1. Add top header button if not present
header_needle = '''                        <button class="main-tab-btn active" id="tabBtnChat">
                            <i class="fa-solid fa-comments"></i> Chatbot
                        </button>'''

header_repl = '''                        <button class="main-tab-btn active" id="tabBtnChat">
                            <i class="fa-solid fa-comments"></i> Chatbot
                        </button>
                        <button class="main-tab-btn" id="tabBtnWeek12Header" style="border: 1px solid rgba(245, 158, 11, 0.4); background: rgba(245, 158, 11, 0.12); color: #F59E0B; font-weight: 600; display: inline-flex; align-items: center; gap: 6px;">
                            <i class="fa-solid fa-trophy" style="color: #F59E0B;"></i> Week 12 Capstone
                        </button>'''

if 'id="tabBtnWeek12Header"' not in html and header_needle in html:
    html = html.replace(header_needle, header_repl, 1)
    print("Added tabBtnWeek12Header to top navigation bar")

# 2. Add KPI grid to viewWeek12 if not already present
kpi_grid_html = '''
                    <!-- SECTION 1: Week 12 Core KPI Metric Cards -->
                    <div class="w7-kpi-grid">
                        <div class="w7-kpi-card" style="border-color: rgba(16, 185, 129, 0.4); background: rgba(16, 185, 129, 0.05);">
                            <div class="w7-kpi-label"><i class="fa-solid fa-ban" style="color: #10B981;"></i> 1. Superseded Policy Citation</div>
                            <div class="w7-kpi-val" style="color: #34D399;">20% &rarr; 0.0%</div>
                            <div class="w7-kpi-sub" style="color: #A7F3D0;">Eliminated CEO escalation root cause (n=26)</div>
                        </div>
                        <div class="w7-kpi-card" style="border-color: rgba(99, 102, 241, 0.4); background: rgba(99, 102, 241, 0.05);">
                            <div class="w7-kpi-label"><i class="fa-solid fa-route" style="color: #6366F1;"></i> 2. Outcome-vs-Trajectory Gap</div>
                            <div class="w7-kpi-val" style="color: #818CF8;">30% &rarr; 0.0%</div>
                            <div class="w7-kpi-sub" style="color: #C7D2FE;">Eliminated silent order bypass on TCK-101</div>
                        </div>
                        <div class="w7-kpi-card" style="border-color: rgba(56, 189, 248, 0.4); background: rgba(56, 189, 248, 0.05);">
                            <div class="w7-kpi-label"><i class="fa-solid fa-scale-balanced" style="color: #38BDF8;"></i> 3. LLM Judge Agreement</div>
                            <div class="w7-kpi-val" style="color: #38BDF8;">92.0% (&kappa; = 0.84)</div>
                            <div class="w7-kpi-sub" style="color: #BAE6FD;">Held-out 91.3% vs blind human labels</div>
                        </div>
                        <div class="w7-kpi-card" style="border-color: rgba(245, 158, 11, 0.4); background: rgba(245, 158, 11, 0.05);">
                            <div class="w7-kpi-label"><i class="fa-solid fa-coins" style="color: #F59E0B;"></i> 4. Cost per Deflected Ticket</div>
                            <div class="w7-kpi-val" style="color: #FBBF24;">$0.0004666</div>
                            <div class="w7-kpi-sub" style="color: #FDE68A;">99.997% cheaper than human Tier-1 rep ($14)</div>
                        </div>
                    </div>
'''

w12_header_card_needle = 'Track A: Customer Support Tickets · Tier-1 Deflection Assistant · Gate M6 Passed\n                            </p>\n                        </div>'
if w12_header_card_needle not in html:
    w12_header_card_needle = 'Track A: Customer Support Tickets · Tier-1 Deflection Assistant · Gate M6 Passed\r\n                            </p>\r\n                        </div>'

w12_header_end_needle = '</div>\n                    </div>\n\n                    <!-- Capstone Overview & Executive Context -->'
if w12_header_end_needle not in html:
    w12_header_end_needle = '</div>\r\n                    </div>\r\n\r\n                    <!-- Capstone Overview & Executive Context -->'

if 'class="w7-kpi-grid"' not in html[html.find('id="viewWeek12"'):]:
    if w12_header_end_needle in html:
        html = html.replace(w12_header_end_needle, '</div>\n                    </div>\n' + kpi_grid_html + '\n                    <!-- Capstone Overview & Executive Context -->', 1)
        print("Added KPI grid to viewWeek12")

# Cache-bust script tag
html = html.replace('src="/static/app.js?v=18"', 'src="/static/app.js?v=20"')
html = html.replace('src="/static/app.js?v=19"', 'src="/static/app.js?v=20"')

index_path.write_text(html, encoding="utf-8")
print("Updated index.html successfully!")

# Update app.js to wire tabBtnWeek12Header
js = app_path.read_text(encoding="utf-8")

if 'tabBtnWeek12Header' not in js:
    # Add declaration
    js = js.replace(
        "const tabBtnWeek12 = document.getElementById('tabBtnWeek12');",
        "const tabBtnWeek12 = document.getElementById('tabBtnWeek12');\n    const tabBtnWeek12Header = document.getElementById('tabBtnWeek12Header');"
    )
    # Add click event
    click_code = """
    if (tabBtnWeek12Header) {
        tabBtnWeek12Header.addEventListener('click', () => switchView('week12'));
    }
"""
    # Allow switchView to open week12 even if role is user!
    js = js.replace(
        "if (currentUserRole === 'user' && target !== 'chat') {",
        "if (currentUserRole === 'user' && target !== 'chat' && target !== 'week12') {"
    )
    js = js.replace(
        "if (tabBtnWeek12) tabBtnWeek12.classList.add('active');",
        "if (tabBtnWeek12) tabBtnWeek12.classList.add('active');\n                if (tabBtnWeek12Header) tabBtnWeek12Header.classList.add('active');"
    )
    idx = js.rfind("});")
    if idx != -1:
        js = js[:idx] + click_code + "\n" + js[idx:]
    app_path.write_text(js, encoding="utf-8")
    print("Updated app.js with tabBtnWeek12Header handling!")

