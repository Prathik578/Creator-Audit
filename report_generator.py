from datetime import datetime


def generate_report_html(profiles: list) -> str:
    date_str = datetime.now().strftime("%B %d, %Y")
    cards_html = ""

    for p in profiles:
        analysis = p.get("analysis", {})
        issues_html = "".join(f'<li>{i}</li>' for i in analysis.get("top_issues", []))
        recs_html = "".join(f'<li>{r}</li>' for r in analysis.get("recommendations", []))
        hooks_html = ""
        for hb in analysis.get("hook_breakdown", [])[:4]:
            score = hb.get("score", 0)
            color = "#22c55e" if score >= 70 else "#f59e0b" if score >= 45 else "#ef4444"
            hooks_html += f"""
            <div class="hook-item">
                <div class="hook-text">"{hb.get('hook', 'N/A')}"</div>
                <div class="hook-score" style="color:{color}">Score: {score}/100</div>
                {'<div class="hook-issue">' + hb['issues'][0] + '</div>' if hb.get('issues') else ''}
            </div>"""

        opp_score = analysis.get("opportunity_score", 0)
        opp_label = analysis.get("opportunity_label", "Unknown")
        if opp_score >= 75:
            opp_color = "#ef4444"
            opp_bg = "#fef2f2"
        elif opp_score >= 50:
            opp_color = "#f59e0b"
            opp_bg = "#fffbeb"
        else:
            opp_color = "#22c55e"
            opp_bg = "#f0fdf4"

        engagement = analysis.get("engagement_rate", 0)
        hook_score = analysis.get("hook_score", 0)
        hook_quality = analysis.get("hook_quality", "N/A")

        cards_html += f"""
        <div class="profile-card">
            <div class="card-header">
                <div class="profile-info">
                    <div class="avatar">@{p.get('username', '?')[0].upper()}</div>
                    <div>
                        <h2>@{p.get('username', 'unknown')}</h2>
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

            <div class="section">
                <h3>Key Issues Identified</h3>
                <ul class="issues-list">{issues_html}</ul>
            </div>

            <div class="section">
                <h3>Recent Hook Analysis</h3>
                <div class="hooks-container">{hooks_html}</div>
            </div>

            <div class="section pitch-section">
                <h3>Your Pitch Talking Points</h3>
                <ul class="recs-list">{recs_html}</ul>
            </div>

            <div class="pitch-box">
                <h3>Suggested Outreach Message</h3>
                <p class="pitch-text">
                    "Hey {p.get('full_name', '@' + p.get('username', ''))}! I've been looking at your content and I love what you're building.
                    I noticed your engagement could be pushed higher — specifically your hooks aren't grabbing attention as fast as they could.
                    I help creators like you with scroll-stopping hooks and viral content ideas. Would you be open to seeing a free sample script for one of your upcoming posts?"
                </p>
            </div>
        </div>"""

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
  .section {{ padding: 24px 32px; border-bottom: 1px solid #f1f5f9; }}
  .section h3 {{ font-size: 0.95rem; font-weight: 700; color: #475569; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 16px; }}
  .issues-list {{ list-style: none; display: flex; flex-direction: column; gap: 10px; }}
  .issues-list li {{ padding: 10px 14px; background: #fff7ed; border-left: 3px solid #f97316; border-radius: 6px; font-size: 0.9rem; color: #431407; }}
  .recs-list {{ list-style: none; display: flex; flex-direction: column; gap: 10px; }}
  .recs-list li {{ padding: 10px 14px; background: #f0fdf4; border-left: 3px solid #22c55e; border-radius: 6px; font-size: 0.9rem; color: #14532d; }}
  .hooks-container {{ display: flex; flex-direction: column; gap: 12px; }}
  .hook-item {{ background: #f8fafc; border-radius: 8px; padding: 14px; border: 1px solid #e2e8f0; }}
  .hook-text {{ font-size: 0.9rem; color: #334155; font-style: italic; margin-bottom: 6px; }}
  .hook-score {{ font-size: 0.8rem; font-weight: 700; }}
  .hook-issue {{ font-size: 0.78rem; color: #ef4444; margin-top: 4px; }}
  .pitch-section {{ background: #fafafa; }}
  .pitch-box {{ padding: 28px 32px; background: linear-gradient(135deg, #ede9fe, #ddd6fe); }}
  .pitch-box h3 {{ font-size: 0.95rem; font-weight: 700; color: #5b21b6; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 14px; }}
  .pitch-text {{ font-size: 0.92rem; color: #4c1d95; line-height: 1.7; font-style: italic; }}
  .report-footer {{ text-align: center; padding: 40px 20px; color: #94a3b8; font-size: 0.85rem; }}
</style>
</head>
<body>
<div class="report-header">
  <h1>Instagram Creator Audit Report</h1>
  <p>Identify low-performing creators and turn their weaknesses into your sales pitch</p>
  <div class="report-meta">
    <div class="meta-item">Generated: {date_str}</div>
    <div class="meta-item">Profiles Analyzed: {len(profiles)}</div>
    <div class="meta-item">Service: Script Writing & Idea Generation</div>
  </div>
</div>
<div class="container">
  {cards_html}
</div>
<div class="report-footer">
  <p>Generated by CreatorAudit — Instagram Performance Intelligence Tool</p>
</div>
</body>
</html>"""


def format_number(n: int) -> str:
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M"
    elif n >= 1_000:
        return f"{n / 1_000:.1f}K"
    return str(n)
