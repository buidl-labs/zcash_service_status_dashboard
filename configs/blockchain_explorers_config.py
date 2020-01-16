import os
from datetime import datetime

from prometheus_client import (Enum, Gauge, Histogram, Summary, start_http_server)

ZCHA_BLOCK_URL = "https://api.zcha.in/v2/mainnet/blocks/"
ZCHA_BLOCK_HEIGHT_PORT = Enum(
    'zcha_block_height_check', 'ZCHA Block Height Check', states=['1', '0'])
ZCHA_LAST_BLOCK_CHECK_PORT = Enum(
    'zcha_last_block_check', 'ZCHA LAST BLOCK CHECK', states=['1', '0'])

ZCASHNETWORKINFO_BLOCK_URL = "https://zcashnetwork.info/api/block/"
ZCASHNETWORKINFO_BLOCK_HEIGHT_PORT = Enum(
    'zcashnetworkinfo_block_height_check', 'ZCASHNETWORKINFO Block Height Check', states=['1', '0'])
ZCASHNETWORKINFO_LAST_BLOCK_CHECK_PORT = Enum(
    'zcashnetworkinfo_last_block_check', 'ZCASHNETWORKINFO LAST BLOCK CHECK', states=['1', '0'])

CHAINSO_BLOCK_URL = "https://chain.so/api/v2/block/ZEC/"
CHAINSO_BLOCK_HEIGHT_PORT = Enum(
    'chainso_block_height_check', 'CHAINSO Block Height Check', states=['1', '0'])
CHAINSO_LAST_BLOCK_CHECK_PORT = Enum(
    'chainso_last_block_check', 'CHAINSO LAST BLOCK CHECK', states=['1', '0'])

ZECMATE_BLOCK_URL = "https://explorer.zecmate.com/api/block/"
ZECMATE_BLOCK_HEIGHT_PORT = Enum(
    'zecmate_block_height_check', 'ZECMATE Block Height Check', states=['1', '0'])
ZECMATE_LAST_BLOCK_CHECK_PORT = Enum(
    'zecmate_last_block_check', 'ZECMATE LAST BLOCK CHECK', states=['1', '0'])

ZCASHFR_BLOCK_URL = "https://explorer.zcashfr.io/api/block/"
ZCASHFR_BLOCK_HEIGHT_PORT = Enum(
    'zcashfr_block_height_check', 'ZCASHFR Block Height Check', states=['1', '0'])
ZCASHFR_LAST_BLOCK_CHECK_PORT = Enum(
    'zcashfr_last_block_check', 'ZCASHFR LAST BLOCK CHECK', states=['1', '0'])

NETDNA_BLOCK_URL = "https://live-sochain-blockioinc.netdna-ssl.com/api/v2/block/ZEC/"
NETDNA_BLOCK_HEIGHT_PORT = Enum(
    'netdna_block_height_check', 'NETDNA Block Height Check', states=['1', '0'])
NETDNA_LAST_BLOCK_CHECK_PORT = Enum(
    'netdna_last_block_check', 'NETDNA LAST BLOCK CHECK', states=['1', '0'])
