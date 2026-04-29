"""Optional secret-safe OpenAI live smoke test for local development."""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any

DEFAULT_OPENAI_MODEL = "gpt-5-nano"
DEFAULT_RESPONSES_URL = "https://api.openai.com/v1/responses"
DEFAULT_PROMPT = (
    "Return exactly CORTEX_LIVE_OK. Do not include explanation or extra text."
)


@dataclass(frozen=True)
class LiveOpenAIConfig:
    api_key: str
    api_key_source: str
    model: str
    responses_url: str
    prompt: str
    max_output_tokens: int
    reasoning_effort: str | None


def load_env_file(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}

    values: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[len("export ") :].strip()
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key:
            values[key] = value
    return values


def load_live_openai_config(
    *,
    env_file: Path,
    model: str | None = None,
    prompt: str = DEFAULT_PROMPT,
    max_output_tokens: int = 24,
    reasoning_effort: str | None = "minimal",
) -> LiveOpenAIConfig:
    file_values = load_env_file(env_file)
    api_key = os.environ.get("OPENAI_API_KEY") or file_values.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is missing from environment or .env.local")

    return LiveOpenAIConfig(
        api_key=api_key,
        api_key_source="environment"
        if os.environ.get("OPENAI_API_KEY")
        else str(env_file),
        model=(
            model
            or os.environ.get("CORTEX_LIVE_OPENAI_MODEL")
            or file_values.get("CORTEX_LIVE_OPENAI_MODEL")
            or DEFAULT_OPENAI_MODEL
        ),
        responses_url=(
            os.environ.get("OPENAI_RESPONSES_URL")
            or file_values.get("OPENAI_RESPONSES_URL")
            or DEFAULT_RESPONSES_URL
        ),
        prompt=prompt,
        max_output_tokens=max_output_tokens,
        reasoning_effort=reasoning_effort,
    )


def build_responses_payload(config: LiveOpenAIConfig) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "model": config.model,
        "input": config.prompt,
        "max_output_tokens": config.max_output_tokens,
        "store": False,
    }
    if config.reasoning_effort:
        payload["reasoning"] = {"effort": config.reasoning_effort}
    return payload


def extract_output_text(response: dict[str, Any]) -> str:
    output_text = response.get("output_text")
    if isinstance(output_text, str) and output_text:
        return output_text

    parts: list[str] = []
    for item in response.get("output", []):
        if not isinstance(item, dict):
            continue
        for content in item.get("content", []):
            if not isinstance(content, dict):
                continue
            text = content.get("text")
            if isinstance(text, str):
                parts.append(text)
    return "".join(parts)


def call_responses_api(config: LiveOpenAIConfig) -> dict[str, Any]:
    data = json.dumps(build_responses_payload(config)).encode("utf-8")
    request = urllib.request.Request(
        config.responses_url,
        data=data,
        headers={
            "Authorization": f"Bearer {config.api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def run_smoke(
    *,
    env_file: Path,
    model: str | None = None,
    prompt: str = DEFAULT_PROMPT,
    max_output_tokens: int = 24,
    reasoning_effort: str | None = "minimal",
    dry_run: bool = False,
    assert_contains: str | None = None,
) -> dict[str, Any]:
    config = load_live_openai_config(
        env_file=env_file,
        model=model,
        prompt=prompt,
        max_output_tokens=max_output_tokens,
        reasoning_effort=reasoning_effort,
    )
    if dry_run:
        return {
            "ok": True,
            "live": False,
            "model": config.model,
            "api_key_source": config.api_key_source,
            "responses_url": config.responses_url,
            "reasoning_effort": config.reasoning_effort,
            "would_send_store_false": True,
        }

    response = call_responses_api(config)
    text = extract_output_text(response).strip()
    ok = True if assert_contains is None else assert_contains in text
    return {
        "ok": ok,
        "live": True,
        "model": config.model,
        "response_id": response.get("id"),
        "output_text": text,
        "usage": response.get("usage", {}),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--env-file", default=".env.local")
    parser.add_argument("--model", default=None)
    parser.add_argument("--prompt", default=DEFAULT_PROMPT)
    parser.add_argument("--max-output-tokens", type=int, default=24)
    parser.add_argument(
        "--reasoning-effort",
        default="minimal",
        help="Set to 'none' to omit the reasoning field.",
    )
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--assert-contains", default=None)
    args = parser.parse_args(argv)

    try:
        result = run_smoke(
            env_file=Path(args.env_file),
            model=args.model,
            prompt=args.prompt,
            max_output_tokens=args.max_output_tokens,
            reasoning_effort=None
            if args.reasoning_effort == "none"
            else args.reasoning_effort,
            dry_run=args.dry_run,
            assert_contains=args.assert_contains,
        )
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        print(
            json.dumps(
                {
                    "ok": False,
                    "live": not args.dry_run,
                    "status": exc.code,
                    "error": body,
                },
                indent=2,
            ),
            file=sys.stderr,
        )
        return 1
    except Exception as exc:
        print(
            json.dumps({"ok": False, "live": not args.dry_run, "error": str(exc)}),
            file=sys.stderr,
        )
        return 2

    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
