import pytest

from engine.config_validation import ConfigError, validate_config


def base_cfg(**overrides):
    cfg = {
        "texts": {"start": "start", "help": "help", "unknown": "unknown", "autoHelp": True},
        "commands": [{"command": "about", "description": "about us", "reply": "we are great"}],
        "buttons": [[{"text": "Btn", "reply": "pressed"}]],
        "keywords": [{"words": ["hi"], "reply": "hello"}],
        "adminIds": [123],
    }
    cfg.update(overrides)
    return cfg


def test_valid_config_passes():
    validate_config(base_cfg())


def test_missing_texts_key_raises():
    cfg = base_cfg(texts={"start": "s", "help": "h"})
    with pytest.raises(ConfigError, match="unknown"):
        validate_config(cfg)


def test_empty_start_text_raises():
    cfg = base_cfg(texts={"start": "  ", "help": "h", "unknown": "u"})
    with pytest.raises(ConfigError):
        validate_config(cfg)


def test_invalid_command_name_raises():
    cfg = base_cfg(commands=[{"command": "Bad Name!", "description": "x", "reply": "y"}])
    with pytest.raises(ConfigError, match="Bad Name!"):
        validate_config(cfg)


def test_duplicate_command_raises():
    cfg = base_cfg(
        commands=[
            {"command": "cat", "description": "x", "reply": "y"},
            {"command": "cat", "description": "x2", "reply": "y2"},
        ]
    )
    with pytest.raises(ConfigError, match="двічі"):
        validate_config(cfg)


def test_command_collides_with_builtin_raises():
    cfg = base_cfg(commands=[{"command": "start", "description": "x", "reply": "y"}])
    with pytest.raises(ConfigError, match="вбудованою"):
        validate_config(cfg)


def test_empty_command_reply_raises():
    cfg = base_cfg(commands=[{"command": "about", "description": "x", "reply": ""}])
    with pytest.raises(ConfigError, match="порожня відповідь"):
        validate_config(cfg)


def test_command_description_too_long_raises():
    cfg = base_cfg(commands=[{"command": "about", "description": "x" * 257, "reply": "y"}])
    with pytest.raises(ConfigError, match="257|довший"):
        validate_config(cfg)


def test_button_without_reply_raises():
    cfg = base_cfg(buttons=[[{"text": "Lonely"}]])
    with pytest.raises(ConfigError, match="Lonely"):
        validate_config(cfg)


def test_duplicate_button_text_raises():
    cfg = base_cfg(
        buttons=[
            [{"text": "Same", "reply": "a"}],
            [{"text": "Same", "reply": "b"}],
        ]
    )
    with pytest.raises(ConfigError, match="повторюється"):
        validate_config(cfg)


def test_keyword_without_reply_raises():
    cfg = base_cfg(keywords=[{"words": ["hi"], "reply": ""}])
    with pytest.raises(ConfigError, match="hi"):
        validate_config(cfg)


def test_admin_id_not_int_raises():
    cfg = base_cfg(adminIds=["123"])
    with pytest.raises(ConfigError, match="числом"):
        validate_config(cfg)
