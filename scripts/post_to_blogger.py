import os
import json
import requests

# Ambil nilai dari GitHub Secrets
BLOG_ID = os.environ["BLOGGER_BLOG_ID"]
CLIENT_ID = os.environ["GOOGLE_CLIENT_ID"]
CLIENT_SECRET = os.environ["GOOGLE_CLIENT_SECRET"]
REFRESH_TOKEN = os.environ["BLOGGER_REFRESH_TOKEN"]

# Path dasar
SCRIPT_DIR = os.path.dirname(__file__)
ROOT_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
CONFIG_PATH = os.path.join(ROOT_DIR, "config", "next_article.json")
CONTENT_PATH = os.path.join(ROOT_DIR, "content", "next_post.html")


def get_access_token():
    resp = requests.post(
        "https://oauth2.googleapis.com/token",
        data={
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "refresh_token": REFRESH_TOKEN,
            "grant_type": "refresh_token",
        },
        timeout=15,
    )
    resp.raise_for_status()
    return resp.json()["access_token"]


def load_title_from_config(default="Artikel dari next_post.html"):
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            cfg = json.load(f)
        title = cfg.get("title") or default
        return title
    except Exception:
        return default


def main():
    # Baca isi HTML artikel dari file
    with open(CONTENT_PATH, "r", encoding="utf-8") as f:
        body_html = f.read()

    # Judul diambil dari config
    title = load_title_from_config()

    access_token = get_access_token()
    url = f"https://www.googleapis.com/blogger/v3/blogs/{BLOG_ID}/posts/"

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    payload = {
        "kind": "blogger#post",
        "blog": {"id": BLOG_ID},
        "title": title,
        "content": body_html,
    }

    resp = requests.post(url, headers=headers, json=payload, timeout=20)
    resp.raise_for_status()
    data = resp.json()
    print("Berhasil posting ke:", data.get("url"))


if __name__ == "__main__":
    main()
