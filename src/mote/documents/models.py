from pathlib import Path
from dataclasses import dataclass

@dataclass(frozen=True, slots=True)
class DiscoveredFile:
    path: Path
    relative_path: Path
    size_bytes: int
    modified_time_ns: int

    @property
    def extension(self) -> str:
        return self.path.suffix.lower()


@dataclass(frozen=True, slots=True)
class Document:
    source: DiscoveredFile
    text: str