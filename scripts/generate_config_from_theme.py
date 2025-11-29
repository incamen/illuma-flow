import os
import json
from gradio_client import Client

SCRIPT_DIR = os.path.dirname(__file__)
ROOT_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))

THEME_PATH = os.path.join(ROOT_DIR, "config", "next_theme.txt")
CONFIG_PATH = os.path.join(ROOT_DIR, "config", "next_article.json")

# Nama Space sesuai yang tertulis di docs: Penerang/Teuing-Ah
SPACE_NAME = "Penerang/Teuing-Ah"
API_NAME = "/generate_config"  # dari API documentation di tab App


def load_theme_text():
    if not os.path.exists(THEME_PATH):
        return "(file config/next_theme.txt belum ada)"
    with open(THEME_PATH, "r", encoding="utf-8") as f:
        return f.read().strip()


def main():
    theme_text = load_theme_text()
    print("Tema yang dikirim ke Space:")
    print(theme_text)

    client = Client(SPACE_NAME)
    # Panggil fungsi generate_config di Space
    result = client.predict(
        theme_text=theme_text,
        api_name=API_NAME,
    )

    # Space mengembalikan string JSON, kita parse ke dict
    if isinstance(result, str):
        cfg = json.loads(result)
    else:
        # Kalau sudah dict langsung saja
        cfg = result

    # Simpan ke next_article.json
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)

    print("Berhasil menulis config/next_article.json dari Space.")
    print("Judul:", cfg.get("title", "(tanpa judul)"))


if __name__ == "__main__":
    main()
