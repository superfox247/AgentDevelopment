import statistics
import sys
import time

"""
Gemini Model Benchmarking Tool.

Discovers available Gemini models in the project's region and runs latency tests
to help select the best model for 'Flash' (fast) vs 'Pro' (quality) use cases.
"""

from google import genai

from agent_platform.config import PlatformConfig

# Force UTF-8 output for Windows consoles/subprocesses
if sys.platform == "win32":
    try:
        from io import TextIOWrapper
        from typing import cast

        cast(TextIOWrapper, sys.stdout).reconfigure(encoding="utf-8")
        cast(TextIOWrapper, sys.stderr).reconfigure(encoding="utf-8")
    except AttributeError:
        pass  # python < 3.7 or other odd env


def _discover_models(client: genai.Client) -> list[str]:
    print("\n🔎 Discovering Models...", flush=True)
    all_models = list(client.models.list())
    candidates = [
        m.name
        for m in all_models
        if m.name
        and "gemini" in m.name
        and "flash" in m.name
        and "vision" not in m.name
        and "legacy" not in m.name
    ]
    return sorted(set(candidates))


def _select_targets(candidates: list[str]) -> list[str]:
    targets = []
    priorities = [
        "models/gemini-2.0-flash",
        "models/gemini-2.0-flash-lite-preview-02-05",
        "models/gemini-1.5-flash",
    ]
    for p in priorities:
        if p in candidates:
            targets.append(p)

    for c in candidates:
        if c not in targets and len(targets) < 4:
            targets.append(c)

    print(f"🎯 Selected Targets: {targets}", flush=True)
    return targets


def _run_benchmarks(client: genai.Client, targets: list[str]) -> dict[str, float]:
    results = {}
    print("\n⏱️  Running Latency Tests (3 iterations)...", flush=True)
    prompt = "Explain quantum computing in 5 words."

    for model in targets:
        latencies = []
        print(f"  👉 Testing {model}...", end="", flush=True)

        for _i in range(3):
            try:
                start = time.time()
                client.models.generate_content(model=model, contents=prompt)
                dur = time.time() - start
                latencies.append(dur)
            except Exception as e:
                print(f" [Error: {str(e)[:50]}]", end="", flush=True)

        if latencies:
            avg = statistics.mean(latencies)
            results[model] = avg
            print(f" ✅ Avg: {avg:.4f}s", flush=True)
        else:
            print(" ❌ All Failed", flush=True)
    return results


def _print_results(results: dict[str, float]) -> None:
    print("\n🏆 BENCHMARK RESULTS", flush=True)
    print("=======================", flush=True)
    sorted_results = sorted(results.items(), key=lambda x: x[1])

    for model, lat in sorted_results:
        bar = "█" * int(lat * 10)
        print(f"{model:<40} | {lat:.4f}s | {bar}", flush=True)

    if sorted_results:
        winner = sorted_results[0][0]
        print(f"\n✨ Recommended Model: {winner}", flush=True)


def benchmark_models() -> None:
    print("🚀 Benchmarking Gemini Models...", flush=True)

    try:
        config = PlatformConfig()
        client = genai.Client(api_key=config.gemini_api_key)

        candidates = _discover_models(client)
        targets = _select_targets(candidates)
        results = _run_benchmarks(client, targets)
        _print_results(results)

    except Exception as e:
        print(f"\n❌ Benchmark Failed: {e}", flush=True)


if __name__ == "__main__":
    benchmark_models()
