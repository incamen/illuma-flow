from verse_utils import get_verse_block_html

def main():
    block = get_verse_block_html(44, 2, 6)  # contoh: Ad-Dukhan 44:2–6
    print("=== HTML BLOCK AYAT 44:2–6 ===")
    print(block)

if __name__ == "__main__":
    main()
