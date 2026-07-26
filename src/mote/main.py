from pathlib import Path

from mote.documents.scanner import Scanner
from mote.documents.extractor import TextExtractor
from mote.analysis.tokenizer import Tokenizer
from mote.index.inverted import InvertedIndex


MAX_FILE_SIZE_BYTES = 10_000_000


def main() -> None:
    scanner = Scanner(
        supported_extensions={".md", ".txt"},
        excluded_directories={
            ".git",
            ".venv",
            "__pycache__",
            "node_modules"
        },
        max_file_size_bytes=MAX_FILE_SIZE_BYTES,
    )

    extractor = TextExtractor(
        max_file_size_bytes=MAX_FILE_SIZE_BYTES,
    )

    tokenizer = Tokenizer()
    index = InvertedIndex()

    for discovered_file in scanner.scan(Path("./data")):
      document = extractor.extract(discovered_file)

      index.add_document(
          document,
          tokenizer.tokenize(document.text),
      )

    while True:
        query = input("Search (blank to quit): ").strip()

        if not query:
            break

        document_ids = index.search(query)

        if not document_ids:
            print("No results.")
            continue

        for document_id in document_ids:
            source = index.get_source(document_id)
            print(source.relative_path)


if __name__ == "__main__":
    main()