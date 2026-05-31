import re
from typing import Any

WEAK_HOOK_PATTERNS = [
    r"^(good morning|good night|hello|hi everyone|hey guys)",
    r"^(check out|new post|posting|just posted)",
    r"^(follow me|follow us|don't forget to)",
    r"^\s*$",
    r"^(today|yesterday|this week|this month)",
    r"^[#@]",
]

STRONG_HOOK_INDICATORS = [
    r"\?",
    r"(secret|hack|mistake|wrong|truth|never|always|stop|start|why|how|what if)",
    r"(you need to|you should|you must|don't|do this)",
    r"(number|#\d|\d+ (ways|tips|reasons|things|steps|mistakes))",
    r"(nobody|everyone|most people|few people)",
    r"(!{1,3}$)",
]

VIRAL_TOPIC_KEYWORDS = [
    "money", "income", "rich", "wealth", "side hustle", "passive income",
    "transformation", "before after", "weight loss", "fitness", "gym",
    "relationship", "dating", "love", "toxic", "red flag",
    "travel", "luxury", "lifestyle", "aesthetic",
    "ai", "chatgpt", "automation", "tech",
    "mindset", "motivation", "success", "hustle",
    "recipe", "food", "cook", "meal prep",
]


def analyze_profile(profile: dict) -> dict:
    posts = profile.get("posts", [])
    followers = profile.get("followers", 1)
    is_verified = profile.get("is_verified", False)

    if not posts:
        return {
            "engagement_rate": 0,
            "avg_likes": 0,
            "avg_comments": 0,
            "hook_score": 0,
            "hook_quality": "Insufficient data",
            "posting_consistency": "Unknown",
            "top_issues": ["Not enough observable post data to generate a meaningful analysis"],
            "opportunity_score": 0,
            "opportunity_label": "Unknown",
            "recommendations": [],
            "hook_breakdown": [],
            "data_note": "Analysis requires at least 1 public post to generate insights.",
            "posts_analyzed": 0,
        }

    likes_list = [p["likes"] for p in posts]
    comments_list = [p["comments"] for p in posts]
    avg_likes = sum(likes_list) / len(likes_list) if likes_list else 0
    avg_comments = sum(comments_list) / len(comments_list) if comments_list else 0

    engagement_rate = ((avg_likes + avg_comments) / max(followers, 1)) * 100

    hook_scores = []
    hook_breakdown = []
    for post in posts:
        hook = post.get("hook", "")
        score, issues, strengths = score_hook(hook)
        hook_scores.append(score)
        hook_breakdown.append({
            "hook": hook[:80] + ("..." if len(hook) > 80 else ""),
            "score": score,
            "issues": issues,
            "strengths": strengths,
        })

    avg_hook_score = sum(hook_scores) / len(hook_scores) if hook_scores else 0

    consistency_score = analyze_posting_consistency(posts)
    top_issues = identify_top_issues(engagement_rate, avg_hook_score, consistency_score, posts, followers, is_verified)
    recommendations = generate_recommendations(engagement_rate, avg_hook_score, top_issues, posts, is_verified)
    opportunity_score, opportunity_label = calculate_opportunity(engagement_rate, avg_hook_score, followers, is_verified)

    if avg_hook_score >= 70:
        hook_quality = "Strong"
    elif avg_hook_score >= 45:
        hook_quality = "Average"
    else:
        hook_quality = "Weak"

    posts_analyzed = len(posts)
    data_note = (
        f"Insights are based on {posts_analyzed} observable public posts and should be treated as directional rather than definitive."
        if posts_analyzed < 6
        else f"Analysis based on {posts_analyzed} observable public posts."
    )

    return {
        "engagement_rate": round(engagement_rate, 2),
        "avg_likes": round(avg_likes),
        "avg_comments": round(avg_comments),
        "hook_score": round(avg_hook_score),
        "hook_quality": hook_quality,
        "posting_consistency": consistency_score,
        "top_issues": top_issues,
        "opportunity_score": opportunity_score,
        "opportunity_label": opportunity_label,
        "recommendations": recommendations,
        "hook_breakdown": hook_breakdown[:6],
        "data_note": data_note,
        "posts_analyzed": posts_analyzed,
    }


def score_hook(hook: str) -> tuple:
    if not hook or len(hook) < 5:
        return 10, ["Hook is missing or too short to evaluate"], []

    score = 50
    issues = []
    strengths = []

    hook_lower = hook.lower()

    for pattern in WEAK_HOOK_PATTERNS:
        if re.search(pattern, hook_lower):
            score -= 20
            issues.append("Hook opens with a generic or passive phrase that may not stop the scroll")
            break

    for pattern in STRONG_HOOK_INDICATORS:
        if re.search(pattern, hook_lower, re.IGNORECASE):
            score += 15
            strengths.append("Uses engaging language or curiosity-driving structure")
            break

    if len(hook) < 20:
        score -= 15
        issues.append("Hook appears too short to convey a compelling reason to keep reading")
    elif len(hook) > 100:
        score -= 10
        issues.append("Hook may be overly long — first lines tend to perform better when punchy and concise")
    else:
        score += 5
        strengths.append("Hook length appears appropriate")

    if hook[0].isupper():
        score += 5
    else:
        score -= 5
        issues.append("Hook does not begin with a capital letter")

    if hook.endswith("?") or hook.endswith("!"):
        score += 10
        strengths.append("Ends with punctuation that may encourage continued reading")

    has_viral = any(kw in hook.lower() for kw in VIRAL_TOPIC_KEYWORDS)
    if has_viral:
        score += 10
        strengths.append("References a topic with demonstrated audience interest")

    emoji_count = len(re.findall(r'[\U00010000-\U0010ffff]|[\U0001F300-\U0001F9FF]', hook))
    if emoji_count == 1:
        score += 5
        strengths.append("Moderate emoji use")
    elif emoji_count > 3:
        score -= 5
        issues.append("Heavy emoji use may reduce perceived credibility")

    score = max(0, min(100, score))
    return score, issues, strengths


def analyze_posting_consistency(posts: list) -> str:
    if len(posts) < 2:
        return "Insufficient data"
    try:
        from datetime import datetime
        dates = sorted([datetime.fromisoformat(p["date"].replace("Z", "+00:00")) for p in posts], reverse=True)
        if len(dates) < 2:
            return "Insufficient data"
        gaps = [(dates[i] - dates[i + 1]).days for i in range(min(len(dates) - 1, 5))]
        avg_gap = sum(gaps) / len(gaps)
        if avg_gap <= 2:
            return "Very consistent (daily)"
        elif avg_gap <= 5:
            return "Consistent (every few days)"
        elif avg_gap <= 14:
            return "Moderate (weekly-ish)"
        else:
            return "Inconsistent (infrequent)"
    except Exception:
        return "Unknown"


def identify_top_issues(engagement_rate, hook_score, consistency, posts, followers, is_verified=False):
    issues = []

    # Tier-aware engagement benchmarks
    if is_verified or followers >= 500000:
        if engagement_rate < 0.5:
            issues.append(f"Engagement rate of {engagement_rate:.2f}% appears low relative to large creator benchmarks — audience interaction signals may indicate content-audience fit challenges")
        elif engagement_rate < 1.5:
            issues.append(f"Engagement rate of {engagement_rate:.2f}% is within a common range for large creators, though there may be room to deepen audience connection")
    elif followers >= 50000:
        if engagement_rate < 1.5:
            issues.append(f"Engagement rate of {engagement_rate:.2f}% appears below benchmark for creators at this follower count — content resonance may be a contributing factor")
        elif engagement_rate < 3.0:
            issues.append(f"Engagement rate of {engagement_rate:.2f}% is moderate — there appears to be room to strengthen audience interaction signals")
    else:
        if engagement_rate < 1.0:
            issues.append(f"Engagement rate of {engagement_rate:.2f}% appears below typical expectations for this follower tier — content may not be resonating strongly with the current audience")
        elif engagement_rate < 3.0:
            issues.append(f"Engagement rate of {engagement_rate:.2f}% is below the 3-5% range often seen in growing small creator accounts — hook and content quality may be contributing factors")

    if hook_score < 40:
        issues.append("Hook analysis suggests weak opening line construction — first lines appear to rely on generic or passive phrasing rather than curiosity-driving structure")
    elif hook_score < 60:
        issues.append("Hook quality appears average — opening lines may benefit from sharper curiosity gaps or more specific value signals")

    if "Inconsistent" in consistency or "Moderate" in consistency:
        issues.append("Posting frequency appears irregular — inconsistent publishing patterns may be limiting algorithmic reach")

    video_posts = [p for p in posts if p.get("is_video")]
    if video_posts:
        avg_video_views = sum(p.get("video_view_count") or 0 for p in video_posts) / len(video_posts)
        avg_likes = sum(p["likes"] for p in posts) / len(posts) if posts else 0
        if avg_video_views > 0 and avg_video_views < avg_likes * 2:
            issues.append("Video content appears to be generating fewer views relative to static post engagement — format or hook approach may benefit from review")

    caption_lengths = [len(p.get("caption", "")) for p in posts]
    avg_caption_len = sum(caption_lengths) / len(caption_lengths) if caption_lengths else 0
    if avg_caption_len < 50:
        issues.append("Average caption length appears short — there may be missed opportunities for storytelling or context that drives saves")

    hashtag_counts = [len(p.get("hashtags", [])) for p in posts]
    avg_hashtags = sum(hashtag_counts) / len(hashtag_counts) if hashtag_counts else 0
    if avg_hashtags < 3:
        issues.append("Observable hashtag usage is minimal — discoverability through tag-based reach may be limited")

    if not issues:
        issues.append("Observable signals appear relatively healthy — there may still be opportunities to deepen engagement and content differentiation")

    return issues[:4]


def generate_recommendations(engagement_rate, hook_score, issues, posts, is_verified=False):
    recs = []

    if hook_score < 60:
        recs.append("Consider rewriting post hooks using curiosity gaps, specific questions, or bold claims — opening line quality appears to be a key lever based on observable data")
    if engagement_rate < 3 and not is_verified:
        recs.append("Experimenting with story-driven caption structures — problem, context, resolution — may help improve the depth of audience engagement")
    recs.append("Establishing a consistent posting schedule of 3-5 posts per week may help maintain algorithmic visibility over time")
    recs.append("Structuring captions with a clear hook, body, and call-to-action aligns with formats that tend to drive saves and comments in most niches")
    if any("hashtag" in i.lower() for i in issues):
        recs.append("Researching and rotating niche-specific hashtags may expand discoverability — particularly relevant for accounts still building reach")
    recs.append("Adding a specific call-to-action at the end of each caption — a question, save prompt, or DM invite — may help signal engagement to the algorithm")

    return recs[:5]


def calculate_opportunity(engagement_rate, hook_score, followers, is_verified=False):
    score = 0

    if is_verified or followers >= 500000:
        score += 5
    elif followers < 5000:
        score += 25
    elif followers < 20000:
        score += 20
    elif followers < 100000:
        score += 10

    if engagement_rate < 1.0:
        score += 35
    elif engagement_rate < 3.0:
        score += 25
    elif engagement_rate < 5.0:
        score += 10

    if hook_score < 40:
        score += 30
    elif hook_score < 60:
        score += 20
    elif hook_score < 75:
        score += 10

    score = min(score, 100)

    if is_verified or followers >= 500000:
        label = "Optimization Opportunity" if score >= 50 else "Established Creator"
    else:
        if score >= 75:
            label = "High Priority Lead"
        elif score >= 50:
            label = "Good Prospect"
        elif score >= 30:
            label = "Moderate Opportunity"
        else:
            label = "Already Performing Well"

    return score, label
