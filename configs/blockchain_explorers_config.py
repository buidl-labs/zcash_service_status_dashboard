import os
from datetime import datetime

from prometheus_client import (Enum, Gauge, Histogram, Summary,
                               start_http_server)

ZCHA_NETWORK_URL = "https://api.zcha.in/v2/mainnet/network"
ZCHA_BLOCK_URL = "https://api.zcha.in/v2/mainnet/blocks/"
ZCHA_BLOCK_HEIGHT_PORT = Enum(
    'zcha_block_height_check', 'ZCHA Block Height Check', states=['1', '0'])
ZCHA_LAST_BLOCK_CHECK_PORT = Enum(
    'zcha_last_block_check', 'ZCHA LAST BLOCK CHECK', states=['1', '0'])
