import os
import json

SCRIPT_DIR = os.path.dirname(__file__)
ROOT_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))

THEME_PATH = os.path.join(ROOT_DIR, "config", "next_theme.txt")
CONFIG_PATH = os.path.join(ROOT_DIR, "config", "next_article.json")


def main():
    # Baca isi tema (hanya untuk log di GitHub Actions)
    if os.path.exists(THEME_PATH):
        with open(THEME_PATH, "r", encoding="utf-8") as f:
            theme_text = f.read().strip()
    else:
        theme_text = "(file config/next_theme.txt belum ada)"

    print("=== Tema yang dibaca dari config/next_theme.txt ===")
    print(theme_text)
    print("=== Sementara script ini BELUM mengubah next_article.json ===")

    # Kalau next_article.json belum ada sama sekali, buat draft minimal
    if not os.path.exists(CONFIG_PATH):
        basic = {
            "title": "Artikel dari config (default)",
            "intro_heading": "Pembuka",
            "intro_paragraphs": [
                "Ini adalah contoh config default. Nanti akan diisi otomatis dari tema."
            ],
            "slots": {}
        }
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(basic, f, ensure_ascii=False, indent=2)
        print("Membuat config/next_article.json default.")
    else:
        print("config/next_article.json sudah ada, tidak diubah.")


if __name__ == "__main__":
    main()
