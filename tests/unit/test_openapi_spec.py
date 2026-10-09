import warnings


def test_openapi_schema_has_no_duplicate_operation_ids():
    from apps.api.main import app

    app.openapi_schema = None

    with warnings.catch_warnings(record=True) as captured:
        warnings.simplefilter("always")
        schema = app.openapi()

    duplicate_messages = [
        str(item.message)
        for item in captured
        if "Duplicate Operation ID" in str(item.message)
    ]

    assert schema["openapi"] == "3.1.0"
    assert schema["info"]["title"] == "Clisonix Cloud API"
    assert not duplicate_messages, f"Duplicate OpenAPI operation IDs found: {duplicate_messages}"
