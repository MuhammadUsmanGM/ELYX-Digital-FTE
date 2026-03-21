#!/usr/bin/env python3
"""
ELYX - Autonomous AI Employee
Main Startup Script - ALL-IN-ONE

Starts all services, shows a clean status table, then streams logs.
"""

import os
import sys
import time
import threading
import subprocess
import signal
import atexit
import logging
from pathlib import Path
from datetime import datetime

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


def print_row(service, port, ok, note=""):
    icon = status_icon(ok)
    status = f"{G}running{X}" if ok else f"{R}failed{X}"
    note_str = f"  {D}{note}{X}" if note else ""
    print(f"  {icon}  {service:<22} {D}:{X}{port:<6} {status}{note_str}")


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

    # ── Status Table ──────────────────────────────────────────────
    print(f"  {B}ELYX Startup{X}  {D}{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{X}  {D}Brain: {brain}{X}")
    print(f"  {D}{'─'*58}{X}")

    r1 = start_vault_api()
    print_row("Vault API", "8080", r1)

    r2 = start_settings_api()
    print_row("Settings API", "8081", r2)

    r3 = start_main_api()
    print_row("Main API (FastAPI)", port, r3)

    r4 = start_frontend()
    if not r4 and not (project_root / "frontend" / "node_modules").exists():
        print_row("Frontend (Next.js)", "3000", False, "run: cd frontend && npm install")
    else:
        print_row("Frontend (Next.js)", "3000", r4)

    r5, orch = start_orchestrator(vault_path)
    print_row("Orchestrator", "—", r5, "watchers + task monitor")

    is_vault_git_repo()
    print_row("Vault Git Sync", "—", vault_git_enabled, "hourly auto-commit" if vault_git_enabled else "no .git found")

    total = sum([r1, r2, r3, r4, r5])
    print(f"  {D}{'─'*58}{X}")

    if total == 5:
        print(f"\n  {G}{B}ALL SYSTEMS OPERATIONAL{X}  {D}({total}/5 services){X}\n")
    elif total >= 3:
        print(f"\n  {Y}{B}PARTIALLY OPERATIONAL{X}  {D}({total}/5 services){X}\n")
    else:
        print(f"\n  {R}{B}STARTUP FAILED{X}  {D}({total}/5 services){X}\n")

    # ── Watchers Table ────────────────────────────────────────────
    config = orch.config if orch else {}
    watchers = probe_watchers(config)
    w_ok = sum(1 for _, _, s in watchers if s == "ok")

    print(f"  {B}Watchers{X}  {D}({w_ok}/{len(watchers)} enabled){X}")
    print(f"  {D}{'─'*58}{X}")
    for wname, interval, wstatus in watchers:
        if wstatus == "ok":
            icon = f"{G}✓{X}"
            label = f"{G}enabled{X}"
        elif wstatus == "disabled":
            icon = f"{D}—{X}"
            label = f"{D}disabled{X}"
        elif wstatus == "missing":
            icon = f"{Y}!{X}"
            label = f"{Y}import err{X}"
        else:
            icon = f"{R}✗{X}"
            label = f"{R}error{X}"
        print(f"  {icon}  {wname:<18} {D}every{X} {interval:<5}  {label}")
    print(f"  {D}{'─'*58}{X}")

    # ── Quick Links ───────────────────────────────────────────────
    print(f"\n  {B}Access Points{X}")
    print(f"  {D}{'─'*58}{X}")
    print(f"  Dashboard      {C}http://localhost:3000{X}")
    print(f"  API Docs       {C}http://localhost:{port}/docs{X}")
    print(f"  Vault API      {C}http://localhost:8080{X}")
    print(f"  Settings API   {C}http://localhost:8081{X}")
    print(f"  {D}{'─'*58}{X}")
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
