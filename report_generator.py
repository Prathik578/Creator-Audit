from datetime import datetime
import json


def _esc(s):
    return str(s or '').replace('&','&amp;').replace('<','&lt;').replace('>','&gt;').replace('"','&quot;')


def _exec_summary_html(exec_summary: dict) -> str:
    if not exec_summary or not exec_summary.get("position"):
        return ""
    pos = _esc(exec_summary.get("position",""))
    blk = _esc(exec_summary.get("blocker",""))
    opp = _esc(exec_summary.get("opportunity",""))
    dire = _esc(exec_summary.get("direction",""))
    return f"""<div style="padding:24px 32px;border-bottom:1px solid #f1f5f9;background:linear-gradient(135deg,#faf5ff,#f5f3ff)">
      <div style="display:inline-block;background:linear-gradient(135deg,#7c3aed,#6366f1);color:white;font-size:0.68rem;font-weight:700;padding:3px 10px;border-radius:20px;text-transform:uppercase;letter-spacing:0.5px;margin-bottom:14px">✦ Executive Summary</div>
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px">
        <div style="background:white;border:1px solid #e2e8f0;border-radius:10px;padding:14px">
          <div style="font-size:0.66rem;font-weight:700;color:#94a3b8;text-transform:uppercase;letter-spacing:0.5px;margin-bottom:6px">Current Position</div>
          <div style="font-size:0.84rem;color:#1e293b;line-height:1.5">{pos}</div>
        </div>
        <div style="background:white;border:1px solid #fecaca;border-radius:10px;padding:14px">
          <div style="font-size:0.66rem;font-weight:700;color:#dc2626;text-transform:uppercase;letter-spacing:0.5px;margin-bottom:6px">⚡ Growth Blocker</div>
          <div style="font-size:0.84rem;color:#1e293b;line-height:1.5">{blk}</div>
        </div>
        <div style="background:white;border:1px solid #bbf7d0;border-radius:10px;padding:14px">
          <div style="font-size:0.66rem;font-weight:700;color:#16a34a;text-transform:uppercase;letter-spacing:0.5px;margin-bottom:6px">✦ Top Opportunity</div>
          <div style="font-size:0.84rem;color:#1e293b;line-height:1.5">{opp}</div>
        </div>
        <div style="background:white;border:1px solid #ede9fe;border-radius:10px;padding:14px">
          <div style="font-size:0.66rem;font-weight:700;color:#7c3aed;text-transform:uppercase;letter-spacing:0.5px;margin-bottom:6px">→ Strategic Direction</div>
          <div style="font-size:0.84rem;color:#1e293b;line-height:1.5">{dire}</div>
        </div>
      </div>
    </div>"""


def _qw_pf_html(quick_wins: list, priority_fixes: list) -> str:
    if not quick_wins and not priority_fixes:
        return ""
    qw_items = ''.join(f'<li style="display:flex;align-items:flex-start;gap:8px;margin-bottom:8px;font-size:0.84rem;color:#166534;line-height:1.5"><span style="color:#22c55e;flex-shrink:0;margin-top:1px">✓</span>{_esc(w)}</li>' for w in quick_wins)
    pf_items = ''.join(f'<li style="display:flex;align-items:flex-start;gap:8px;margin-bottom:8px;font-size:0.84rem;color:#991b1b;line-height:1.5"><span style="color:#ef4444;flex-shrink:0;margin-top:1px">✕</span>{_esc(f)}</li>' for f in priority_fixes)
    return f"""<div style="padding:24px 32px;border-bottom:1px solid #f1f5f9">
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:14px">
        <div style="background:#f0fdf4;border:1px solid #bbf7d0;border-radius:12px;padding:16px">
          <div style="font-size:0.7rem;font-weight:700;color:#16a34a;text-transform:uppercase;letter-spacing:0.5px;margin-bottom:12px">⚡ Quick Wins</div>
          <ul style="list-style:none">{qw_items}</ul>
        </div>
        <div style="background:#fef2f2;border:1px solid #fecaca;border-radius:12px;padding:16px">
          <div style="font-size:0.7rem;font-weight:700;color:#dc2626;text-transform:uppercase;letter-spacing:0.5px;margin-bottom:12px">🔴 Priority Fixes</div>
          <ul style="list-style:none">{pf_items}</ul>
        </div>
      </div>
    </div>"""


def _lt_html(long_term: list) -> str:
    if not long_term:
        return ""
    cards = ''.join(f'<div style="background:#f8fafc;border:1px solid #e2e8f0;border-radius:12px;padding:16px"><div style="font-size:1.4rem;font-weight:800;color:#c4b5fd;line-height:1;margin-bottom:8px">0{i+1}</div><div style="font-size:0.84rem;color:#1e293b;line-height:1.55">{_esc(lt)}</div></div>' for i, lt in enumerate(long_term))
    return f"""<div style="padding:24px 32px;border-bottom:1px solid #f1f5f9">
      <div class="section-title">Long-Term Growth Opportunities</div>
      <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:12px">{cards}</div>
    </div>"""


def _checklist_html(items: list) -> str:
    if not items:
        return ""
    rows = ''.join(f'<div style="display:flex;align-items:flex-start;gap:10px;padding:10px 12px;background:#f8fafc;border:1px solid #e2e8f0;border-radius:10px;margin-bottom:6px"><div style="width:16px;height:16px;border:2px solid #7c3aed;border-radius:4px;flex-shrink:0;margin-top:1px"></div><div style="font-size:0.84rem;color:#334155;line-height:1.45">{_esc(item)}</div></div>' for item in items)
    return f"""<div style="padding:24px 32px;border-bottom:1px solid #f1f5f9">
      <div class="section-title">Weekly Growth Checklist</div>
      {rows}
    </div>"""


def generate_report_html(profiles: list, base_url: str = "") -> str:
    date_str = datetime.now().strftime("%B %d, %Y")
    cards_html = ""
    all_hooks_by_profile = []

    for p in profiles:
        analysis = p.get("analysis", {})
        ai = p.get("ai_insights", {})
        username = p.get("username", "unknown")

        profile_hooks = []
        hooks_rows = ""
        for hb in analysis.get("hook_breakdown", [])[:4]:
            score = hb.get("score", 0)
            hook_text = hb.get("hook", "")
            color = "#22c55e" if score >= 70 else "#f59e0b" if score >= 45 else "#ef4444"
            bar_w = score
            hooks_rows += f"""<tr>
              <td style="padding:10px 0;font-size:0.85rem;color:#94a3b8;font-style:italic;border-bottom:1px solid #e2e8f0">"{_esc(hook_text)}"</td>
              <td style="padding:10px 0 10px 12px;border-bottom:1px solid #e2e8f0;white-space:nowrap">
                <span style="display:inline-block;padding:3px 10px;border-radius:20px;font-size:0.75rem;font-weight:700;background:{color}22;color:{color}">{score}/100</span>
              </td>
            </tr>"""
            if hook_text:
                profile_hooks.append(hook_text)

        if profile_hooks:
            all_hooks_by_profile.append({"username": username, "hooks": profile_hooks})

        issues_html = "".join(
            f'<li style="padding:8px 12px;background:#fff7ed;border-left:3px solid #f97316;border-radius:6px;font-size:0.85rem;color:#431407;margin-bottom:8px">{_esc(i)}</li>'
            for i in analysis.get("top_issues", [])
        )

        strengths_html = "".join(
            f'<li style="padding:6px 0;font-size:0.85rem;color:#166534;display:flex;gap:8px"><span style="color:#16a34a;flex-shrink:0">✓</span>{_esc(s)}</li>'
            for s in ai.get("strengths", [])
        )
        weaknesses_html = "".join(
            f'<li style="padding:6px 0;font-size:0.85rem;color:#991b1b;display:flex;gap:8px"><span style="color:#dc2626;flex-shrink:0">✕</span>{_esc(w)}</li>'
            for w in ai.get("weaknesses", [])
        )
        opps_html = "".join(
            f'<li style="padding:6px 0;font-size:0.85rem;color:#1e3a5f;display:flex;gap:8px"><span style="color:#7c3aed;flex-shrink:0">✦</span>{_esc(o)}</li>'
            for o in ai.get("opportunities", [])
        )

        action_plan_html = ""
        for i, action in enumerate(ai.get("action_plan", [])):
            action_plan_html += f"""<div style="display:flex;gap:14px;align-items:flex-start;padding:12px 0;border-bottom:1px solid #f1f5f9">
              <div style="width:32px;height:32px;border-radius:8px;background:#ede9fe;color:#7c3aed;font-size:0.7rem;font-weight:700;display:flex;align-items:center;justify-content:center;flex-shrink:0">D{i+1}</div>
              <div style="font-size:0.875rem;color:#334155;line-height:1.5;padding-top:6px">{_esc(action)}</div>
            </div>"""

        ideas_html = ""
        for idx, idea in enumerate(ai.get("content_ideas", [])):
            ideas_html += f"""<div style="display:flex;gap:10px;align-items:flex-start;background:#f5f3ff;border:1px solid #ede9fe;border-radius:10px;padding:12px 14px;margin-bottom:8px">
              <span style="color:#7c3aed;font-weight:800;font-size:1rem;flex-shrink:0">{idx+1}</span>
              <span style="font-size:0.875rem;color:#4c1d95;line-height:1.5">{_esc(idea)}</span>
            </div>"""

        aud = ai.get("audience_analysis", {})

        overall = ai.get("overall_score", 0)
        branding = ai.get("branding_score", 0)
        eng_sc = ai.get("engagement_score", 0)
        consist = ai.get("consistency_score", 0)
        growth = ai.get("growth_score", 0)
        overall_color = "#22c55e" if overall >= 70 else "#f59e0b" if overall >= 45 else "#ef4444"

        engagement = analysis.get("engagement_rate", 0)
        followers = p.get("followers", 0)
        hook_score = analysis.get("hook_score", 0)
        hook_quality = analysis.get("hook_quality", "N/A")
        opp_score = analysis.get("opportunity_score", 0)
        opp_label = analysis.get("opportunity_label", "Unknown")
        consistency = analysis.get("posting_consistency", "Unknown")
        confidence = ai.get("confidence_level", "Medium")
        audit_summary = ai.get("audit_summary", "")
        dm_message = ai.get("dm_message", "")
        content_strategy = ai.get("content_strategy", "")

        if opp_score >= 75:
            opp_color = "#ef4444"; opp_bg = "#fef2f2"
        elif opp_score >= 50:
            opp_color = "#f59e0b"; opp_bg = "#fffbeb"
        else:
            opp_color = "#22c55e"; opp_bg = "#f0fdf4"

        conf_color = "#16a34a" if confidence == "High" else "#d97706" if confidence == "Medium" else "#dc2626"
        conf_bg = "#f0fdf4" if confidence == "High" else "#fffbeb" if confidence == "Medium" else "#fef2f2"

        bench_level = 2 if (followers > 100000 or engagement > 5) else 1 if (followers > 10000 and engagement >= 1) else 0
        bench_labels = ["Beginner Creator", "Growing Creator", "Advanced Creator"]

        cards_html += f"""
        <div class="profile-card">
          <div style="display:flex;justify-content:space-between;align-items:flex-start;padding:28px 32px;border-bottom:1px solid #f1f5f9;flex-wrap:wrap;gap:16px">
            <div style="display:flex;align-items:center;gap:16px">
              <div style="width:56px;height:56px;border-radius:50%;background:linear-gradient(135deg,#6366f1,#8b5cf6);color:white;display:flex;align-items:center;justify-content:center;font-size:1.5rem;font-weight:700;flex-shrink:0">{username[0].upper()}</div>
              <div>
                <h2 style="font-size:1.3rem;font-weight:700;color:#1e293b">@{_esc(username)}</h2>
                <div style="color:#64748b;font-size:0.85rem;margin-top:4px;display:flex;align-items:center;gap:8px;flex-wrap:wrap">
                  {_esc(p.get('full_name',''))}
                  <span style="background:#ede9fe;color:#7c3aed;padding:2px 8px;border-radius:20px;font-size:0.72rem;font-weight:600">{_esc(consistency)}</span>
                  <span style="background:{conf_bg};color:{conf_color};padding:2px 8px;border-radius:20px;font-size:0.72rem;font-weight:600">{confidence} Confidence</span>
                </div>
              </div>
            </div>
            <div style="background:{opp_bg};color:{opp_color};border:2px solid {opp_color};border-radius:12px;padding:12px 20px;text-align:center;min-width:140px">
              <div style="font-size:2rem;font-weight:800;line-height:1">{opp_score}</div>
              <div style="font-size:0.72rem;font-weight:600;margin-top:4px;text-transform:uppercase;letter-spacing:0.5px">{_esc(opp_label)}</div>
            </div>
          </div>

          <div style="padding:24px 32px;border-bottom:1px solid #f1f5f9">
            <div style="display:grid;grid-template-columns:auto 1fr;gap:24px;align-items:center">
              <div style="text-align:center">
                {_svg_circle(overall, overall_color, 42, 110)}
                <div style="font-size:0.68rem;font-weight:700;text-transform:uppercase;letter-spacing:0.5px;color:#64748b;margin-top:6px">Overall Score</div>
              </div>
              <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px">
                {_score_bar_html("Branding", branding)}
                {_score_bar_html("Engagement", eng_sc)}
                {_score_bar_html("Consistency", consist)}
                {_score_bar_html("Growth", growth)}
              </div>
            </div>
          </div>

          <div style="padding:16px 32px;border-bottom:1px solid #f1f5f9">
            <div style="font-size:0.68rem;font-weight:700;text-transform:uppercase;letter-spacing:0.6px;color:#64748b;margin-bottom:10px">Creator Benchmark</div>
            <div style="display:flex;border-radius:8px;overflow:hidden;border:1px solid #e2e8f0">
              {''.join(f'<div style="flex:1;padding:10px;text-align:center;background:{"#ede9fe" if i==bench_level else "#f8fafc"};border-right:{"none" if i==2 else "1px solid #e2e8f0"}"><div style="font-size:0.72rem;font-weight:700;color:{"#7c3aed" if i==bench_level else "#94a3b8"};text-transform:uppercase;letter-spacing:0.4px">{_esc(bench_labels[i])}</div><div style="width:6px;height:6px;border-radius:50%;background:{"#7c3aed" if i==bench_level else "#e2e8f0"};margin:6px auto 0"></div></div>' for i in range(3))}
            </div>
          </div>

          {_exec_summary_html(ai.get("executive_summary", {}))}

          <div style="padding:24px 32px;border-bottom:1px solid #f1f5f9">
            <div class="section-title">✦ AI Audit Summary</div>
            <div style="background:linear-gradient(135deg,#faf5ff,#f5f3ff);border:1px solid #e9d5ff;border-radius:12px;padding:18px">
              <div style="display:inline-block;background:linear-gradient(135deg,#7c3aed,#6366f1);color:white;font-size:0.7rem;font-weight:700;padding:3px 10px;border-radius:20px;text-transform:uppercase;letter-spacing:0.5px;margin-bottom:10px">✦ Gemini AI</div>
              <p style="font-size:0.9rem;color:#4c1d95;line-height:1.75;font-style:italic">{_esc(audit_summary)}</p>
            </div>
          </div>

          {_qw_pf_html(ai.get("quick_wins", []), ai.get("priority_fixes", []))}

          {'<div style="padding:24px 32px;border-bottom:1px solid #f1f5f9"><div class="section-title">Strengths · Weaknesses · Opportunities</div><div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:12px">' +
            f'<div style="background:#f0fdf4;border:1px solid #bbf7d0;border-radius:12px;padding:16px"><div style="font-size:0.72rem;font-weight:700;color:#16a34a;text-transform:uppercase;letter-spacing:0.5px;margin-bottom:10px">✓ Strengths</div><ul style="list-style:none">{strengths_html}</ul></div>' +
            f'<div style="background:#fef2f2;border:1px solid #fecaca;border-radius:12px;padding:16px"><div style="font-size:0.72rem;font-weight:700;color:#dc2626;text-transform:uppercase;letter-spacing:0.5px;margin-bottom:10px">✕ Weaknesses</div><ul style="list-style:none">{weaknesses_html}</ul></div>' +
            f'<div style="background:#f5f3ff;border:1px solid #ede9fe;border-radius:12px;padding:16px"><div style="font-size:0.72rem;font-weight:700;color:#7c3aed;text-transform:uppercase;letter-spacing:0.5px;margin-bottom:10px">✦ Opportunities</div><ul style="list-style:none">{opps_html}</ul></div>' +
            '</div></div>' if (strengths_html or weaknesses_html or opps_html) else ''}

          {f'<div style="padding:24px 32px;border-bottom:1px solid #f1f5f9"><div class="section-title">Content Strategy</div><div style="background:#f5f3ff;border:1px solid #ede9fe;border-radius:10px;padding:14px 16px;font-size:0.9rem;color:#4c1d95;line-height:1.75">{_esc(content_strategy)}</div></div>' if content_strategy else ''}

          {f'<div style="padding:24px 32px;border-bottom:1px solid #f1f5f9"><div class="section-title">7-Day Action Plan</div>{action_plan_html}</div>' if action_plan_html else ''}

          {f'<div style="padding:24px 32px;border-bottom:1px solid #f1f5f9"><div class="section-title">AI Content Ideas</div>{ideas_html}</div>' if ideas_html else ''}

          {_lt_html(ai.get("long_term_opportunities", []))}

          {_checklist_html(ai.get("weekly_checklist", []))}

          {f'''<div style="padding:24px 32px;border-bottom:1px solid #f1f5f9"><div class="section-title">Audience Analysis</div>
            <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:12px">
              <div style="background:#f8fafc;border:1px solid #e2e8f0;border-radius:12px;padding:14px"><div style="font-size:0.68rem;font-weight:700;color:#64748b;text-transform:uppercase;letter-spacing:0.5px;margin-bottom:8px">Audience Type</div><div style="font-size:0.82rem;color:#334155;line-height:1.5">{_esc(aud.get("type",""))}</div></div>
              <div style="background:#f8fafc;border:1px solid #e2e8f0;border-radius:12px;padding:14px"><div style="font-size:0.68rem;font-weight:700;color:#64748b;text-transform:uppercase;letter-spacing:0.5px;margin-bottom:8px">Engagement Behavior</div><div style="font-size:0.82rem;color:#334155;line-height:1.5">{_esc(aud.get("behavior",""))}</div></div>
              <div style="background:#f8fafc;border:1px solid #e2e8f0;border-radius:12px;padding:14px"><div style="font-size:0.68rem;font-weight:700;color:#64748b;text-transform:uppercase;letter-spacing:0.5px;margin-bottom:8px">Content Preference</div><div style="font-size:0.82rem;color:#334155;line-height:1.5">{_esc(aud.get("preference",""))}</div></div>
            </div>
          </div>''' if aud.get("type") else ''}

          {f'<div style="padding:24px 32px;border-bottom:1px solid #f1f5f9"><div class="section-title">Recent Hook Analysis</div><table style="width:100%;border-collapse:collapse">{hooks_rows}</table></div>' if hooks_rows else ''}

          {f'<div style="padding:24px 32px;border-bottom:1px solid #f1f5f9"><div class="section-title">Key Issues</div><ul style="list-style:none">{issues_html}</ul></div>' if issues_html else ''}

          <div style="padding:28px 32px;background:linear-gradient(135deg,#ede9fe,#ddd6fe)">
            <div style="font-size:0.75rem;font-weight:700;color:#5b21b6;text-transform:uppercase;letter-spacing:0.5px;margin-bottom:14px">✦ AI-Written Outreach DM</div>
            <p style="font-size:0.9rem;color:#4c1d95;line-height:1.75;font-style:italic">{_esc(dm_message) if dm_message else 'No message generated.'}</p>
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
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  body {{ font-family:'Segoe UI',system-ui,-apple-system,sans-serif; background:#f8fafc; color:#1e293b; }}
  .report-header {{ background:linear-gradient(135deg,#6366f1 0%,#8b5cf6 100%); color:white; padding:48px 40px; text-align:center; }}
  .report-header h1 {{ font-size:2rem; font-weight:800; margin-bottom:8px; }}
  .report-header p {{ opacity:0.85; font-size:1rem; }}
  .report-meta {{ display:flex; gap:24px; justify-content:center; margin-top:24px; flex-wrap:wrap; }}
  .meta-item {{ background:rgba(255,255,255,0.15); padding:8px 18px; border-radius:8px; font-size:0.85rem; }}
  .container {{ max-width:980px; margin:0 auto; padding:40px 20px; }}
  .profile-card {{ background:white; border-radius:20px; box-shadow:0 4px 24px rgba(0,0,0,0.08); margin-bottom:48px; overflow:hidden; }}
  .section-title {{ font-size:0.75rem; font-weight:700; color:#475569; text-transform:uppercase; letter-spacing:0.6px; margin-bottom:16px; display:flex; align-items:center; gap:8px; }}
  .section-title::before {{ content:''; display:inline-block; width:3px; height:14px; border-radius:2px; background:#7c3aed; }}
  .report-footer {{ text-align:center; padding:40px 20px; color:#94a3b8; font-size:0.85rem; }}

  /* Hook Rewriter */
  .rewriter-section {{ background:#0f0f13; border-radius:20px; margin:0 0 40px; overflow:hidden; }}
  .rewriter-header {{ background:linear-gradient(135deg,#7c3aed,#6366f1); padding:28px 32px; }}
  .rewriter-header h2 {{ color:white; font-size:1.3rem; font-weight:800; margin-bottom:6px; }}
  .rewriter-header p {{ color:rgba(255,255,255,0.75); font-size:0.875rem; }}
  .rewriter-body {{ padding:28px 32px; }}
  .profile-group {{ margin-bottom:24px; }}
  .profile-group-label {{ font-size:0.75rem; font-weight:700; color:#6366f1; text-transform:uppercase; letter-spacing:0.6px; margin-bottom:12px; }}
  .hook-checkbox-item {{ display:flex; align-items:flex-start; gap:12px; padding:12px 16px; background:#18181f; border:1px solid #2a2a38; border-radius:10px; margin-bottom:8px; cursor:pointer; transition:border-color 0.2s; }}
  .hook-checkbox-item:hover {{ border-color:#6366f1; }}
  .hook-checkbox-item input {{ margin-top:2px; accent-color:#7c3aed; width:16px; height:16px; flex-shrink:0; cursor:pointer; }}
  .hook-checkbox-label {{ font-size:0.875rem; color:#94a3b8; font-style:italic; line-height:1.5; cursor:pointer; }}
  .rewrite-btn {{ width:100%; padding:16px; background:linear-gradient(135deg,#7c3aed,#6366f1); color:white; border:none; border-radius:12px; font-size:1rem; font-weight:700; cursor:pointer; margin-top:8px; transition:all 0.2s; font-family:inherit; }}
  .rewrite-btn:hover:not(:disabled) {{ transform:translateY(-1px); box-shadow:0 8px 32px rgba(124,58,237,0.4); }}
  .rewrite-btn:disabled {{ opacity:0.6; cursor:not-allowed; }}
  .rewrite-spinner {{ display:none; text-align:center; padding:20px; color:#6366f1; font-size:0.9rem; }}
  .results-area {{ margin-top:24px; display:none; }}
  .result-card {{ background:#18181f; border:1px solid #2a2a38; border-radius:12px; padding:20px; margin-bottom:16px; }}
  .result-original {{ font-size:0.78rem; color:#4a4a5e; font-style:italic; margin-bottom:12px; }}
  .result-label {{ font-size:0.7rem; font-weight:700; text-transform:uppercase; letter-spacing:0.6px; color:#7c3aed; margin-bottom:8px; }}
  .result-text {{ font-size:1rem; font-weight:600; color:#f1f5f9; line-height:1.5; }}
  .copy-result-btn {{ margin-top:12px; padding:6px 14px; background:rgba(124,58,237,0.2); border:1px solid rgba(124,58,237,0.4); color:#a78bfa; border-radius:8px; font-size:0.78rem; font-weight:600; cursor:pointer; font-family:inherit; transition:background 0.2s; }}
  .copy-result-btn:hover {{ background:rgba(124,58,237,0.35); }}
  .no-sel-msg {{ color:#ef4444; font-size:0.85rem; margin-top:8px; display:none; text-align:center; }}
</style>
</head>
<body>
<div class="report-header">
  <h1>Instagram Creator Audit Report</h1>
  <p>AI-powered premium creator analysis — identify leads and pitch your script writing services</p>
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


def _svg_circle(score: int, color: str, r: int, size: int) -> str:
    circ = 2 * 3.14159 * r
    fill = (score / 100) * circ
    sw = 9
    cx = cy = size // 2
    font_size = 20
    return (f'<svg viewBox="0 0 {size} {size}" width="{size}" height="{size}">'
            f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="#e2e8f0" stroke-width="{sw}"/>'
            f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{color}" stroke-width="{sw}" '
            f'stroke-linecap="round" stroke-dasharray="{fill:.1f} {circ:.1f}" transform="rotate(-90 {cx} {cy})"/>'
            f'<text x="{cx}" y="{cy+7}" text-anchor="middle" fill="#1e293b" font-size="{font_size}" '
            f'font-weight="700" font-family="Segoe UI,system-ui,sans-serif">{score}</text>'
            f'</svg>')


def _score_bar_html(label: str, score: int) -> str:
    color = "#22c55e" if score >= 70 else "#f59e0b" if score >= 45 else "#ef4444"
    return (f'<div style="background:#f8fafc;border:1px solid #e2e8f0;border-radius:10px;padding:12px 14px">'
            f'<div style="display:flex;justify-content:space-between;margin-bottom:6px">'
            f'<span style="font-size:0.72rem;font-weight:600;color:#64748b;text-transform:uppercase;letter-spacing:0.4px">{label}</span>'
            f'<span style="font-size:0.85rem;font-weight:700;color:{color}">{score}</span>'
            f'</div>'
            f'<div style="background:#e2e8f0;border-radius:100px;height:5px">'
            f'<div style="height:5px;border-radius:100px;background:{color};width:{score}%"></div>'
            f'</div></div>')


def _build_hook_rewriter(hooks_by_profile: list, base_url: str) -> str:
    if not hooks_by_profile:
        return ""

    checkboxes_html = ""
    for group in hooks_by_profile:
        username = group["username"]
        checkboxes_html += f'<div class="profile-group"><div class="profile-group-label">@{_esc(username)}</div>'
        for hook in group["hooks"]:
            hook_esc = hook.replace('"', '&quot;').replace("'", "&#39;")
            checkboxes_html += f'''<label class="hook-checkbox-item">
                <input type="checkbox" class="hook-select" value="{hook_esc}">
                <span class="hook-checkbox-label">"{hook_esc}"</span>
            </label>'''
        checkboxes_html += '</div>'

    api_url = base_url + "/api/rewrite-hook"

    return f"""
<div class="rewriter-section">
  <div class="rewriter-header">
    <h2>✦ Hook Rewriter</h2>
    <p>Select hooks from the analysis above, then click Rewrite. Two-pass AI rewrites then humanises each hook — only the final natural-sounding version is shown.</p>
  </div>
  <div class="rewriter-body">
    {checkboxes_html}
    <p class="no-sel-msg" id="noSelMsg">Please select at least one hook to rewrite.</p>
    <button class="rewrite-btn" id="rewriteBtn" onclick="rewriteHooks()">✦ Rewrite Selected Hooks</button>
    <div class="rewrite-spinner" id="rewriteSpinner">⟳ &nbsp;AI is rewriting and humanising your hooks — this takes a few seconds</div>
    <div class="results-area" id="resultsArea"></div>
  </div>
</div>

<script>
async function rewriteHooks() {{
  const checked = Array.from(document.querySelectorAll('.hook-select:checked')).map(el => el.value);
  const noSel = document.getElementById('noSelMsg');
  if (checked.length === 0) {{ noSel.style.display = 'block'; return; }}
  noSel.style.display = 'none';
  const btn = document.getElementById('rewriteBtn');
  const spinner = document.getElementById('rewriteSpinner');
  const area = document.getElementById('resultsArea');
  btn.disabled = true; spinner.style.display = 'block'; area.style.display = 'none'; area.innerHTML = '';
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
      const id = 'r' + Math.random().toString(36).slice(2);
      html += '<div class="result-card">'
            + '<div class="result-original">Original: ' + escHtml(r.original) + '</div>'
            + '<div class="result-label">✦ Rewritten &amp; Humanised</div>'
            + '<div class="result-text" id="' + id + '">' + escHtml(r.rewritten) + '</div>'
            + '<button class="copy-result-btn" onclick="copyHook(\\'' + id + '\\')">Copy</button>'
            + '</div>';
    }});
    area.innerHTML = html; area.style.display = 'block';
  }} catch(err) {{
    area.innerHTML = '<div style="color:#ef4444;font-size:0.875rem;padding:12px">Error: ' + escHtml(err.message) + '. Make sure you are online and the app is running.</div>';
    area.style.display = 'block';
  }} finally {{
    btn.disabled = false; spinner.style.display = 'none';
  }}
}}
function copyHook(id) {{
  const el = document.getElementById(id);
  if (!el) return;
  navigator.clipboard.writeText(el.textContent).then(() => {{
    const btn = el.nextElementSibling;
    if (btn) {{ btn.textContent = 'Copied!'; setTimeout(() => btn.textContent = 'Copy', 2000); }}
  }});
}}
function escHtml(str) {{
  return String(str||'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}}
</script>"""




def format_number(n: int) -> str:
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M"
    elif n >= 1_000:
        return f"{n / 1_000:.1f}K"
    return str(n)
