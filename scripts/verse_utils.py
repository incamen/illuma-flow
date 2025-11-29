import os
import json

SCRIPT_DIR = os.path.dirname(__file__)
ROOT_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
DATASETS_DIR = os.path.join(ROOT_DIR, "datasets")

# File-file dataset (sesuaikan dengan nama di folder datasets)
QURAN_AR_FILE = os.path.join(DATASETS_DIR, "quran-ar.json")
QURAN_ID_FILE = os.path.join(DATASETS_DIR, "quran-id.json")
CHAPTERS_ID_FILE = os.path.join(DATASETS_DIR, "chapters-id.json")


_QURAN_AR = None
_QURAN_ID = None
_CHAPTERS_ID = None


def _load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_datasets():
    """
    Lazy-load dataset Qur'an (Arab, ID, dan metadata surat).
    Dipanggil otomatis oleh get_verse_block_html().
    """
    global _QURAN_AR, _QURAN_ID, _CHAPTERS_ID

    if _QURAN_AR is None:
        _QURAN_AR = _load_json(QURAN_AR_FILE)
    if _QURAN_ID is None:
        _QURAN_ID = _load_json(QURAN_ID_FILE)
    if _CHAPTERS_ID is None:
        _CHAPTERS_ID = _load_json(CHAPTERS_ID_FILE)


def get_surah_name_id(chapter):
    """
    Ambil nama surat (transliterasi) dari chapters-id.json
    berdasarkan nomor surat (chapter).
    """
    load_datasets()
    cid = int(chapter)
    for ch in _CHAPTERS_ID:
        if int(ch.get("id")) == cid:
            # Pakai transliterasi latin: "Al-Fatihah", "Al-Baqarah", dll.
            return ch.get("transliteration", f"Surah {cid}")
    return f"Surah {cid}"


def get_verse_block_html(chapter, verse_start, verse_end=None):
    """
    Ambil ayat Arab + terjemahan Indonesia dari dataset dan
    kembalikan HTML <blockquote class="quran-verse"> siap dipakai.

    chapter     : nomor surat (int atau str), mis. 44
    verse_start : ayat awal (int)
    verse_end   : ayat akhir (int) jika ingin rentang, kalau None → hanya 1 ayat
    """
    load_datasets()

    chapter_str = str(chapter)
    v_start = int(verse_start)
    v_end = int(verse_end) if verse_end is not None else v_start

    # Ambil semua ayat dalam rentang dari quran-ar.json dan quran-id.json
    arab_lines = []
    id_lines = []

    # Struktur di quran-ar.json & quran-id.json: { "1": [ { "chapter":1,"verse":1,"text":... }, ... ] }
    ar_list = _QURAN_AR.get(chapter_str, [])
    id_list = _QURAN_ID.get(chapter_str, [])

    for v in range(v_start, v_end + 1):
        # cari di list arab
        ar_text = ""
        for item in ar_list:
            if int(item.get("verse")) == v:
                ar_text = item.get("text", "")
                break
        # cari di list terjemahan ID
        id_text = ""
        for item in id_list:
            if int(item.get("verse")) == v:
                id_text = item.get("text", "")
                break

        if ar_text:
            arab_lines.append(ar_text)
        if id_text:
            id_lines.append(f"Ayat {v}: {id_text}")

    arab_html = "<br/>\n".join(arab_lines)
    id_html = "<br/>\n".join(id_lines)

    surah_name = get_surah_name_id(chapter)
    if v_start == v_end:
        ref = f"QS. {surah_name} [{chapter}]: {v_start}"
    else:
        ref = f"QS. {surah_name} [{chapter}]: {v_start}–{v_end}"

    block = f"""
<blockquote class="quran-verse">
  <div class="ayat-arab">
    {arab_html}
  </div>
  <div class="ayat-id">
    {id_html}
  </div>
  <span class="ayat-ref">{ref}</span>
</blockquote>
""".strip()

    return block
