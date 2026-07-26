"""
An inverted index maps each search term to the documents containing it.

We search the term in the map to the document, not the term in the document. Simples.

Planned: indexing should be configurable by field and support document body,
filename, relative path, and extension. Fields should remain separate so Mote
can weight filename matches differently and support filters such as `path:`
and `ext:` without making token positions ambiguous.
"""


from collections.abc import Iterable
from pathlib import Path

from mote.analysis.models import Token
from mote.documents.models import Document, DiscoveredFile


class InvertedIndex:
    def __init__(self) -> None:
        # Search term -> document ID -> positions within that document.
        self._postings_by_term: dict[str, dict[int, list[int]]] = {}

        # Document ID -> file path and filesystem metadata.
        self._sources_by_document_id: dict[int, DiscoveredFile] = {}

        # File path -> its current document ID.
        self._document_id_by_path: dict[Path, int] = {}

        # Document ID -> unique terms, used to clean up postings on deletion.
        self._terms_by_document_id: dict[int, frozenset[str]] = {}

        # The next unused ID. Deleted IDs are never reused.
        self._next_document_id = 0


    def add_document(
        self,
        document: Document,
        tokens: Iterable[Token],
    ) -> int:
        # Build the document's term data before changing the main index.
        positions_by_term: dict[str, list[int]] = {}

        for token in tokens:
            positions = positions_by_term.setdefault(token.term, [])
            positions.append(token.position)

        # Re-indexing the same path replaces its previous index entry.
        existing_document_id = self._document_id_by_path.get(
            document.source.path
        )

        if existing_document_id is not None:
            self.remove_document(existing_document_id)

        # Give this version of the document a fresh ID.
        document_id = self._next_document_id
        self._next_document_id += 1

        # Record lookups in both directions.
        self._sources_by_document_id[document_id] = document.source
        self._document_id_by_path[document.source.path] = document_id

        # Remember its terms so deletion only visits relevant posting lists.
        self._terms_by_document_id[document_id] = frozenset(
            positions_by_term
        )

        # Merge this document's positions into the main inverted index.
        for term, positions in positions_by_term.items():
            positions_by_document_id = self._postings_by_term.setdefault(
                term,
                {},
            )
            positions_by_document_id[document_id] = positions

        return document_id


    def remove_document(self, document_id: int) -> bool:
      source = self._sources_by_document_id.get(document_id)

      if source is None:
          return False

      terms = self._terms_by_document_id.get(document_id)

      if terms is None:
          raise RuntimeError(
              f"Document {document_id} has no stored term information"
          )

      document_id_for_path = self._document_id_by_path.get(source.path)

      if document_id_for_path != document_id:
          raise RuntimeError(
              f"Path {source.path} does not point to document {document_id}"
          )

      for term in terms:
          positions_by_document_id = self._postings_by_term.get(term)

          if (
              positions_by_document_id is None
              or document_id not in positions_by_document_id
          ):
              raise RuntimeError(
                  f"Term {term!r} has no posting for document {document_id}"
              )

      # All related state is valid, so deletion can now begin.
      self._sources_by_document_id.pop(document_id)
      self._document_id_by_path.pop(source.path)
      self._terms_by_document_id.pop(document_id)

      for term in terms:
          positions_by_document_id = self._postings_by_term[term]
          positions_by_document_id.pop(document_id)

          if not positions_by_document_id:
              self._postings_by_term.pop(term)

      return True


    def search(self, term: str) -> list[int]:
        positions_by_document_id = self._postings_by_term.get(
            term.casefold(),
            {}
        )

        return list(positions_by_document_id)


    def get_source(self, document_id: int) -> DiscoveredFile:
        return self._sources_by_document_id[document_id]
        
