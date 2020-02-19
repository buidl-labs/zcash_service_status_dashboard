import json

import requests

from .static_url import SLACK_URL


def send_slack_notification(message):
    url = SLACK_URL
    headers = {'Content-Type': 'application/json'}
    data = {"text": message}
    try:
        response = requests.post(url, data=json.dumps(
        data), headers=headers, timeout=20)
        # Unsure whether the message was posted!
        return response
    except:
        print("Error in posting to slack")

def send_slack_notification_urgent(message):
    url = SLACK_URL_URGENT
    headers = {'Content-Type': 'application/json'}
    data = {"text": message}
    try:
        response = requests.post(url, data=json.dumps(
        data), headers=headers, timeout=20)
        # Unsure whether the message was posted!
        return response
    except:
        print("Error in posting to slack")