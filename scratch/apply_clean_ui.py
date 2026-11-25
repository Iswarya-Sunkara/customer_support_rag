import re

with open('src/static/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Replace sidebarCurriculumSection (lines 145-191) with clean app navigation
old_sidebar_section = """            <!-- Master Curriculum Navigator (Weeks 3-9) in Sidebar (Admin Only) -->
            <div class="sidebar-shortcut-section" id="sidebarCurriculumSection">
                <div class="sidebar-shortcut-header">
                    <i class="fa-solid fa-graduation-cap"></i> Curriculum (Weeks 3–9)
                </div>
                <div style="display: flex; flex-direction: column; gap: 6px; margin-top: 4px;">
                    <button class="btn-sidebar-view" id="sidebarWeek3Btn"
                        style="text-align: left; display: flex; align-items: center; gap: 8px;">
                        <i class="fa-solid fa-chart-line" style="color: #F59E0B;"></i> Week 3: Dense Baseline
                    </button>
                    <button class="btn-sidebar-view" id="sidebarWeek4Btn"
                        style="text-align: left; display: flex; align-items: center; gap: 8px;">
                        <i class="fa-solid fa-bolt" style="color: #06B6D4;"></i> Week 4: Hybrid RAG
                    </button>
                    <button class="btn-sidebar-view" id="sidebarWeek5Btn"
                        style="text-align: left; display: flex; align-items: center; gap: 8px;">
                        <i class="fa-solid fa-list-check" style="color: #A78BFA;"></i> Week 5: Error Taxonomy
                    </button>
                    <button class="btn-sidebar-view" id="sidebarWeek6Btn"
                        style="text-align: left; display: flex; align-items: center; gap: 8px;">
                        <i class="fa-solid fa-scale-balanced" style="color: #38BDF8;"></i> Week 6: LLM-as-a-Judge
                    </button>
                    <button class="btn-sidebar-view" id="sidebarWeek7Btn"
                        style="text-align: left; display: flex; align-items: center; gap: 8px; color: #F472B6; border-color: rgba(236,72,153,0.3); background: rgba(236,72,153,0.1);">
                        <i class="fa-solid fa-code-compare" style="color: #EC4899;"></i> Week 7: Agent vs Workflow
                    </button>
                    <button class="btn-sidebar-view" id="sidebarWeek8Btn"
                        style="text-align: left; display: flex; align-items: center; gap: 8px; color: #818CF8; border-color: rgba(99,102,241,0.3); background: rgba(99,102,241,0.1);">
                        <i class="fa-solid fa-route" style="color: #6366F1;"></i> Week 8: Trajectory Evals
                    </button>
                    <button class="btn-sidebar-view" id="sidebarWeek9Btn"
                        style="text-align: left; display: flex; align-items: center; gap: 8px; color: #C084FC; border-color: rgba(168,85,247,0.3); background: rgba(168,85,247,0.1);">
                        <i class="fa-solid fa-network-wired" style="color: #A855F7;"></i> Week 9: MCP & Tools
                    </button>
                    <button class="btn-sidebar-view" id="sidebarWeek12Btn"
                        style="text-align: left; display: flex; align-items: center; gap: 8px; color: #F59E0B; border-color: rgba(245,158,11,0.5); background: rgba(245,158,11,0.18); font-weight: 600;">
                        <i class="fa-solid fa-trophy" style="color: #F59E0B;"></i> Week 12: Capstone
                    </button>
                    <button class="btn-sidebar-view" id="sidebarWeek10Btn"
                        style="text-align: left; display: flex; align-items: center; gap: 8px; color: #FB923C; border-color: rgba(249,115,22,0.3); background: rgba(249,115,22,0.1);">
                        <i class="fa-solid fa-users-gear" style="color: #F97316;"></i> Week 10: Multi-Agent Race
                    </button>
                    <button class="btn-sidebar-view" id="sidebarLangfuseBtn"
                        style="text-align: left; display: flex; align-items: center; gap: 8px; color: #10B981; border-color: rgba(160,185,129,0.3); background: rgba(16,185,129,0.1);">
                        <i class="fa-solid fa-satellite-dish"></i> Langfuse Telemetry
                    </button>
                </div>
            </div>"""

new_sidebar_section = """            <!-- Production App Navigation -->
            <div class="sidebar-shortcut-section" id="sidebarNavSection">
                <div class="sidebar-shortcut-header">
                    <i class="fa-solid fa-compass"></i> App Navigation
                </div>
                <div style="display: flex; flex-direction: column; gap: 8px; margin-top: 6px;">
                    <button class="btn-sidebar-view active" id="sidebarChatBtn"
                        style="text-align: left; display: flex; align-items: center; gap: 10px; font-weight: 600;">
                        <i class="fa-solid fa-headset" style="color: #06B6D4;"></i> Tier-1 Support Assistant
                    </button>
                    <button class="btn-sidebar-view" id="sidebarWeek12Btn"
                        style="text-align: left; display: flex; align-items: center; gap: 10px; color: #F59E0B; border-color: rgba(245,158,11,0.5); background: rgba(245,158,11,0.15); font-weight: 600;">
                        <i class="fa-solid fa-trophy" style="color: #F59E0B;"></i> Capstone Command Center
                    </button>
                    <button class="btn-sidebar-view" id="sidebarRunTicket1aBtn"
                        style="text-align: left; display: flex; align-items: center; gap: 10px; color: #34D399; border-color: rgba(16,185,129,0.3); background: rgba(16,185,129,0.1); font-size: 0.82rem;">
                        <i class="fa-solid fa-play" style="color: #10B981;"></i> Demo 1a: 30-Day Refund
                    </button>
                    <button class="btn-sidebar-view" id="sidebarRunTicket1bBtn"
                        style="text-align: left; display: flex; align-items: center; gap: 10px; color: #F87171; border-color: rgba(239,68,68,0.3); background: rgba(239,68,68,0.1); font-size: 0.82rem;">
                        <i class="fa-solid fa-shield-halved" style="color: #EF4444;"></i> Demo 1b: Fraud Escalation
                    </button>
                </div>
            </div>"""

assert old_sidebar_section in html, "old_sidebar_section not found"
html = html.replace(old_sidebar_section, new_sidebar_section)
print("1. Replaced sidebar curriculum section.")

# 2. Clean up header: replace nav-tabs and remove weeksPopoverWrapper + filterSwitchContainer
# Find from <div class="nav-tabs"> to </header>
header_start = html.find('<!-- Top Navigation Tabs across All Weeks -->')
header_end = html.find('<!-- VIEW 1: Universal Document Chatbot Feed -->')
assert header_start != -1 and header_end != -1, "header landmarks not found"

new_header_snippet = """<!-- Top Navigation Tabs across Production App -->
                    <div class="nav-tabs">
                        <button class="main-tab-btn active" id="tabBtnChat">
                            <i class="fa-solid fa-comments"></i> Tier-1 Assistant
                        </button>
                        <button class="main-tab-btn" id="tabBtnWeek12Header" style="border: 1px solid rgba(245, 158, 11, 0.5); background: rgba(245, 158, 11, 0.15); color: #F59E0B; font-weight: 600; display: inline-flex; align-items: center; gap: 6px;">
                            <i class="fa-solid fa-trophy" style="color: #F59E0B;"></i> Capstone & Production Dashboard
                        </button>
                    </div>
                </div>

                <div class="header-right" style="display: flex; align-items: center; gap: 12px;">
                    <a href="/dashboard" target="_blank" class="btn-tool" id="btnFullscreenEval" title="Open Eval Dashboard in new tab">
                        <i class="fa-solid fa-chart-pie"></i> Eval Dashboard
                    </a>

                    <!-- Role Switcher Trigger Button -->
                    <div class="role-switcher-container" id="roleSwitcherContainer">
                        <button type="button" class="btn-role-switch" id="btnSwitchRole" title="Switch between Customer and Admin role">
                            <i class="fa-solid fa-user-gear"></i>
                            <span id="roleButtonLabel">Switch Role</span>
                        </button>
                    </div>

                    <div class="header-actions">
                        <button class="icon-btn" id="btnClearChat" title="Clear Chat History">
                            <i class="fa-solid fa-arrows-rotate"></i> Reset Chat
                        </button>
                    </div>
                </div>
            </header>

            """

html = html[:header_start] + new_header_snippet + html[header_end:]
print("2. Replaced header navigation and removed weeks popover.")

# 3. Remove viewWeek3 through viewWeek10
# Find viewChat closing tag: </div>\n\n            <!-- VIEW 2: Week 3 Dense Baseline
vw3_marker = html.find('<!-- VIEW 2: Week 3 Dense Baseline')
vw12_marker = html.find('<!-- Week 12: Production & Capstone — Tier-1 Deflection Assistant     -->')
assert vw3_marker != -1 and vw12_marker != -1, "view landmarks not found"

# We want to keep everything up to vw3_marker, and everything from vw12_marker onwards
html = html[:vw3_marker] + html[vw12_marker:]
print("3. Removed viewWeek3 through viewWeek10.")

# Bump version to v=50
html = html.replace("app.js?v=40", "app.js?v=50")
html = html.replace("styles.css?v=40", "styles.css?v=50")

with open('src/static/index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Saved clean index.html!")

