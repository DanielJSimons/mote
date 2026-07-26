"""
Scanner is designed to walk directories, apply exclusions, check supported extension, read filesystem metadata, yield discovered file records. Not reading anything.
"""

import os
from pathlib import Path
from _collections_abc import Iterator

from mote.documents.models import DiscoveredFile


class Scanner:
    def __init__(
            self,
            *,
            supported_extensions: set[str],
            excluded_directories: set[str],
            max_file_size_bytes: int,
            follow_symlinks: bool = False,
    ) -> None:
        self.supported_extensions = frozenset(extension.lower() for extension in supported_extensions)
        self.excluded_directories = excluded_directories
        self.max_file_size_bytes = max_file_size_bytes
        self.follow_symlinks = follow_symlinks

    def scan(self, root: Path) -> Iterator[DiscoveredFile]:
        root = root.expanduser().resolve()

        if not root.is_dir():
            raise NotADirectoryError(root)

        for directory, directory_names, file_names in os.walk(
            root,
            followlinks=self.follow_symlinks,
        ):
            directory_names[:] = [
                name for name in directory_names if name not in self.excluded_directories
            ]

            directory_path = Path(directory)

            for file_name in file_names:
                path = directory_path / file_name

                # skip unsupported filetypes
                if path.suffix.lower() not in self.supported_extensions:
                    continue

                # fetch file metadata
                try:
                    metadata = path.stat()

                except OSError:
                    continue

                if metadata.st_size > self.max_file_size_bytes:
                    continue

                yield DiscoveredFile(
                    path=path,
                    relative_path=path.relative_to(root),
                    size_bytes=metadata.st_size,
                    modified_time_ns=metadata.st_mtime_ns,
                )
                
            

    
