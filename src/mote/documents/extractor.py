from mote.documents.models import DiscoveredFile, Document


class TextExtractor:
    def __init__(self, *, max_file_size_bytes: int) -> None:
        self.max_file_size_bytes = max_file_size_bytes

    def extract(self, source: DiscoveredFile) -> Document:
        with source.path.open("rb") as file:
            content = file.read(self.max_file_size_bytes + 1)

        if len(content) > self.max_file_size_bytes:
            raise ValueError(
                f"{source.path} exceeds the file-size limit."
            )

        text = content.decode("utf-8")

        return Document(
            source=source,
            text=text,
        )