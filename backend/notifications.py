from const import NOTIFICATION_MODE


def notify(title, action, content, description):
    match NOTIFICATION_MODE:
        case "discord":
            from const import VN30_DISCORD_URL
            from discord import build_discord, send_discord

            data = build_discord(title, action, content, description)
            resp = send_discord(VN30_DISCORD_URL, data)
            return {
                "status_code": resp.status_code,
                "response": resp.text,
            }

        case "email":
            from const import EMAIL_RECEIVERS
            from send_mail import build_email_data, send_email

            data = build_email_data(action, content, description)
            for email in EMAIL_RECEIVERS.split(","):
                send_email(email, title, data)
            return {
                "status": f"Email sent successfully to {EMAIL_RECEIVERS}",
            }
        
        case "onesignal":
            from onesignal import build_onesignal_notification, send_onesignal_notification
            data = build_onesignal_notification(title, description, action)
            resp = send_onesignal_notification(data)
            return {
                "status_code": resp.status_code,
                "response": resp.text,
            }

        case _:
            raise ValueError(f"Unsupported notification mode: {NOTIFICATION_MODE}")
