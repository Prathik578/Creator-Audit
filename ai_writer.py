import os
import re
from google import genai

GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY", "")


def _get_client():
    if not GOOGLE_API_KEY:
        return None
    return genai.Client(api_key=GOOGLE_API_KEY)


def _detect_creator_tier(followers: int, engagement: float, is_verified: bool) -> str:
    if is_verified or followers >= 500000:
        return "large"
    if followers >= 50000 or (followers >= 10000 and engagement >= 3.0):
        return "mid"
    return "small"


def _detect_niche(bio: str, hooks: list) -> str:
    combined = (bio + " " + " ".join(hooks)).lower()
    niche_map = {
        "fitness": ["fitness", "gym", "workout", "weight loss", "muscle", "nutrition", "diet", "health", "coach"],
        "business": ["entrepreneur", "business", "income", "money", "invest", "finance", "wealth", "passive income", "sales"],
        "gaming": ["gaming", "gamer", "stream", "twitch", "youtube", "game", "play", "esport"],
        "education": ["learn", "teach", "course", "tips", "how to", "tutorial", "guide", "knowledge", "study"],
        "lifestyle": ["lifestyle", "travel", "luxury", "aesthetic", "vlog", "day in", "routine", "fashion", "style"],
        "commentary": ["opinion", "reaction", "commentary", "take", "rant", "review", "thoughts on"],
        "personal_brand": ["story", "journey", "mindset", "motivation", "personal", "growth", "self"],
    }
    scores = {}
    for niche, keywords in niche_map.items():
        scores[niche] = sum(1 for kw in keywords if kw in combined)
    top = max(scores, key=scores.get)
    return top if scores[top] > 0 else "personal_brand"


def _tier_context(tier: str, niche: str) -> str:
    tier_guidance = {
        "large": (
            "This is a large or verified creator. Frame insights around retention, audience depth, format diversification, "
            "and brand expansion — not basic growth fundamentals. Avoid framing them as 'failing' without nuance. "
            "Focus on optimizing an already established presence."
        ),
        "mid": (
            "This is a mid-size creator in a growth phase. Focus on positioning clarity, content differentiation, "
            "consistency systems, and capitalizing on momentum. Avoid treating them as a beginner."
        ),
        "small": (
            "This is a smaller creator still building their audience. Emphasize experimentation, audience-building, "
            "hook development, and finding their content-market fit. Be encouraging but realistic."
        ),
    }
    niche_guidance = {
        "fitness": "Fitness niche: prioritize transformation proof, practical how-to formats, authority hooks, and habit-building content.",
        "business": "Business niche: prioritize credibility signals, case studies, proof of results, and educational authority content.",
        "gaming": "Gaming niche: prioritize pacing, reaction formats, challenge content, community hooks, and consistency with platform-specific formats.",
        "education": "Education niche: prioritize knowledge sequencing, retention hooks, authority positioning, and value-first formats.",
        "lifestyle": "Lifestyle niche: prioritize aspirational framing, visual consistency, relatable storytelling, and trend alignment.",
        "commentary": "Commentary niche: prioritize strong takes, contrarian angles, discussion-driving hooks, and timely relevance.",
        "personal_brand": "Personal brand niche: prioritize storytelling, vulnerability, consistent voice, and positioning around a clear transformation or value promise.",
    }
    return f"{tier_guidance.get(tier, tier_guidance['small'])}\n{niche_guidance.get(niche, '')}"


def generate_ai_insights(profile: dict, analysis: dict) -> dict:
    client = _get_client()
    if not client:
        return _fallback_insights(profile, analysis)

    username = profile.get("username", "")
    full_name = profile.get("full_name", "") or f"@{username}"
    bio = profile.get("biography", "")
    followers = profile.get("followers", 0)
    is_verified = profile.get("is_verified", False)
    engagement = analysis.get("engagement_rate", 0)
    hook_score = analysis.get("hook_score", 0)
    hook_quality = analysis.get("hook_quality", "")
    opp_label = analysis.get("opportunity_label", "")
    issues = analysis.get("top_issues", [])
    posts = profile.get("posts", [])
    consistency = analysis.get("posting_consistency", "Unknown")
    post_count = len(posts)

    tier = _detect_creator_tier(followers, engagement, is_verified)
    recent_hooks = [p.get("hook", "") for p in posts[:6] if p.get("hook")]
    niche = _detect_niche(bio, recent_hooks)
    tier_ctx = _tier_context(tier, niche)

    hooks_text = "\n".join(f'- "{h}"' for h in recent_hooks) if recent_hooks else "No hooks available"
    confidence_note = "Low" if post_count < 3 else ("Medium" if post_count < 6 else "High")

    prompt = f"""You are a senior creator intelligence analyst producing a structured growth report. Your outputs must be measured, evidence-aware, and analytically credible — not motivational or exaggerated.

CREATOR DATA:
- Username: @{username}
- Name: {full_name}
- Bio: {bio}
- Followers: {followers:,}
- Verified: {is_verified}
- Engagement Rate: {engagement}%
- Hook Score: {hook_score}/100 ({hook_quality})
- Posting Consistency: {consistency}
- Lead Priority: {opp_label}
- Key Diagnosed Issues: {"; ".join(issues)}
- Posts Analyzed: {post_count}

RECENT OBSERVABLE HOOKS:
{hooks_text}

TIER & NICHE CONTEXT:
{tier_ctx}

IMPORTANT STYLE RULES — follow exactly:
- Use measured language: "may suggest", "appears to", "could indicate", "directional signal", "observable pattern"
- DO NOT claim certainty about things inferred from limited public data
- DO NOT use fake percentages like "63% increase" — use qualitative descriptions instead
- DO NOT repeat the same recommendation across sections — each section must add new information
- Adapt framing to creator tier: large creators should not be called "failing"; small creators get growth-focused advice
- Acknowledge data limitations naturally where relevant
- Sound analytical and strategic, not motivational or AI-guru-like

Output EXACTLY the sections below in order.

---OVERALL_SCORE---
[Single integer 0-100. Base it on observable data honestly. Large verified creators with active engagement should score higher.]

---SCORES---
Branding: [0-100]
Engagement: [0-100. Benchmarks: <1% = 10-30, 1-3% = 30-55, 3-6% = 55-75, >6% = 75-95]
Consistency: [0-100. Daily = 80-100, few days = 60-80, weekly = 35-60, infrequent = 10-35]
Growth: [0-100]

---SCORE_DRIVERS---
Branding drivers: [2-3 specific observable factors that influenced the branding score]
Engagement drivers: [2-3 specific factors — engagement rate vs benchmark, hook quality]
Consistency drivers: [Observable posting frequency pattern note]
Growth drivers: [What signals growth potential or risk]

---OBSERVED_SIGNALS---
- [Specific observable pattern from actual hook or bio data]
- [Second specific observable signal]
- [Third observable signal]
- [Optional fourth signal]

---STRENGTHS---
- [Specific strength referencing observable data — analytical framing]
- [Second specific strength]
- [Third specific strength]

---WEAKNESSES---
- [Specific weakness with measured framing — reference observable data]
- [Second specific weakness]
- [Third specific weakness]

---OPPORTUNITIES---
- [Concrete strategic opportunity — directional, not guaranteed. Niche-specific.]
- [Second opportunity — different information from weaknesses]
- [Third opportunity]

---CONTENT_STRATEGY---
[2-3 concise analytical sentences on what approach appears most aligned with this creator's niche and audience signals. No filler.]

---ACTION_PLAN---
Day 1: [Specific concrete action tied to observed issues]
Day 2: [Specific concrete action]
Day 3: [Specific concrete action]
Day 4: [Specific concrete action]
Day 5: [Specific concrete action]
Day 6: [Specific concrete action]
Day 7: [Specific concrete action]

---CONTENT_IDEAS---
1. [Viral idea with hook line — niche-specific. One sentence on why it fits this creator.]
2. [Different format/angle from idea 1]
3. [Viral idea]
4. [Viral idea]
5. [Viral idea]

---AUDIENCE_ANALYSIS---
Type: [One analytical sentence on likely audience — framed as directional based on bio and niche]
Behavior: [One sentence on apparent engagement behavior patterns]
Preference: [One sentence on likely preferred content formats based on niche and signals]

---CONFIDENCE---
{confidence_note} [One sentence explaining why — reference post count or data availability]

---EXECUTIVE_SUMMARY---
Position: [One precise analytical sentence — reference specific data points]
Blocker: [Most significant observable pattern limiting growth — measured framing]
Opportunity: [Most actionable strategic direction based on visible signals]
Direction: [One strategic sentence on a realistic 60-90 day focus — tier-appropriate]

---QUICK_WINS---
- [Specific immediately actionable step — doable today, tied to observed data]
- [Second quick win — different from priority fixes]
- [Third quick win]

---PRIORITY_FIXES---
- [Most impactful observable issue to address — specific, measured, ranked by likely impact]
- [Second priority fix — new information, not repeated from elsewhere]
- [Third priority fix]

---LONG_TERM_OPPORTUNITIES---
- [Strategic play for 3-6 months — niche-specific, tier-appropriate. No guaranteed growth claims.]
- [Second long-term strategic opportunity]
- [Third]

---WEEKLY_CHECKLIST---
- [Weekly operational habit #1 — specific and niche-aware]
- [Weekly habit #2]
- [Weekly habit #3]
- [Weekly habit #4]
- [Weekly habit #5]
- [Weekly habit #6]
- [Weekly habit #7]

---AUDIT_SUMMARY---
[2-3 analytically grounded sentences. Reference observable data. Avoid hyperbole. Acknowledge data limitations.]

---DM_MESSAGE---
[Personalized human-sounding outreach DM. 3-4 sentences. Reference something specific from their bio or content. End with a soft offer of free help. Sound like a real person, not a sales bot. No guaranteed results claims.]"""

    try:
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=prompt,
        )
        text = response.text
        return _parse_structured_response(text, full_name, username, analysis, tier, niche)
    except Exception:
        return _fallback_insights(profile, analysis)


def _parse_structured_response(text: str, full_name: str, username: str, analysis: dict, tier: str = "small", niche: str = "personal_brand") -> dict:
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

    def extract_bullets(s, max_items=3):
        lines = []
        for line in s.split('\n'):
            line = line.strip()
            if line.startswith('-') or line.startswith('•'):
                cleaned = line.lstrip('-•').strip()
                if cleaned:
                    lines.append(cleaned)
        return lines[:max_items]

    overall_raw = extract("---OVERALL_SCORE---", "---SCORES---")
    overall_score = extract_number(overall_raw, 50)

    scores_raw = extract("---SCORES---", "---SCORE_DRIVERS---")
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

    drivers_raw = extract("---SCORE_DRIVERS---", "---OBSERVED_SIGNALS---")
    score_drivers = {"branding": [], "engagement": [], "consistency": [], "growth": []}
    for line in drivers_raw.split('\n'):
        line = line.strip()
        for key in score_drivers:
            prefix = f"{key} drivers:"
            if line.lower().startswith(prefix):
                rest = line[len(prefix):].strip()
                score_drivers[key] = [f.strip() for f in rest.split(',') if f.strip()]

    observed_signals = extract_bullets(extract("---OBSERVED_SIGNALS---", "---STRENGTHS---"), max_items=4)

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
    if confidence_raw.lower().startswith("high"):
        confidence = "High"
    elif confidence_raw.lower().startswith("low"):
        confidence = "Low"
    confidence_note = re.sub(r'^(High|Medium|Low)\s*', '', confidence_raw, flags=re.IGNORECASE).strip()

    exec_raw = extract("---EXECUTIVE_SUMMARY---", "---QUICK_WINS---")
    exec_summary = {"position": "", "blocker": "", "opportunity": "", "direction": ""}
    for line in exec_raw.split('\n'):
        line = line.strip()
        for field in ["Position", "Blocker", "Opportunity", "Direction"]:
            if line.startswith(field + ":"):
                exec_summary[field.lower()] = line.split(":", 1)[1].strip()

    if not exec_summary.get("position"):
        eng = analysis.get("engagement_rate", 0)
        issues_list = analysis.get("top_issues", [])
        hook_q = analysis.get("hook_quality", "average")
        exec_summary = {
            "position": f"@{username} shows a {eng:.1f}% engagement rate — observable signals suggest {'below-benchmark' if eng < 3 else 'near-benchmark'} performance for their follower tier",
            "blocker": issues_list[0] if issues_list else f"Hook quality appears {hook_q.lower()} based on observable post patterns — opening lines may not be generating sufficient scroll-stops",
            "opportunity": "Improving hook construction and posting regularity appear to be the most actionable directions based on available signals",
            "direction": "A focused 60-day effort on content quality and consistency may help establish clearer algorithmic momentum"
        }

    quick_wins = extract_bullets(extract("---QUICK_WINS---", "---PRIORITY_FIXES---"))
    priority_fixes = extract_bullets(extract("---PRIORITY_FIXES---", "---LONG_TERM_OPPORTUNITIES---"))
    long_term = extract_bullets(extract("---LONG_TERM_OPPORTUNITIES---", "---WEEKLY_CHECKLIST---"))

    if not quick_wins:
        quick_wins = [
            "Revisit the opening line of your most recent posts and test a question or bold claim format",
            "Add a specific CTA to your next post before publishing — saves and comments signal quality to the algorithm",
            "Respond to existing comments on recent posts to activate engagement signals this week"
        ]
    if not priority_fixes:
        priority_fixes = [
            f"Hook construction appears to be limiting reach — {analysis.get('hook_quality','average').lower()} signals suggest opening lines may not be stopping the scroll",
            f"Engagement of {analysis.get('engagement_rate',0):.1f}% appears below the expected range — caption structure and CTA patterns may be contributing factors",
            "Posting regularity appears inconsistent — scheduled publishing could help maintain algorithmic visibility"
        ]
    if not long_term:
        long_term = [
            "Developing a recurring weekly content format may help build appointment-style viewership and audience loyalty",
            "Building an owned channel (email list or DM lead magnet) could reduce platform dependency as the audience grows",
            "Strategic collaborations with complementary creators in the niche may accelerate growth through cross-exposure"
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
            "Publish 3-5 posts with intentional curiosity-driven hooks on each",
            "Spend time engaging in your niche's comment sections to build visibility",
            "Review last week's analytics and identify which format appeared to perform strongest",
            "Prepare content in advance to maintain a consistent posting cadence",
            "Respond to comments and DMs within 24 hours to sustain engagement signals",
            "Research one trending topic or format within your niche this week",
            "Add new content ideas to your bank based on what's resonating in your space"
        ]

    summary = extract("---AUDIT_SUMMARY---", "---DM_MESSAGE---")
    dm = extract("---DM_MESSAGE---")

    if not strengths:
        strengths = [
            "An existing audience base provides a foundation to build from",
            "Content niche shows clear audience demand based on category signals",
            "Observable posting history allows pattern analysis and optimization"
        ]
    if not weaknesses:
        weaknesses = [
            f"Engagement of {analysis.get('engagement_rate', 0):.1f}% appears below typical benchmarks for this follower tier",
            f"Hook quality signals ({analysis.get('hook_quality','average').lower()}) suggest opening lines may not be generating strong scroll-stops",
            "Content differentiation from similar creators is not immediately apparent from observable signals"
        ]

    return {
        "overall_score": overall_score,
        "branding_score": branding_score,
        "engagement_score": engagement_score,
        "consistency_score": consistency_score,
        "growth_score": growth_score,
        "score_drivers": score_drivers,
        "observed_signals": observed_signals,
        "creator_tier": tier,
        "detected_niche": niche,
        "confidence_note": confidence_note,
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

    rewrite_prompt = f"""You are an Instagram content strategist. Rewrite the following hook into a stronger, more compelling opening line.

Rules:
- Keep it under 15 words
- Use one format: curiosity gap, bold claim, direct question, contrarian statement, or numbered opener
- Make it punchy and specific — avoid generic motivational phrasing
- Do NOT explain yourself, just write the hook

Original hook: "{hook}"

Rewritten hook:"""

    try:
        rewrite_response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=rewrite_prompt,
        )
        rewritten = rewrite_response.text.strip().strip('"').strip("'")

        humanise_prompt = f"""Take this hook and make it sound completely natural — like a real creator typed it, not an AI.

Rules:
- Remove corporate, over-polished, or marketing-copy phrasing
- Make it feel direct and conversational
- Keep the same core message and impact
- Do NOT add explanations, just return the final text only
- Keep it under 15 words

Hook: "{rewritten}"

Human version:"""

        human_response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=humanise_prompt,
        )
        return human_response.text.strip().strip('"').strip("'")

    except Exception:
        return f"Rewrite unavailable for: {hook}"


def _fallback_insights(profile: dict, analysis: dict) -> dict:
    username = profile.get("username", "")
    full_name = profile.get("full_name", "") or f"@{username}"
    hook_quality = analysis.get("hook_quality", "average")
    engagement = analysis.get("engagement_rate", 0)
    hook_score = analysis.get("hook_score", 0)
    opp_score = analysis.get("opportunity_score", 50)
    followers = profile.get("followers", 0)
    is_verified = profile.get("is_verified", False)
    posts = profile.get("posts", [])
    bio = profile.get("biography", "")
    recent_hooks = [p.get("hook", "") for p in posts[:6] if p.get("hook")]
    tier = _detect_creator_tier(followers, engagement, is_verified)
    niche = _detect_niche(bio, recent_hooks)

    overall_score = max(10, min(85, 100 - opp_score + 10))
    eng_score = max(10, min(80, int(engagement * 15)))
    h_score = max(10, min(90, hook_score))

    tier_position = {
        "large": f"@{username} maintains a significant presence with {followers:,} followers — analysis is based on observable public engagement signals",
        "mid": f"@{username} is in an active growth phase with {followers:,} followers — engagement signals suggest room for optimization",
        "small": f"@{username} is in the early audience-building stage with {followers:,} followers — directional signals indicate growth opportunities",
    }

    return {
        "overall_score": overall_score,
        "branding_score": 45,
        "engagement_score": eng_score,
        "consistency_score": 50,
        "growth_score": 60,
        "score_drivers": {
            "branding": ["Bio clarity and niche focus", "Tone consistency across posts"],
            "engagement": [f"Engagement rate of {engagement:.1f}% vs benchmark", "Hook quality signal"],
            "consistency": ["Observable posting frequency pattern"],
            "growth": ["Content quality signals", "Audience size relative to engagement"],
        },
        "observed_signals": [
            f"Observable engagement rate of {engagement:.1f}% appears {'below' if engagement < 3 else 'near'} the expected range for this follower tier",
            f"Hook analysis suggests {hook_quality.lower()} opening line construction across recent posts",
            "Posting consistency appears to be a contributing factor based on available data",
        ],
        "creator_tier": tier,
        "detected_niche": niche,
        "confidence_note": f"Based on {len(posts)} publicly observable posts",
        "strengths": [
            "Existing audience base provides a foundation to iterate from",
            "Content niche appears to have clear audience demand",
            "Observable posting history allows directional pattern analysis"
        ],
        "weaknesses": [
            f"Engagement rate of {engagement:.1f}% appears below typical benchmarks for this follower tier",
            f"Hook construction signals ({hook_quality.lower()}) suggest opening lines may not be generating strong scroll-stops",
            "Content differentiation from similar creators is not immediately apparent from observable patterns"
        ],
        "opportunities": [
            "Improving hook construction may increase scroll-stop rates — the audience appears to exist but engagement with current opening lines may be limited",
            "Introducing more story-driven caption formats could improve saves and shares based on niche patterns",
            "A more consistent posting cadence could improve algorithmic reach over the medium term"
        ],
        "content_strategy": "Based on observable signals, a shift toward curiosity-driven hooks combined with structured storytelling appears most aligned with this niche. Establishing 2-3 repeatable content formats may help build recognition and reduce content creation friction over time.",
        "action_plan": [
            "Review your last 12 posts and identify which format received the most engagement relative to reach",
            "Rewrite the opening line of your next 3 posts using a curiosity gap or direct question format",
            "Post one piece of content using your strongest historically performing format",
            "Spend time engaging authentically in your niche's comment sections",
            "Review top-performing accounts in your niche and note which content formats drive the most saves",
            "Develop a content bank of ideas mapped to your audience's observable interests",
            "Review analytics from the week and identify which content type showed the strongest engagement signal"
        ],
        "content_ideas": [
            "A 'common mistakes in [your niche]' format — myth-busting content tends to drive saves across most niches",
            "A behind-the-scenes or process-reveal post — authenticity signals tend to build trust and retention",
            "A contrarian take on a widely held belief in your niche — strong opinion content drives discussion",
            "A before/after or transformation format with specific observable details — proof-based content builds credibility",
            "A 'what nobody tells you about [your niche]' angle — hidden-truth framing tends to drive saves"
        ],
        "audience_analysis": {
            "type": f"Based on bio and niche signals, the likely audience appears interested in {niche.replace('_', ' ')}-related content and outcomes",
            "behavior": "Current engagement signals suggest a passive consumption pattern — content may not be generating strong enough responses to drive saves and shares",
            "preference": "Based on niche patterns, this audience likely responds to practical, specific, outcome-oriented content over generic inspirational posts"
        },
        "confidence_level": "Medium",
        "executive_summary": {
            "position": tier_position.get(tier, f"@{username} shows a {engagement:.1f}% engagement rate based on observable public signals"),
            "blocker": f"Hook quality signals ({hook_quality.lower()}) suggest opening lines may be the primary friction point — content may get scrolled past before the value lands",
            "opportunity": "Improving the first line of every post appears to be the most actionable direction based on available signal data",
            "direction": "A focused 60-day effort on hook construction and posting consistency appears most aligned with the current growth stage"
        },
        "quick_wins": [
            "Revisit the opening line of your 3 most recent posts and test a question or bold claim format",
            "Add a specific call-to-action to your next post before publishing — saves signal content quality to the algorithm",
            "Reply to all existing comments on recent posts to activate engagement signals this week"
        ],
        "priority_fixes": [
            f"Hook construction appears to be limiting reach — {hook_quality.lower()} signals suggest opening lines may not be stopping the scroll",
            f"Engagement of {engagement:.1f}% appears below expected range — caption structure and CTA patterns may be contributing factors",
            "Posting regularity appears inconsistent — scheduled publishing could help maintain algorithmic visibility"
        ],
        "long_term_opportunities": [
            "Developing a recurring content series could build appointment-style viewership and loyalty over time",
            "Building an owned channel (email list or DM lead magnet) could reduce platform dependency as the audience grows",
            "Strategic collaborations with complementary creators in the niche may accelerate audience growth through cross-exposure"
        ],
        "weekly_checklist": [
            "Publish 3-5 posts with intentional curiosity-driven hooks leading each caption",
            "Spend time engaging in your niche's comment sections to build visibility",
            "Review last week's analytics and identify which format appeared to perform strongest",
            "Prepare content in advance to maintain a consistent posting cadence",
            "Respond to comments and DMs within 24 hours to sustain engagement signals",
            "Research one trending topic or format within your niche this week",
            "Add new content ideas to your bank based on what's resonating in your space"
        ],
        "audit_summary": (
            f"@{username}'s observable signals suggest {'significant' if engagement < 1 else 'moderate'} room for optimization. "
            f"With a {engagement:.1f}% engagement rate and {hook_quality.lower()} hook signals, "
            f"the primary pattern appears to be content not generating sufficient scroll-stops. "
            f"Insights are directional and based on {len(posts)} publicly observable posts."
        ),
        "dm_message": (
            f"Hey {full_name}! I've been looking at your content and I think there's a real opportunity here. "
            f"Based on what I can see, your engagement signals suggest the hooks might be the main thing holding back the reach. "
            f"I help creators write stronger opening lines and content scripts that tend to improve engagement. "
            f"Want me to put together a free rewrite of one of your recent posts so you can see what a difference the hook makes?"
        ),
    }
