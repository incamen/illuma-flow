import os
import requests

# Ambil nilai dari GitHub Secrets
BLOG_ID = os.environ["BLOGGER_BLOG_ID"]
CLIENT_ID = os.environ["GOOGLE_CLIENT_ID"]
CLIENT_SECRET = os.environ["GOOGLE_CLIENT_SECRET"]
REFRESH_TOKEN = os.environ["BLOGGER_REFRESH_TOKEN"]


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


def main():
    # Tentukan path ke file content/next_post.html
    script_dir = os.path.dirname(__file__)
    content_path = os.path.join(script_dir, "..", "content", "next_post.html")
    content_path = os.path.abspath(content_path)

    # Baca isi HTML artikel dari file
    with open(content_path, "r", encoding="utf-8") as f:
        body_html = f.read()

    # Untuk sementara, judul kita isi manual.
    # Nanti bisa dibuat lebih pintar (misal ambil dari <h1>/<h2> pertama).
    title = "Artikel dari next_post.html"

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
