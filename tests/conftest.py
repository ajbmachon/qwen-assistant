import pytest
from qwen_assistant.security import api_keys, auth, data_protection, logging as sec_logging, security_manager

@pytest.fixture(autouse=True)
def reset_singletons(monkeypatch):
    """Reset singleton caches between tests for isolation."""
    # clear lru_cache on get_api_key_manager
    try:
        api_keys.get_api_key_manager.cache_clear()
    except AttributeError:
        pass
    monkeypatch.setattr(auth, "_auth_instance", None, raising=False)
    monkeypatch.setattr(data_protection, "_data_protection_instance", None, raising=False)
    monkeypatch.setattr(sec_logging, "_security_logger", None, raising=False)
    monkeypatch.setattr(security_manager, "_security_manager", None, raising=False)
    yield
