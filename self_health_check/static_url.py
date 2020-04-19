import os

SLACK_URL = os.getenv('SLACK_URL', '')
SLACK_URL_URGENT = os.getenv('SLACK_URL_URGENT', '')
BLACKBOX_EXPORTER_URL = 'http://localhost:9115'
