"""
Finance API routes

Exposes financial data to the frontend, backed by Odoo when configured.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import List, Literal, Optional

from fastapi import APIRouter, Query
from pydantic import BaseModel

from ...services.odoo_service import get_odoo_service


finance_router = APIRouter(prefix="/finance", tags=["finance"])


class TransactionResponse(BaseModel):
    id: str
    type: Literal["income", "expense"]
    amount: float
    category: str
    merchant: str
    date: str
    status: Literal["completed", "pending", "flagged"]


class KPIResponse(BaseModel):
    label: str
    value: str
    change: float
    trend: Literal["up", "down", "neutral"]


def _pct_change(current: float, previous: float) -> float:
    if previous == 0:
        return 0.0
    return round(((current - previous) / previous) * 100.0, 2)


def _trend(change: float) -> Literal["up", "down", "neutral"]:
    if change > 0:
        return "up"
    if change < 0:
        return "down"
    return "neutral"


def _format_currency(amount: float) -> str:
    return f"${amount:,.2f}"


@finance_router.get("/transactions", response_model=dict)
def get_transactions(
    limit: int = Query(25, ge=1, le=200),
    include_expenses: bool = Query(True),
):
    """
    Return recent transactions derived from Odoo invoices/bills.

    Response shape:
      { "transactions": TransactionResponse[], "source": "odoo"|"fallback" }
    """
    odoo = get_odoo_service()
    if not odoo or not getattr(odoo, "authenticated", False):
        now = datetime.utcnow().isoformat()
        return {
            "source": "fallback",
            "transactions": [
                TransactionResponse(
                    id="T1",
                    type="income",
                    amount=4500.00,
                    category="Services",
                    merchant="Client A",
                    date=now,
                    status="completed",
                ).model_dump()
            ],
        }

    domain_income = [
        ["move_type", "=", "out_invoice"],
        ["state", "=", "posted"],
        ["company_id", "=", odoo.company_id],
    ]
    domain_expense = [
        ["move_type", "=", "in_invoice"],
        ["state", "=", "posted"],
        ["company_id", "=", odoo.company_id],
    ]

    income = odoo.get_invoices(domain=domain_income, limit=limit) or []
    expenses = odoo.get_invoices(domain=domain_expense, limit=limit) or []

    moves = income + (expenses if include_expenses else [])

    def sort_key(m: dict) -> str:
        return str(m.get("invoice_date") or m.get("date") or "")

    moves.sort(key=sort_key, reverse=True)
    moves = moves[:limit]

    transactions: List[dict] = []
    for m in moves:
        move_type = m.get("move_type") or ""
        is_income = move_type == "out_invoice"
        payment_state = (m.get("payment_state") or "").lower()

        partner = m.get("partner_id")
        if isinstance(partner, list) and len(partner) >= 2:
            merchant = str(partner[1])
        else:
            merchant = "Unknown"

        invoice_date = m.get("invoice_date") or datetime.utcnow().strftime("%Y-%m-%d")

        status: Literal["completed", "pending", "flagged"]
        if payment_state == "paid":
            status = "completed"
        elif payment_state in {"not_paid", "partial", "in_payment"}:
            status = "pending"
        else:
            status = "pending"

        transactions.append(
            TransactionResponse(
                id=f"odoo-{m.get('id', 'unknown')}",
                type="income" if is_income else "expense",
                amount=float(m.get("amount_total") or 0.0),
                category="Invoice" if is_income else "Bill",
                merchant=merchant,
                date=str(invoice_date),
                status=status,
            ).model_dump()
        )

    return {"source": "odoo", "transactions": transactions}


@finance_router.get("/kpis", response_model=dict)
def get_kpis():
    """
    Return business KPIs derived from Odoo accounting where available.

    Response shape:
      { "kpis": KPIResponse[], "source": "odoo"|"fallback", "generated_at": ISO }
    """
    generated_at = datetime.utcnow().isoformat()

    odoo = get_odoo_service()
    if not odoo or not getattr(odoo, "authenticated", False):
        return {
            "source": "fallback",
            "generated_at": generated_at,
            "kpis": [
                KPIResponse(
                    label="Revenue (Week)",
                    value=_format_currency(0.0),
                    change=0.0,
                    trend="neutral",
                ).model_dump(),
                KPIResponse(
                    label="Revenue (Month)",
                    value=_format_currency(0.0),
                    change=0.0,
                    trend="neutral",
                ).model_dump(),
                KPIResponse(
                    label="Unpaid Invoices",
                    value="0",
                    change=0.0,
                    trend="neutral",
                ).model_dump(),
                KPIResponse(
                    label="Overdue Invoices",
                    value="0",
                    change=0.0,
                    trend="neutral",
                ).model_dump(),
            ],
        }

    today = datetime.utcnow()
    start_of_week = (today - timedelta(days=today.weekday())).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    start_of_prev_week = start_of_week - timedelta(days=7)
    end_of_prev_week = start_of_week

    def revenue_between(start: datetime, end: datetime) -> float:
        domain = [
            ["move_type", "=", "out_invoice"],
            ["state", "=", "posted"],
            ["invoice_date", ">=", start.strftime("%Y-%m-%d")],
            ["invoice_date", "<", end.strftime("%Y-%m-%d")],
            ["company_id", "=", odoo.company_id],
        ]
        invoices = odoo.get_invoices(domain=domain, limit=200) or []
        return float(sum(inv.get("amount_total", 0) for inv in invoices))

    revenue_week = float(odoo.get_revenue_this_week() or 0.0)
    revenue_prev_week = revenue_between(start_of_prev_week, end_of_prev_week)
    change_week = _pct_change(revenue_week, revenue_prev_week)

    revenue_month = float(odoo.get_revenue_this_month() or 0.0)
    unpaid = odoo.get_unpaid_invoices() or []
    overdue = odoo.get_overdue_invoices() or []

    kpis = [
        KPIResponse(
            label="Revenue (Week)",
            value=_format_currency(revenue_week),
            change=change_week,
            trend=_trend(change_week),
        ).model_dump(),
        KPIResponse(
            label="Revenue (Month)",
            value=_format_currency(revenue_month),
            change=0.0,
            trend="neutral",
        ).model_dump(),
        KPIResponse(
            label="Unpaid Invoices",
            value=str(len(unpaid)),
            change=0.0,
            trend="neutral",
        ).model_dump(),
        KPIResponse(
            label="Overdue Invoices",
            value=str(len(overdue)),
            change=0.0,
            trend="neutral",
        ).model_dump(),
    ]

    return {"source": "odoo", "generated_at": generated_at, "kpis": kpis}

