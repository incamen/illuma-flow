import os
import json
import requests

SCRIPT_DIR = os.path.dirname(__file__)
ROOT_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))

THEME_PATH = os.path.join(ROOT_DIR, "config", "next_theme.txt")
CONFIG_PATH = os.path.join(ROOT_DIR, "config", "next_article.json")

SPACE_API = "https://Penerang-Teuing-Ah.hf.space/generate_config"  # REST API FastAPI kamu


def load_theme():
    if not os.path.exists(THEME_PATH):
        return {"title": "", "description": "", "author": ""}

    with open(THEME_PATH, "r", encoding="utf-8") as f:
        lines = f.read().strip().split("\n")

    # Format file next_theme.txt:
    # line 1 → title
    # line 2 → description
    # line 3 → author
    return {
        "title": lines[0] if len(lines) > 0 else "",
        "description": lines[1] if len(lines) > 1 else "",
        "author": lines[2] if len(lines) > 2 else ""
    }


def call_space_rest_api(payload, token):
    headers = {"Authorization": f"Bearer {token}"}
    
    print("Mengirim request ke:", SPACE_API)
    resp = requests.post(SPACE_API, headers=headers, json=payload, timeout=60)
    resp.raise_for_status()

    return resp.json()


def main():
    HF_TOKEN = os.getenv("HF_TOKEN")
    if not HF_TOKEN:
        print("ERROR: HF_TOKEN tidak ditemukan di environment.")
        return

    theme = load_theme()

    print("Theme loaded:")
    print(theme)

    # === Panggil REST API FastAPI Space ===
    try:
        response = call_space_rest_api(theme, HF_TOKEN)
    except Exception as e:
        print("Gagal memanggil Space:", e)
        return

    print("Response:")
    print(response)

    # Simpan hasil ke next_article.json
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(response, f, ensure_ascii=False, indent=2)

    print("Config berhasil ditulis:", CONFIG_PATH)


if __name__ == "__main__":
    main()
