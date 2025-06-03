import requests
import json

from const import (
    ACTION_BUY,
    ACTION_SELL,
    DISCORD_NEGATIVE_COLOR,
    DISCORD_NEUTRAL_COLOR,
    DISCORD_POSITIVE_COLOR,
)


def send_discord(url, data):
    return requests.post(
        url,
        data=json.dumps(data),
        headers={
            "Content-Type": "application/json",
        },
    )


def build_discord(title, action, content, description):
    color = (
        DISCORD_POSITIVE_COLOR
        if action == ACTION_BUY
        else DISCORD_NEGATIVE_COLOR if action == ACTION_SELL else DISCORD_NEUTRAL_COLOR
    )

    return {
        "username": "Signal BOT",
        "content": content,
        "embeds": [
            {
                "title": title,
                "description": description,
                "color": color,
            },
        ],
    }
