import smtplib
from email.message import EmailMessage

from src.core.config import settings


def send_otp_email(
    to_email: str,
    otp: str,
    purpose: str,
) -> None:
    if purpose == "email_verification":
        subject = "Verify your email"
        body = (
            f"Your verification code is: {otp}\n\n"
            f"This code will expire in "
            f"{settings.email_otp_expire_minutes} minutes."
        )

    elif purpose == "password_reset":
        subject = "Reset your password"
        body = (
            f"Your password reset code is: {otp}\n\n"
            f"This code will expire in "
            f"{settings.email_otp_expire_minutes} minutes."
        )

    else:
        raise ValueError("Unsupported OTP purpose")

    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = settings.smtp_from
    message["To"] = to_email
    message.set_content(body)

    with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
        server.starttls()
        server.login(
            settings.smtp_username,
            settings.smtp_password,
        )
        server.send_message(message)