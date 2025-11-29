import os
import json
from gradio_client import Client

SCRIPT_DIR = os.path.dirname(__file__)
ROOT_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))

THEME_PATH = os.path.join(ROOT_DIR, "config", "next_theme.txt")
CONFIG_PATH = os.path.join(ROOT_DIR, "config", "next_article.json")

SPACE_NAME = "Penerang/Teuing-Ah"
API_NAME = "/api_generate"  # nama endpoint di Space


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

    # ===== try gradio_client first =====
    result = None
    try:
        client = Client(SPACE_NAME, token=HF_TOKEN)
        result = client.predict(theme_text, api_name=API_NAME)
        print("Menggunakan gradio_client.Client --> OK")
    except Exception as e:
        print("gradio_client.Client gagal, akan coba fallback HTTP:", repr(e))

    # ===== defensive handling: if result empty or invalid, try HTTP fallback =====
    def try_http_fallback():
        api_url = f"https://api-inference.huggingface.co/spaces/{SPACE_NAME}/run/predict"
        headers = {"Authorization": f"Bearer {HF_TOKEN}", "Content-Type": "application/json"}
        payload = {"data": [theme_text], "api_name": API_NAME}
        print("Mencoba fallback HTTP ke:", api_url)
        resp = requests.post(api_url, headers=headers, json=payload, timeout=60)
        resp.raise_for_status()
        return resp.json()

    # if result is None or empty tuple/list, or otherwise suspicious -> fallback
    need_fallback = False
    if result is None:
        need_fallback = True
        print("Result dari gradio_client kosong (None).")
    else:
        print("Raw result type:", type(result), " repr:", repr(result)[:500])
        if isinstance(result, (tuple, list)) and len(result) == 0:
            need_fallback = True
            print("Result adalah tuple/list kosong -> fallback needed.")
        # some gradio_client returns ("" ,) or (None,) etc — handle below

    if need_fallback:
        try:
            result = try_http_fallback()
            print("Fallback HTTP -> OK")
            print("Raw fallback result type:", type(result), " repr:", repr(result)[:500])
        except Exception as e:
            raise RuntimeError(f"Both gradio_client and HTTP fallback gagal: {e}")

    # ===== normalize result: tuple/list -> take first element if present =====
    if isinstance(result, (tuple, list)):
        if len(result) > 0:
            result = result[0]
            print("Mengambil elemen pertama dari tuple/list result.")
        else:
            # should not reach here because we fallback earlier, but guard anyway
            raise ValueError("Result tuple/list kosong setelah fallback — tidak dapat melanjutkan.")

    # ===== parse result =====
    cfg = None
    if isinstance(result, str):
        try:
            cfg = json.loads(result)
        except Exception as e:
            raise ValueError(f"Response string tidak valid JSON: {e}\nResponse repr: {repr(result)[:1000]}")
    elif isinstance(result, dict):
        cfg = result
    else:
        raise ValueError(f"Tidak dapat mengurai response Space: {type(result)} repr: {repr(result)[:500]}")

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
