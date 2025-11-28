import os
import json
import requests

SCRIPT_DIR = os.path.dirname(__file__)
ROOT_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))

THEME_PATH = os.path.join(ROOT_DIR, "config", "next_theme.txt")
CONFIG_PATH = os.path.join(ROOT_DIR, "config", "next_article.json")

HF_API_TOKEN = os.environ["HF_API_TOKEN"]
# Model instruksi gratis di Hugging Face, boleh diganti nanti kalau mau
MODEL_ID = "mistralai/Mistral-7B-Instruct-v0.2"

API_URL = f"https://api-inference.huggingface.co/models/{MODEL_ID}"


def load_theme_text():
    with open(THEME_PATH, "r", encoding="utf-8") as f:
        return f.read().strip()


def call_hf_api(prompt: str) -> str:
    headers = {"Authorization": f"Bearer {HF_API_TOKEN}"}
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 1024,
            "temperature": 0.7
        }
    }
    resp = requests.post(API_URL, headers=headers, json=payload, timeout=60)
    resp.raise_for_status()
    data = resp.json()
    # Untuk text-generation, biasanya data = [{"generated_text": "..."}]
    if isinstance(data, list) and len(data) > 0 and "generated_text" in data[0]:
        return data[0]["generated_text"]
    # Fallback: jika format berbeda
    if isinstance(data, dict) and "generated_text" in data:
        return data["generated_text"]
    # Jika format tak terduga, tulis ke log
    raise RuntimeError(f"Unexpected HF response format: {data}")


def extract_json(text: str) -> dict:
    # Ambil bagian antara { ... } terakhir di output
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise ValueError("Tidak menemukan JSON dalam respon model.")
    json_str = text[start : end + 1]
    return json.loads(json_str)


def build_prompt(theme_text: str) -> str:
    return f"""
