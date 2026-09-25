"""A minimal in-memory job queue shared between the API and the worker."""

_QUEUE = []


def enqueue(job_type, payload):
    _QUEUE.append({"job_type": job_type, "payload": payload})


def dequeue():
    if not _QUEUE:
        return None
    return _QUEUE.pop(0)


def pending_count():
    return len(_QUEUE)
