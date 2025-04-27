import re
from collections import Counter

WORDS_TO_SEARCH = [
    "clarissa", "lovelace", "letter", "dear", "miss", "virtue"
]


def load_text(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        return f.read().lower()


def count_words(text, words):
    counts = Counter()
    for word in words:
        pattern = fr"\b{re.escape(word)}\b"
        counts[word] = len(re.findall(pattern, text))
    return counts


def main():
    text = load_text("book.txt")
    results = count_words(text, WORDS_TO_SEARCH)
    for word, count in results.items():
        print(f"{word}: {count}")


if __name__ == "__main__":
    main()
