import os
import json

from verse_utils import get_verse_block_html

SCRIPT_DIR = os.path.dirname(__file__)
ROOT_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))

CONFIG_PATH = os.path.join(ROOT_DIR, "config", "next_article.json")
OUTPUT_PATH = os.path.join(ROOT_DIR, "content", "next_post.html")


def load_config():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def build_html(cfg: dict) -> str:
    parts = []

    # Pembuka
    intro_heading = cfg.get("intro_heading", "Pembuka")
    intro_pars = cfg.get("intro_paragraphs", [])
    parts.append(f"<h2>{intro_heading}</h2>")
    for p in intro_pars:
        parts.append(f"<p>\n{p}\n</p>")

    slots = cfg.get("slots", {})
    ayat_refs_cfg = cfg.get("ayat_refs", {})

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

        # Ambil referensi ayat untuk slot ini
        refs = ayat_refs_cfg.get(key, [])
        blocks_html_list = []

        for ref in refs:
            # ref bisa [surah, ayat] atau [surah, ayat_awal, ayat_akhir]
            try:
                if isinstance(ref, list) and len(ref) >= 2:
                    chapter = ref[0]
                    v_start = ref[1]
                    v_end = ref[2] if len(ref) >= 3 else ref[1]
                    block_html = get_verse_block_html(chapter, v_start, v_end)
                    blocks_html_list.append(block_html)
            except Exception as e:
                blocks_html_list.append(
                    f"<!-- error mengambil ayat {ref}: {e} -->"
                )

            if blocks_html_list:
        blocks_html = "\n".join(blocks_html_list)
    else:
        blocks_html = f"<!-- Belum ada ayat untuk slot {key} -->"

    # Hanya slot "pernyataan" yang dibuka default, lainnya tertutup
    open_attr = ' open' if key == "pernyataan" else ''

    parts.append(
        f'<details class="ayat-accordion"{open_attr}>\n'
        f"  <summary>{summary}</summary>\n"
        f"{blocks_html}\n"
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
