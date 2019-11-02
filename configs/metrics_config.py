import os
from datetime import datetime

from prometheus_client import (Enum, Gauge, Histogram, Summary,
                               start_http_server)

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
BLOCK_HEIGHT_GAUGE = Gauge('block_height_gauge', 
                           'block_height_gauge gauge')
