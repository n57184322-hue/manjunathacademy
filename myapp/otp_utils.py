import json
import random
import urllib.request

from django.core.mail import get_connection, send_mail
from django.utils import timezone
from datetime import timedelta

OTP_VALIDITY_MINUTES = 10


def generate_otp_code():
    return f"{random.randint(0, 999999):06d}"


def create_otp(target, channel):
    from .models import OTPRequest

    code = generate_otp_code()
    return OTPRequest.objects.create(
        target=target,
        channel=channel,
        code=code,
        expires_at=timezone.now() + timedelta(minutes=OTP_VALIDITY_MINUTES),
    )


def send_email_otp(settings_obj, to_email, code):
    message = f'Your Manjunath Academy verification code is {code}. It expires in {OTP_VALIDITY_MINUTES} minutes.'
    if settings_obj and settings_obj.smtp_configured:
        try:
            connection = get_connection(
                backend='django.core.mail.backends.smtp.EmailBackend',
                host=settings_obj.smtp_host,
                port=settings_obj.smtp_port or 587,
                username=settings_obj.smtp_username,
                password=settings_obj.smtp_password,
                use_tls=settings_obj.smtp_use_tls,
            )
            from_email = settings_obj.smtp_from_email or settings_obj.smtp_username
            send_mail('Your verification code', message, from_email, [to_email], connection=connection)
            return True, f'Sent via configured SMTP ({settings_obj.smtp_host}).'
        except Exception as exc:
            return False, f'SMTP send failed: {exc}'
    try:
        send_mail('Your verification code', message, None, [to_email])
        return True, 'Sent via the site\'s default email backend.'
    except Exception as exc:
        return False, f'Default email send failed: {exc}'


def send_sms_otp(settings_obj, to_phone, code):
    message = f'Your Manjunath Academy verification code is {code}. It expires in {OTP_VALIDITY_MINUTES} minutes.'
    if not (settings_obj and settings_obj.sms_configured):
        return False, 'No SMS provider is configured yet. Add one under Customization → SMS & Email, or send the OTP by email instead.'
    try:
        payload = json.dumps({
            'api_key': settings_obj.sms_api_key,
            'sender': settings_obj.sms_sender_id,
            'to': to_phone,
            'message': message,
        }).encode('utf-8')
        req = urllib.request.Request(
            settings_obj.sms_api_url,
            data=payload,
            headers={'Content-Type': 'application/json'},
            method='POST',
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            status = resp.getcode()
        return True, f'Sent via {settings_obj.sms_provider_name or "the configured SMS provider"} (HTTP {status}).'
    except Exception as exc:
        return False, f'SMS provider error: {exc}'


def send_otp(settings_obj, target, channel):
    otp = create_otp(target, channel)
    if channel == 'sms':
        ok, detail = send_sms_otp(settings_obj, target, otp.code)
    else:
        ok, detail = send_email_otp(settings_obj, target, otp.code)
    return ok, detail, otp


def verify_otp(target, channel, code):
    from .models import OTPRequest

    otp = OTPRequest.objects.filter(target=target, channel=channel, code=code).order_by('-created_at').first()
    if not otp or not otp.is_valid_now():
        return False
    otp.is_verified = True
    otp.save(update_fields=['is_verified'])
    return True
