import os
import re
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
    consistency = analysis.get("posting_consistency", "Unknown")

    recent_hooks = [p.get("hook", "") for p in posts[:6] if p.get("hook")]
    hooks_text = "\n".join(f'- "{h}"' for h in recent_hooks) if recent_hooks else "No hooks available"

    prompt = f"""You are a senior Instagram growth strategist producing a premium creator audit report.

CREATOR DATA:
- Username: @{username}
- Name: {full_name}
- Bio: {bio}
- Followers: {followers:,}
- Engagement Rate: {engagement}%
- Hook Score: {hook_score}/100 ({hook_quality})
- Posting Consistency: {consistency}
- Lead Priority: {opp_label}
- Key Issues: {"; ".join(issues)}

RECENT HOOKS FROM THEIR POSTS:
{hooks_text}

Output EXACTLY the sections below in order. Be specific, data-driven, and reference their actual content. No generic advice.

---OVERALL_SCORE---
[Single integer 0-100. Weak hooks + low engagement + inconsistent posting = lower score. Be honest.]

---SCORES---
Branding: [0-100, rate bio clarity, niche focus, profile cohesion]
Engagement: [0-100, benchmark engagement rate: <1% = 15-30, 1-3% = 30-55, 3-6% = 55-75, >6% = 75-95]
Consistency: [0-100, daily = 85-100, few days = 65-85, weekly = 40-65, infrequent = 10-40]
Growth: [0-100, overall growth trajectory signal based on content quality and engagement]

---STRENGTHS---
- [Specific strength referencing their actual data or bio]
- [Second specific strength]
- [Third specific strength]

---WEAKNESSES---
- [Specific weakness with data reference e.g. engagement rate or hook score]
- [Second specific weakness]
- [Third specific weakness]

---OPPORTUNITIES---
- [Concrete growth opportunity #1 — specific and actionable]
- [Concrete growth opportunity #2]
- [Concrete growth opportunity #3]

---CONTENT_STRATEGY---
[2-3 punchy sentences on exactly what content strategy this creator should adopt. Niche-specific. No fluff.]

---ACTION_PLAN---
Day 1: [Specific, concrete action]
Day 2: [Specific, concrete action]
Day 3: [Specific, concrete action]
Day 4: [Specific, concrete action]
Day 5: [Specific, concrete action]
Day 6: [Specific, concrete action]
Day 7: [Specific, concrete action]

---CONTENT_IDEAS---
1. [Viral idea — include a hook line and one-sentence explanation, niche-specific]
2. [Viral idea — include a hook line and one-sentence explanation, niche-specific]
3. [Viral idea — include a hook line and one-sentence explanation, niche-specific]
4. [Viral idea — include a hook line and one-sentence explanation, niche-specific]
5. [Viral idea — include a hook line and one-sentence explanation, niche-specific]

---AUDIENCE_ANALYSIS---
Type: [One sentence describing the likely audience demographic and psychographic]
Behavior: [One sentence on current engagement behavior patterns]
Preference: [One sentence on what content format this audience responds best to]

---CONFIDENCE---
[High if 6+ posts analyzed and bio is clear. Medium if limited data. Low if almost no data.]

---EXECUTIVE_SUMMARY---
Position: [One precise sentence on where this creator stands today — be specific with numbers]
Blocker: [The single biggest specific thing preventing growth — data-referenced, blunt]
Opportunity: [The single highest-leverage action available right now — specific and actionable]
Direction: [One strategic sentence on their optimal path forward over the next 90 days]

---QUICK_WINS---
- [Action they can do TODAY with immediate impact — hyper-specific]
- [Second quick win — doable this week]
- [Third quick win — low effort, high reward]

---PRIORITY_FIXES---
- [Most impactful problem to fix first — specific, data-referenced]
- [Second priority fix — ranked by growth impact]
- [Third priority fix]

---LONG_TERM_OPPORTUNITIES---
- [Strategic play for 3-6 months that could 2-5x their growth — niche-specific]
- [Second long-term strategic opportunity]
- [Third long-term opportunity]

---WEEKLY_CHECKLIST---
- [Weekly habit #1 for consistent algorithmic growth]
- [Weekly habit #2]
- [Weekly habit #3]
- [Weekly habit #4]
- [Weekly habit #5]
- [Weekly habit #6]
- [Weekly habit #7]

---AUDIT_SUMMARY---
[2-3 blunt, specific sentences summarizing why this creator underperforms and the core fix. Reference their niche and numbers.]

---DM_MESSAGE---
[Natural, personalized DM 3-5 sentences. Reference their bio or a specific hook. End with free sample script CTA. Sound like a human, not a bot.]"""

    try:
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=prompt,
        )
        text = response.text
        return _parse_structured_response(text, full_name, username, analysis)
    except Exception:
        return _fallback_insights(profile, analysis)


def _parse_structured_response(text: str, full_name: str, username: str, analysis: dict) -> dict:
    def extract(marker_start, marker_end=None):
        start = text.find(marker_start)
        if start == -1:
            return ""
        start += len(marker_start)
        if marker_end:
            end = text.find(marker_end, start)
            return text[start:end].strip() if end != -1 else text[start:].strip()
        return text[start:].strip()

    def extract_number(s, default=50):
        m = re.search(r'\d+', s)
        return max(0, min(100, int(m.group()))) if m else default

    def extract_bullets(s):
        lines = []
        for line in s.split('\n'):
            line = line.strip()
            if line.startswith('-') or line.startswith('•'):
                cleaned = line.lstrip('-•').strip()
                if cleaned:
                    lines.append(cleaned)
        return lines[:3]

    overall_raw = extract("---OVERALL_SCORE---", "---SCORES---")
    overall_score = extract_number(overall_raw, 50)

    scores_raw = extract("---SCORES---", "---STRENGTHS---")
    branding_score = engagement_score = consistency_score = growth_score = 50
    for line in scores_raw.split('\n'):
        if 'Branding:' in line:
            branding_score = extract_number(line, 50)
        elif 'Engagement:' in line:
            engagement_score = extract_number(line, 50)
        elif 'Consistency:' in line:
            consistency_score = extract_number(line, 50)
        elif 'Growth:' in line:
            growth_score = extract_number(line, 50)

    strengths = extract_bullets(extract("---STRENGTHS---", "---WEAKNESSES---"))
    weaknesses = extract_bullets(extract("---WEAKNESSES---", "---OPPORTUNITIES---"))
    opportunities = extract_bullets(extract("---OPPORTUNITIES---", "---CONTENT_STRATEGY---"))
    content_strategy = extract("---CONTENT_STRATEGY---", "---ACTION_PLAN---")

    action_plan_raw = extract("---ACTION_PLAN---", "---CONTENT_IDEAS---")
    action_plan = []
    for line in action_plan_raw.split('\n'):
        line = line.strip()
        if re.match(r'^Day\s*\d+\s*:', line, re.IGNORECASE):
            colon = line.find(':')
            if colon != -1:
                action = line[colon + 1:].strip()
                if action:
                    action_plan.append(action)
    action_plan = action_plan[:7]

    ideas_raw = extract("---CONTENT_IDEAS---", "---AUDIENCE_ANALYSIS---")
    ideas = []
    for line in ideas_raw.split('\n'):
        line = line.strip()
        if line and line[0].isdigit():
            cleaned = re.sub(r'^\d+[.)]\s*', '', line).strip()
            if cleaned:
                ideas.append(cleaned)
    ideas = ideas[:5]

    audience_raw = extract("---AUDIENCE_ANALYSIS---", "---CONFIDENCE---")
    audience = {"type": "", "behavior": "", "preference": ""}
    for line in audience_raw.split('\n'):
        if 'Type:' in line:
            audience["type"] = line.split('Type:', 1)[1].strip()
        elif 'Behavior:' in line:
            audience["behavior"] = line.split('Behavior:', 1)[1].strip()
        elif 'Preference:' in line:
            audience["preference"] = line.split('Preference:', 1)[1].strip()

    confidence_raw = extract("---CONFIDENCE---", "---EXECUTIVE_SUMMARY---").strip()
    confidence = "Medium"
    if "High" in confidence_raw:
        confidence = "High"
    elif "Low" in confidence_raw:
        confidence = "Low"

    exec_raw = extract("---EXECUTIVE_SUMMARY---", "---QUICK_WINS---")
    exec_summary = {"position": "", "blocker": "", "opportunity": "", "direction": ""}
    for line in exec_raw.split('\n'):
        line = line.strip()
        for field in ["Position", "Blocker", "Opportunity", "Direction"]:
            if line.startswith(field + ":"):
                exec_summary[field.lower()] = line.split(":", 1)[1].strip()

    if not exec_summary.get("position"):
        eng = analysis.get("engagement_rate", 0)
        issues = analysis.get("top_issues", [])
        hook_q = analysis.get("hook_quality", "weak")
        exec_summary = {
            "position": f"@{username} generates {eng:.1f}% engagement — {'below' if eng < 3 else 'near'} the 3–5% benchmark for growing creators in their niche",
            "blocker": issues[0] if issues else f"Hook quality is {hook_q.lower()} — most posts are failing to stop the scroll before the content can land",
            "opportunity": "Improving hook quality and posting consistency are the two highest-leverage fixes available right now",
            "direction": "Prioritize content quality and consistency over the next 30–60 days before expanding into new formats or platforms"
        }

    quick_wins_raw = extract_bullets(extract("---QUICK_WINS---", "---PRIORITY_FIXES---"))
    priority_fixes_raw = extract_bullets(extract("---PRIORITY_FIXES---", "---LONG_TERM_OPPORTUNITIES---"))
    long_term_raw = extract_bullets(extract("---LONG_TERM_OPPORTUNITIES---", "---WEEKLY_CHECKLIST---"))

    quick_wins = quick_wins_raw if quick_wins_raw else [
        "Rewrite the hooks on your 3 most recent posts today — no new content needed",
        "Add a bold question or stat to your next post's opening line before publishing",
        "Reply to every comment on your last 5 posts to boost algorithmic engagement signals"
    ]
    priority_fixes = priority_fixes_raw if priority_fixes_raw else [
        f"Fix hook quality immediately — {analysis.get('hook_quality','weak').lower()} hooks are suppressing reach on every post",
        f"Boost engagement from {analysis.get('engagement_rate',0):.1f}% toward 3%+ through storytelling-led captions",
        "Establish a 3–5 post per week cadence — inconsistent posting actively kills algorithmic momentum"
    ]
    long_term = long_term_raw if long_term_raw else [
        "Build a signature weekly content series that creates appointment viewing and audience loyalty",
        "Develop a DM-based lead magnet that converts followers to an owned email or contact list",
        "Collaborate with 3–5 complementary creators to cross-pollinate audiences and accelerate growth"
    ]

    checklist_raw = extract("---WEEKLY_CHECKLIST---", "---AUDIT_SUMMARY---")
    weekly_checklist = []
    for line in checklist_raw.split('\n'):
        line = line.strip()
        if line.startswith('-') or line.startswith('•'):
            cleaned = line.lstrip('-•').strip()
            if cleaned:
                weekly_checklist.append(cleaned)
    weekly_checklist = weekly_checklist[:7]
    if not weekly_checklist:
        weekly_checklist = [
            "Post 3–5 times with a scroll-stopping hook leading every single caption",
            "Spend 20 minutes engaging authentically in your niche's comment sections",
            "Review last week's analytics and double down on your highest-performing format",
            "Film or write 3 pieces of content in advance to protect your consistency",
            "Check and respond to every DM and comment within 24 hours",
            "Research one trending topic or format in your niche this week",
            "Add 5 new content ideas to your bank based on what's resonating right now"
        ]

    summary = extract("---AUDIT_SUMMARY---", "---DM_MESSAGE---")
    dm = extract("---DM_MESSAGE---")

    if not strengths:
        strengths = ["Established presence with an existing audience to build on",
                     "Content niche has demonstrated market demand",
                     "Posting history provides clear patterns to optimize from"]
    if not weaknesses:
        weaknesses = [f"Engagement rate of {analysis.get('engagement_rate', 0)}% needs improvement",
                      "Hook quality not consistently stopping the scroll",
                      "Content differentiation from competitors is unclear"]

    return {
        "overall_score": overall_score,
        "branding_score": branding_score,
        "engagement_score": engagement_score,
        "consistency_score": consistency_score,
        "growth_score": growth_score,
        "strengths": strengths,
        "weaknesses": weaknesses,
        "opportunities": opportunities,
        "content_strategy": content_strategy,
        "action_plan": action_plan,
        "content_ideas": ideas,
        "audience_analysis": audience,
        "confidence_level": confidence,
        "executive_summary": exec_summary,
        "quick_wins": quick_wins,
        "priority_fixes": priority_fixes,
        "long_term_opportunities": long_term,
        "weekly_checklist": weekly_checklist,
        "audit_summary": summary,
        "dm_message": dm,
    }


def rewrite_and_humanise_hook(hook: str) -> str:
    client = _get_client()
    if not client:
        return f"[AI unavailable] Could not rewrite: {hook}"

    rewrite_prompt = f"""You are a viral Instagram content expert. Rewrite the following weak hook into a powerful, scroll-stopping opening line.

Rules:
- Keep it under 15 words
- Use one of these proven formats: curiosity gap, bold claim, direct question, contrarian statement, or numbered list opener
- Make it feel punchy and urgent
- Do NOT explain yourself, just write the hook

Original hook: "{hook}"

Rewritten hook:"""

    try:
        rewrite_response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=rewrite_prompt,
        )
        rewritten = rewrite_response.text.strip().strip('"').strip("'")

        humanise_prompt = f"""Take this AI-generated hook and rewrite it so it sounds completely natural and human — like a real creator typed it, not a robot.

Rules:
- Remove any phrases that sound corporate, over-polished, or like marketing copy
- Make it feel casual, direct, and genuine
- Keep the same message and power but make it conversational
- Do NOT add explanations, just return the final hook text only
- Keep it under 15 words

AI hook: "{rewritten}"

Human version:"""

        human_response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=humanise_prompt,
        )
        return human_response.text.strip().strip('"').strip("'")

    except Exception:
        return f"Rewrite failed for: {hook}"


def _fallback_insights(profile: dict, analysis: dict) -> dict:
    username = profile.get("username", "")
    full_name = profile.get("full_name", "") or f"@{username}"
    hook_quality = analysis.get("hook_quality", "weak")
    engagement = analysis.get("engagement_rate", 0)
    hook_score = analysis.get("hook_score", 0)
    opp_score = analysis.get("opportunity_score", 50)

    overall_score = max(10, min(85, 100 - opp_score + 10))
    eng_score = max(10, min(80, int(engagement * 15)))
    h_score = max(10, min(90, hook_score))

    return {
        "overall_score": overall_score,
        "branding_score": 45,
        "engagement_score": eng_score,
        "consistency_score": 50,
        "growth_score": 60,
        "strengths": [
            "Established audience base to build momentum from",
            "Content niche shows clear audience demand",
            "Posting history provides patterns to optimize"
        ],
        "weaknesses": [
            f"Engagement rate of {engagement}% is below platform benchmarks",
            f"Hook quality is {hook_quality.lower()} — content isn't stopping the scroll",
            "Content strategy lacks clear differentiation from competitors"
        ],
        "opportunities": [
            "Rewriting hooks with curiosity gaps could 2-3x engagement within 30 days",
            "Introducing story-driven formats could significantly boost saves and shares",
            "Consistent posting schedule could improve algorithmic reach by 40-60%"
        ],
        "content_strategy": "Focus on scroll-stopping hooks combined with value-driven storytelling. Establish 3 core content pillars that speak directly to your niche audience's pain points and aspirations. Every post needs a hook, story, and CTA.",
        "action_plan": [
            "Audit your last 12 posts and identify your 3 highest-performing content formats",
            "Rewrite hooks for your next 5 posts using curiosity gap or bold claim format",
            "Post one piece of content using your strongest proven format",
            "Engage with 20 accounts in your niche to boost algorithmic visibility",
            "Research top 5 competitors and note which content formats get the most saves",
            "Create a content bank of 10 ideas mapped to your audience's top pain points",
            "Schedule your next 7 posts in advance and review weekly metrics"
        ],
        "content_ideas": [
            "\"3 mistakes most creators in your niche make (and how I fixed mine)\" — myth-busting format drives saves",
            "A day-in-the-life showing your behind-the-scenes process — builds authenticity and trust",
            "\"Unpopular opinion:\" contrarian take on a common belief — sparks debate and comments",
            "Before/after transformation with specific numbers and timeline — proof-driven content",
            "\"What nobody tells you about [your niche]\" — reveals a hidden truth your audience craves"
        ],
        "audience_analysis": {
            "type": "Core niche followers with passive consumption habits looking for value and inspiration",
            "behavior": "Currently engaging at below-average rates, suggesting content isn't triggering strong emotional responses",
            "preference": "Likely responds better to educational, story-driven content over promotional or generic posts"
        },
        "confidence_level": "Medium",
        "executive_summary": {
            "position": f"@{username} has {profile.get('followers', 0):,} followers but is significantly underperforming with a {engagement}% engagement rate",
            "blocker": f"Weak hook quality ({hook_quality.lower()} score) means most posts are getting scrolled past before the content can land",
            "opportunity": "Rewriting the first line of every post with a curiosity gap or bold claim is the single highest-leverage fix available right now",
            "direction": "Prioritize hook quality and posting consistency for the next 30 days before expanding into new content formats"
        },
        "quick_wins": [
            "Rewrite the hooks on your 3 most recent posts and update the captions today",
            "Add a bold question or stat to your next post's opening line before you publish it",
            "Reply to every comment on your last 5 posts to signal engagement to the algorithm"
        ],
        "priority_fixes": [
            f"Fix hook quality immediately — {hook_quality.lower()} hooks are costing you reach on every single post",
            f"Boost engagement rate from {engagement}% toward the 3%+ benchmark through content format changes",
            "Establish a consistent posting rhythm — irregular posting actively suppresses algorithmic reach"
        ],
        "long_term_opportunities": [
            "Build a signature content series that runs weekly — creates appointment viewing and loyalty",
            "Develop a lead magnet in your bio that converts followers to an owned email or DM list",
            "Collaborate with 3-5 complementary creators in your niche to cross-pollinate audiences"
        ],
        "weekly_checklist": [
            "Post 3-5 times with scroll-stopping hooks on every caption",
            "Spend 20 minutes engaging in your niche's comment sections",
            "Review last week's analytics and identify your highest-performing post format",
            "Create 3 pieces of content in advance to maintain consistency",
            "Check and respond to every DM and comment within 24 hours",
            "Research one trending topic or format in your niche this week",
            "Update your content bank with 5 new ideas based on what's performing in your niche"
        ],
        "audit_summary": (
            f"@{username}'s content is leaving significant reach on the table. "
            f"With a {engagement}% engagement rate and {hook_quality.lower()} hooks, "
            f"their posts aren't breaking through the algorithm the way they should be."
        ),
        "dm_message": (
            f"Hey {full_name}! I've been following your content and love what you're building. "
            f"I noticed your posts could be pulling way more engagement with some tweaks to the hooks and content angles. "
            f"I help creators write scroll-stopping scripts and viral content ideas. "
            f"Want me to send over a free sample script for one of your next posts?"
        ),
    }
