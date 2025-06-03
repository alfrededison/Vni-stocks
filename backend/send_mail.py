import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from const import (
    ACTION_BUY,
    ACTION_SELL,
    EMAIL_NEGATIVE_COLOR,
    EMAIL_NEUTRAL_COLOR,
    EMAIL_POSITIVE_COLOR,
    EMAIL_PASSWORD,
    EMAIL_SENDER,
)


def send_email(email, title, body):
    msg = MIMEMultipart("alternative")
    msg["Subject"] = title
    msg["From"] = "vn30f1m@vnistocks.com"
    msg["To"] = email

    msg.attach(MIMEText(body, "html"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.send_message(msg)


def build_email_data(action, content, description):
    color = (
        EMAIL_POSITIVE_COLOR
        if action == ACTION_BUY
        else EMAIL_NEGATIVE_COLOR if action == ACTION_SELL else EMAIL_NEUTRAL_COLOR
    )

    return f"""
    <html>
        <body style="font-family: Arial, sans-serif">
            <h1 style="color:{color}">{content}</h1>
            <p>{description}</p>
        </body>
    </html>
    """
