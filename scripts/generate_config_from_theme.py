import os
import json
from gradio_client import Client

SCRIPT_DIR = os.path.dirname(__file__)
ROOT_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))

THEME_PATH = os.path.join(ROOT_DIR, "config", "next_theme.txt")
CONFIG_PATH = os.path.join(ROOT_DIR, "config", "next_article.json")

SPACE_NAME = "Penerang/Teuing-Ah"
API_NAME = "/generate_config"  # dari docs API Space


def load_theme_text():
    if not os.path.exists(THEME_PATH):
        return "(file config/next_theme.txt belum ada)"
    with open(THEME_PATH, "r", encoding="utf-8") as f:
        return f.read().strip()


def main():
    import requests

    HF_TOKEN = os.getenv("HF_TOKEN")
    if not HF_TOKEN:
        print("ERROR: HF_TOKEN tidak ditemukan di environment.")
        return

    theme_text = load_theme_text()
    print("Tema yang dikirim ke Space:")
    print(theme_text)

    # Coba pakai gradio_client Client dulu (lebih ringkas)
    try:
        client = Client(SPACE_NAME, token=HF_TOKEN)
        # panggil predict dengan argumen posisi (bukan keyword) — banyak versi client mengharapkan ini
        result = client.predict(theme_text, api_name=API_NAME)
        print("Menggunakan gradio_client.Client --> OK")
    except Exception as e:
        print("gradio_client.Client gagal, coba fallback HTTP:", repr(e))
        # Fallback: panggil inference API HF langsung
        api_url = f"https://api-inference.huggingface.co/spaces/{SPACE_NAME}/run/predict"
        headers = {
            "Authorization": f"Bearer {HF_TOKEN}",
            "Content-Type": "application/json",
        }
        payload = {"data": [theme_text], "api_name": API_NAME}
        resp = requests.post(api_url, headers=headers, json=payload, timeout=60)
        resp.raise_for_status()
        result = resp.json()

    # Space biasanya mengembalikan string JSON atau struktur JSON
    if isinstance(result, str):
        cfg = json.loads(result)
    elif isinstance(result, dict) and "data" in result and isinstance(result["data"], list) and len(result["data"])>0:
        # beberapa endpoint HF mengembalikan {"data":[<string-json>]}
        first = result["data"][0]
        if isinstance(first, str):
            cfg = json.loads(first)
        else:
            cfg = first
    else:
        cfg = result

    # ==== pertahankan ayat_refs lama jika ada ====
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f_old:
                old_cfg = json.load(f_old)
            if "ayat_refs" in old_cfg and "ayat_refs" not in cfg:
                cfg["ayat_refs"] = old_cfg["ayat_refs"]
                print("ayat_refs lama disalin ke config baru.")
        except Exception as e:
            print("Peringatan: gagal memuat ayat_refs lama:", e)
    # =============================================

    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)

    print("Berhasil menulis config/next_article.json dari Space.")
    print("Judul:", cfg.get("title", "(tanpa judul)"))


if __name__ == "__main__":
    main()
