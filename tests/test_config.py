import pytest

from improving_assistant.config import Config, ConfigError, load_config


def test_loads_all_fields_from_toml(tmp_path):
    f = tmp_path / "config.toml"
    f.write_text('project = "Acme - Dev"\nhours_per_day = 6\npto_type = "Guatemala PTO"\ncountry = "us"\n')

    assert load_config(f) == Config(project="Acme - Dev", hours_per_day=6, pto_type="Guatemala PTO", country="us")


def test_defaults_apply_when_only_project_is_given(tmp_path):
    f = tmp_path / "config.toml"
    f.write_text('project = "Acme - Dev"\n')

    assert load_config(f) == Config(project="Acme - Dev", hours_per_day=8, pto_type="Guatemala PTO", country="us")


def test_missing_file_raises_helpful_error(tmp_path):
    with pytest.raises(ConfigError, match="config.example.toml"):
        load_config(tmp_path / "nope.toml")


def test_missing_project_raises(tmp_path):
    f = tmp_path / "config.toml"
    f.write_text("hours_per_day = 8\n")

    with pytest.raises(ConfigError, match="project"):
        load_config(f)


def test_example_config_in_repo_is_valid():
    from pathlib import Path

    example = Path(__file__).resolve().parents[1] / "config.example.toml"
    assert load_config(example).project
