from masking_tool.replacement.mapping import ReplacementMapper


def test_replacement_mapping_is_deterministic() -> None:
    mapper = ReplacementMapper()
    assert mapper.get("EMAIL", "a@example.com") == "EMAIL_001"
    assert mapper.get("EMAIL", "b@example.com") == "EMAIL_002"
    assert mapper.get("EMAIL", "a@example.com") == "EMAIL_001"
    assert mapper.get("PERSON", "Alice") == "PERSON_001"
