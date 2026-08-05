"""Minimal Razorpay Orders API client using only the standard library.

Avoids adding the `razorpay` package as a hard dependency — order creation and
payment-signature verification are simple enough to do directly.
"""
import base64
import hashlib
import hmac
import json
import urllib.error
import urllib.request

RAZORPAY_ORDERS_URL = 'https://api.razorpay.com/v1/orders'


class RazorpayError(Exception):
    pass


def create_order(key_id, key_secret, amount_rupees, receipt):
    """Creates a Razorpay order. Amount is in rupees; Razorpay expects paise."""
    payload = json.dumps({
        'amount': int(round(float(amount_rupees) * 100)),
        'currency': 'INR',
        'receipt': receipt,
    }).encode('utf-8')

    auth = base64.b64encode(f'{key_id}:{key_secret}'.encode('utf-8')).decode('ascii')
    request = urllib.request.Request(
        RAZORPAY_ORDERS_URL,
        data=payload,
        method='POST',
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Basic {auth}',
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            return json.loads(response.read().decode('utf-8'))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode('utf-8', errors='ignore')
        raise RazorpayError(f'Razorpay order creation failed: {detail}') from exc
    except urllib.error.URLError as exc:
        raise RazorpayError(f'Could not reach Razorpay: {exc}') from exc


def verify_payment_signature(key_secret, razorpay_order_id, razorpay_payment_id, razorpay_signature):
    message = f'{razorpay_order_id}|{razorpay_payment_id}'.encode('utf-8')
    expected = hmac.new(key_secret.encode('utf-8'), message, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, razorpay_signature or '')
