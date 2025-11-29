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
    result = client.predict(
        theme_text=theme_text,
        api_name=API_NAME,
    )

    if isinstance(result, str):
        cfg = json.loads(result)
    else:
        cfg = result

    # Tambahan: bawa ayat_refs lama kalau ada
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f_old:
                old_cfg = json.load(f_old)
            if "ayat_refs" in old_cfg and "ayat_refs" not in cfg:
                cfg["ayat_refs"] = old_cfg["ayat_refs"]
        except Exception as e:
            print("Peringatan: gagal memuat ayat_refs lama:", e)

    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)

    print("Berhasil menulis config/next_article.json dari Space.")
    print("Judul:", cfg.get("title", "(tanpa judul)"))
