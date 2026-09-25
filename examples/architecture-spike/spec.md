# Spike: per-client rate limiter

Implement a class named `RateLimiter` satisfying this interface:

```python
class RateLimiter:
    def __init__(self, max_requests: int, window_seconds: float):
        """Allow at most max_requests per client in any window_seconds-long span."""

    def allow(self, client_id: str, now: float) -> bool:
        """Return True if a request from client_id at time `now` should be
        allowed, False if it should be rejected. Must record the request if
        (and only if) it's allowed.
        """
```

Constraints:

- **Per-client isolation.** One client's usage must never affect another
  client's limit.
- **No wall-clock reads.** Never call `time.time()`, `time.monotonic()`, or
  sleep. `now` is always supplied by the caller (this is what lets the
  comparison harness drive time deterministically instead of waiting on a
  real clock).
- **Standard library only.** No third-party dependencies.
- Put your implementation in the file path given in your prompt, named
  exactly `limiter.py`, defining exactly one class: `RateLimiter`.

Your assigned approach — a specific algorithm to implement this interface
with — is given in your prompt. Implement that approach faithfully; the
point of this spike is to compare how different algorithms behave against
the *same* interface, not to invent a fourth one.
