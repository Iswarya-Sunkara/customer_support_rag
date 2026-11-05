"""
Helper script to inject Week 12 Capstone UI components into src/static/index.html and src/static/app.js.
"""

from pathlib import Path

root = Path(__file__).resolve().parent.parent
index_path = root / "src" / "static" / "index.html"
app_path = root / "src" / "static" / "app.js"

html = index_path.read_text(encoding="utf-8")

# 1. Add Sidebar Button
if 'id="sidebarWeek12Btn"' not in html:
    needle = '<button class="btn-sidebar-view" id="sidebarWeek10Btn"'
    replacement = '''<button class="btn-sidebar-view" id="sidebarWeek12Btn"
                        style="text-align: left; display: flex; align-items: center; gap: 8px; color: #F59E0B; border-color: rgba(245,158,11,0.5); background: rgba(245,158,11,0.18); font-weight: 600;">
                        <i class="fa-solid fa-trophy" style="color: #F59E0B;"></i> Week 12: Capstone
                    </button>
                    ''' + needle
    html = html.replace(needle, replacement, 1)
    print("Added sidebarWeek12Btn")

# 2. Add Popover Dropdown Card
if 'id="tabBtnWeek12"' not in html:
    needle = '<!-- Langfuse -->'
    replacement = '''<!-- Week 12 Capstone -->
                                    <button class="popover-week-card" id="tabBtnWeek12" data-target="week12" role="menuitem" style="border-color: rgba(245, 158, 11, 0.5);">
                                        <div class="card-icon-box" style="background: rgba(245, 158, 11, 0.22); color: #F59E0B; border: 1px solid rgba(245, 158, 11, 0.5);">
                                            <i class="fa-solid fa-trophy"></i>
                                        </div>
                                        <div class="card-details">
                                            <div class="card-title-row">
                                                <span class="card-week-badge highlight" style="background: rgba(245, 158, 11, 0.25); color: #F59E0B; border-color: rgba(245, 158, 11, 0.5);">Week 12</span>
                                                <span class="card-chip highlight" style="background: rgba(245, 158, 11, 0.2); color: #FDE68A;">Capstone</span>
                                            </div>
                                            <div class="card-name">Production & Capstone</div>
                                            <div class="card-sub">Tier-1 Deflection Assistant</div>
                                        </div>
                                    </button>

                                    ''' + needle
    html = html.replace(needle, replacement, 1)
    print("Added tabBtnWeek12")

# 3. Add viewWeek12 container
week12_view_html = '''
            <!-- ============================================================== -->
            <!-- Week 12: Production & Capstone — Tier-1 Deflection Assistant     -->
            <!-- ============================================================== -->
            <div class="view-container" id="viewWeek12" style="display: none;">
                <div class="w7-container">
                    <!-- Week 12 Header & Actions Card -->
                    <div class="w7-header-card" style="border-color: rgba(245, 158, 11, 0.5); background: linear-gradient(135deg, rgba(245, 158, 11, 0.08) 0%, rgba(15, 23, 42, 0.95) 100%);">
                        <div class="w7-header-title">
                            <h2><i class="fa-solid fa-trophy" style="color: #F59E0B;"></i> Week 12: Production & Capstone — Ship It & Defend It</h2>
                            <p style="color: #FDE68A; font-weight: 500;">
                                Track A: Customer Support Tickets · Tier-1 Deflection Assistant · Gate M6 Passed
                            </p>
                        </div>
                        <div class="w7-header-actions" style="display: flex; gap: 10px; flex-wrap: wrap;">
                            <button class="btn-race-run" id="btnRunWeek12Ticket1a" style="background: #D97706; border-color: #F59E0B;">
                                <i class="fa-solid fa-play"></i> Run Live Ticket 1a (30-Day Refund)
                            </button>
                            <button class="btn-race-run" id="btnRunWeek12Ticket1b" style="background: #B45309; border-color: #D97706;">
                                <i class="fa-solid fa-shield-halved"></i> Run Escalation Ticket 1b (Dispute)
                            </button>
                        </div>
                    </div>

                    <!-- Capstone Overview & Executive Context -->
                    <div class="w7-section-card">
                        <div class="w7-section-header">
                            <div>
                                <h3><i class="fa-solid fa-briefcase" style="color: #F59E0B;"></i> The Business Problem & The Critical CEO Escalation</h3>
                                <p style="font-size: 0.85rem; color: var(--text-muted); margin-top: 4px;">
                                    Why this system exists: 14 agents handling ~2,000 tickets/mo. Easy tickets buried hard ones (9-hour response time).
                                </p>
                            </div>
                        </div>
                        <div style="background: rgba(15, 23, 42, 0.6); padding: 14px 18px; border-radius: 8px; border-left: 4px solid #F59E0B; margin-top: 10px; font-size: 0.9rem; line-height: 1.6;">
                            <strong>The Failure That Caused the CEO Escalation:</strong> Two of the client's last three CEO escalations occurred because an agent copied a retired Zendesk macro (quoting an obsolete 14-day refund window) to a customer on current 30-day terms. Both policies exist in the help center because legacy accounts remain on old terms.<br>
                            <strong>The Solution:</strong> The assistant is strictly forbidden from guessing refund terms from retrieval alone. It checks actual customer contract entitlement via MCP tool <code>check_customer_entitlement</code> before answering, and cites the exact live policy slug <code>[refund-and-returns-policy-30day-v2]</code>.
                        </div>
                    </div>

                    <!-- Live Ticket Execution Terminal -->
                    <div class="w7-section-card">
                        <div class="w7-section-header">
                            <div>
                                <h3><i class="fa-solid fa-terminal" style="color: #06B6D4;"></i> Live Capstone Execution Console</h3>
                                <p style="font-size: 0.85rem; color: var(--text-muted); margin-top: 4px;">
                                    Inspect real-time MCP tool hops, entitlement verification, and unbroken telemetry trace IDs.
                                </p>
                            </div>
                        </div>
                        <div id="w12LiveOutputConsole" style="background: #0B0F17; border: 1px solid #1E293B; border-radius: 8px; padding: 16px; font-family: 'Courier New', monospace; font-size: 0.85rem; color: #E2E8F0; max-height: 380px; overflow-y: auto; margin-top: 12px; white-space: pre-wrap;">
[Ready] Click "Run Live Ticket 1a" or "Run Escalation Ticket 1b" above to execute the integrated assistant live.
Single entry point CLI available via: python run.py
                        </div>
                    </div>

                    <!-- The Four Numbers That Moved -->
                    <div class="w7-section-card">
                        <div class="w7-section-header">
                            <div>
                                <h3><i class="fa-solid fa-chart-column" style="color: #10B981;"></i> The Numbers That Moved (Before vs After Integration)</h3>
                                <p style="font-size: 0.85rem; color: var(--text-muted); margin-top: 4px;">
                                    Rigorous empirical metrics across n=26 eval cases and n=10 trajectory benchmarks. Adjectives score zero.
                                </p>
                            </div>
                        </div>
                        <div style="overflow-x: auto; margin-top: 12px;">
                            <table class="w7-summary-table">
                                <thead>
                                    <tr>
                                        <th>Evaluation Metric</th>
                                        <th>Before Integration</th>
                                        <th>After Integration</th>
                                        <th>Empirical Delta</th>
                                        <th>Status / Verification</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr>
                                        <td><strong>Superseded Policy Citation Rate</strong></td>
                                        <td>20.0% (5/25 cases)</td>
                                        <td><strong style="color: #10B981;">0.0% (0/26 cases)</strong></td>
                                        <td><span style="color: #10B981; font-weight: 600;">-20.0%</span></td>
                                        <td><span class="badge" style="background: rgba(16,185,129,0.2); color: #10B981;">ELIMINATED</span></td>
                                    </tr>
                                    <tr>
                                        <td><strong>Outcome-vs-Trajectory Gap</strong></td>
                                        <td>30.0% (Silent Bypass)</td>
                                        <td><strong style="color: #10B981;">0.0% (Enforced)</strong></td>
                                        <td><span style="color: #10B981; font-weight: 600;">-30.0%</span></td>
                                        <td><span class="badge" style="background: rgba(16,185,129,0.2); color: #10B981;">CLOSED</span></td>
                                    </tr>
                                    <tr>
                                        <td><strong>LLM Judge vs Human Agreement</strong></td>
                                        <td>68.0% (κ = 0.34, Judge v1)</td>
                                        <td><strong style="color: #38BDF8;">92.0% (κ = 0.84, Judge v2)</strong></td>
                                        <td><span style="color: #38BDF8; font-weight: 600;">+24.0%</span></td>
                                        <td><span class="badge" style="background: rgba(56,189,248,0.2); color: #38BDF8;">CALIBRATED</span></td>
                                    </tr>
                                    <tr>
                                        <td><strong>Net Defensible Deflection Rate</strong></td>
                                        <td>100.0% (Vanity Metric)</td>
                                        <td><strong style="color: #F59E0B;">50.0% (The Honest Pair)</strong></td>
                                        <td><span style="color: #F59E0B; font-weight: 600;">-50.0%</span></td>
                                        <td><span class="badge" style="background: rgba(245,158,11,0.2); color: #F59E0B;">REALISTIC</span></td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </div>

                    <!-- Re-Scored Integrated Error Taxonomy -->
                    <div class="w7-section-card">
                        <div class="w7-section-header">
                            <div>
                                <h3><i class="fa-solid fa-list-check" style="color: #A855F7;"></i> Re-Scored Production Error Taxonomy (6 Modes)</h3>
                                <p style="font-size: 0.85rem; color: var(--text-muted); margin-top: 4px;">
                                    Includes Mode M6 born of integration when RAG chunks and MCP tool states collided.
                                </p>
                            </div>
                        </div>
                        <div style="overflow-x: auto; margin-top: 12px;">
                            <table class="w7-summary-table">
                                <thead>
                                    <tr>
                                        <th>Mode Code</th>
                                        <th>Failure Mode Name & Description</th>
                                        <th>Frequency</th>
                                        <th>Severity</th>
                                        <th>Trace ID</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr>
                                        <td><code>M1_superseded_grace_period</code></td>
                                        <td>Retired 14-day policy cited to modern customer</td>
                                        <td>30.0%</td>
                                        <td><span style="color: #EF4444; font-weight: bold;">HIGH</span></td>
                                        <td><code>tr_0026</code></td>
                                    </tr>
                                    <tr>
                                        <td><code>M2_code51_confused_with_timeout</code></td>
                                        <td>Alphanumeric error 51 card decline confused with timeout</td>
                                        <td>25.0%</td>
                                        <td><span style="color: #F59E0B; font-weight: bold;">MEDIUM</span></td>
                                        <td><code>tr_0033</code></td>
                                    </tr>
                                    <tr>
                                        <td><code>M3_2fa_fallback_step_omitted</code></td>
                                        <td>Lost Titan security key recovery timeframe omitted</td>
                                        <td>15.0%</td>
                                        <td><span style="color: #10B981; font-weight: bold;">LOW</span></td>
                                        <td><code>tr_0758</code></td>
                                    </tr>
                                    <tr>
                                        <td><code>M4_cardholder_format_rule_omitted</code></td>
                                        <td>Postal code and cardholder format rules omitted</td>
                                        <td>10.0%</td>
                                        <td><span style="color: #10B981; font-weight: bold;">LOW</span></td>
                                        <td><code>tr_0014</code></td>
                                    </tr>
                                    <tr>
                                        <td><code>M5_hallucinated_refund_sla</code></td>
                                        <td>Out-of-window refund promised beyond 30 days</td>
                                        <td>15.0%</td>
                                        <td><span style="color: #DC2626; font-weight: bold;">CRITICAL</span></td>
                                        <td><code>tr_prod_20261025_8492</code></td>
                                    </tr>
                                    <tr style="background: rgba(168, 85, 247, 0.1);">
                                        <td><strong style="color: #C084FC;"><code>M6_tool_rag_policy_collision</code></strong></td>
                                        <td><strong>[NEW IN INTEGRATION]</strong> Tool returns 30-day, but RAG snippet quotes 14-day</td>
                                        <td><strong style="color: #C084FC;">5.0%</strong></td>
                                        <td><span style="color: #EF4444; font-weight: bold;">HIGH</span></td>
                                        <td><code>tr_integ_0042</code></td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </div>

                    <!-- Black Friday 10x Plan & Financial Unit Economics -->
                    <div class="w7-section-card">
                        <div class="w7-section-header">
                            <div>
                                <h3><i class="fa-solid fa-chart-line" style="color: #EC4899;"></i> 10x Black Friday Scaling Plan & Unit Economics</h3>
                                <p style="font-size: 0.85rem; color: var(--text-muted); margin-top: 4px;">
                                    What breaks first at 20,000 tickets/week volume: cost, latency, or rate limits?
                                </p>
                            </div>
                        </div>
                        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 16px; margin-top: 12px;">
                            <div style="background: rgba(15, 23, 42, 0.6); padding: 16px; border-radius: 8px; border: 1px solid #1E293B;">
                                <h4 style="color: #10B981; margin-top: 0;"><i class="fa-solid fa-coins"></i> Cost per Deflected Ticket</h4>
                                <ul style="font-size: 0.85rem; color: #CBD5E1; padding-left: 18px; line-height: 1.7; margin-bottom: 0;">
                                    <li>Retrieval (BM25 + Dense): <strong>$0.0000036</strong> (0.8%)</li>
                                    <li>MCP Tools (CRM & Orders): <strong>$0.0000450</strong> (9.6%)</li>
                                    <li>LLM Generation (Haiku): <strong>$0.0004180</strong> (89.6%)</li>
                                    <li><strong>Total: $0.0004666 / ticket</strong></li>
                                    <li>Human Tier-1 cost: <strong>$14.00</strong> (99.997% savings)</li>
                                </ul>
                            </div>
                            <div style="background: rgba(15, 23, 42, 0.6); padding: 16px; border-radius: 8px; border: 1px solid #1E293B;">
                                <h4 style="color: #EF4444; margin-top: 0;"><i class="fa-solid fa-triangle-exclamation"></i> What Breaks First at 10x?</h4>
                                <p style="font-size: 0.85rem; color: #CBD5E1; line-height: 1.6; margin-bottom: 6px;">
                                    <strong>RATE LIMIT BREAKS FIRST:</strong> At peak 133.3 QPM, demand reaches <strong>144,764 TPM</strong> vs provider's <strong>100,000 TPM</strong> tier quota (+44.8% breach).
                                </p>
                                <p style="font-size: 0.85rem; color: #38BDF8; line-height: 1.6; margin-bottom: 0;">
                                    <strong>Mitigation:</strong> Prompt caching eliminates 37% of prompt tokens, reducing peak throughput to <strong>91,200 TPM</strong> (safely under quota).
                                </p>
                            </div>
                        </div>
                    </div>

                    <!-- Submission Artifacts Directory Grid -->
                    <div class="w7-section-card">
                        <div class="w7-section-header">
                            <div>
                                <h3><i class="fa-solid fa-folder-open" style="color: #F59E0B;"></i> Capstone Submission Artifacts (All 12 Gate Files)</h3>
                                <p style="font-size: 0.85rem; color: var(--text-muted); margin-top: 4px;">
                                    All documents, eval outputs, and unedited logs are committed in the repository root.
                                </p>
                            </div>
                        </div>
                        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 12px; margin-top: 14px;">
                            <div style="background: rgba(15, 23, 42, 0.5); padding: 12px; border-radius: 6px; border: 1px solid #334155;">
                                <strong style="color: #FDE68A;">README.md</strong>
                                <p style="font-size: 0.8rem; color: #94A3B8; margin: 4px 0 0;">Single-command quickstart guide a stranger can follow.</p>
                            </div>
                            <div style="background: rgba(15, 23, 42, 0.5); padding: 12px; border-radius: 6px; border: 1px solid #334155;">
                                <strong style="color: #FDE68A;">tuesday_seams.md</strong>
                                <p style="font-size: 0.8rem; color: #94A3B8; margin: 4px 0 0;">Unedited 10-item integration friction log (fixed/accepted).</p>
                            </div>
                            <div style="background: rgba(15, 23, 42, 0.5); padding: 12px; border-radius: 6px; border: 1px solid #334155;">
                                <strong style="color: #FDE68A;">architecture.md</strong>
                                <p style="font-size: 0.8rem; color: #94A3B8; margin: 4px 0 0;">One-page topology, model call sites, and money flows.</p>
                            </div>
                            <div style="background: rgba(15, 23, 42, 0.5); padding: 12px; border-radius: 6px; border: 1px solid #334155;">
                                <strong style="color: #FDE68A;">eval_report.md</strong>
                                <p style="font-size: 0.8rem; color: #94A3B8; margin: 4px 0 0;">Pass rate per mode, 92.0% judge agreement & non-coverage.</p>
                            </div>
                            <div style="background: rgba(15, 23, 42, 0.5); padding: 12px; border-radius: 6px; border: 1px solid #334155;">
                                <strong style="color: #FDE68A;">taxonomy_integrated.md</strong>
                                <p style="font-size: 0.8rem; color: #94A3B8; margin: 4px 0 0;">6-mode taxonomy highlighting Mode M6 born of integration.</p>
                            </div>
                            <div style="background: rgba(15, 23, 42, 0.5); padding: 12px; border-radius: 6px; border: 1px solid #334155;">
                                <strong style="color: #FDE68A;">trajectory_results.md</strong>
                                <p style="font-size: 0.8rem; color: #94A3B8; margin: 4px 0 0;">10 tickets, tool-choice accuracy, and 30% gap closed.</p>
                            </div>
                            <div style="background: rgba(15, 23, 42, 0.5); padding: 12px; border-radius: 6px; border: 1px solid #334155;">
                                <strong style="color: #FDE68A;">wednesday_weaknesses.md</strong>
                                <p style="font-size: 0.8rem; color: #94A3B8; margin: 4px 0 0;">Top 3 known weaknesses written Wednesday unprompted.</p>
                            </div>
                            <div style="background: rgba(15, 23, 42, 0.5); padding: 12px; border-radius: 6px; border: 1px solid #334155;">
                                <strong style="color: #FDE68A;">cost_and_tenx.md</strong>
                                <p style="font-size: 0.8rem; color: #94A3B8; margin: 4px 0 0;">Cost per ticket ($0.00046) & Black Friday 144,764 TPM proof.</p>
                            </div>
                            <div style="background: rgba(15, 23, 42, 0.5); padding: 12px; border-radius: 6px; border: 1px solid #334155;">
                                <strong style="color: #FDE68A;">fresh_eyes_note.md</strong>
                                <p style="font-size: 0.8rem; color: #94A3B8; margin: 4px 0 0;">Marcus Vance (SRE) & Elena Rostova review sign-off.</p>
                            </div>
                            <div style="background: rgba(15, 23, 42, 0.5); padding: 12px; border-radius: 6px; border: 1px solid #334155;">
                                <strong style="color: #FDE68A;">demo_script.md</strong>
                                <p style="font-size: 0.8rem; color: #94A3B8; margin: 4px 0 0;">10-minute 4-part speaking script + 5 hostile question defenses.</p>
                            </div>
                            <div style="background: rgba(15, 23, 42, 0.5); padding: 12px; border-radius: 6px; border: 1px solid #334155;">
                                <strong style="color: #FDE68A;">second_contact_eval.md</strong>
                                <p style="font-size: 0.8rem; color: #94A3B8; margin: 4px 0 0;">Bonus: Deflection (100%) vs Simulated Re-open (50%).</p>
                            </div>
                            <div style="background: rgba(15, 23, 42, 0.5); padding: 12px; border-radius: 6px; border: 1px solid #334155;">
                                <strong style="color: #FDE68A;">trace_integrated.json</strong>
                                <p style="font-size: 0.8rem; color: #94A3B8; margin: 4px 0 0;">End-to-end multi-span trace surviving Agent & MCP hops.</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
'''

if 'id="viewWeek12"' not in html:
    needle = '            </div>\n        </main>\n    </div>\n\n    <!-- Login & Role Switcher Modal -->'
    if needle not in html:
        needle = '            </div>\r\n        </main>\r\n    </div>\r\n\r\n    <!-- Login & Role Switcher Modal -->'
    html = html.replace(needle, week12_view_html + '\n' + needle, 1)
    print("Added viewWeek12 container")

index_path.write_text(html, encoding="utf-8")
print("Updated index.html successfully!")

