from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from shared.static_pool import should_allow_frozen_text_as_input


DEFAULT_TIMEOUT = 180
DEFAULT_TEMPERATURE = 0.2
DEFAULT_TOP_P = 0.95


def load_text(path: str | None) -> str:
    if not path:
        return ""
    return Path(path).read_text(encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Delegate structured drafting work to an external OpenAI-compatible LLM."
    )
    parser.add_argument("--base-url", default=os.environ.get("DELEGATE_LLM_BASE_URL", "").strip())
    parser.add_argument("--api-key", default=os.environ.get("DELEGATE_LLM_API_KEY", "").strip())
    parser.add_argument("--model", default=os.environ.get("DELEGATE_LLM_MODEL", "").strip())
    parser.add_argument("--system-file", help="Path to a system prompt file.")
    parser.add_argument("--user-file", help="Path to a user/task prompt file.")
    parser.add_argument("--input-file", help="Path to a structured input payload to append.")
    parser.add_argument("--output-file", help="Optional path to write the raw assistant text.")
    parser.add_argument(
        "--input-source-tag",
        action="append",
        default=[],
        help="Declare the source tag for outgoing input. Frozen source tags will be rejected.",
    )
    parser.add_argument("--temperature", type=float, default=DEFAULT_TEMPERATURE)
    parser.add_argument("--top-p", type=float, default=DEFAULT_TOP_P)
    parser.add_argument("--max-tokens", type=int, default=4000)
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT)
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Request plain text or JSON object output.",
    )
    parser.add_argument(
        "--print-request",
        action="store_true",
        help="Print the outgoing JSON payload to stderr before sending.",
    )
    return parser


def require_value(name: str, value: str) -> str:
    clean = value.strip()
    if not clean:
        raise SystemExit(f"Missing required value: {name}")
    return clean


def normalize_base_url(base_url: str) -> str:
    clean = base_url.rstrip("/")
    if clean.endswith("/chat/completions"):
        return clean
    return f"{clean}/chat/completions"


def build_user_message(user_prompt: str, input_payload: str) -> str:
    parts: list[str] = []
    if user_prompt.strip():
        parts.append(user_prompt.strip())
    if input_payload.strip():
        parts.append("## Structured Input\n")
        parts.append(input_payload.strip())
    return "\n\n".join(parts).strip()


def build_payload(args: argparse.Namespace, system_prompt: str, user_message: str) -> dict:
    payload: dict = {
        "model": args.model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
        "temperature": args.temperature,
        "top_p": args.top_p,
        "max_tokens": args.max_tokens,
    }
    if args.format == "json":
        payload["response_format"] = {"type": "json_object"}
    return payload


def extract_text(data: dict) -> str:
    choices = data.get("choices") or []
    if not choices:
        raise SystemExit(f"Unexpected response: {json.dumps(data, ensure_ascii=False)[:1000]}")
    message = choices[0].get("message") or {}
    content = message.get("content")
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        text_parts = []
        for item in content:
            if isinstance(item, dict) and item.get("type") == "text":
                text_parts.append(item.get("text", ""))
        if text_parts:
            return "\n".join(text_parts).strip()
    raise SystemExit(f"Unsupported message content: {json.dumps(message, ensure_ascii=False)[:1000]}")


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    args.base_url = require_value("base-url / DELEGATE_LLM_BASE_URL", args.base_url)
    args.api_key = require_value("api-key / DELEGATE_LLM_API_KEY", args.api_key)
    args.model = require_value("model / DELEGATE_LLM_MODEL", args.model)

    system_prompt = load_text(args.system_file).strip()
    if not system_prompt:
        system_prompt = (
            "You are an auxiliary analyst. Work only on the abstracted inputs provided. "
            "Do not assume access to any original source files. "
            "If evidence is insufficient, say so explicitly."
        )

    user_prompt = load_text(args.user_file)
    input_payload = load_text(args.input_file)
    for source_tag in args.input_source_tag:
        if not should_allow_frozen_text_as_input(source_tag):
            raise SystemExit(f"Frozen input source is not allowed for external delegation: {source_tag}")
    user_message = build_user_message(user_prompt, input_payload)
    if not user_message:
        raise SystemExit("At least one of --user-file or --input-file is required.")

    payload = build_payload(args, system_prompt, user_message)
    if args.print_request:
        print(json.dumps(payload, ensure_ascii=False, indent=2), file=sys.stderr)

    response = requests.post(
        normalize_base_url(args.base_url),
        headers={
            "Authorization": f"Bearer {args.api_key}",
            "Content-Type": "application/json",
        },
        json=payload,
        timeout=args.timeout,
    )
    response.raise_for_status()
    text = extract_text(response.json())

    if args.output_file:
        Path(args.output_file).write_text(text, encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
