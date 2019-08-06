import json

import requests

from .config import SLACK_URL


def send_slack_notification(message):
    url = SLACK_URL
    headers = {'Content-Type': 'application/json'}
    data = {"text": message}
    response = requests.post(url, data=json.dumps(
        data), headers=headers, timeout=15)
    # Unsure whether the message was posted!
    return response
