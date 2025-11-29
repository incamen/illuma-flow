import os
import json
import requests

SCRIPT_DIR = os.path.dirname(__file__)
ROOT_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))

THEME_PATH = os.path.join(ROOT_DIR, "config", "next_theme.txt")
CONFIG_PATH = os.path.join(ROOT_DIR, "config", "next_article.json")

SPACE_NAME = "Penerang/Teuing-Ah"
FUNCTION_NAME = "generate_config"     # sesuai gradio 6: api/invoke/<name>


def load_theme_text():
    if not os.path.exists(THEME_PATH):
        return "(file config/next_theme.txt belum ada)"
    with open(THEME_PATH, "r", encoding="utf-8") as f:
        return f.read().strip()


def call_gradio6_function(theme_text, HF_TOKEN):
    """
    Memanggil custom function di Gradio 6 via endpoint:
    POST /api/invoke/<function_name>
    """
    url = f"https://huggingface.co/spaces/{SPACE_NAME}/api/invoke/{FUNCTION_NAME}"

    headers = {
        "Authorization": f"Bearer {HF_TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "data": {
            "text": theme_text
        }
    }

    print("Mengirim request ke:", url)

    resp = requests.post(url, headers=headers, json=payload, timeout=90)
    resp.raise_for_status()

    raw = resp.json()
    print("Raw response:", str(raw)[:500])

    if "data" not in raw:
        raise ValueError("Response tidak memiliki field 'data'")

    return raw["data"]


def normalize_result(result):
    """
    Gradio 6 selalu return:
    { "data": [ ... ] }
    Jadi result sudah berupa array, kita ambil elemen pertama.
    """
    if isinstance(result, list) and len(result) > 0:
        result = result[0]
    else:
        raise ValueError(
            f"Format result salah. Hasil: {repr(result)[:300]}"
        )

    # Convert JSON string -> dict
    if isinstance(result, str):
        try:
            return json.loads(result)
        except Exception as e:
            raise ValueError(f"String bukan JSON valid: {e}")

    if isinstance(result, dict):
        return result

    raise ValueError(f"Format elemen tidak dikenali: {type(result)}")


def main():
    HF_TOKEN = os.getenv("HF_TOKEN")
    if not HF_TOKEN:
        print("ERROR: Tidak ada HF_TOKEN di environment.")
        return

    theme_text = load_theme_text()
    print("Tema yang dikirim ke Space:\n", theme_text, "\n")

    # === Panggil Gradio 6 ===
    try:
        raw_data = call_gradio6_function(theme_text, HF_TOKEN)
    except Exception as e:
        print("Gagal memanggil Gradio 6:", repr(e))
        return

    # === Normalisasi ===
    cfg = normalize_result(raw_data)

    # === Pertahankan ayat_refs lama ===
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f_old:
                old_cfg = json.load(f_old)

            if "ayat_refs" in old_cfg and "ayat_refs" not in cfg:
                cfg["ayat_refs"] = old_cfg["ayat_refs"]
                print("→ Menyalin ayat_refs dari config lama.")
        except Exception as e:
            print("Gagal membaca config lama:", e)

    # === Simpan ===
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)

    print("\nBerhasil menulis config/next_article.json")
    print("Judul:", cfg.get("title", "(tanpa judul)"))


if __name__ == "__main__":
    main()
