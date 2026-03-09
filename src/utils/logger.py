import logging
import json
import hashlib
from pathlib import Path
from datetime import datetime, timedelta
import os


def setup_logger(name, log_file=None, level=logging.INFO):
    """
    Set up a logger with both file and console handlers
    """
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Avoid adding duplicate handlers
    if not logger.handlers:
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        # File handler (if log_file is provided)
        if log_file:
            # Ensure log directory exists
            log_dir = Path(log_file).parent
            log_dir.mkdir(parents=True, exist_ok=True)

            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

    return logger


def _compute_sha3_512(data: str) -> str:
    """Compute SHA3-512 hash of the given string."""
    return hashlib.sha3_512(data.encode('utf-8')).hexdigest()


def _get_previous_hash(audit_file: Path) -> str:
    """Get the hash of the last entry in the audit trail for chaining."""
    if not audit_file.exists():
        return "0" * 128  # Genesis hash
    try:
        with open(audit_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        if lines:
            last_entry = json.loads(lines[-1])
            return last_entry.get('hash', "0" * 128)
    except Exception:
        pass
    return "0" * 128


def log_activity(activity_type, message, vault_path):
    """
    Log an activity to the vault's log directory with timestamp.
    Also appends a cryptographically signed entry to the audit trail.
    """
    vault_path = Path(vault_path)
    log_dir = vault_path / "Logs"
    log_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # 1. Human-readable daily log
    log_file = log_dir / f"{datetime.now().strftime('%Y-%m-%d')}.log"
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(f"[{timestamp}] {activity_type.upper()}: {message}\n")

    # 2. Cryptographic audit trail (SHA3-512 chained hashing)
    audit_file = log_dir / "audit_trail.json"
    try:
        previous_hash = _get_previous_hash(audit_file)

        entry = {
            "timestamp": datetime.now().isoformat(),
            "action_type": activity_type.upper(),
            "message": message,
            "actor": "elyx_ai_employee",
            "previous_hash": previous_hash,
        }

        # Create hash of the entry data + previous hash (blockchain-style chaining)
        hash_payload = f"{entry['timestamp']}|{entry['action_type']}|{entry['message']}|{previous_hash}"
        entry["hash"] = _compute_sha3_512(hash_payload)

        with open(audit_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(entry) + '\n')

    except Exception:
        pass  # Never let audit logging break the main flow


def verify_audit_trail(vault_path) -> dict:
    """
    Verify the integrity of the audit trail by checking the SHA3-512 hash chain.

    Returns:
        dict with 'valid' (bool), 'entries_checked' (int), 'errors' (list)
    """
    audit_file = Path(vault_path) / "Logs" / "audit_trail.json"
    if not audit_file.exists():
        return {"valid": True, "entries_checked": 0, "errors": []}

    errors = []
    previous_hash = "0" * 128
    count = 0

    with open(audit_file, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
                count += 1

                # Verify previous hash matches
                if entry.get("previous_hash") != previous_hash:
                    errors.append(f"Line {line_num}: previous_hash mismatch (chain broken)")

                # Verify the entry's own hash
                hash_payload = (
                    f"{entry['timestamp']}|{entry['action_type']}|"
                    f"{entry['message']}|{entry['previous_hash']}"
                )
                expected_hash = _compute_sha3_512(hash_payload)
                if entry.get("hash") != expected_hash:
                    errors.append(f"Line {line_num}: hash mismatch (entry tampered)")

                previous_hash = entry.get("hash", previous_hash)

            except json.JSONDecodeError:
                errors.append(f"Line {line_num}: invalid JSON")

    return {"valid": len(errors) == 0, "entries_checked": count, "errors": errors}


def get_recent_logs(vault_path, days=1):
    """
    Get recent log entries from the log directory
    """
    log_dir = Path(vault_path) / "Logs"
    if not log_dir.exists():
        return []

    log_entries = []
    for day_offset in range(days):
        date_str = (datetime.now() - timedelta(days=day_offset)).strftime('%Y-%m-%d')
        log_file = log_dir / f"{date_str}.log"

        if log_file.exists():
            with open(log_file, 'r', encoding='utf-8') as f:
                log_entries.extend(f.readlines())

    return log_entries
