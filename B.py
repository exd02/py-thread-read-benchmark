import re
import sys
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from collections import Counter

WORDS_TO_SEARCH = [
    "clarissa", "lovelace", "letter", "dear", "miss", "virtue"
]


def load_text(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        return f.read().lower()


def count_word(text, word):
    pattern = fr"\b{re.escape(word)}\b"
    return word, len(re.findall(pattern, text))


def count_words_parallel(text, words, num_threads, executor_type="process"):
    counts = Counter()
    
    # Choose the executor based on the parameter
    if executor_type.lower() == "thread":
        ExecutorClass = ThreadPoolExecutor
    else:
        ExecutorClass = ProcessPoolExecutor
    
    with ExecutorClass(max_workers=num_threads) as executor:
        futures = []
    
        for word in words:
           future = executor.submit(count_word, text, word)
           futures.append(future)

        for future in futures:
            word, count = future.result()
            counts[word] = count

    return counts


def main():
    if len(sys.argv) < 2:
        print("Usage: B.py <num_threads> [executor_type]")
        print("  executor_type: 'process' (default) or 'thread'")
        sys.exit(1)

    num_threads = int(sys.argv[1])
    
    # Parse executor type if provided, default to "process"
    executor_type = "process"
    if len(sys.argv) > 2:
        executor_type = sys.argv[2].lower()
        if executor_type not in ["process", "thread"]:
            print("Error: executor_type must be 'process' or 'thread'")
            sys.exit(1)
    

    text = load_text("book.txt")
    results = count_words_parallel(text, WORDS_TO_SEARCH, num_threads, executor_type)
    
    for word, count in results.items():
        print(f"{word}: {count}")


if __name__ == "__main__":
    main()