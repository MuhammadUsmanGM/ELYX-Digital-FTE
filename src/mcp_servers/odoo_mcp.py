"""
ELYX Odoo MCP Server
Odoo ERP integration: invoices, payments, revenue, overdue tracking.
"""

import os
import json
from datetime import datetime, timedelta

import httpx
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("elyx-odoo-mcp")

# --- Odoo client ---

ODOO_URL = os.environ.get("ODOO_URL", "https://elyx-ai.odoo.com")
ODOO_DB = os.environ.get("ODOO_DB", "elyx-ai")
ODOO_USERNAME = os.environ.get("ODOO_USERNAME", "")
ODOO_PASSWORD = os.environ.get("ODOO_PASSWORD", "")
ODOO_API_KEY = os.environ.get("ODOO_API_KEY", "")

_uid = None
_session_cookies: dict = {}


def _jsonrpc(url: str, method: str, params: dict) -> dict:
    payload = {"jsonrpc": "2.0", "id": 1, "method": method, "params": params}
    resp = httpx.post(url, json=payload, cookies=_session_cookies, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    if "error" in data:
        raise RuntimeError(data["error"].get("data", {}).get("message", str(data["error"])))
    return data.get("result")


def _authenticate():
    global _uid
    if _uid is not None:
        return _uid
    result = _jsonrpc(f"{ODOO_URL}/web/session/authenticate", "call", {
        "db": ODOO_DB,
        "login": ODOO_USERNAME,
        "password": ODOO_API_KEY or ODOO_PASSWORD,
    })
    _uid = result.get("uid")
    if not _uid:
        raise RuntimeError("Odoo authentication failed")
    return _uid


def _call(model: str, method: str, args: list, kwargs: dict | None = None):
    uid = _authenticate()
    return _jsonrpc(f"{ODOO_URL}/web/dataset/call_kw", "call", {
        "model": model,
        "method": method,
        "args": args,
        "kwargs": kwargs or {},
    })


# --- Tools ---


@mcp.tool()
def create_invoice(partner_id: int, invoice_lines: list[dict], invoice_date: str = "") -> str:
    """Create a customer invoice in Odoo.
    invoice_lines: list of {product_id, quantity, price_unit, name}"""
    lines = []
    for line in invoice_lines:
        lines.append((0, 0, {
            "product_id": line.get("product_id"),
            "quantity": line.get("quantity", 1),
            "price_unit": line.get("price_unit", 0),
            "name": line.get("name", ""),
        }))
    vals = {
        "partner_id": partner_id,
        "move_type": "out_invoice",
        "invoice_line_ids": lines,
    }
    if invoice_date:
        vals["invoice_date"] = invoice_date
    result = _call("account.move", "create", [vals])
    return json.dumps({"success": True, "invoice_id": result})


@mcp.tool()
def register_payment(invoice_id: int, amount: float, payment_date: str = "") -> str:
    """Register a payment for an invoice."""
    vals = {"amount": amount}
    if payment_date:
        vals["payment_date"] = payment_date

    ctx = {"active_model": "account.move", "active_ids": [invoice_id]}
    wizard = _call("account.payment.register", "create", [vals], {"context": ctx})
    _call("account.payment.register", "action_create_payments", [[wizard]], {"context": ctx})
    return json.dumps({"success": True, "invoice_id": invoice_id, "amount": amount})


@mcp.tool()
def search_invoices(
    move_type: str = "",
    state: str = "",
    payment_state: str = "",
    partner_id: int = 0,
    limit: int = 50,
) -> str:
    """Search invoices with optional filters.
    move_type: out_invoice | in_invoice | out_refund | in_refund
    state: draft | posted | cancel
    payment_state: not_paid | partial | paid | reversed"""
    domain = []
    if move_type:
        domain.append(("move_type", "=", move_type))
    if state:
        domain.append(("state", "=", state))
    if payment_state:
        domain.append(("payment_state", "=", payment_state))
    if partner_id:
        domain.append(("partner_id", "=", partner_id))

    ids = _call("account.move", "search", [domain], {"limit": limit})
    if not ids:
        return json.dumps({"count": 0, "invoices": []})

    records = _call("account.move", "read", [ids], {
        "fields": ["name", "partner_id", "amount_total", "state", "payment_state", "invoice_date", "move_type"]
    })
    invoices = []
    for r in records:
        invoices.append({
            "id": r["id"],
            "name": r.get("name"),
            "partner": r.get("partner_id", [None, ""])[1] if isinstance(r.get("partner_id"), list) else "",
            "amount": r.get("amount_total"),
            "state": r.get("state"),
            "payment_state": r.get("payment_state"),
            "date": r.get("invoice_date"),
            "type": r.get("move_type"),
        })
    return json.dumps({"count": len(invoices), "invoices": invoices})


@mcp.tool()
def get_revenue(period: str = "month", start_date: str = "", end_date: str = "") -> str:
    """Get revenue data. period: week | month | year (overridden by start/end dates)."""
    today = datetime.now().date()
    if start_date and end_date:
        d_start, d_end = start_date, end_date
    elif period == "week":
        d_start = str(today - timedelta(days=7))
        d_end = str(today)
    elif period == "year":
        d_start = str(today.replace(month=1, day=1))
        d_end = str(today)
    else:
        d_start = str(today.replace(day=1))
        d_end = str(today)

    domain = [
        ("move_type", "=", "out_invoice"),
        ("state", "=", "posted"),
        ("invoice_date", ">=", d_start),
        ("invoice_date", "<=", d_end),
    ]
    ids = _call("account.move", "search", [domain])
    if not ids:
        return json.dumps({"total_revenue": 0, "invoice_count": 0, "period": period})

    records = _call("account.move", "read", [ids], {"fields": ["amount_total"]})
    total = sum(r.get("amount_total", 0) for r in records)
    return json.dumps({"total_revenue": total, "invoice_count": len(ids), "period": period, "start": d_start, "end": d_end})


@mcp.tool()
def get_overdue_invoices(days_overdue: int = 1, limit: int = 50) -> str:
    """Get overdue customer invoices."""
    cutoff = str(datetime.now().date() - timedelta(days=days_overdue))
    domain = [
        ("move_type", "=", "out_invoice"),
        ("state", "=", "posted"),
        ("payment_state", "in", ["not_paid", "partial"]),
        ("invoice_date_due", "<", cutoff),
    ]
    ids = _call("account.move", "search", [domain], {"limit": limit})
    if not ids:
        return json.dumps({"count": 0, "invoices": []})

    records = _call("account.move", "read", [ids], {
        "fields": ["name", "partner_id", "amount_total", "amount_residual", "invoice_date_due"]
    })
    invoices = []
    for r in records:
        invoices.append({
            "id": r["id"],
            "name": r.get("name"),
            "partner": r.get("partner_id", [None, ""])[1] if isinstance(r.get("partner_id"), list) else "",
            "total": r.get("amount_total"),
            "remaining": r.get("amount_residual"),
            "due_date": r.get("invoice_date_due"),
        })
    return json.dumps({"count": len(invoices), "invoices": invoices})


if __name__ == "__main__":
    mcp.run(transport="stdio")
