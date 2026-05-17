import os
from google import genai

GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY", "")


def _get_client():
    if not GOOGLE_API_KEY:
        return None
    return genai.Client(api_key=GOOGLE_API_KEY)


def generate_ai_insights(profile: dict, analysis: dict) -> dict:
    client = _get_client()
    if not client:
        return _fallback_insights(profile, analysis)

    username = profile.get("username", "")
    full_name = profile.get("full_name", "") or f"@{username}"
    bio = profile.get("biography", "")
    followers = profile.get("followers", 0)
    engagement = analysis.get("engagement_rate", 0)
    hook_score = analysis.get("hook_score", 0)
    hook_quality = analysis.get("hook_quality", "")
    opp_label = analysis.get("opportunity_label", "")
    issues = analysis.get("top_issues", [])
    posts = profile.get("posts", [])

    recent_hooks = [p.get("hook", "") for p in posts[:6] if p.get("hook")]
    hooks_text = "\n".join(f'- "{h}"' for h in recent_hooks) if recent_hooks else "No hooks available"

    prompt = f"""You are an expert Instagram content strategist and sales consultant. 
Analyze this creator's profile and produce a sharp, specific audit to help me sell them script writing and content idea services.

CREATOR DATA:
- Username: @{username}
- Name: {full_name}
- Bio: {bio}
- Followers: {followers:,}
- Engagement Rate: {engagement}%
- Hook Score: {hook_score}/100 ({hook_quality})
- Lead Priority: {opp_label}
- Key Issues: {"; ".join(issues)}

RECENT HOOKS FROM THEIR POSTS:
{hooks_text}

Write the following 3 sections. Be specific, direct, and persuasive. Reference their actual bio and hooks where relevant. Do NOT use generic advice.

---AUDIT_SUMMARY---
Write 2-3 punchy sentences summarizing exactly WHY this creator is underperforming and what the core problem is. Be blunt and specific. Mention their niche if you can infer it from the bio.

---CONTENT_IDEAS---
Give 3 specific viral content ideas tailored to their niche that would dramatically improve their performance. Format as a numbered list. Each idea should have a hook line and a one-sentence explanation.

---DM_MESSAGE---
Write a short, natural DM message (3-5 sentences) I can send to this creator to pitch my script writing service. Sound like a real person, not a bot. Reference something specific about their content or bio. End with a low-pressure CTA offering a free sample script."""

    try:
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=prompt,
        )
        text = response.text
        return _parse_response(text, full_name, username)
    except Exception:
        return _fallback_insights(profile, analysis)


def _parse_response(text: str, full_name: str, username: str) -> dict:
    def extract_section(marker_start, marker_end=None):
        start = text.find(marker_start)
        if start == -1:
            return ""
        start += len(marker_start)
        if marker_end:
            end = text.find(marker_end, start)
            return text[start:end].strip() if end != -1 else text[start:].strip()
        return text[start:].strip()

    summary = extract_section("---AUDIT_SUMMARY---", "---CONTENT_IDEAS---")
    ideas_raw = extract_section("---CONTENT_IDEAS---", "---DM_MESSAGE---")
    dm = extract_section("---DM_MESSAGE---")

    ideas = []
    for line in ideas_raw.split("\n"):
        line = line.strip()
        if line and (line[0].isdigit() or line.startswith("-")):
            cleaned = line.lstrip("0123456789.-) ").strip()
            if cleaned:
                ideas.append(cleaned)

    return {
        "audit_summary": summary,
        "content_ideas": ideas[:3],
        "dm_message": dm,
    }


def _fallback_insights(profile: dict, analysis: dict) -> dict:
    username = profile.get("username", "")
    full_name = profile.get("full_name", "") or f"@{username}"
    hook_quality = analysis.get("hook_quality", "weak")
    engagement = analysis.get("engagement_rate", 0)

    return {
        "audit_summary": (
            f"@{username}'s content is leaving significant reach on the table. "
            f"With a {engagement}% engagement rate and {hook_quality.lower()} hooks, "
            f"their posts aren't breaking through the algorithm the way they should be."
        ),
        "content_ideas": [
            "3 mistakes most creators in your niche are making (and how to avoid them)",
            "A day-in-the-life format showing behind-the-scenes of your process",
            "Controversial take on a common belief in your niche — start with 'Unpopular opinion:'",
        ],
        "dm_message": (
            f"Hey {full_name}! I've been following your content and love what you're building. "
            f"I noticed your posts could be pulling way more engagement with some tweaks to the hooks and content angles. "
            f"I help creators write scroll-stopping scripts and viral content ideas. "
            f"Want me to send over a free sample script for one of your next posts?"
        ),
    }
