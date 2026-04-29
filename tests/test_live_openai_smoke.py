import json

import pytest

from cortex_memory_os.live_openai_smoke import (
    DEFAULT_OPENAI_MODEL,
    build_responses_payload,
    extract_output_text,
    load_env_file,
    load_live_openai_config,
    run_smoke,
)


def test_load_env_file_handles_quotes_and_export(tmp_path):
    env_file = tmp_path / ".env.local"
    env_file.write_text(
        "export OPENAI_API_KEY='test-key-secret'\n"
        'CORTEX_LIVE_OPENAI_MODEL="gpt-5-nano"\n',
        encoding="utf-8",
    )

    values = load_env_file(env_file)

    assert values["OPENAI_API_KEY"] == "test-key-secret"
    assert values["CORTEX_LIVE_OPENAI_MODEL"] == "gpt-5-nano"


def test_dry_run_uses_env_file_without_returning_secret(tmp_path, monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    env_file = tmp_path / ".env.local"
    env_file.write_text("OPENAI_API_KEY=test-key-secret\n", encoding="utf-8")

    result = run_smoke(env_file=env_file, dry_run=True)
    serialized = json.dumps(result)

    assert result["ok"] is True
    assert result["live"] is False
    assert result["model"] == DEFAULT_OPENAI_MODEL
    assert "test-key-secret" not in serialized
    assert result["would_send_store_false"] is True


def test_build_responses_payload_uses_store_false(tmp_path, monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    env_file = tmp_path / ".env.local"
    env_file.write_text("OPENAI_API_KEY=test-key-secret\n", encoding="utf-8")
    config = load_live_openai_config(env_file=env_file)

    payload = build_responses_payload(config)

    assert payload["model"] == DEFAULT_OPENAI_MODEL
    assert payload["store"] is False
    assert payload["max_output_tokens"] == 24
    assert payload["reasoning"] == {"effort": "minimal"}


def test_extract_output_text_supports_responses_shapes():
    assert (
        extract_output_text({"output_text": "CORTEX_LIVE_OK"})
        == "CORTEX_LIVE_OK"
    )
    assert (
        extract_output_text(
            {
                "output": [
                    {
                        "content": [
                            {"type": "output_text", "text": "CORTEX"},
                            {"type": "output_text", "text": "_LIVE_OK"},
                        ]
                    }
                ]
            }
        )
        == "CORTEX_LIVE_OK"
    )


def test_missing_key_error_does_not_include_secret(tmp_path, monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    with pytest.raises(RuntimeError, match="OPENAI_API_KEY is missing"):
        load_live_openai_config(env_file=tmp_path / ".env.local")
