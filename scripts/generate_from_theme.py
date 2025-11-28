import os
import json

# Lokasi root repo (folder illuma-flow)
SCRIPT_DIR = os.path.dirname(__file__)
ROOT_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))

CONFIG_PATH = os.path.join(ROOT_DIR, "config", "next_article.json")
OUTPUT_PATH = os.path.join(ROOT_DIR, "content", "next_post.html")


def load_config():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def build_html(cfg: dict) -> str:
    parts = []

    # Judul artikel ditetapkan nanti di post_to_blogger (cfg["title"])
    intro_heading = cfg.get("intro_heading", "Pembuka")
    intro_pars = cfg.get("intro_paragraphs", [])

    parts.append(f"<h2>{intro_heading}</h2>")
    for p in intro_pars:
        parts.append(f"<p>\n{p}\n</p>")

    slots = cfg.get("slots", {})
    order = [
        "dasar_hukum",
        "petunjuk",
        "perintah",
        "larangan",
        "contoh",
        "sejarah",
        "pernyataan",
    ]

    for key in order:
        slot = slots.get(key)
        if not slot:
            continue

        heading = slot.get("heading", "")
        summary = slot.get("summary", "")
        paragraphs = slot.get("paragraphs", [])

        if heading:
            parts.append(f"<h2>{heading}</h2>")

        # Placeholder untuk blok ayat (nanti bisa diisi otomatis/manual)
        parts.append(f"<!-- SLOT: {key} -->")
        parts.append(
            f'<details class="ayat-accordion" open>\n'
            f"  <summary>{summary}</summary>\n"
            f"  <blockquote class=\"quran-verse\">\n"
            f"    <!-- Tambahkan blok ayat untuk slot {key} di sini -->\n"
            f"  </blockquote>\n"
            f"</details>"
        )

        for p in paragraphs:
            parts.append(f"<p>\n{p}\n</p>")

    html = "\n\n".join(parts)
    return html


def main():
    cfg = load_config()
    html = build_html(cfg)

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(html)

    print("Berhasil generate content/next_post.html dari config/next_article.json")


if __name__ == "__main__":
    main()
