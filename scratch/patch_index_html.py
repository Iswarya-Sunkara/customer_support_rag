with open('src/static/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update viewWeek12 tag
old_w12_tag = '<div class="view-container" id="viewWeek12" style="display: none;">'
new_w12_tag = '<div class="view-container" id="viewWeek12">'
assert old_w12_tag in content, "old_w12_tag not found"
content = content.replace(old_w12_tag, new_w12_tag)

# 2. Update buttons to btn-primary
old_btn_1a = """                            <button class="btn-race-run" id="btnRunWeek12Ticket1a" style="background: #D97706; border-color: #F59E0B;">
                                <i class="fa-solid fa-play"></i> Run Live Ticket 1a (30-Day Refund)
                            </button>
                            <button class="btn-race-run" id="btnRunWeek12Ticket1b" style="background: #B45309; border-color: #D97706;">
                                <i class="fa-solid fa-shield-halved"></i> Run Escalation Ticket 1b (Dispute)
                            </button>"""

new_btn_1a = """                            <button class="btn-primary" id="btnRunWeek12Ticket1a" style="background: linear-gradient(135deg, #D97706, #B45309); border: 1px solid #F59E0B; padding: 9px 18px; border-radius: 8px; font-weight: 600; cursor: pointer; display: inline-flex; align-items: center; gap: 8px; color: #FFFFFF;">
                                <i class="fa-solid fa-play"></i> Run Live Ticket 1a (30-Day Refund)
                            </button>
                            <button class="btn-primary" id="btnRunWeek12Ticket1b" style="background: linear-gradient(135deg, #B45309, #92400E); border: 1px solid #D97706; padding: 9px 18px; border-radius: 8px; font-weight: 600; cursor: pointer; display: inline-flex; align-items: center; gap: 8px; color: #FFFFFF;">
                                <i class="fa-solid fa-shield-halved"></i> Run Escalation Ticket 1b (Dispute)
                            </button>"""

assert old_btn_1a in content, "old_btn_1a not found"
content = content.replace(old_btn_1a, new_btn_1a)

# 3. Update cache busters
old_script = '<script src="/static/app.js?v=20"></script>'
new_script = '<script src="/static/app.js?v=30"></script>'
assert old_script in content, "old_script not found"
content = content.replace(old_script, new_script)

old_css = '<link rel="stylesheet" href="/static/styles.css?v=17">'
new_css = '<link rel="stylesheet" href="/static/styles.css?v=30">'
assert old_css in content, "old_css not found"
content = content.replace(old_css, new_css)

with open('src/static/index.html', 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated src/static/index.html successfully!")

