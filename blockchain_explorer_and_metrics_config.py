import os
from datetime import datetime

from prometheus_client import (Enum, Gauge, Histogram, Summary,
                               start_http_server)

#ZCHA EXPLORER Configs
ZCHA_NETWORK_URL = "https://api.zcha.in/v2/mainnet/network"
ZCHA_BLOCK_URL = "https://api.zcha.in/v2/mainnet/blocks/"
ZCHA_BLOCK_HEIGHT_PORT = Enum(
    'zcha_block_height_check', 'ZCHA Block Height Check', states=['1', '0'])
ZCHA_LAST_BLOCK_CHECK_PORT = Enum(
    'zcha_last_block_check', 'ZCHA LAST BLOCK CHECK', states=['1', '0'])

#METRICS
SPROUT_VALUE_POOL_GAUGE = Gauge('sprout_value_pool_gauge',
                                'sprout_value_pool_gauge gauge')
SAPLING_VALUE_POOL_GAUGE = Gauge('sapling_value_pool_gauge',
                                 'sapling_value_pool_gauge gauge')
ZCASH_DIFFICULTY_GAUGE = Gauge('zcash_difficulty_gauge',
                               'zcash_difficulty_gauge gauge')
TRANSPARENT_TRANSACTIONS_IN_BLOCK_GAUGE = Gauge('transparent_transactions_in_block_gauge',
                                                'transparent_transactions_in_block_gauge gauge')
SHIELDED_TRANSACTIONS_IN_BLOCK_GAUGE = Gauge('shielded_transactions_in_block_gauge',
                                             'shielded_transactions_in_block_gauge gauge')
