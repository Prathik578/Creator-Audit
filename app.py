from flask import Flask, request, jsonify, render_template, send_file
from flask_cors import CORS
import instaloader
import json
import re
import io
import os
from datetime import datetime, timezone
from analyzer import analyze_profile
from report_generator import generate_report_html

app = Flask(__name__)
CORS(app)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/scrape", methods=["POST"])
def scrape():
    data = request.get_json()
    usernames = data.get("usernames", [])
    if not usernames:
        return jsonify({"error": "No usernames provided"}), 400

    results = []
    errors = []

    L = instaloader.Instaloader(
        download_pictures=False,
        download_videos=False,
        download_video_thumbnails=False,
        download_geotags=False,
        download_comments=False,
        save_metadata=False,
        compress_json=False,
        quiet=True,
        request_timeout=15,
        max_connection_attempts=2,
    )

    for username in usernames:
        username = username.strip().lstrip("@")
        try:
            profile = instaloader.Profile.from_username(L.context, username)
            posts_data = []
            count = 0
            for post in profile.get_posts():
                if count >= 12:
                    break
                caption = post.caption or ""
                hook = extract_hook(caption)
                posts_data.append({
                    "shortcode": post.shortcode,
                    "likes": post.likes,
                    "comments": post.comments,
                    "caption": caption[:300],
                    "hook": hook,
                    "is_video": post.is_video,
                    "video_view_count": post.video_view_count if post.is_video else None,
                    "date": post.date_utc.isoformat(),
                    "hashtags": list(post.caption_hashtags)[:10],
                })
                count += 1

            profile_data = {
                "username": profile.username,
                "full_name": profile.full_name,
                "biography": profile.biography,
                "followers": profile.followers,
                "following": profile.followees,
                "post_count": profile.mediacount,
                "is_verified": profile.is_verified,
                "posts": posts_data,
            }
            analysis = analyze_profile(profile_data)
            profile_data["analysis"] = analysis
            results.append(profile_data)
        except instaloader.exceptions.ProfileNotExistsException:
            errors.append({"username": username, "error": "Profile not found"})
        except instaloader.exceptions.LoginRequiredException:
            errors.append({"username": username, "error": "Profile is private"})
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


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
