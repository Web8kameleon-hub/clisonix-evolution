"""Shared upload-limit policy for Ocean document endpoints."""

ONE_GIB = 1024 * 1024 * 1024


def resolve_document_upload_limit(configured_bytes: int) -> int | None:
    """Return the effective byte limit; -1 explicitly means unlimited."""
    if configured_bytes == -1:
        return None
    if configured_bytes <= 0:
        return ONE_GIB
    return configured_bytes
