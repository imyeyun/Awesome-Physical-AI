"""
Unit tests for scripts/validate_data.py

Run with:
  pytest tests/test_validate_data.py -v
"""

import pytest
import validate_data as vd


# ─────────────────────────────────────────────────────────────────────────────
# Fixtures
# ─────────────────────────────────────────────────────────────────────────────

@pytest.fixture(autouse=True)
def clear_errors():
    """Reset the global errors list before each test."""
    vd.errors.clear()
    yield
    vd.errors.clear()


def _minimal_model(**overrides) -> dict:
    base = {
        "id": "test-model",
        "name": "Test Model",
        "org": "Test Org",
        "year": 2024,
        "description_en": "A test model.",
        "description_ko": "테스트 모델.",
        "categories": ["manipulation"],
        "hardware": ["manipulator"],
        "learning": ["IL"],
        "framework": ["pytorch"],
        "communication": [],
        "github_url": "https://github.com/test/repo",
        "paper_url": "",
        "hf_url": "",
        "added_date": "2024-01-01",
    }
    base.update(overrides)
    return base


def _minimal_dataset(**overrides) -> dict:
    base = {
        "id": "test-dataset",
        "name": "Test Dataset",
        "org": "Test Org",
        "year": 2023,
        "description_en": "A test dataset.",
        "description_ko": "테스트 데이터셋.",
        "categories": ["manipulation"],
        "hardware": ["manipulator"],
        "source": ["real"],
        "modality": ["rgb"],
        "github_url": "https://github.com/test/dataset",
        "paper_url": "",
        "hf_url": "",
        "added_date": "2023-06-01",
    }
    base.update(overrides)
    return base


def _minimal_tool(**overrides) -> dict:
    base = {
        "id": "test-tool",
        "name": "Test Sim",
        "org": "Test Org",
        "year": 2022,
        "description_en": "A test simulator.",
        "description_ko": "테스트 시뮬레이터.",
        "type": "physics_engine",
        "gpu_accelerated": False,
        "ros_support": False,
        "language": ["python"],
        "github_url": "https://github.com/test/sim",
        "paper_url": "",
        "project_url": "",
        "added_date": "2022-01-01",
    }
    base.update(overrides)
    return base


# ─────────────────────────────────────────────────────────────────────────────
# check_list_values
# ─────────────────────────────────────────────────────────────────────────────

def test_check_list_values_all_valid():
    vd.check_list_values("x", "categories", ["manipulation", "locomotion"], vd.VALID_CATEGORIES)
    assert vd.errors == []


def test_check_list_values_unknown_value():
    vd.check_list_values("x", "categories", ["flying"], vd.VALID_CATEGORIES)
    assert len(vd.errors) == 1
    assert "flying" in vd.errors[0]


def test_check_list_values_empty_list():
    vd.check_list_values("x", "categories", [], vd.VALID_CATEGORIES)
    assert vd.errors == []


# ─────────────────────────────────────────────────────────────────────────────
# validate_model
# ─────────────────────────────────────────────────────────────────────────────

def test_validate_model_valid_entry():
    vd.validate_model(_minimal_model())
    assert vd.errors == []


def test_validate_model_missing_required_field():
    m = _minimal_model()
    del m["org"]
    vd.validate_model(m)
    assert any("org" in e for e in vd.errors)


def test_validate_model_invalid_category():
    vd.validate_model(_minimal_model(categories=["flying"]))
    assert any("flying" in e for e in vd.errors)


def test_validate_model_invalid_hardware():
    vd.validate_model(_minimal_model(hardware=["jetpack"]))
    assert any("jetpack" in e for e in vd.errors)


def test_validate_model_invalid_learning():
    vd.validate_model(_minimal_model(learning=["magic"]))
    assert any("magic" in e for e in vd.errors)


def test_validate_model_no_url():
    m = _minimal_model(github_url="", paper_url="", hf_url="")
    vd.validate_model(m)
    assert any("at least one" in e for e in vd.errors)


def test_validate_model_year_out_of_range():
    vd.validate_model(_minimal_model(year=1999))
    assert any("year" in e for e in vd.errors)


def test_validate_model_year_valid_boundary():
    vd.validate_model(_minimal_model(year=2015))
    assert vd.errors == []


# ─────────────────────────────────────────────────────────────────────────────
# validate_dataset
# ─────────────────────────────────────────────────────────────────────────────

def test_validate_dataset_valid_entry():
    vd.validate_dataset(_minimal_dataset())
    assert vd.errors == []


def test_validate_dataset_missing_field():
    d = _minimal_dataset()
    del d["modality"]
    vd.validate_dataset(d)
    assert any("modality" in e for e in vd.errors)


def test_validate_dataset_invalid_source():
    vd.validate_dataset(_minimal_dataset(source=["youtube"]))
    assert any("youtube" in e for e in vd.errors)


def test_validate_dataset_invalid_modality():
    vd.validate_dataset(_minimal_dataset(modality=["smell"]))
    assert any("smell" in e for e in vd.errors)


def test_validate_dataset_no_url():
    d = _minimal_dataset(github_url="", paper_url="", hf_url="")
    vd.validate_dataset(d)
    assert any("at least one" in e for e in vd.errors)


# ─────────────────────────────────────────────────────────────────────────────
# validate_tool
# ─────────────────────────────────────────────────────────────────────────────

def test_validate_tool_valid_entry():
    vd.validate_tool(_minimal_tool())
    assert vd.errors == []


def test_validate_tool_missing_required_field():
    t = _minimal_tool()
    del t["type"]
    vd.validate_tool(t)
    assert any("type" in e for e in vd.errors)


def test_validate_tool_invalid_type():
    vd.validate_tool(_minimal_tool(type="game_engine"))
    assert any("game_engine" in e for e in vd.errors)


def test_validate_tool_valid_types():
    for tool_type in vd.VALID_TOOL_TYPES:
        vd.errors.clear()
        vd.validate_tool(_minimal_tool(type=tool_type))
        assert vd.errors == [], f"type '{tool_type}' should be valid"


def test_validate_tool_no_url():
    t = _minimal_tool(github_url="", paper_url="", project_url="")
    vd.validate_tool(t)
    assert any("at least one" in e for e in vd.errors)


def test_validate_tool_year_out_of_range():
    vd.validate_tool(_minimal_tool(year=2005))
    assert any("year" in e for e in vd.errors)


# ─────────────────────────────────────────────────────────────────────────────
# check_unique_ids
# ─────────────────────────────────────────────────────────────────────────────

def test_check_unique_ids_no_duplicates():
    entries = [{"id": "a"}, {"id": "b"}, {"id": "c"}]
    vd.check_unique_ids(entries, "models")
    assert vd.errors == []


def test_check_unique_ids_with_duplicate():
    entries = [{"id": "a"}, {"id": "b"}, {"id": "a"}]
    vd.check_unique_ids(entries, "models")
    assert any("Duplicate" in e and "a" in e for e in vd.errors)


def test_check_unique_ids_missing_id():
    entries = [{"name": "no-id-entry"}]
    vd.check_unique_ids(entries, "models")
    # Empty string ids still get added; second empty string would be a duplicate
    # No error for a single missing id
    assert vd.errors == []
