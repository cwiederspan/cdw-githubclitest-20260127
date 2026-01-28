#!/usr/bin/env python3
"""
generate_image.py - OpenAI Images API helper

- Reads OPENAI_API_KEY from environment
- Saves generated PNG files to the current working directory (or --out-dir)
- Supports gpt-image-1 (base64 output) and dall-e-3 (url or base64_json)

Docs:
- https://platform.openai.com/docs/api-reference/images
"""

from __future__ import annotations

import argparse
import base64
import datetime as _dt
import json
import os
import sys
import urllib.request
from typing import Any, Dict, List, Optional, Tuple


def _utc_stamp() -> str:
    return _dt.datetime.utcnow().strftime("%Y%m%d-%H%M%S")


def _env(name: str, default: Optional[str] = None) -> Optional[str]:
    v = os.getenv(name)
    return v if v not in (None, "") else default


def _mask_key(k: str) -> str:
    if len(k) <= 8:
        return "****"
    return f"{k[:2]}****{k[-4:]}"


def _http_json(
    url: str,
    api_key: str,
    payload: Dict[str, Any],
    timeout: int = 120,
) -> Dict[str, Any]:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, method="POST")
    req.add_header("Authorization", f"Bearer {api_key}")
    req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        body = resp.read().decode("utf-8")
    return json.loads(body)


def _download_file(url: str, out_path: str, timeout: int = 120) -> None:
    with urllib.request.urlopen(url, timeout=timeout) as resp:
        data = resp.read()
    with open(out_path, "wb") as f:
        f.write(data)


def _write_b64_png(b64: str, out_path: str) -> None:
    raw = base64.b64decode(b64)
    with open(out_path, "wb") as f:
        f.write(raw)


def main() -> int:
    p = argparse.ArgumentParser(description="Generate images using the OpenAI Images API and save to disk.")
    p.add_argument("--prompt", required=True, help="Text prompt describing the desired image.")
    p.add_argument("--model", default=_env("OPENAI_IMAGE_MODEL", "gpt-image-1"), help="Model to use (default: gpt-image-1).")
    p.add_argument("--size", default=_env("OPENAI_IMAGE_SIZE", "auto"),
                   help="Image size. For gpt-image models: auto|1024x1024|1536x1024|1024x1536. For dall-e-3: 1024x1024|1792x1024|1024x1792.")
    p.add_argument("--n", type=int, default=int(_env("OPENAI_IMAGE_N", "1")), help="Number of images to generate (default: 1).")
    p.add_argument("--quality", default=_env("OPENAI_IMAGE_QUALITY", None),
                   help="Quality for gpt-image models: low|medium|high. For dall-e-3: standard|hd. (Optional)")
    p.add_argument("--style", default=_env("OPENAI_IMAGE_STYLE", None),
                   help="Style for dall-e-3: vivid|natural. (Optional)")
    p.add_argument("--out-dir", default=".", help="Output directory (default: current directory).")
    p.add_argument("--out-prefix", default="generated", help="Output filename prefix (default: generated).")
    p.add_argument("--verbose", action="store_true", help="Print request/response metadata (never prints full API key).")
    args = p.parse_args()

    api_key = _env("OPENAI_API_KEY")
    if not api_key:
        print("ERROR: OPENAI_API_KEY is not set.", file=sys.stderr)
        return 2

    base_url = _env("OPENAI_BASE_URL", "https://api.openai.com").rstrip("/")
    endpoint = f"{base_url}/v1/images"

    # Payload per OpenAI Images API
    payload: Dict[str, Any] = {
        "model": args.model,
        "prompt": args.prompt,
        "size": args.size,
        "n": args.n,
    }

    # Optional fields (only include when set)
    if args.quality:
        payload["quality"] = args.quality
    if args.style:
        payload["style"] = args.style

    # dall-e-3 supports response_format; gpt-image models always return base64.
    if args.model.startswith("dall-e"):
        payload.setdefault("response_format", "b64_json")

    if args.verbose:
        print(f"Using endpoint: {endpoint}")
        print(f"Using API key: {_mask_key(api_key)}")
        print("Payload:")
        print(json.dumps(payload, indent=2))

    try:
        resp = _http_json(endpoint, api_key, payload)
    except Exception as e:
        print(f"ERROR calling Images API: {e}", file=sys.stderr)
        return 3

    if args.verbose:
        # Avoid dumping the entire base64 payload in verbose mode.
        meta = dict(resp)
        if isinstance(meta.get("data"), list):
            meta["data"] = [{"keys": list(d.keys())} for d in meta["data"]]
        print("Response metadata:")
        print(json.dumps(meta, indent=2))

    data = resp.get("data", [])
    if not isinstance(data, list) or len(data) == 0:
        print("ERROR: No images returned.", file=sys.stderr)
        return 4

    os.makedirs(args.out_dir, exist_ok=True)
    stamp = _utc_stamp()
    saved: List[str] = []

    for i, item in enumerate(data, start=1):
        out_name = f"{args.out_prefix}-{stamp}-{i}.png"
        out_path = os.path.join(args.out_dir, out_name)

        if "b64_json" in item:
            _write_b64_png(item["b64_json"], out_path)
        elif "url" in item:
            _download_file(item["url"], out_path)
        else:
            print(f"ERROR: Unexpected image item keys: {list(item.keys())}", file=sys.stderr)
            return 5

        saved.append(out_path)

    # Print saved files (one per line) for easy parsing
    for s in saved:
        print(s)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
