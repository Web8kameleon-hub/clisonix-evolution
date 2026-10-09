#!/usr/bin/env python3
import argparse
import json
import os
import time
from typing import Optional

import requests


def run_benchmark(host: str, model: str, prompt: str, timeout: int) -> int:
    url = f"{host.rstrip('/')}/api/generate"
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": True,
        "keep_alive": "30m",
    }

    started = time.perf_counter()
    first_token_at: Optional[float] = None
    collected = []
    eval_count = None
    eval_duration_ns = None

    with requests.post(url, json=payload, stream=True, timeout=timeout) as response:
        response.raise_for_status()
        for raw_line in response.iter_lines(decode_unicode=True):
            if not raw_line:
                continue
            try:
                item = json.loads(raw_line)
            except json.JSONDecodeError:
                continue

            token = item.get("response", "")
            if token:
                collected.append(token)
                if first_token_at is None:
                    first_token_at = time.perf_counter()

            if item.get("done"):
                eval_count = item.get("eval_count")
                eval_duration_ns = item.get("eval_duration")
                break

    finished = time.perf_counter()

    text = "".join(collected)
    words = len(text.split())
    total_s = max(finished - started, 1e-9)
    ttfb_s = (first_token_at - started) if first_token_at else total_s
    words_per_s = words / total_s

    print("\n=== CPU Benchmark (No GPU) ===")
    print(f"Host:                 {host}")
    print(f"Model:                {model}")
    print(f"Prompt chars:         {len(prompt)}")
    print(f"Time-to-first-token:  {ttfb_s:.3f}s")
    print(f"Total time:           {total_s:.3f}s")
    print(f"Generated words:      {words}")
    print(f"Words/sec:            {words_per_s:.2f}")

    if eval_count and eval_duration_ns:
        tok_s = eval_count / (eval_duration_ns / 1_000_000_000)
        print(f"Eval tokens:          {eval_count}")
        print(f"Eval tok/sec:         {tok_s:.2f}")

    print("\nTip: krahaso rezultate para/pas cpu_boost_no_gpu.* dhe para/pas modelit quantized.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Benchmark Ollama throughput on CPU (no GPU)")
    parser.add_argument("--host", default=os.getenv("OLLAMA_HOST", "http://localhost:11434"))
    parser.add_argument("--model", default=os.getenv("MODEL", "llama3.2:3b"))
    parser.add_argument(
        "--prompt",
        default="Shpjego shkurt si optimizohet inferenca LLM pa GPU dhe jep hapa praktik.",
    )
    parser.add_argument("--timeout", type=int, default=180)
    args = parser.parse_args()

    try:
        return run_benchmark(args.host, args.model, args.prompt, args.timeout)
    except requests.HTTPError as http_error:
        print(f"HTTP error: {http_error}")
        return 2
    except requests.RequestException as request_error:
        print(f"Network error: {request_error}")
        return 3
    except Exception as error:
        print(f"Unexpected error: {error}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
