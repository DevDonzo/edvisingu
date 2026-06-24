"""Tool 6 — Stripe revenue (hermes-finance). Mock by default (Manual 23.6)."""

import os
from datetime import datetime, timedelta

from tools import is_live


def get_mrr() -> dict:
    if is_live("STRIPE_SECRET_KEY"):  # pragma: no cover - needs key
        import stripe

        stripe.api_key = os.environ["STRIPE_SECRET_KEY"]
        subs = stripe.Subscription.list(status="active", limit=100)
        mrr = sum(
            s["items"]["data"][0]["price"]["unit_amount"] * s["items"]["data"][0]["quantity"]
            for s in subs["data"]
        ) / 100
        return {"mrr": mrr, "active_subscriptions": len(subs["data"])}
    return {"mock": True, "mrr": 4230.0, "active_subscriptions": 89}


def get_recent_revenue(days: int = 30) -> dict:
    if is_live("STRIPE_SECRET_KEY"):  # pragma: no cover - needs key
        import stripe

        stripe.api_key = os.environ["STRIPE_SECRET_KEY"]
        since = int((datetime.now() - timedelta(days=days)).timestamp())
        charges = stripe.Charge.list(created={"gte": since}, limit=100)
        total = sum(c["amount"] for c in charges["data"] if c["paid"]) / 100
        return {"total_revenue": total, "transactions": len(charges["data"]), "days": days}
    return {"mock": True, "total_revenue": 6120.0, "transactions": 142, "days": days}
