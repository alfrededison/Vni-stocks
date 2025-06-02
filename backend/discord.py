import requests
import json


def send_discord(url, data):
    return requests.post(
        url,
        data=json.dumps(data),
        headers={
            "Content-Type": "application/json",
        },
    )
