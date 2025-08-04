import os
import time

# Paths to the files you uploaded
ARXIV_PATH = r"D:\AI DEVELOPMENT\AI Development\hyper_ai_core\cerebral_cortex\source_handlers\external_loaders\arxiv_handler.py"
WIKI_PATH = r"D:\AI DEVELOPMENT\AI Development\hyper_ai_core\cerebral_cortex\source_handlers\external_loaders\wiki_handler.py"

# Fix for ArXiv: skip empty subjects
def patch_arxiv():
    with open(ARXIV_PATH, "r", encoding="utf-8") as f:
        lines = f.readlines()

    patched = []
    inserted = False
    for line in lines:
        patched.append(line)
        if not inserted and "root = ET.fromstring(data)" in line:
            patched.append("\n")
            patched.append("    # Skip early if no entries returned\n")
            patched.append("    entries = root.findall(\"atom:entry\", ns)\n")
            patched.append("    if not entries:\n")
            patched.append("        print(f\"[ArXiv] No entries found for subject: {subject}. Skipping...\")\n")
            patched.append("        return []\n")
            inserted = True

    with open(ARXIV_PATH, "w", encoding="utf-8") as f:
        f.writelines(patched)

    print("[✓] ArXiv patch applied: empty subject guard inserted.")

# Fix for Wikipedia: delay on failed response
def patch_wiki():
    with open(WIKI_PATH, "r", encoding="utf-8") as f:
        code = f.read()

    if "import time" not in code:
        code = "import time\n" + code

    # Patch the request line
    patched = code.replace(
        "response = requests.get(url)",
        (
            "try:\n"
            "        response = requests.get(url, timeout=10)\n"
            "        if not response.ok or not response.text:\n"
            "            print(f\"[Wiki] Empty or failed response for category {category}, retrying...\")\n"
            "            time.sleep(2)\n"
            "            continue\n"
            "    except Exception as e:\n"
            "        print(f\"[Wiki] Request failed for {category}: {e}\")\n"
            "        time.sleep(2)\n"
            "        continue"
        )
    )

    with open(WIKI_PATH, "w", encoding="utf-8") as f:
        f.write(patched)

    print("[✓] Wikipedia patch applied: retry delay added.")

if __name__ == "__main__":
    patch_arxiv()
    patch_wiki()
