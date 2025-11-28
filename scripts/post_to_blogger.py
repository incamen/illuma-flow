import os
import requests
import textwrap

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
    access_token = get_access_token()

    # Konten dummy dulu – nanti diganti artikel 7 slot
    title = "TEST ILLUMA AUTOPOST (hapus setelah cek)"
    body_html = textwrap.dedent("""
        <h2>Ini postingan uji coba dari GitHub Actions</h2>
        <p>
          Jika kamu melihat artikel ini muncul di blog ILLUMA tanpa kamu tulis manual,
          berarti koneksi GitHub Actions → Blogger API sudah berhasil.
        </p>
        <p>
          Setelah pengujian ini, isi artikel akan diganti dengan format kajian
          ILLUMA (7 jalinan ayat + renungan).
        </p>
    """)

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
