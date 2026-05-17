from datetime import datetime
import json


def generate_report_html(profiles: list, base_url: str = "") -> str:
    date_str = datetime.now().strftime("%B %d, %Y")
    cards_html = ""

    all_hooks_by_profile = []

    for p in profiles:
        analysis = p.get("analysis", {})
        ai = p.get("ai_insights", {})
        username = p.get("username", "unknown")

        issues_html = "".join(f'<li>{i}</li>' for i in analysis.get("top_issues", []))
        hooks_html = ""
        profile_hooks = []
        for hb in analysis.get("hook_breakdown", [])[:4]:
            score = hb.get("score", 0)
            hook_text = hb.get("hook", "")
            color = "#22c55e" if score >= 70 else "#f59e0b" if score >= 45 else "#ef4444"
            hooks_html += f"""
            <div class="hook-item">
                <div class="hook-text">"{hook_text}"</div>
                <div class="hook-score" style="color:{color}">Score: {score}/100</div>
                {'<div class="hook-issue">' + hb["issues"][0] + '</div>' if hb.get("issues") else ''}
            </div>"""
            if hook_text:
                profile_hooks.append(hook_text)

        if profile_hooks:
            all_hooks_by_profile.append({
                "username": username,
                "hooks": profile_hooks,
            })

        ideas_html = ""
        for idea in ai.get("content_ideas", []):
            ideas_html += f'<li>{idea}</li>'

        opp_score = analysis.get("opportunity_score", 0)
        opp_label = analysis.get("opportunity_label", "Unknown")
        if opp_score >= 75:
            opp_color = "#ef4444"; opp_bg = "#fef2f2"
        elif opp_score >= 50:
            opp_color = "#f59e0b"; opp_bg = "#fffbeb"
        else:
            opp_color = "#22c55e"; opp_bg = "#f0fdf4"

        engagement = analysis.get("engagement_rate", 0)
        hook_score = analysis.get("hook_score", 0)
        hook_quality = analysis.get("hook_quality", "N/A")
        audit_summary = ai.get("audit_summary", "")
        dm_message = ai.get("dm_message", "")

        cards_html += f"""
        <div class="profile-card">
            <div class="card-header">
                <div class="profile-info">
                    <div class="avatar">{username[0].upper()}</div>
                    <div>
                        <h2>@{username}</h2>
                        <p class="full-name">{p.get('full_name', '')}</p>
                    </div>
                </div>
                <div class="opportunity-badge" style="background:{opp_bg};color:{opp_color};border:2px solid {opp_color}">
                    <div class="opp-score">{opp_score}</div>
                    <div class="opp-label">{opp_label}</div>
                </div>
            </div>

            <div class="stats-grid">
                <div class="stat">
                    <div class="stat-value">{format_number(p.get('followers', 0))}</div>
                    <div class="stat-label">Followers</div>
                </div>
                <div class="stat">
                    <div class="stat-value" style="color:{'#ef4444' if engagement < 1 else '#f59e0b' if engagement < 3 else '#22c55e'}">{engagement}%</div>
                    <div class="stat-label">Engagement Rate</div>
                </div>
                <div class="stat">
                    <div class="stat-value">{format_number(analysis.get('avg_likes', 0))}</div>
                    <div class="stat-label">Avg Likes</div>
                </div>
                <div class="stat">
                    <div class="stat-value" style="color:{'#ef4444' if hook_score < 45 else '#f59e0b' if hook_score < 70 else '#22c55e'}">{hook_quality}</div>
                    <div class="stat-label">Hook Quality ({hook_score}/100)</div>
                </div>
            </div>

            {f'''<div class="ai-summary-section">
                <div class="ai-badge">✦ AI Audit</div>
                <p class="ai-summary-text">{audit_summary}</p>
            </div>''' if audit_summary else ''}

            <div class="section">
                <h3>Key Issues Identified</h3>
                <ul class="issues-list">{issues_html}</ul>
            </div>

            <div class="section">
                <h3>Recent Hook Analysis</h3>
                <div class="hooks-container">{hooks_html}</div>
            </div>

            {f'''<div class="section">
                <h3>✦ AI-Generated Content Ideas for Their Niche</h3>
                <ul class="ideas-list">{ideas_html}</ul>
            </div>''' if ideas_html else ''}

            <div class="pitch-box">
                <h3>✦ AI-Written Outreach DM</h3>
                <p class="pitch-text">{dm_message or 'No message generated.'}</p>
            </div>
        </div>"""

    hook_rewriter_section = _build_hook_rewriter(all_hooks_by_profile, base_url)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Instagram Creator Audit Report — {date_str}</title>
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{ font-family: 'Segoe UI', system-ui, -apple-system, sans-serif; background: #f8fafc; color: #1e293b; }}
  .report-header {{ background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%); color: white; padding: 48px 40px; text-align: center; }}
  .report-header h1 {{ font-size: 2rem; font-weight: 800; margin-bottom: 8px; }}
  .report-header p {{ opacity: 0.85; font-size: 1rem; }}
  .report-meta {{ display: flex; gap: 32px; justify-content: center; margin-top: 24px; flex-wrap: wrap; }}
  .meta-item {{ background: rgba(255,255,255,0.15); padding: 10px 20px; border-radius: 8px; font-size: 0.9rem; }}
  .container {{ max-width: 960px; margin: 0 auto; padding: 40px 20px; }}
  .profile-card {{ background: white; border-radius: 16px; box-shadow: 0 4px 24px rgba(0,0,0,0.08); margin-bottom: 40px; overflow: hidden; }}
  .card-header {{ display: flex; justify-content: space-between; align-items: center; padding: 28px 32px; border-bottom: 1px solid #f1f5f9; flex-wrap: wrap; gap: 16px; }}
  .profile-info {{ display: flex; align-items: center; gap: 16px; }}
  .avatar {{ width: 56px; height: 56px; border-radius: 50%; background: linear-gradient(135deg, #6366f1, #8b5cf6); color: white; display: flex; align-items: center; justify-content: center; font-size: 1.5rem; font-weight: 700; flex-shrink: 0; }}
  .profile-info h2 {{ font-size: 1.4rem; font-weight: 700; color: #1e293b; }}
  .full-name {{ color: #64748b; font-size: 0.9rem; margin-top: 2px; }}
  .opportunity-badge {{ border-radius: 12px; padding: 12px 20px; text-align: center; min-width: 140px; }}
  .opp-score {{ font-size: 2rem; font-weight: 800; line-height: 1; }}
  .opp-label {{ font-size: 0.75rem; font-weight: 600; margin-top: 4px; text-transform: uppercase; letter-spacing: 0.5px; }}
  .stats-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); padding: 24px 32px; gap: 16px; border-bottom: 1px solid #f1f5f9; }}
  @media(max-width:600px) {{ .stats-grid {{ grid-template-columns: repeat(2, 1fr); }} }}
  .stat {{ text-align: center; }}
  .stat-value {{ font-size: 1.4rem; font-weight: 700; color: #1e293b; }}
  .stat-label {{ font-size: 0.75rem; color: #94a3b8; margin-top: 4px; font-weight: 500; }}
  .ai-summary-section {{ padding: 20px 32px; background: linear-gradient(135deg, #faf5ff, #f5f3ff); border-bottom: 1px solid #e9d5ff; }}
  .ai-badge {{ display: inline-block; background: linear-gradient(135deg, #7c3aed, #6366f1); color: white; font-size: 0.7rem; font-weight: 700; padding: 3px 10px; border-radius: 20px; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 10px; }}
  .ai-summary-text {{ font-size: 0.95rem; color: #4c1d95; line-height: 1.7; font-style: italic; }}
  .section {{ padding: 24px 32px; border-bottom: 1px solid #f1f5f9; }}
  .section h3 {{ font-size: 0.95rem; font-weight: 700; color: #475569; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 16px; }}
  .issues-list {{ list-style: none; display: flex; flex-direction: column; gap: 10px; }}
  .issues-list li {{ padding: 10px 14px; background: #fff7ed; border-left: 3px solid #f97316; border-radius: 6px; font-size: 0.9rem; color: #431407; }}
  .ideas-list {{ list-style: none; display: flex; flex-direction: column; gap: 10px; }}
  .ideas-list li {{ padding: 10px 14px; background: #f5f3ff; border-left: 3px solid #8b5cf6; border-radius: 6px; font-size: 0.9rem; color: #2e1065; }}
  .hooks-container {{ display: flex; flex-direction: column; gap: 12px; }}
  .hook-item {{ background: #f8fafc; border-radius: 8px; padding: 14px; border: 1px solid #e2e8f0; }}
  .hook-text {{ font-size: 0.9rem; color: #334155; font-style: italic; margin-bottom: 6px; }}
  .hook-score {{ font-size: 0.8rem; font-weight: 700; }}
  .hook-issue {{ font-size: 0.78rem; color: #ef4444; margin-top: 4px; }}
  .pitch-box {{ padding: 28px 32px; background: linear-gradient(135deg, #ede9fe, #ddd6fe); }}
  .pitch-box h3 {{ font-size: 0.95rem; font-weight: 700; color: #5b21b6; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 14px; }}
  .pitch-text {{ font-size: 0.92rem; color: #4c1d95; line-height: 1.7; }}
  .report-footer {{ text-align: center; padding: 40px 20px; color: #94a3b8; font-size: 0.85rem; }}

  /* Hook Rewriter */
  .rewriter-section {{ background: #0f0f13; border-radius: 20px; margin: 40px 0; overflow: hidden; }}
  .rewriter-header {{ background: linear-gradient(135deg, #7c3aed, #6366f1); padding: 28px 32px; }}
  .rewriter-header h2 {{ color: white; font-size: 1.3rem; font-weight: 800; margin-bottom: 6px; }}
  .rewriter-header p {{ color: rgba(255,255,255,0.75); font-size: 0.875rem; }}
  .rewriter-body {{ padding: 28px 32px; }}
  .profile-group {{ margin-bottom: 24px; }}
  .profile-group-label {{ font-size: 0.75rem; font-weight: 700; color: #6366f1; text-transform: uppercase; letter-spacing: 0.6px; margin-bottom: 12px; }}
  .hook-checkbox-item {{ display: flex; align-items: flex-start; gap: 12px; padding: 12px 16px; background: #18181f; border: 1px solid #2a2a38; border-radius: 10px; margin-bottom: 8px; cursor: pointer; transition: border-color 0.2s; }}
  .hook-checkbox-item:hover {{ border-color: #6366f1; }}
  .hook-checkbox-item input[type="checkbox"] {{ margin-top: 2px; accent-color: #7c3aed; width: 16px; height: 16px; flex-shrink: 0; cursor: pointer; }}
  .hook-checkbox-label {{ font-size: 0.875rem; color: #94a3b8; font-style: italic; line-height: 1.5; cursor: pointer; }}
  .rewrite-btn {{ width: 100%; padding: 16px; background: linear-gradient(135deg, #7c3aed, #6366f1); color: white; border: none; border-radius: 12px; font-size: 1rem; font-weight: 700; cursor: pointer; margin-top: 8px; transition: all 0.2s; font-family: inherit; }}
  .rewrite-btn:hover:not(:disabled) {{ transform: translateY(-1px); box-shadow: 0 8px 32px rgba(124,58,237,0.4); }}
  .rewrite-btn:disabled {{ opacity: 0.6; cursor: not-allowed; transform: none; }}
  .rewrite-spinner {{ display: none; text-align: center; padding: 20px; color: #6366f1; font-size: 0.9rem; }}
  .results-area {{ margin-top: 24px; display: none; }}
  .result-card {{ background: #18181f; border: 1px solid #2a2a38; border-radius: 12px; padding: 20px; margin-bottom: 16px; }}
  .result-original {{ font-size: 0.78rem; color: #4a4a5e; font-style: italic; margin-bottom: 12px; }}
  .result-original span {{ color: #64748b; }}
  .result-label {{ font-size: 0.7rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.6px; color: #7c3aed; margin-bottom: 8px; }}
  .result-text {{ font-size: 1rem; font-weight: 600; color: #f1f5f9; line-height: 1.5; }}
  .copy-result-btn {{ margin-top: 12px; padding: 6px 14px; background: rgba(124,58,237,0.2); border: 1px solid rgba(124,58,237,0.4); color: #a78bfa; border-radius: 8px; font-size: 0.78rem; font-weight: 600; cursor: pointer; font-family: inherit; transition: background 0.2s; }}
  .copy-result-btn:hover {{ background: rgba(124,58,237,0.35); }}
  .no-selection-msg {{ color: #ef4444; font-size: 0.85rem; margin-top: 8px; display: none; text-align: center; }}
</style>
</head>
<body>
<div class="report-header">
  <h1>Instagram Creator Audit Report</h1>
  <p>AI-powered creator analysis — identify leads and pitch your script writing services</p>
  <div class="report-meta">
    <div class="meta-item">Generated: {date_str}</div>
    <div class="meta-item">Profiles Analyzed: {len(profiles)}</div>
    <div class="meta-item">Powered by Google Gemini AI</div>
  </div>
</div>
<div class="container">
  {cards_html}
  {hook_rewriter_section}
</div>
<div class="report-footer">
  <p>Generated by CreatorAudit — AI-Powered Instagram Lead Intelligence</p>
</div>
</body>
</html>"""


def _build_hook_rewriter(hooks_by_profile: list, base_url: str) -> str:
    if not hooks_by_profile:
        return ""

    checkboxes_html = ""
    for group in hooks_by_profile:
        username = group["username"]
        checkboxes_html += f'<div class="profile-group"><div class="profile-group-label">@{username}</div>'
        for i, hook in enumerate(group["hooks"]):
            hook_escaped = hook.replace('"', '&quot;').replace("'", "&#39;")
            checkboxes_html += f'''<label class="hook-checkbox-item">
                <input type="checkbox" class="hook-select" value="{hook_escaped}">
                <span class="hook-checkbox-label">"{hook_escaped}"</span>
            </label>'''
        checkboxes_html += '</div>'

    api_url = base_url + "/api/rewrite-hook"

    return f"""
<div class="rewriter-section">
  <div class="rewriter-header">
    <h2>✦ Hook Rewriter</h2>
    <p>Select hooks from the analysis below, then click Rewrite. AI rewrites and humanises each one — only the final human-sounding version is shown.</p>
  </div>
  <div class="rewriter-body">
    {checkboxes_html}
    <p class="no-selection-msg" id="noSelMsg">Please select at least one hook to rewrite.</p>
    <button class="rewrite-btn" id="rewriteBtn" onclick="rewriteHooks()">✦ Rewrite Selected Hooks</button>
    <div class="rewrite-spinner" id="rewriteSpinner">⟳ &nbsp;AI is rewriting and humanising your hooks... this takes a few seconds</div>
    <div class="results-area" id="resultsArea"></div>
  </div>
</div>

<script>
async function rewriteHooks() {{
  const checked = Array.from(document.querySelectorAll('.hook-select:checked')).map(el => el.value);
  const noSel = document.getElementById('noSelMsg');
  if (checked.length === 0) {{
    noSel.style.display = 'block';
    return;
  }}
  noSel.style.display = 'none';

  const btn = document.getElementById('rewriteBtn');
  const spinner = document.getElementById('rewriteSpinner');
  const area = document.getElementById('resultsArea');

  btn.disabled = true;
  spinner.style.display = 'block';
  area.style.display = 'none';
  area.innerHTML = '';

  try {{
    const res = await fetch('{api_url}', {{
      method: 'POST',
      headers: {{ 'Content-Type': 'application/json' }},
      body: JSON.stringify({{ hooks: checked }})
    }});
    const data = await res.json();
    if (data.error) throw new Error(data.error);

    let html = '';
    (data.results || []).forEach(r => {{
      html += '<div class="result-card">'
             + '<div class="result-original">Original: <span>' + escHtml(r.original) + '</span></div>'
             + '<div class="result-label">✦ Rewritten &amp; Humanised</div>'
             + '<div class="result-text" id="rt-' + Math.random().toString(36).slice(2) + '">' + escHtml(r.rewritten) + '</div>'
             + '<button class="copy-result-btn" onclick="copyText(this, \'' + escAttr(r.rewritten) + '\')">Copy</button>'
             + '</div>';
    }});

    area.innerHTML = html;
    area.style.display = 'block';
  }} catch(err) {{
    area.innerHTML = '<div style="color:#ef4444;font-size:0.875rem;padding:12px">Error: ' + escHtml(err.message) + '. Make sure you are online and the app is running.</div>';
    area.style.display = 'block';
  }} finally {{
    btn.disabled = false;
    spinner.style.display = 'none';
  }}
}}

function copyText(btn, text) {{
  navigator.clipboard.writeText(text).then(() => {{
    btn.textContent = 'Copied!';
    setTimeout(() => btn.textContent = 'Copy', 2000);
  }});
}}

function escHtml(str) {{
  return String(str).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}}

function escAttr(str) {{
  return String(str).replace(/\\\\/g,'\\\\\\\\').replace(/'/g,"\\\\'");
}}
</script>"""


def format_number(n: int) -> str:
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M"
    elif n >= 1_000:
        return f"{n / 1_000:.1f}K"
    return str(n)
