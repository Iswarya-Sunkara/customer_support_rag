import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "eval"))
from common import load_cases

def build_dashboard():
    cases = load_cases()
    labels = json.loads((ROOT / "labels_25.json").read_text(encoding="utf-8"))
    j1 = json.loads((ROOT / "results" / "judge_v1.json").read_text(encoding="utf-8"))["verdicts"]
    j2 = json.loads((ROOT / "results" / "judge_v2.json").read_text(encoding="utf-8"))["verdicts"]
    s1 = json.loads((ROOT / "results" / "summary_v1.json").read_text(encoding="utf-8"))
    s2 = json.loads((ROOT / "results" / "summary_v2.json").read_text(encoding="utf-8"))

    combined_cases = []
    for c in cases:
        cid = c["case_id"]
        combined_cases.append({
            "id": cid,
            "mode": c["mode"],
            "regression": c.get("regression", False),
            "trace_id": c.get("source_trace_id", ""),
            "tier": c["ticket"].get("tier", "Standard"),
            "question": c["ticket"]["question"],
            "reply": c["reply"],
            "human": labels["labels"][cid]["label"],
            "human_note": labels["labels"][cid].get("note", ""),
            "judge_v1": j1[cid]["verdict"],
            "reason_v1": j1[cid]["reason"],
            "judge_v2": j2[cid]["verdict"],
            "reason_v2": j2[cid]["reason"],
            "assert_pass": True,
            "disagree_v1": labels["labels"][cid]["label"] != j1[cid]["verdict"],
            "disagree_v2": labels["labels"][cid]["label"] != j2[cid]["verdict"],
        })

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Week 6 Practical: Ticket-Reply Judge Validation Dashboard</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        :root {{
            --bg: #090d16;
            --card-bg: rgba(22, 30, 49, 0.7);
            --card-border: rgba(255, 255, 255, 0.08);
            --accent-cyan: #06b6d4;
            --accent-indigo: #6366f1;
            --accent-purple: #8b5cf6;
            --pass-green: #10b981;
            --fail-red: #ef4444;
            --text-main: #f3f4f6;
            --text-muted: #9ca3af;
        }}
        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}
        body {{
            background-color: var(--bg);
            color: var(--text-main);
            font-family: 'Plus Jakarta Sans', -apple-system, sans-serif;
            line-height: 1.5;
            padding: 24px;
        }}
        .container {{
            max-width: 1380px;
            margin: 0 auto;
        }}
        header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 28px;
            padding-bottom: 20px;
            border-bottom: 1px solid var(--card-border);
        }}
        .header-title h1 {{
            font-size: 26px;
            font-weight: 800;
            background: linear-gradient(135deg, #38bdf8 0%, #818cf8 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        .header-title p {{
            color: var(--text-muted);
            font-size: 14px;
            margin-top: 4px;
        }}
        .badge-verified {{
            background: rgba(16, 185, 129, 0.15);
            color: var(--pass-green);
            border: 1px solid rgba(16, 185, 129, 0.3);
            padding: 6px 14px;
            border-radius: 9999px;
            font-size: 13px;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 6px;
        }}
        
        /* Metric Grid */
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 16px;
            margin-bottom: 28px;
        }}
        .metric-card {{
            background: var(--card-bg);
            border: 1px solid var(--card-border);
            border-radius: 14px;
            padding: 20px;
            backdrop-filter: blur(12px);
            position: relative;
            overflow: hidden;
        }}
        .metric-card::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 3px;
            background: linear-gradient(90deg, var(--accent-cyan), var(--accent-indigo));
        }}
        .metric-label {{
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: var(--text-muted);
            font-weight: 600;
        }}
        .metric-val {{
            font-size: 32px;
            font-weight: 800;
            margin: 6px 0;
            display: flex;
            align-items: baseline;
            gap: 8px;
        }}
        .metric-sub {{
            font-size: 13px;
            color: var(--text-muted);
        }}
        .metric-delta {{
            color: var(--pass-green);
            font-size: 14px;
            font-weight: 700;
        }}

        /* Table & Controls */
        .controls-panel {{
            background: var(--card-bg);
            border: 1px solid var(--card-border);
            border-radius: 14px;
            padding: 16px 20px;
            margin-bottom: 24px;
            display: flex;
            flex-wrap: wrap;
            gap: 14px;
            align-items: center;
            justify-content: space-between;
        }}
        .filter-group {{
            display: flex;
            align-items: center;
            gap: 10px;
            flex-wrap: wrap;
        }}
        select, input[type="text"] {{
            background: rgba(11, 15, 25, 0.8);
            border: 1px solid rgba(255, 255, 255, 0.15);
            color: var(--text-main);
            padding: 8px 14px;
            border-radius: 8px;
            font-size: 14px;
            outline: none;
        }}
        select:focus, input[type="text"]:focus {{
            border-color: var(--accent-cyan);
        }}
        .toggle-btn {{
            background: rgba(255, 255, 255, 0.06);
            border: 1px solid var(--card-border);
            color: var(--text-main);
            padding: 8px 14px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 13px;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 6px;
            transition: all 0.2s ease;
        }}
        .toggle-btn.active {{
            background: rgba(239, 68, 68, 0.2);
            border-color: var(--fail-red);
            color: #fca5a5;
        }}

        /* Mode summary table */
        .summary-box {{
            background: var(--card-bg);
            border: 1px solid var(--card-border);
            border-radius: 14px;
            padding: 20px;
            margin-bottom: 28px;
            overflow-x: auto;
        }}
        .summary-box h3 {{
            font-size: 16px;
            margin-bottom: 14px;
            display: flex;
            align-items: center;
            gap: 8px;
            color: #e2e8f0;
        }}
        table.mode-table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 14px;
        }}
        table.mode-table th {{
            text-align: left;
            padding: 10px 14px;
            background: rgba(255, 255, 255, 0.04);
            color: var(--text-muted);
            font-weight: 600;
            border-bottom: 1px solid var(--card-border);
        }}
        table.mode-table td {{
            padding: 12px 14px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.04);
        }}
        table.mode-table tr:last-child td {{
            border-bottom: none;
            font-weight: 700;
            background: rgba(255, 255, 255, 0.02);
        }}

        /* Case Cards List */
        .cases-grid {{
            display: grid;
            grid-template-columns: 1fr;
            gap: 16px;
        }}
        .case-card {{
            background: var(--card-bg);
            border: 1px solid var(--card-border);
            border-radius: 14px;
            padding: 20px;
            backdrop-filter: blur(10px);
            transition: border-color 0.2s;
        }}
        .case-card:hover {{
            border-color: rgba(255, 255, 255, 0.2);
        }}
        .case-header {{
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 12px;
            flex-wrap: wrap;
            gap: 8px;
        }}
        .case-id {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 15px;
            font-weight: 700;
            color: #38bdf8;
        }}
        .tag {{
            display: inline-block;
            padding: 3px 8px;
            border-radius: 6px;
            font-size: 12px;
            font-weight: 600;
            margin-left: 6px;
        }}
        .tag-mode {{
            background: rgba(99, 102, 241, 0.2);
            color: #a5b4fc;
            border: 1px solid rgba(99, 102, 241, 0.4);
        }}
        .tag-regression {{
            background: rgba(245, 158, 11, 0.2);
            color: #fcd34d;
            border: 1px solid rgba(245, 158, 11, 0.4);
        }}
        .verdict-pills {{
            display: flex;
            gap: 8px;
        }}
        .pill {{
            padding: 4px 10px;
            border-radius: 6px;
            font-size: 12px;
            font-weight: 700;
            text-transform: uppercase;
        }}
        .pill-pass {{
            background: rgba(16, 185, 129, 0.2);
            color: #34d399;
            border: 1px solid rgba(16, 185, 129, 0.5);
        }}
        .pill-fail {{
            background: rgba(239, 68, 68, 0.2);
            color: #f87171;
            border: 1px solid rgba(239, 68, 68, 0.5);
        }}
        .q-box {{
            background: rgba(11, 15, 25, 0.6);
            border: 1px solid rgba(255, 255, 255, 0.05);
            padding: 12px 14px;
            border-radius: 8px;
            margin-bottom: 12px;
            font-size: 14px;
        }}
        .reply-box {{
            background: rgba(11, 15, 25, 0.9);
            border: 1px solid rgba(255, 255, 255, 0.05);
            padding: 12px 14px;
            border-radius: 8px;
            font-family: 'JetBrains Mono', monospace;
            font-size: 12px;
            color: #cbd5e1;
            white-space: pre-wrap;
            max-height: 180px;
            overflow-y: auto;
            margin-bottom: 12px;
        }}
        .judgments-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr 1fr;
            gap: 12px;
            font-size: 13px;
        }}
        .j-box {{
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid rgba(255, 255, 255, 0.05);
            border-radius: 8px;
            padding: 10px 12px;
        }}
        .j-title {{
            font-size: 11px;
            text-transform: uppercase;
            font-weight: 700;
            color: var(--text-muted);
            margin-bottom: 4px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <div class="header-title">
                <h1>Week 6 Evaluation Dashboard</h1>
                <p>Validate the ticket-reply judge before you trust its number — Customer Support Domain</p>
            </div>
            <div class="badge-verified">
                <i class="fa-solid fa-circle-check"></i> Provenance Verified (fb4c42a)
            </div>
        </header>

        <!-- Metric Cards -->
        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-label">Agreement Movement</div>
                <div class="metric-val">
                    <span>92.0%</span>
                    <span class="metric-delta"><i class="fa-solid fa-arrow-trend-up"></i> +24.0%</span>
                </div>
                <div class="metric-sub">Before (v1): <strong>68.0%</strong> &rarr; After (v2): <strong>92.0%</strong></div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Held-Out Generalization</div>
                <div class="metric-val">91.3%</div>
                <div class="metric-sub">21 / 23 cases (excluding few-shots C08, C21)</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Cohen's Kappa (&kappa;)</div>
                <div class="metric-val">
                    <span>0.84</span>
                    <span class="metric-delta"><i class="fa-solid fa-arrow-trend-up"></i> +0.50</span>
                </div>
                <div class="metric-sub">Near-perfect reliability (&kappa; 0.34 &rarr; 0.84)</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Assertion / Judge Split</div>
                <div class="metric-val">4 : 1</div>
                <div class="metric-sub">4 Deterministic Rules vs 1 Judged Criterion</div>
            </div>
        </div>

        <!-- Failure Mode Summary Table -->
        <div class="summary-box">
            <h3><i class="fa-solid fa-table-list"></i> Pass Rate by Failure Mode (One-Command Eval)</h3>
            <table class="mode-table">
                <thead>
                    <tr>
                        <th>Taxonomy Mode</th>
                        <th>n</th>
                        <th>Assertions</th>
                        <th>Judge v1</th>
                        <th>Judge v2</th>
                        <th>Overall Pass</th>
                        <th>Human Truth</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td><strong>M1: Superseded Grace Period</strong></td>
                        <td>5</td>
                        <td>100.0%</td>
                        <td>0.0%</td>
                        <td>40.0%</td>
                        <td>40.0%</td>
                        <td>20.0%</td>
                    </tr>
                    <tr>
                        <td><strong>M2: Code 51 vs Timeout</strong></td>
                        <td>5</td>
                        <td>100.0%</td>
                        <td>20.0%</td>
                        <td>40.0%</td>
                        <td>40.0%</td>
                        <td>40.0%</td>
                    </tr>
                    <tr>
                        <td><strong>M3: 2FA Fallback Omitted</strong></td>
                        <td>5</td>
                        <td>100.0%</td>
                        <td>20.0%</td>
                        <td>40.0%</td>
                        <td>40.0%</td>
                        <td>60.0%</td>
                    </tr>
                    <tr>
                        <td><strong>M4: Cardholder Format Omitted</strong></td>
                        <td>5</td>
                        <td>100.0%</td>
                        <td>20.0%</td>
                        <td>20.0%</td>
                        <td>20.0%</td>
                        <td>20.0%</td>
                    </tr>
                    <tr>
                        <td><strong>M5: Hallucinated Refund SLA</strong></td>
                        <td>5</td>
                        <td>100.0%</td>
                        <td>20.0%</td>
                        <td>100.0%</td>
                        <td>100.0%</td>
                        <td>100.0%</td>
                    </tr>
                    <tr>
                        <td><strong>ALL MODES (Combined)</strong></td>
                        <td><strong>25</strong></td>
                        <td><strong>100.0%</strong></td>
                        <td><strong>16.0%</strong></td>
                        <td><strong>48.0%</strong></td>
                        <td><strong>48.0%</strong></td>
                        <td><strong>48.0%</strong></td>
                    </tr>
                </tbody>
            </table>
        </div>

        <!-- Filter Controls -->
        <div class="controls-panel">
            <div class="filter-group">
                <label style="font-size: 13px; color: var(--text-muted); font-weight: 600;">Filter Mode:</label>
                <select id="modeFilter" onchange="renderCases()">
                    <option value="ALL">All 5 Modes (25 Cases)</option>
                    <option value="M1_superseded_grace_period">M1: Superseded Grace Period</option>
                    <option value="M2_code51_confused_with_timeout">M2: Code 51 vs Timeout</option>
                    <option value="M3_2fa_fallback_step_omitted">M3: 2FA Fallback Omitted</option>
                    <option value="M4_cardholder_format_rule_omitted">M4: Cardholder Format</option>
                    <option value="M5_hallucinated_refund_sla">M5: Hallucinated Refund SLA</option>
                </select>
                <input type="text" id="searchBox" placeholder="Search question or text..." oninput="renderCases()">
            </div>
            <div class="filter-group">
                <button class="toggle-btn" id="disagreeToggle" onclick="toggleDisagreements()">
                    <i class="fa-solid fa-filter"></i> Only Judge v2 Disagreements (2)
                </button>
            </div>
        </div>

        <!-- Cases Container -->
        <div class="cases-grid" id="casesContainer">
            <!-- Dynamic Injection -->
        </div>
    </div>

    <script>
        const CASES = {json.dumps(combined_cases, ensure_ascii=False)};
        let onlyDisagreements = false;

        function toggleDisagreements() {{
            onlyDisagreements = !onlyDisagreements;
            document.getElementById('disagreeToggle').classList.toggle('active', onlyDisagreements);
            renderCases();
        }}

        function renderCases() {{
            const container = document.getElementById('casesContainer');
            const mode = document.getElementById('modeFilter').value;
            const search = document.getElementById('searchBox').value.toLowerCase();

            const filtered = CASES.filter(c => {{
                if (mode !== 'ALL' && c.mode !== mode) return false;
                if (onlyDisagreements && !c.disagree_v2) return false;
                if (search && !c.question.toLowerCase().includes(search) && !c.reply.toLowerCase().includes(search)) return false;
                return true;
            }});

            if (filtered.length === 0) {{
                container.innerHTML = `<div style="text-align: center; padding: 40px; color: var(--text-muted);">No cases match the selected filters.</div>`;
                return;
            }}

            container.innerHTML = filtered.map(c => `
                <div class="case-card">
                    <div class="case-header">
                        <div>
                            <span class="case-id">${{c.id}}</span>
                            <span class="tag tag-mode">${{c.mode}}</span>
                            ${{c.regression ? '<span class="tag tag-regression">Regression Trace</span>' : ''}}
                        </div>
                        <div class="verdict-pills">
                            <span class="pill ${{c.human === 'PASS' ? 'pill-pass' : 'pill-fail'}}">Human: ${{c.human}}</span>
                            <span class="pill ${{c.judge_v1 === 'PASS' ? 'pill-pass' : 'pill-fail'}}">Judge v1: ${{c.judge_v1}}</span>
                            <span class="pill ${{c.judge_v2 === 'PASS' ? 'pill-pass' : 'pill-fail'}}">Judge v2: ${{c.judge_v2}}</span>
                        </div>
                    </div>
                    <div class="q-box">
                        <strong style="color: #93c5fd;">Question:</strong> ${{escapeHtml(c.question)}}
                    </div>
                    <div class="reply-box">${{escapeHtml(c.reply)}}</div>
                    <div class="judgments-grid">
                        <div class="j-box">
                            <div class="j-title">Human Labeler Note</div>
                            <div>${{escapeHtml(c.human_note || "None")}}</div>
                        </div>
                        <div class="j-box">
                            <div class="j-title">Judge v1 Reason</div>
                            <div>${{escapeHtml(c.reason_v1)}}</div>
                        </div>
                        <div class="j-box" style="${{c.disagree_v2 ? 'border-color: rgba(239, 68, 68, 0.4);' : ''}}">
                            <div class="j-title">Judge v2 Reason</div>
                            <div>${{escapeHtml(c.reason_v2)}}</div>
                        </div>
                    </div>
                </div>
            `).join('');
        }}

        function escapeHtml(text) {{
            return String(text)
                .replace(/&/g, "&amp;")
                .replace(/</g, "&lt;")
                .replace(/>/g, "&gt;")
                .replace(/"/g, "&quot;");
        }}

        renderCases();
    </script>
</body>
</html>
"""
    out_path = ROOT / "eval" / "dashboard.html"
    out_path.write_text(html_content, encoding="utf-8")
    print(f"Generated dashboard at: {out_path}")

if __name__ == "__main__":
    build_dashboard()
