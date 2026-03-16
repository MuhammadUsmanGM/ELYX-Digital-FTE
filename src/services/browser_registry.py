"""
Shared Browser Registry
=======================
Prevents session corruption when a watcher holds a persistent Playwright
browser open and the sender tries to launch a second instance on the same
session directory.

Watchers **register** their live (playwright, browser, page) tuple.
Senders **acquire** the page via a threading lock, use it, then **release**.
If no watcher owns the session, senders fall back to launching their own browser.

Thread-safety: every registered session carries its own `threading.Lock`.
The sender must hold the lock for the entire navigation→send→verify cycle.
"""

import threading
import logging
from typing import Optional, Tuple

logger = logging.getLogger("BrowserRegistry")

# { session_path_str: { "playwright": p, "browser": ctx, "page": page, "lock": Lock } }
_registry: dict = {}
_registry_lock = threading.Lock()


def register(session_path: str, playwright_obj, browser_ctx, page) -> None:
    """Called by a watcher after it opens its persistent browser."""
    key = str(session_path)
    with _registry_lock:
        _registry[key] = {
            "playwright": playwright_obj,
            "browser": browser_ctx,
            "page": page,
            "lock": threading.Lock(),
        }
    logger.info(f"Browser registered for session: {key}")


def unregister(session_path: str) -> None:
    """Called by a watcher when it closes its browser (cleanup / crash recovery)."""
    key = str(session_path)
    with _registry_lock:
        _registry.pop(key, None)
    logger.info(f"Browser unregistered for session: {key}")


def acquire_page(session_path: str, timeout: float = 30) -> Optional[Tuple]:
    """
    Try to borrow the watcher's page for sending.

    Returns (page, release_fn) if a watcher owns the session, else (None, None).
    The caller **must** call release_fn() when done.
    """
    key = str(session_path)
    with _registry_lock:
        entry = _registry.get(key)

    if entry is None:
        return None, None

    lock: threading.Lock = entry["lock"]
    acquired = lock.acquire(timeout=timeout)
    if not acquired:
        logger.warning(f"Timeout acquiring browser lock for {key}")
        return None, None

    page = entry["page"]
    # Verify the page is still alive
    try:
        if page.is_closed():
            lock.release()
            unregister(key)
            return None, None
    except Exception:
        lock.release()
        unregister(key)
        return None, None

    def release():
        lock.release()

    return page, release
