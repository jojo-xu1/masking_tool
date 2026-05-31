from masking_tool.detection.matches import line_context_for


def test_line_context_extracts_full_log_line() -> None:
    text = "INFO start\nWARN owner=Alice Smith email=alice@example.com\nINFO done"
    start = text.index("alice@example.com")

    assert line_context_for(text, start, start + len("alice@example.com")) == "WARN owner=Alice Smith email=alice@example.com"


def test_line_context_keeps_csv_row_boundaries() -> None:
    text = "name,email\r\nAlice Smith,alice@example.com\r\nBob,bob@example.com"
    start = text.index("Alice")

    assert line_context_for(text, start, start + len("Alice Smith")) == "Alice Smith,alice@example.com"
