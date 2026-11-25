with open('src/static/app.js', 'r', encoding='utf-8') as f:
    text = f.read()

old_admin_msg = """            if (welcomeMessageContent) {
                welcomeMessageContent.innerHTML = `
                    <p>👋 Hello Administrator! Welcome to the <strong>DocuMind AI Admin Control Center</strong>.</p>
                    <p>You have full access to upload any documents without restriction, run benchmark tests across <strong>Weeks 3–10</strong>, evaluate trajectories, and test the <strong>MCP Gateway & RBAC audit logs</strong>.</p>
                    <p style="margin-top: 8px; font-size: 0.85rem; color: #9CA3AF;">
                        📌 <em>Use the <strong>Curriculum Modules</strong> popover above or the sidebar buttons to switch between Dense Baseline, Hybrid RAG, Error Taxonomy, LLM Judge, Race & Budgets, Trajectory Evals, MCP Tools, and <strong>Week 10: Multi-Agent Race</strong>.</em>
                    </p>
                `;
            }"""

new_admin_msg = """            if (welcomeMessageContent) {
                welcomeMessageContent.innerHTML = `
                    <p>👋 Hello Administrator! Welcome to the <strong>Tier-1 Deflection Assistant & Capstone Command Center</strong>.</p>
                    <p>You have full access to test customer tickets, upload documents, inspect <strong>Gate M6 Production Evals</strong>, and execute live multi-span MCP calls with trace telemetry.</p>
                    <p style="margin-top: 8px; font-size: 0.85rem; color: #9CA3AF;">
                        📌 <em>Use the <strong>Capstone & Production Dashboard</strong> tab above or the sidebar buttons to inspect KPI cards, the 4 numbers that moved, re-scored error taxonomy, and 10x Black Friday scaling plans.</em>
                    </p>
                `;
            }"""

assert old_admin_msg in text, "old_admin_msg not found"
text = text.replace(old_admin_msg, new_admin_msg)

with open('src/static/app.js', 'w', encoding='utf-8') as f:
    f.write(text)

print("Updated welcome message in app.js!")

