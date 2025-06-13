import requests

from const import ONESIGNAL_API_KEY, ONESIGNAL_API_URL, ONESIGNAL_APP_ID


def send_onesignal_notification(payload):
    return requests.post(
        ONESIGNAL_API_URL,
        json=payload,
        headers={
            "accept": "application/json",
            "Authorization": f"Key {ONESIGNAL_API_KEY}",
            "content-type": "application/json",
        },
    )


def build_onesignal_notification(title, content, action):
    return {
        "app_id": ONESIGNAL_APP_ID,
        "headings": {"en": title},
        "contents": {"en": content},
        "web_buttons": [
            {
                "id": "action",
                "text": action,
            }
        ],
        "included_segments": ["Active Subscriptions"],
    }
