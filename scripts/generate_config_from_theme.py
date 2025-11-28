import os
import json
import requests

SCRIPT_DIR = os.path.dirname(__file__)
ROOT_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))

THEME_PATH = os.path.join(ROOT_DIR, "config", "next_theme.txt")
CONFIG_PATH = os.path.join(ROOT_DIR, "config", "next_article.json")

HF_API_TOKEN = os.environ["HF_API_TOKEN"]
MODEL_ID = "tiiuae/falcon-7b-instruct"  # boleh diganti model instruksi lain
API_URL = f"https://api-inference.huggingface.co/models/{MODEL_ID}"


def load_theme_text():
    if not os.path.exists(THEME_PATH):
        return "(file config/next_theme.txt belum ada)"
    with open(THEME_PATH, "r", encoding="utf-8") as f:
        return f.read().strip()


PROMPT_TEMPLATE = """
Kamu adalah penulis untuk blog ILLUMA.

ILLUMA menulis renungan berbasis jalinan ayat Al-Qur'an dengan 7 slot tetap:
1) dasar_hukum, 2) petunjuk, 3) perintah, 4) larangan, 5) contoh, 6) sejarah, 7) pernyataan.

Tugasmu:
- Dari deskripsi tema di bawah, susun rancangan artikel ILLUMA dalam bahasa Indonesia
  yang lembut, reflektif, dan tidak menggurui.
- Jangan menafsirkan ayat secara ilmiah dan jangan menyebut nomor surat/ayat.
- Fokus pada:
  - pembuka (latar belakang dan kegelisahan manusia),
  - judul untuk setiap bagian,
  - ringkasan pendek untuk setiap slot,
  - paragraf refleksi untuk diri sendiri (pakai kata "aku").

Keluarkan HASIL AKHIR dalam format JSON PERSIS seperti ini:

{
  "title": "...",
  "intro_heading": "...",
  "intro_paragraphs": ["...", "..."],
  "slots": {
    "dasar_hukum": {
      "heading": "...",
      "summary": "...",
      "paragraphs": ["..."]
    },
    "petunjuk": {
      "heading": "...",
      "summary": "...",
      "paragraphs": ["..."]
    },
    "perintah": {
      "heading": "...",
      "summary": "...",
      "paragraphs": ["..."]
    },
    "larangan": {
      "heading": "...",
      "summary": "...",
      "paragraphs": ["..."]
    },
    "contoh": {
      "heading": "...",
      "summary": "...",
      "paragraphs": ["..."]
    },
    "sejarah": {
      "heading": "...",
      "summary": "...",
      "paragraphs": ["..."]
    },
    "pernyataan": {
      "heading": "...",
      "summary": "...",
      "paragraphs": ["..."]
    }
  }
}

Syarat:
- Setiap item di "intro_paragraphs" dan di "paragraphs" harus berupa SATU paragraf pendek.
- Jangan menambah atau mengurangi field JSON.
- Jangan menulis penjelasan di luar JSON.

Berikut deskripsi tema:

<<<
<<THEME_TEXT>>
>>>
"""


def build_prompt(theme_text: str) -> str:
    return PROMPT_TEMPLATE.replace("<<THEME_TEXT>>", theme_text)


def call_hf_api(prompt: str) -> str:
    headers = {"Authorization": f"Bearer {HF_API_TOKEN}"}
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 1024,
            "temperature": 0.7
        }
    }
    resp = requests.post(API_URL, headers=headers, json=payload, timeout=90)
    resp.raise_for_status()
    data = resp.json()
    # Biasanya: [{"generated_text": "..."}]
    if isinstance(data, list) and data and "generated_text" in data[0]:
        return data[0]["generated_text"]
    if isinstance(data, dict) and "generated_text" in data:
        return data["generated_text"]
    raise RuntimeError(f"Format respon HF tidak terduga: {data}")


def extract_json(text: str) -> dict:
    # Ambil substring dari { ... } terakhir di output
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise ValueError("Tidak menemukan JSON dalam respon model.")
    json_str = text[start : end + 1]
    return json.loads(json_str)


def main():
    theme_text = load_theme_text()
    prompt = build_prompt(theme_text)

    print("Mengirim prompt ke Hugging Face...")
    raw_output = call_hf_api(prompt)
    print("Respon mentah (dipotong 400 karakter):")
    print(raw_output[:400])

    cfg = extract_json(raw_output)

    # Simpan ke next_article.json
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)

    print("Berhasil menulis config/next_article.json dari tema.")
    print("Judul:", cfg.get("title", "(tanpa judul)"))


if __name__ == "__main__":
    main()
