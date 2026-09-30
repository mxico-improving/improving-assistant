import pytest


@pytest.fixture(autouse=True)
def isolated_home(tmp_path, monkeypatch):
    """Never let a test touch the real ~/.improving-assistant."""
    home = tmp_path / "ia-home"
    monkeypatch.setenv("IMPROVING_ASSISTANT_HOME", str(home))
    return home
