import os
import json
import yaml

SCRIPT_DIR = os.path.dirname(__file__)
ROOT_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))

CONFIG_PATH = os.path.join(ROOT_DIR, "config", "next_article.json")
CONTENT_PATH = os.path.join(ROOT_DIR, "content", "next_post.html")


def load_generated_yaml_path():
    """
    next_article.json berisi:
    {
      "status": "success",
      "file": "configs/Nama_File.yaml"
    }
    """
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    return data.get("file"), data


def load_yaml_file(path):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def convert_yaml_to_html(cfg):
    """
    YAML kamu hanya berisi:
      title
      description
      author
    Jadi HTML disesuaikan untuk Blogger.
    """
    title = cfg.get("title", "")
    desc = cfg.get("description", "")
    author = cfg.get("author", "")

    html = f"""
    <h1>{title}</h1>
    <p><strong>Author:</strong> {author}</p>
    <p>{desc}</p>
    """.strip()

    return html


def main():
    yaml_path, raw_json = load_generated_yaml_path()

    if not yaml_path:
        print("ERROR: next_article.json tidak berisi path file YAML.")
        return

    full_yaml_path = os.path.join(ROOT_DIR, yaml_path)

    if not os.path.exists(full_yaml_path):
        print("ERROR: File YAML tidak ditemukan:", full_yaml_path)
        return

    print("Memuat YAML:", full_yaml_path)
    data = load_yaml_file(full_yaml_path)

    html = convert_yaml_to_html(data)

    os.makedirs(os.path.dirname(CONTENT_PATH), exist_ok=True)
    with open(CONTENT_PATH, "w", encoding="utf-8") as f:
        f.write(html)

    print("Berhasil generate:", CONTENT_PATH)


if __name__ == "__main__":
    main()
