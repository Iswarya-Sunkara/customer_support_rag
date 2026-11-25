with open('src/static/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Remove sidebarUserSection (from <!-- User Role Support Hub to <!-- 12 Golden Set)
sub_user_start = html.find('<!-- User Role Support Hub')
sub_user_end = html.find('<!-- 12 Golden Set Questions')
if sub_user_start != -1 and sub_user_end != -1:
    html = html[:sub_user_start] + html[sub_user_end:]
    print("1. Removed sidebarUserSection.")

# 2. Update Header: remove Eval Dashboard link, Switch Role button, and headerRoleBadge
old_header_block = """            <!-- Top Navigation Bar -->
            <header class="chat-header">
                <div class="header-info" style="display: flex; align-items: center; gap: 12px;">
                    <button class="icon-btn" id="btnToggleSidebar" title="Toggle Left Sidebar" style="padding: 6px 11px; background: rgba(31, 41, 55, 0.6); font-size: 0.9rem;">
                        <i class="fa-solid fa-bars"></i>
                    </button>
                    <div class="header-titles">
                        <h1 id="headerTitle" style="margin: 0; font-size: 1.15rem; white-space: nowrap;">Customer Support Assistant</h1>
                        <span class="header-role-indicator" id="headerRoleBadge"><i class="fa-solid fa-user"></i> User</span>
                    </div>
                    <!-- Top Navigation Tabs across Production App -->
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
            </header>"""

new_header_block = """            <!-- Top Navigation Bar -->
            <header class="chat-header">
                <div class="header-info" style="display: flex; align-items: center; gap: 14px;">
                    <button class="icon-btn" id="btnToggleSidebar" title="Toggle Left Sidebar" style="padding: 6px 11px; background: rgba(31, 41, 55, 0.6); font-size: 0.9rem;">
                        <i class="fa-solid fa-bars"></i>
                    </button>
                    <div class="header-titles">
                        <h1 id="headerTitle" style="margin: 0; font-size: 1.15rem; font-weight: 700; white-space: nowrap;">
                            <i class="fa-solid fa-shield-halved" style="color: #06B6D4; margin-right: 6px;"></i> Tier-1 Deflection Assistant
                        </h1>
                    </div>
                    <!-- Top Navigation Tabs across Production App -->
                    <div class="nav-tabs">
                        <button class="main-tab-btn active" id="tabBtnChat">
                            <i class="fa-solid fa-comments"></i> Support Assistant
                        </button>
                        <button class="main-tab-btn" id="tabBtnWeek12Header" style="border: 1px solid rgba(245, 158, 11, 0.5); background: rgba(245, 158, 11, 0.15); color: #F59E0B; font-weight: 600; display: inline-flex; align-items: center; gap: 6px;">
                            <i class="fa-solid fa-trophy" style="color: #F59E0B;"></i> Capstone Dashboard
                        </button>
                    </div>
                </div>

                <div class="header-right" style="display: flex; align-items: center; gap: 12px;">
                    <div class="header-actions">
                        <button class="icon-btn" id="btnClearChat" title="Clear Chat History">
                            <i class="fa-solid fa-arrows-rotate"></i> Reset Chat
                        </button>
                    </div>
                </div>
            </header>"""

assert old_header_block in html, "old_header_block not found"
html = html.replace(old_header_block, new_header_block)
print("2. Replaced header navigation without Eval Dashboard or Switch Role.")

# 3. Remove login-modal-overlay
modal_start = html.find('<!-- Login & Role Switcher Modal -->')
modal_end = html.find('<script src="/static/app.js')
assert modal_start != -1 and modal_end != -1, "modal landmarks not found"
html = html[:modal_start] + html[modal_end:]
print("3. Removed login modal overlay.")

# Bump version to v=70
html = html.replace("app.js?v=60", "app.js?v=70")
html = html.replace("styles.css?v=60", "styles.css?v=70")

with open('src/static/index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Saved clean index.html!")

