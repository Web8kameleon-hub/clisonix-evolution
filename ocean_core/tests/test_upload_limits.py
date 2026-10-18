import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from upload_limits import ONE_GIB, resolve_document_upload_limit


def test_default_limit_is_one_gib_for_zero_or_invalid_negative_values():
    assert resolve_document_upload_limit(0) == ONE_GIB
    assert resolve_document_upload_limit(-2) == ONE_GIB


def test_minus_one_means_unlimited():
    assert resolve_document_upload_limit(-1) is None


def test_positive_custom_limit_is_preserved():
    assert resolve_document_upload_limit(ONE_GIB) == ONE_GIB
    assert resolve_document_upload_limit(4096) == 4096
