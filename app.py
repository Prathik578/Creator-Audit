from flask import Flask, request, jsonify, render_template, send_file
import http.client
import json
import io
import os
from datetime import datetime
from urllib.parse import quote
from analyzer import analyze_profile
from report_generator import generate_report_html
from ai_writer import generate_ai_insights

app = Flask(__name__)

RAPIDAPI_KEY = os.environ.get("RAPIDAPI_KEY", "")
RAPIDAPI_HOST = "instagram-looter2.p.rapidapi.com"


def rapidapi_get(path):
    conn = http.client.HTTPSConnection(RAPIDAPI_HOST)
    headers = {
        "x-rapidapi-key": RAPIDAPI_KEY,
        "x-rapidapi-host": RAPIDAPI_HOST,
    }
    conn.request("GET", path, headers=headers)
    res = conn.getresponse()
    data = res.read()
    conn.close()
    return res.status, json.loads(data.decode("utf-8"))


def extract_hook(caption: str) -> str:
    if not caption:
        return ""
    lines = caption.strip().split("\n")
    first_line = lines[0].strip()
    if len(first_line) > 10:
        return first_line[:120]
    if len(lines) > 1:
        return (first_line + " " + lines[1].strip())[:120]
    return first_line[:120]


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/scrape", methods=["POST"])
def scrape():
    data = request.get_json()
    usernames = data.get("usernames", [])
    if not usernames:
        return jsonify({"error": "No usernames provided"}), 400

    if not RAPIDAPI_KEY:
        return jsonify({"error": "RAPIDAPI_KEY not configured"}), 500

    results = []
    errors = []

    for username in usernames:
        username = username.strip().lstrip("@").replace(" ", "").replace("@", "")
        try:
            status, profile_raw = rapidapi_get(f"/profile?username={quote(username)}")

            if status != 200 or not profile_raw.get("status", True) == True:
                err_msg = profile_raw.get("errorMessage") or profile_raw.get("message") or "Failed to fetch profile"
                errors.append({"username": username, "error": err_msg})
                continue

            if profile_raw.get("is_private"):
                errors.append({"username": username, "error": "Profile is private"})
                continue

            followers = (profile_raw.get("edge_followed_by") or {}).get("count", 0)
            following = (profile_raw.get("edge_follow") or {}).get("count", 0)
            media_count = (profile_raw.get("edge_owner_to_timeline_media") or {}).get("count", 0)

            raw_posts = (profile_raw.get("edge_owner_to_timeline_media") or {}).get("edges", [])

            posts_data = []
            for edge in raw_posts[:12]:
                node = edge.get("node", {})
                caption_edges = (node.get("edge_media_to_caption") or {}).get("edges", [])
                caption = caption_edges[0]["node"]["text"] if caption_edges else ""
                hook = extract_hook(caption)
                likes = (node.get("edge_media_preview_like") or {}).get("count", 0)
                comments = (node.get("edge_media_to_comment") or {}).get("count", 0)
                is_video = node.get("__typename") == "GraphVideo"
                hashtags = [w.lstrip("#") for w in caption.split() if w.startswith("#")][:10]

                posts_data.append({
                    "shortcode": node.get("shortcode", ""),
                    "likes": likes,
                    "comments": comments,
                    "caption": caption[:300],
                    "hook": hook,
                    "is_video": is_video,
                    "video_view_count": node.get("video_view_count"),
                    "date": datetime.now().isoformat(),
                    "hashtags": hashtags,
                })

            profile_data = {
                "username": profile_raw.get("username", username),
                "full_name": profile_raw.get("full_name", ""),
                "biography": profile_raw.get("biography", ""),
                "followers": followers,
                "following": following,
                "post_count": media_count,
                "is_verified": profile_raw.get("is_verified", False),
                "profile_pic": profile_raw.get("profile_pic_url_hd") or profile_raw.get("profile_pic_url", ""),
                "posts": posts_data,
            }

            analysis = analyze_profile(profile_data)
            profile_data["analysis"] = analysis
            ai_insights = generate_ai_insights(profile_data, analysis)
            profile_data["ai_insights"] = ai_insights
            results.append(profile_data)

        except json.JSONDecodeError:
            errors.append({"username": username, "error": "Invalid response from Instagram API"})
        except Exception as e:
            errors.append({"username": username, "error": str(e)})

    return jsonify({"results": results, "errors": errors})


@app.route("/api/report", methods=["POST"])
def report():
    data = request.get_json()
    profiles = data.get("profiles", [])
    if not profiles:
        return jsonify({"error": "No profile data provided"}), 400
    html = generate_report_html(profiles)
    buf = io.BytesIO(html.encode("utf-8"))
    buf.seek(0)
    filename = f"instagram_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
    return send_file(buf, mimetype="text/html", as_attachment=True, download_name=filename)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
