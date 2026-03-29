#!/usr/bin/env python3
"""
ELYX - Autonomous AI Employee
Main Startup Script - ALL-IN-ONE

Starts all services, shows a clean status table, then streams logs.
"""

import os
import sys
import io
import time
import threading
import subprocess
import signal
import atexit
import logging
from pathlib import Path
from datetime import datetime

# Force UTF-8 output on Windows (box-drawing chars need it)
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")
    os.system("")  # enable ANSI escape codes on Windows terminal

# ── Project Setup ─────────────────────────────────────────────────────
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

logs_dir = project_root / "obsidian_vault" / "Logs"
logs_dir.mkdir(parents=True, exist_ok=True)

# ── ANSI Helpers ──────────────────────────────────────────────────────
G = "\033[92m"   # green
R = "\033[91m"   # red
Y = "\033[93m"   # yellow
C = "\033[96m"   # cyan
B = "\033[1m"    # bold
D = "\033[2m"    # dim
X = "\033[0m"    # reset
T = "\033[38;2;0;201;167m"  # teal/ELYX brand

# ── Globals ───────────────────────────────────────────────────────────
processes = []
log_handles = []
_cleanup_done = False
vault_git_enabled = False

# Suppress noisy libraries during import
logging.getLogger("uvicorn").setLevel(logging.WARNING)
logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
logging.getLogger("uvicorn.error").setLevel(logging.WARNING)
logging.getLogger("watchdog").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)

# ── Utility ───────────────────────────────────────────────────────────

def _log_file(name: str):
    """Open a log file handle for a child service (appended)."""
    fh = open(logs_dir / f"{name}.log", "a", encoding="utf-8")
    log_handles.append(fh)
    return fh


def run_command(cmd, cwd=None):
    """Run a shell command safely (list form)."""
    try:
        if isinstance(cmd, str):
            import shlex
            cmd = shlex.split(cmd)
        r = subprocess.run(cmd, shell=False, cwd=cwd, capture_output=True, text=True, timeout=10)
        return r.returncode == 0, r.stdout, r.stderr
    except Exception as e:
        return False, "", str(e)


def is_vault_git_repo():
    global vault_git_enabled
    vault_git_enabled = (Path("obsidian_vault") / ".git").exists()
    return vault_git_enabled


def commit_vault_changes(message="Auto-commit: Vault changes"):
    if not vault_git_enabled:
        return False
    try:
        vp = Path("obsidian_vault")
        ok, out, _ = run_command(["git", "status", "--porcelain"], cwd=vp)
        if not out.strip():
            return False
        run_command(["git", "add", "."], cwd=vp)
        run_command(["git", "commit", "-m", message], cwd=vp)
        return True
    except Exception:
        return False


# ── Service Launchers (all output → log files) ───────────────────────

def _start_service(name, cmd, cwd=None, wait=2):
    """Start a subprocess, pipe output to log file. Returns (success, proc)."""
    log = _log_file(name)
    log.write(f"\n{'='*60}\n[{datetime.now().isoformat()}] Starting {name}\n{'='*60}\n")
    log.flush()
    try:
        proc = subprocess.Popen(cmd, cwd=cwd or str(project_root), stdout=log, stderr=log)
        processes.append(proc)
        time.sleep(wait)
        alive = proc.poll() is None
        return alive, proc
    except Exception:
        return False, None


def start_vault_api():
    ok, _ = _start_service(
        "vault_api",
        [sys.executable, str(project_root / "src" / "api" / "vault_api.py"), "--port", "8080"],
        wait=2,
    )
    return ok


def start_settings_api():
    ok, _ = _start_service(
        "settings_api",
        [sys.executable, str(project_root / "src" / "api" / "settings_api.py"), "--port", "8081"],
        wait=2,
    )
    return ok


def start_main_api():
    port = os.getenv("PORT", "8000")
    ok, _ = _start_service(
        "main_api",
        [sys.executable, "-m", "uvicorn", "src.api.main:app",
         "--host", "0.0.0.0", "--port", port, "--log-level", "warning"],
        wait=3,
    )
    return ok


def start_frontend():
    frontend_dir = project_root / "frontend"
    if not (frontend_dir / "node_modules").exists():
        return False
    npm = "npm.cmd" if sys.platform == "win32" else "npm"
    ok, _ = _start_service("frontend", [npm, "run", "dev"], cwd=str(frontend_dir), wait=5)
    return ok


def start_orchestrator(vault_path):
    """Start orchestrator in-process (background thread). Returns (success, orch_instance)."""
    try:
        # Quiet orchestrator / watcher loggers
        for name in ["orchestrator", "orchestrator.main", "orchestrator.filesystem",
                      "gmail_watcher", "whatsapp_watcher",
                      "linkedin_watcher", "facebook_watcher", "twitter_watcher",
                      "instagram_watcher", "odoo_watcher", "filesystem_watcher",
                      "social_media_watcher", "briefing_service"]:
            logging.getLogger(name).setLevel(logging.WARNING)

        from src.agents.orchestrator import Orchestrator
        orch = Orchestrator(vault_path=str(vault_path))
        t = threading.Thread(target=orch.run, daemon=False, name="orchestrator")
        t.start()
        processes.append(orch)
        return True, orch
    except Exception:
        return False, None


# ── Watcher Probing ───────────────────────────────────────────────────

WATCHER_DEFS = [
    ("Gmail",      "integrations.gmail_enabled",     "src.agents.gmail_watcher",      "GmailWatcher",     "2m"),
    ("WhatsApp",   "integrations.whatsapp_enabled",  "src.agents.whatsapp_watcher",   "WhatsAppWatcher",  "1m"),
    ("LinkedIn",   "integrations.linkedin_enabled",  "src.agents.linkedin_watcher",   "LinkedInWatcher",  "1h"),
    ("Facebook",   "integrations.facebook_enabled",  "src.agents.facebook_watcher",   "FacebookWatcher",  "2h"),
    ("Twitter/X",  "integrations.twitter_enabled",   "src.agents.twitter_watcher",    "TwitterWatcher",   "2h"),
    ("Instagram",  "integrations.instagram_enabled", "src.agents.instagram_watcher",  "InstagramWatcher", "2h"),
    ("Odoo",       "integrations.odoo_enabled",      "src.agents.odoo_watcher",       "OdooWatcher",      "1h"),
    ("Filesystem", "integrations.filesystem_enabled","src.agents.filesystem_watcher", "FileSystemWatcher","10s"),
]


def probe_watchers(config: dict):
    """Check which watchers are enabled in config and importable. Returns list of (name, interval, status)."""
    results = []
    integrations = config.get("integrations", {})
    for name, cfg_key, module_path, class_name, interval in WATCHER_DEFS:
        key = cfg_key.split(".")[-1]  # e.g. "gmail_enabled"
        enabled = integrations.get(key, True)
        if not enabled:
            results.append((name, interval, "disabled"))
            continue
        # Try to import the watcher class
        try:
            __import__(module_path, fromlist=[class_name])
            results.append((name, interval, "ok"))
        except ImportError:
            results.append((name, interval, "missing"))
        except Exception:
            results.append((name, interval, "error"))
    return results


# ── Cleanup ───────────────────────────────────────────────────────────

def cleanup(signum=0, frame=None):
    global _cleanup_done
    if _cleanup_done:
        return
    _cleanup_done = True

    print(f"\n\n{Y}{'─'*62}{X}")
    print(f"{B}  Shutting down ELYX ...{X}")
    print(f"{Y}{'─'*62}{X}\n")

    stopped = 0
    for proc in processes:
        try:
            if hasattr(proc, "cleanup"):
                proc.cleanup()
            elif hasattr(proc, "terminate"):
                proc.terminate()
                proc.wait(timeout=5)
            stopped += 1
        except Exception:
            try:
                if hasattr(proc, "kill"):
                    proc.kill()
                stopped += 1
            except Exception:
                pass

    for fh in log_handles:
        try:
            fh.close()
        except Exception:
            pass

    print(f"  {G}✓{X} {stopped} service(s) stopped")
    print(f"  {B}ELYX shutdown complete. Goodbye!{X}\n")


# ── Display ───────────────────────────────────────────────────────────

def print_banner():
    print(f"""
{T}███████╗██╗     ██╗   ██╗██╗  ██╗{X}
{T}██╔════╝██║     ╚██╗ ██╔╝╚██╗██╔╝{X}
{T}█████╗  ██║      ╚████╔╝  ╚███╔╝ {X}
{T}██╔══╝  ██║       ╚██╔╝   ██╔██╗ {X}
{T}███████╗███████╗   ██║   ██╔╝ ██╗{X}
{T}╚══════╝╚══════╝   ╚═╝   ╚═╝  ╚═╝{X}
{B}{C}  Autonomous AI Employee{X}
""")


def status_icon(ok):
    return f"{G}✓{X}" if ok else f"{R}✗{X}"


def ok_text(ok, label_ok="running", label_fail="failed"):
    return f"{G}{label_ok}{X}" if ok else f"{R}{label_fail}{X}"


def print_row(service, port, ok, note=""):
    icon = status_icon(ok)
    status = ok_text(ok)
    note_str = f"  {D}{note}{X}" if note else ""
    print(f"  {icon}  {service:<22} {D}:{X}{port:<6} {status}{note_str}")


# ── Table Drawing Helpers ────────────────────────────────────────────

def _visible_len(s):
    """Length of string without ANSI escape codes."""
    import re
    return len(re.sub(r'\033\[[0-9;]*m', '', s))


def _pad(s, width):
    """Pad string to width accounting for ANSI codes."""
    return s + ' ' * (width - _visible_len(s))


def print_table(headers, rows, col_widths=None):
    """Print a bordered table with ANSI support."""
    cols = len(headers)
    if not col_widths:
        col_widths = [max(
            _visible_len(headers[c]),
            *((_visible_len(str(row[c])) for row in rows) if rows else [0])
        ) + 2 for c in range(cols)]

    def h_line(left, mid, right):
        return left + mid.join('─' * w for w in col_widths) + right

    top    = f"  {D}{h_line('┌', '┬', '┐')}{X}"
    mid    = f"  {D}{h_line('├', '┼', '┤')}{X}"
    bottom = f"  {D}{h_line('└', '┴', '┘')}{X}"

    def fmt_row(cells):
        parts = []
        for i, cell in enumerate(cells):
            parts.append(_pad(str(cell), col_widths[i]))
        return f"  {D}│{X}" + f"{D}│{X}".join(parts) + f"{D}│{X}"

    print(top)
    print(fmt_row([f" {B}{h}{X}" for h in headers]))
    print(mid)
    for r, row in enumerate(rows):
        print(fmt_row([f" {cell}" for cell in row]))
        if r < len(rows) - 1:
            print(mid)
    print(bottom)


# ── Main ──────────────────────────────────────────────────────────────

def main():
    print_banner()

    # Signal handlers
    signal.signal(signal.SIGINT, cleanup)
    if hasattr(signal, "SIGTERM"):
        signal.signal(signal.SIGTERM, cleanup)
    atexit.register(cleanup)

    # Vault
    vault_path = Path("obsidian_vault")
    vault_path.mkdir(exist_ok=True)

    brain = os.getenv("ELYX_ACTIVE_BRAIN", "claude").capitalize()
    port = os.getenv("PORT", "8000")

    # ── Launch Services ─────────────────────────────────────────────
    r1 = start_vault_api()
    r2 = start_settings_api()
    r3 = start_main_api()
    r4 = start_frontend()
    r5, orch = start_orchestrator(vault_path)
    is_vault_git_repo()

    # ── Watchdog ─────────────────────────────────────────────────
    watchdog_ok = False
    try:
        from src.agents.watchdog import WatchdogAgent
        watchdog = WatchdogAgent(str(vault_path))
        watchdog_thread = threading.Thread(target=watchdog.run, kwargs={"check_interval": 120}, daemon=True)
        watchdog_thread.start()
        watchdog_ok = True
    except Exception:
        pass

    total = sum([r1, r2, r3, r4, r5])

    # ── Services Table ───────────────────────────────────────────
    print(f"  {B}ELYX Startup{X}  {D}{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{X}  {D}Brain: {brain}{X}\n")

    print_table(
        ["Service", "Port", "Status"],
        [
            ["Vault API",          f"{D}8080{X}",  ok_text(r1)],
            ["Settings API",       f"{D}8081{X}",  ok_text(r2)],
            ["Main API (FastAPI)", f"{D}{port}{X}", ok_text(r3)],
            ["Frontend (Next.js)", f"{D}3000{X}",  ok_text(r4) if r4 else f"{Y}npm install needed{X}"],
            ["Orchestrator",       f"{D}—{X}",     ok_text(r5)],
            ["Vault Git Sync",    f"{D}—{X}",     ok_text(vault_git_enabled, "enabled", "no .git")],
            ["Watchdog",           f"{D}—{X}",     ok_text(watchdog_ok)],
        ],
        col_widths=[22, 8, 22],
    )

    if total == 5:
        print(f"\n  {G}{B}ALL SYSTEMS OPERATIONAL{X}  {D}({total}/5 services){X}\n")
    elif total >= 3:
        print(f"\n  {Y}{B}PARTIALLY OPERATIONAL{X}  {D}({total}/5 services){X}\n")
    else:
        print(f"\n  {R}{B}STARTUP FAILED{X}  {D}({total}/5 services){X}\n")

    # ── Watchers Table ───────────────────────────────────────────
    config = orch.config if orch else {}
    watchers = probe_watchers(config)
    w_ok = sum(1 for _, _, s in watchers if s == "ok")

    def watcher_status(s):
        if s == "ok":       return f"{G}✓ enabled{X}"
        if s == "disabled": return f"{D}— disabled{X}"
        if s == "missing":  return f"{Y}! import err{X}"
        return f"{R}✗ error{X}"

    print_table(
        ["Watcher", "Interval", "Status"],
        [[n, f"{D}{i}{X}", watcher_status(s)] for n, i, s in watchers],
        col_widths=[16, 10, 18],
    )
    print(f"  {D}{w_ok}/{len(watchers)} watchers enabled{X}\n")

    # ── Integration Modes Table ──────────────────────────────────
    def mcp_cell(name):
        return f"{G}{name} ✓{X}"

    def direct_cell(name):
        return f"{G}{name} ✓{X}"

    print_table(
        ["Mode", "Email", "WhatsApp", "Social", "Odoo"],
        [
            [f"{C}Claude Code{X}",   mcp_cell("email-mcp"),    mcp_cell("whatsapp-mcp"), mcp_cell("social-mcp"), mcp_cell("odoo-mcp")],
            [f"{C}Auto Pipeline{X}", direct_cell("direct_api"), direct_cell("direct_api"), direct_cell("direct_api"), direct_cell("odoo_svc")],
            [f"{C}Ralph Loop{X}",    mcp_cell("email-mcp"),    mcp_cell("whatsapp-mcp"), mcp_cell("social-mcp"), mcp_cell("odoo-mcp")],
        ],
        col_widths=[18, 18, 18, 18, 16],
    )

    # ── Access Points ────────────────────────────────────────────
    print_table(
        ["Endpoint", "URL"],
        [
            ["Dashboard",    f"{C}http://localhost:3000{X}"],
            ["API Docs",     f"{C}http://localhost:{port}/docs{X}"],
            ["Vault API",    f"{C}http://localhost:8080{X}"],
            ["Settings API", f"{C}http://localhost:8081{X}"],
        ],
        col_widths=[18, 36],
    )
    print(f"\n  {Y}Ctrl+C{X} to shut down  {D}│{X}  Logs → {D}obsidian_vault/Logs/*.log{X}\n")

    # ── Keep-alive loop (auto-commit + stream important events) ──
    last_commit = time.time()
    try:
        while True:
            time.sleep(10)
            if vault_git_enabled and (time.time() - last_commit) > 3600:
                if commit_vault_changes(f"Auto-commit: {datetime.now().strftime('%Y-%m-%d %H:%M')}"):
                    print(f"  {D}[{datetime.now().strftime('%H:%M')}]{X} {G}✓{X} Vault changes committed")
                last_commit = time.time()
    except KeyboardInterrupt:
        if vault_git_enabled:
            commit_vault_changes(f"Final commit: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        cleanup()
        sys.exit(0)


if __name__ == "__main__":
    main()
