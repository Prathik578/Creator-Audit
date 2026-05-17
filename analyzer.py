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

    if not posts:
        return {
            "engagement_rate": 0,
            "avg_likes": 0,
            "avg_comments": 0,
            "hook_score": 0,
            "hook_quality": "No data",
            "posting_consistency": "Unknown",
            "top_issues": ["Not enough post data to analyze"],
            "opportunity_score": 0,
            "opportunity_label": "Unknown",
            "recommendations": [],
            "hook_breakdown": [],
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
    top_issues = identify_top_issues(engagement_rate, avg_hook_score, consistency_score, posts, followers)
    recommendations = generate_recommendations(engagement_rate, avg_hook_score, top_issues, posts)
    opportunity_score, opportunity_label = calculate_opportunity(engagement_rate, avg_hook_score, followers)

    if avg_hook_score >= 70:
        hook_quality = "Strong"
    elif avg_hook_score >= 45:
        hook_quality = "Average"
    else:
        hook_quality = "Weak"

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
    }


def score_hook(hook: str) -> tuple[int, list, list]:
    if not hook or len(hook) < 5:
        return 10, ["Hook is missing or too short"], []

    score = 50
    issues = []
    strengths = []

    hook_lower = hook.lower()

    for pattern in WEAK_HOOK_PATTERNS:
        if re.search(pattern, hook_lower):
            score -= 20
            issues.append("Hook starts with a weak/generic phrase")
            break

    for pattern in STRONG_HOOK_INDICATORS:
        if re.search(pattern, hook_lower, re.IGNORECASE):
            score += 15
            strengths.append("Uses engaging language or structure")
            break

    if len(hook) < 20:
        score -= 15
        issues.append("Hook is too short to grab attention")
    elif len(hook) > 100:
        score -= 10
        issues.append("Hook may be too long — first line should be punchy")
    else:
        score += 5
        strengths.append("Good hook length")

    if hook[0].isupper():
        score += 5
    else:
        score -= 5
        issues.append("Hook doesn't start with a capital letter")

    if hook.endswith("?") or hook.endswith("!"):
        score += 10
        strengths.append("Ends with engaging punctuation")

    has_viral = any(kw in hook.lower() for kw in VIRAL_TOPIC_KEYWORDS)
    if has_viral:
        score += 10
        strengths.append("Touches on a high-interest topic")

    emoji_count = len(re.findall(r'[\U00010000-\U0010ffff]|[\U0001F300-\U0001F9FF]', hook))
    if emoji_count == 1:
        score += 5
        strengths.append("Good use of emoji")
    elif emoji_count > 3:
        score -= 5
        issues.append("Too many emojis can reduce credibility")

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


def identify_top_issues(engagement_rate, hook_score, consistency, posts, followers):
    issues = []

    if engagement_rate < 1.0:
        issues.append(f"Very low engagement rate ({engagement_rate:.2f}%) — content isn't resonating with followers")
    elif engagement_rate < 3.0:
        issues.append(f"Below-average engagement ({engagement_rate:.2f}%) — hooks and content ideas need work")

    if hook_score < 40:
        issues.append("Hooks are weak — first lines fail to stop the scroll or create curiosity")
    elif hook_score < 60:
        issues.append("Hooks are average — missing the urgency or intrigue needed to go viral")

    if "Inconsistent" in consistency or "Moderate" in consistency:
        issues.append("Posting inconsistency is hurting algorithmic reach")

    video_posts = [p for p in posts if p.get("is_video")]
    if video_posts:
        avg_video_views = sum(p.get("video_view_count") or 0 for p in video_posts) / len(video_posts)
        avg_likes = sum(p["likes"] for p in posts) / len(posts) if posts else 0
        if avg_video_views > 0 and avg_video_views < avg_likes * 3:
            issues.append("Video content underperforming relative to follower count")

    caption_lengths = [len(p.get("caption", "")) for p in posts]
    avg_caption_len = sum(caption_lengths) / len(caption_lengths) if caption_lengths else 0
    if avg_caption_len < 50:
        issues.append("Captions are too short — not building enough context or storytelling")

    hashtag_counts = [len(p.get("hashtags", [])) for p in posts]
    avg_hashtags = sum(hashtag_counts) / len(hashtag_counts) if hashtag_counts else 0
    if avg_hashtags < 3:
        issues.append("Using very few hashtags — limiting discoverability")

    if not issues:
        issues.append("Profile looks healthy, but could still benefit from sharper hooks and content angles")

    return issues[:4]


def generate_recommendations(engagement_rate, hook_score, issues, posts):
    recs = []

    if hook_score < 60:
        recs.append("Rewrite post hooks using curiosity gaps, bold claims, or direct questions to stop the scroll")
    if engagement_rate < 3:
        recs.append("Develop content pillars with proven viral formats: listicles, 'mistakes to avoid', transformation stories")
    recs.append("Create a content calendar with 3–5 posts/week minimum to satisfy the algorithm")
    recs.append("Use storytelling structures (problem → agitation → solution) in every caption")
    if any("hashtag" in i.lower() for i in issues):
        recs.append("Research and rotate a set of 15–20 niche-specific hashtags per post")
    recs.append("Add a clear CTA (call-to-action) at the end of every caption to drive comments and saves")

    return recs[:5]


def calculate_opportunity(engagement_rate, hook_score, followers):
    score = 0

    if followers < 5000:
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

    if score >= 75:
        label = "High Priority Lead"
    elif score >= 50:
        label = "Good Prospect"
    elif score >= 30:
        label = "Moderate Opportunity"
    else:
        label = "Already Performing Well"

    return score, label
