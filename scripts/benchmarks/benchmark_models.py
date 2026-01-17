import statistics
import sys
import time

from google import genai

from agent_platform.config import PlatformConfig

# Force UTF-8 output for Windows consoles/subprocesses
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
        sys.stderr.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
    except AttributeError:
        pass  # python < 3.7 or other odd env


def benchmark_models() -> None:
    print("🚀 Benchmarking Gemini Models...", flush=True)

    try:
        config = PlatformConfig()
        client = genai.Client(api_key=config.gemini_api_key)

        # 1. Discovery
        print("\n🔎 Discovering Models...", flush=True)
        all_models = list(client.models.list())

        # Filter for generateContent support by name heuristic
        candidates = [
            m.name
            for m in all_models
            if m.name
            and "gemini" in m.name
            and "flash" in m.name
            and "vision" not in m.name
            and "legacy" not in m.name
        ]

        # Deduplicate and sort
        candidates = sorted(list(set(candidates)))

        # Pick top interesting ones to benchmark
        # We want to compare 2.0 vs 1.5 if available, or just different 2.0 variants
        targets = []
        priorities = [
            "models/gemini-2.0-flash",
            "models/gemini-2.0-flash-lite-preview-02-05",
            "models/gemini-1.5-flash",
        ]

        for p in priorities:
            if p in candidates:
                targets.append(p)

        # Fill with others if needed
        for c in candidates:
            if c not in targets and len(targets) < 4:
                targets.append(c)

        print(f"🎯 Selected Targets: {targets}", flush=True)

        results = {}

        # 2. Benchmark Loop
        print("\n⏱️  Running Latency Tests (3 iterations)...", flush=True)
        prompt = "Explain quantum computing in 5 words."

        for model in targets:
            latencies = []
            print(f"  👉 Testing {model}...", end="", flush=True)

            for i in range(3):
                try:
                    start = time.time()
                    resp = client.models.generate_content(model=model, contents=prompt)
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

        # 3. Report
        print("\n🏆 BENCHMARK RESULTS", flush=True)
        print("=======================", flush=True)
        sorted_results = sorted(results.items(), key=lambda x: x[1])

        for model, lat in sorted_results:
            bar = "█" * int(lat * 10)
            print(f"{model:<40} | {lat:.4f}s | {bar}", flush=True)

        # Recommend
        if sorted_results:
            winner = sorted_results[0][0]
            print(f"\n✨ Recommended Model: {winner}", flush=True)

    except Exception as e:
        print(f"\n❌ Benchmark Failed: {e}", flush=True)


if __name__ == "__main__":
    benchmark_models()
