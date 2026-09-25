"""Loads one or more RateLimiter candidates and prints a comparison table.

Usage:
    python3 harness.py <label>=<path/to/limiter.py> [<label>=<path> ...]

Each candidate must define a class `RateLimiter` matching the contract in
spec.md. This harness never edits a candidate; it only imports and calls it.
"""
import importlib.util
import sys
import time

MAX_REQUESTS = 5
WINDOW_SECONDS = 10.0


def load_candidate(label, path):
    spec = importlib.util.spec_from_file_location(f"candidate_{label}", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.RateLimiter


def correctness_test(limiter_cls):
    """Checks invariants every correct implementation must satisfy,
    regardless of algorithm: burst-then-block, isolation, and eventual
    recovery. Does not check exact boundary behavior — that's what
    burst_ratio_test measures, since algorithms legitimately differ there.
    """
    results = []

    limiter = limiter_cls(MAX_REQUESTS, WINDOW_SECONDS)
    allowed = [limiter.allow("a", 0.0) for _ in range(MAX_REQUESTS)]
    results.append(("first max_requests calls all allowed", all(allowed)))

    over_limit = limiter.allow("a", 0.0)
    results.append(("request beyond limit at same instant is denied", not over_limit))

    other_client = limiter.allow("b", 0.0)
    results.append(("a different client is unaffected by a's limit", other_client))

    recovered = limiter.allow("a", WINDOW_SECONDS * 2)
    results.append(("client can make requests again well after the window", recovered))

    return results


def throughput_test(limiter_cls, calls=20000):
    """Raw call overhead: a high limit so allow/deny logic rarely triggers
    the reject path, spread across many clients so per-client bookkeeping
    overhead shows up too."""
    limiter = limiter_cls(MAX_REQUESTS * 1000, WINDOW_SECONDS)
    start = time.perf_counter()
    now = 0.0
    for i in range(calls):
        limiter.allow(f"client-{i % 500}", now)
        now += 0.0001
    elapsed = time.perf_counter() - start
    return calls / elapsed


def burst_ratio_test(limiter_cls):
    """Objective, algorithm-agnostic measurement of the classic boundary
    weakness: hammer requests right at the end of one window and right at
    the start of the next, then compute the worst-case number of allowed
    requests that fall inside any single window_seconds-wide span. A limiter
    that truly enforces "at most N per window_seconds, always" scores
    max_requests here; one with fixed, non-sliding windows can score up to
    2x that at the boundary.
    """
    limiter = limiter_cls(MAX_REQUESTS, WINDOW_SECONDS)
    client = "burst-client"
    epsilon = 1e-6
    allowed_times = []

    t = WINDOW_SECONDS - epsilon
    for _ in range(MAX_REQUESTS * 2):
        if limiter.allow(client, t):
            allowed_times.append(t)

    t = WINDOW_SECONDS + epsilon
    for _ in range(MAX_REQUESTS * 2):
        if limiter.allow(client, t):
            allowed_times.append(t)

    allowed_times.sort()
    worst = 0
    for t_i in allowed_times:
        count = sum(1 for t_j in allowed_times if t_i <= t_j < t_i + WINDOW_SECONDS)
        worst = max(worst, count)
    return worst


def run(candidates):
    rows = []
    for label, path in candidates:
        limiter_cls = load_candidate(label, path)
        correctness = correctness_test(limiter_cls)
        passed = sum(1 for _, ok in correctness if ok)
        throughput = throughput_test(limiter_cls)
        burst = burst_ratio_test(limiter_cls)
        rows.append((label, correctness, passed, len(correctness), throughput, burst))

    print(f"Contract: max {MAX_REQUESTS} requests per {WINDOW_SECONDS}s window\n")
    header = f"{'candidate':<22}{'correctness':<14}{'calls/sec':<14}{'worst burst':<12}"
    print(header)
    print("-" * len(header))
    for label, correctness, passed, total, throughput, burst in rows:
        burst_flag = "" if burst <= MAX_REQUESTS else "  (>N at boundary)"
        print(
            f"{label:<22}{f'{passed}/{total}':<14}{throughput:<14.0f}{burst:<3}{burst_flag}"
        )

    for label, correctness, passed, total, throughput, burst in rows:
        if passed < total:
            print(f"\n{label} failed:")
            for name, ok in correctness:
                if not ok:
                    print(f"  - {name}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    parsed = []
    for arg in sys.argv[1:]:
        label, _, path = arg.partition("=")
        if not path:
            print(f"Bad argument (expected label=path): {arg}")
            sys.exit(1)
        parsed.append((label, path))
    run(parsed)
