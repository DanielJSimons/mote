from mote.documents.scanner import Scanner
from pathlib import Path


supported_extensions = {".txt", ".md"}
excluded_directories = {".git"}
max_file_size_bytes = 100_000_000
follow_symlinks = False


def test_finds_supported_file(tmp_path: Path) -> None:
    document = tmp_path / "hello.md"
    document.write_text("Hello Mote", encoding="utf-8")

    scanner = Scanner(
        supported_extensions=supported_extensions,
        excluded_directories=excluded_directories,
        max_file_size_bytes=max_file_size_bytes,
        )

    results = list(scanner.scan(tmp_path))

    assert len(results) == 1
    assert results[0].path == document


def test_finds_supported_file_nested(tmp_path: Path) -> None:
    nested_directory = tmp_path / "notes" / "personal"
    nested_directory.mkdir(parents=True)

    document = nested_directory / "notes.md"
    document.write_text("Wow these notes are organised.", encoding="utf-8")

    scanner = Scanner(
        supported_extensions=supported_extensions,
        excluded_directories=excluded_directories,
        max_file_size_bytes=max_file_size_bytes
    )

    results = list(scanner.scan(tmp_path))

    assert len(results) == 1
    assert results[0].path == document
    assert results[0].relative_path == Path("notes/personal/notes.md")


def test_skip_unsupported_extension(tmp_path: Path) -> None:
    document = tmp_path / "worksheet.xlsx"
    document.write_text("No spreadsheets here.", encoding="utf-8")

    scanner = Scanner(
        supported_extensions=supported_extensions,
        excluded_directories=excluded_directories,
        max_file_size_bytes=max_file_size_bytes
    )

    results = list(scanner.scan(tmp_path))

    assert len(results) == 0


def test_skips_excluded_directory(tmp_path: Path) -> None:
    excluded_directory = tmp_path / ".git"
    excluded_directory.mkdir()

    excluded_document = excluded_directory / "hidden.md"
    excluded_document.write_text("This should not be found.", encoding="utf-8")

    visible_document = tmp_path / "visible.md"
    visible_document.write_text("This should be found.", encoding="utf-8")

    scanner = Scanner(
        supported_extensions=supported_extensions,
        excluded_directories=excluded_directories,
        max_file_size_bytes=max_file_size_bytes,
    )

    results = list(scanner.scan(tmp_path))

    assert len(results) == 1
    assert results[0].path == visible_document
