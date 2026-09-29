from src.ingestion.validate_sources import (
    validate_file_exists,
    validate_file_not_empty,
    validate_schema,
    validate_all_sources,
)
import pytest


def test_validate_file_exists_when_file_exists(tmp_path):
    test_file = tmp_path / "test.csv"
    test_file.write_text("id,value\n1,100\n")

    result = validate_file_exists(
        file_name="test.csv",
        file_path=test_file,
    )

    assert result is True


def test_validate_file_exists_when_file_is_missing(tmp_path):
    missing_file = tmp_path / "missing.csv"

    result = validate_file_exists(
        file_name="missing.csv",
        file_path=missing_file,
    )

    assert result is False


def test_validate_file_not_empty_with_content(tmp_path):
    test_file = tmp_path / "test.csv"
    test_file.write_text("id,value\n1,100\n")

    result = validate_file_not_empty(
        file_name="test.csv",
        file_path=test_file,
    )

    assert result is True


def test_validate_file_not_empty_when_empty(tmp_path):
    empty_file = tmp_path / "empty.csv"
    empty_file.touch()

    result = validate_file_not_empty(
        file_name="empty.csv",
        file_path=empty_file,
    )

    assert result is False

def test_validate_schema_when_schema_is_valid(tmp_path):
    test_file = tmp_path / "test.csv"
    test_file.write_text(
        "building_id,meter,timestamp,meter_reading\n"
        "1,0,2016-01-01 00:00:00,100.5\n"
    )

    required_columns = [
        "building_id",
        "meter",
        "timestamp",
        "meter_reading",
    ]

    result = validate_schema(
        file_name="test.csv",
        file_path=test_file,
        required_columns=required_columns,
    )

    assert result is True


def test_validate_schema_when_column_is_missing(tmp_path):
    test_file = tmp_path / "test.csv"
    test_file.write_text(
        "building_id,meter,timestamp\n"
        "1,0,2016-01-01 00:00:00\n"
    )

    required_columns = [
        "building_id",
        "meter",
        "timestamp",
        "meter_reading",
    ]

    result = validate_schema(
        file_name="test.csv",
        file_path=test_file,
        required_columns=required_columns,
    )

    assert result is False

def test_validate_all_sources_raises_error_when_source_is_invalid(monkeypatch):
    def fake_validate_source(file_name, file_config):
        return False

    monkeypatch.setattr(
        "src.ingestion.validate_sources.validate_source",
        fake_validate_source,
    )

    with pytest.raises(RuntimeError):
        validate_all_sources()


def test_validate_all_sources_succeeds_when_all_sources_are_valid(monkeypatch):
    def fake_validate_source(file_name, file_config):
        return True

    monkeypatch.setattr(
        "src.ingestion.validate_sources.validate_source",
        fake_validate_source,
    )

    validate_all_sources()