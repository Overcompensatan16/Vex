import os


def load_facts_from_file(filename):
    """
    Loads facts from a text file. Each line = 1 fact.
    Blank lines and leading/trailing spaces are ignored.
    """
    facts = []
    try:
        with open(filename, 'r') as file:
            for line in file:
                fact = line.strip()
                if fact:
                    facts.append(fact)
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
    except Exception as e:
        print(f"Error reading file '{filename}': {e}")
    return facts


def discover_fact_files(directory):
    """
    Discover all .txt fact files in the given directory.
    Returns a list of file paths.
    """
    files = []
    try:
        for f in os.listdir(directory):
            if f.endswith(".txt"):
                files.append(os.path.join(directory, f))
    except Exception as e:
        print(f"Error discovering fact files in '{directory}': {e}")
    return files
