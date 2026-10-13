"""Server-side FamGateway UPI order and verification helpers.
Set FAMGATEWAY_API_KEY in the web service's private environment variables.
No API secret is sent to browser JavaScript or written to logs.
"""
import json
import os
import urllib.parse
import urllib.request

import db

BASE = os.environ.get("FAMGATEWAY_BASE", "https://famgateway.in").rstrip("/")


def _key():
    # Website admin-panel key overrides Render env; never return it to browser.
    try:
        stored = db.get_setting("famgateway_api_key", "").strip()
    except Exception:
        stored = ""
    return stored or os.environ.get("FAMGATEWAY_API_KEY", "").strip()


def enabled():
    try:
        flag = db.get_setting("famgateway_enabled", "").strip().lower()
    except Exception:
        flag = ""
    if flag in ("0", "false", "off", "no"):
        return False
    if flag in ("1", "true", "on", "yes"):
        return True
    return bool(_key())


def configured():
    return bool(enabled() and _key())


def admin_state():
    return {"enabled": enabled(), "key_configured": bool(_key())}


def create_order(amount, user, webhook_url=""):
    key = _key()
    if not key:
        return None, "FamGateway API key website environment me set nahi hai."
    payload = {
        "amount": round(float(amount), 2),
        "customer_name": str(user.get("id", "Customer")),
        "customer_email": user.get("email", ""),
        "customer_phone": user.get("phone", ""),
    }
    if webhook_url:
        payload["webhook_url"] = webhook_url
    req = urllib.request.Request(
        BASE + "/api/create-order",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", "Accept": "application/json",
                 "X-Api-Key": key, "Authorization": "Bearer " + key,
                 "User-Agent": "RAVAN-X-Web/1.0"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            body = json.loads(resp.read().decode("utf-8"))
        data = body.get("data") or {}
        if body.get("status") != "success" or not data.get("order_id"):
            return None, str(body.get("message") or "FamGateway order create fail")[:160]
        return {
            "order_id": str(data["order_id"]),
            "amount": float(data.get("payable_amount") or data.get("amount") or amount),
            "qr_url": str(data.get("qr_url") or ""),
            "checkout_url": str(data.get("checkout_url") or ""),
            "upi_intent": str(data.get("upi_intent") or ""),
            "expires_at_ist": str(data.get("expires_at_ist") or ""),
        }, ""
    except Exception as exc:
        # Do not include request URL or credentials in errors.
        return None, f"FamGateway connect/order error: {type(exc).__name__}"


def verify_order(order_id):
    key = _key()
    if not key:
        return {"status": "error", "message": "Gateway key missing"}
    query = urllib.parse.urlencode({"order_id": order_id})
    req = urllib.request.Request(
        BASE + "/api/verify-order.php?" + query,
        headers={"Accept": "application/json", "X-Api-Key": key,
                 "Authorization": "Bearer " + key,
                 "User-Agent": "RAVAN-X-Web/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            body = json.loads(resp.read().decode("utf-8"))
        return body
    except Exception as exc:
        return {"status": "error", "message": type(exc).__name__}
