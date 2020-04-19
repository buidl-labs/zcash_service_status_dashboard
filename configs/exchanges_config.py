import os
from datetime import datetime

from prometheus_client import (Enum, Gauge, Histogram, Summary,
                               start_http_server)

# Exmo Configs
EXMO_URL = "https://api.exmo.com/v1/ticker/"
EXMO_SPOT_PRICE_USD_PORT = Enum('exmo_spot_price_usd_check',
                                'Exmo Spot Price USD Check', states=['1', '0'])
EXMO_SPOT_PRICE_BTC_PORT = Enum('exmo_spot_price_btc_check',
                                'Exmo Spot Price BTC Check', states=['1', '0'])
EXMO_TRANSACTION_VOLUME_USD_PORT = Enum(
    'exmo_transaction_volume_usd_check', 'Exmo Transaction Volume USD Check', states=['1', '0'])
EXMO_TRANSACTION_VOLUME_BTC_PORT = Enum(
    'exmo_transaction_volume_btc_check', 'Exmo Transaction Volume BTC Check', states=['1', '0'])
EXMO_SPOT_PRICE_MEDIAN_DEVIATION_PORT = Histogram(
    'exmo_spot_price_deviation_check', 'Exmo Spot Price Deviation Check')
EXMO_SUMMARY = Summary('request_latency_seconds', 'Description of summary')
EXMO_USD_SPOT_PRICE_DEVIATION_GAUGE = Gauge('exmo_usd_spot_price_deviation_gauge',
                                            'exmo_usd_spot_price_deviation_gauge gauge')
EXMO_BTC_SPOT_PRICE_DEVIATION_GAUGE = Gauge('exmo_btc_spot_price_deviation_gauge',
                                            'exmo_btc_spot_price_deviation_gauge gauge')
EXMO_USD_SPOT_PRICE_ABSOLUTE = Gauge(
    'exmo_usd_spot_price_absolute', 'exmo_usd_spot_price_absolute_gauge')
EXMO_BTC_SPOT_PRICE_ABSOLUTE = Gauge(
    'exmo_btc_spot_price_absolute', 'exmo_btc_spot_price_absolute_gauge')
EXMO_USD_TRANSACTION_VOLUME_ABSOLUTE = Gauge(
    'exmo_usd_transaction_volume_absolute', 'exmo_usd_transaction_volume_absolute_gauge')
EXMO_BTC_TRANSACTION_VOLUME_ABSOLUTE = Gauge(
    'exmo_btc_transaction_volume_absolute', 'exmo_btc_transaction_volume_absolute_gauge')

# Bittrex Configs
BITTREX_ZEC_USD_SPOT_PRICE_URL = "https://api.bittrex.com/api/v1.1/public/getticker?market=USD-ZEC"
BITTREX_ZEC_BTC_SPOT_PRICE_URL = "https://api.bittrex.com/api/v1.1/public/getticker?market=BTC-ZEC"
BITTREX_TRANSACTION_VOLUME_URL = "https://api.bittrex.com/v3/markets/summaries"
BITTREX_SPOT_PRICE_BTC_PORT = Enum('bittrex_spot_price_btc_check',
                                   'Bittrex Spot Price BTC Check', states=['1', '0'])
BITTREX_SPOT_PRICE_USD_PORT = Enum('bittrex_spot_price_usd_check',
                                   'Bittrex Spot Price USD Check', states=['1', '0'])
BITTREX_TRANSACTION_VOLUME_USD_PORT = Enum(
    'bittrex_transaction_volume_usd_check', 'Bittrex Transaction Volume USD Check', states=['1', '0'])
BITTREX_TRANSACTION_VOLUME_BTC_PORT = Enum(
    'bittrex_transaction_volume_btc_check', 'Bittrex Transaction Volume BTC Check', states=['1', '0'])
BITTREX_SPOT_PRICE_MEDIAN_DEVIATION_PORT = Histogram(
    'bittrex_spot_price_deviation_check', 'Bittrex Spot Price Deviation Check')
BITTREX_USD_SPOT_PRICE_DEVIATION_GAUGE = Gauge('bittrex_usd_spot_price_deviation_gauge',
                                               'bittrex_usd_spot_price_deviation_gauge gauge')
BITTREX_BTC_SPOT_PRICE_DEVIATION_GAUGE = Gauge('bittrex_btc_spot_price_deviation_gauge',
                                               'bittrex_btc_spot_price_deviation_gauge gauge')
BITTREX_USD_SPOT_PRICE_ABSOLUTE = Gauge(
    'bittrex_usd_spot_price_absolute', 'bittrex_usd_spot_price_absolute_gauge')
BITTREX_BTC_SPOT_PRICE_ABSOLUTE = Gauge(
    'bittrex_btc_spot_price_absolute', 'bittrex_btc_spot_price_absolute_gauge')
BITTREX_USD_TRANSACTION_VOLUME_ABSOLUTE = Gauge(
    'bittrex_usd_transaction_volume_absolute', 'bittrex_usd_transaction_volume_absolute_gauge')
BITTREX_BTC_TRANSACTION_VOLUME_ABSOLUTE = Gauge(
    'bittrex_btc_transaction_volume_absolute', 'bittrex_btc_transaction_volume_absolute_gauge')

# Gemini Configs
GEMINI_ZEC_BTC_URL = "https://api.gemini.com/v1/pubticker/zecbtc"
GEMINI_ZEC_USD_URL = "https://api.gemini.com/v1/pubticker/zecusd"
GEMINI_SPOT_PRICE_BTC_PORT = Enum('gemini_spot_price_btc_check',
                                  'Gemini Spot Price BTC Check', states=['1', '0'])
GEMINI_SPOT_PRICE_USD_PORT = Enum('gemini_spot_price_usd_check',
                                  'Gemini Spot Price USD Check', states=['1', '0'])
GEMINI_TRANSACTION_VOLUME_BTC_PORT = Enum(
    'gemini_transaction_volume_btc_check', 'Gemini Transaction Volume BTC Check', states=['1', '0'])
GEMINI_TRANSACTION_VOLUME_USD_PORT = Enum(
    'gemini_transaction_volume_usd_check', 'Gemini Transaction Volume USD Check', states=['1', '0'])
GEMINI_SPOT_PRICE_MEDIAN_DEVIATION_PORT = Histogram(
    'gemini_spot_price_deviation_check', 'Gemini Spot Price Deviation Check')
GEMINI_USD_SPOT_PRICE_DEVIATION_GAUGE = Gauge('gemini_usd_spot_price_deviation_gauge',
                                              'gemini_usd_spot_price_deviation_gauge gauge')
GEMINI_BTC_SPOT_PRICE_DEVIATION_GAUGE = Gauge('gemini_btc_spot_price_deviation_gauge',
                                              'gemini_btc_spot_price_deviation_gauge gauge')
GEMINI_USD_SPOT_PRICE_ABSOLUTE = Gauge(
    'gemini_usd_spot_price_absolute', 'gemini_usd_spot_price_absolute_gauge')
GEMINI_BTC_SPOT_PRICE_ABSOLUTE = Gauge(
    'gemini_btc_spot_price_absolute', 'gemini_btc_spot_price_absolute_gauge')
GEMINI_USD_TRANSACTION_VOLUME_ABSOLUTE = Gauge(
    'gemini_usd_transaction_volume_absolute', 'gemini_usd_transaction_volume_absolute_gauge')
GEMINI_BTC_TRANSACTION_VOLUME_ABSOLUTE = Gauge(
    'gemini_btc_transaction_volume_absolute', 'gemini_btc_transaction_volume_absolute_gauge')

# Bitfinex Configs
BITFINEX_ZEC_USD_URL = "https://api-pub.bitfinex.com/v2/tickers?symbols=tZECUSD"
BITFINEX_ZEC_BTC_URL = "https://api-pub.bitfinex.com/v2/tickers?symbols=tZECBTC"
BITFINEX_SPOT_PRICE_BTC_PORT = Enum('bitfinex_spot_price_btc_check',
                                    'Bitfinex Spot Price BTC Check', states=['1', '0'])
BITFINEX_SPOT_PRICE_USD_PORT = Enum('bitfinex_spot_price_usd_check',
                                    'Bitfinex Spot Price USD Check', states=['1', '0'])
BITFINEX_TRANSACTION_VOLUME_BTC_PORT = Enum(
    'bitfinex_transaction_volume_btc_check', 'Bitfinex Transaction Volume BTC Check', states=['1', '0'])
BITFINEX_TRANSACTION_VOLUME_USD_PORT = Enum(
    'bitfinex_transaction_volume_usd_check', 'Bitfinex Transaction Volume USD Check', states=['1', '0'])
BITFINEX_SPOT_PRICE_MEDIAN_DEVIATION_PORT = Histogram(
    'bitfinex_spot_price_deviation_check', 'Bitfinex Spot Price Deviation Check')
BITFINEX_USD_SPOT_PRICE_DEVIATION_GAUGE = Gauge('bitfinex_usd_spot_price_deviation_gauge',
                                                'bitfinex_usd_spot_price_deviation_gauge gauge')
BITFINEX_BTC_SPOT_PRICE_DEVIATION_GAUGE = Gauge('bitfinex_btc_spot_price_deviation_gauge',
                                                'bitfinex_btc_spot_price_deviation_gauge gauge')
BITFINEX_USD_SPOT_PRICE_ABSOLUTE = Gauge(
    'bitfinex_usd_spot_price_absolute', 'bitfinex_usd_spot_price_absolute_gauge')
BITFINEX_BTC_SPOT_PRICE_ABSOLUTE = Gauge(
    'bitfinex_btc_spot_price_absolute', 'bitfinex_btc_spot_price_absolute_gauge')
BITFINEX_USD_TRANSACTION_VOLUME_ABSOLUTE = Gauge(
    'bitfinex_usd_transaction_volume_absolute', 'bitfinex_usd_transaction_volume_absolute_gauge')
BITFINEX_BTC_TRANSACTION_VOLUME_ABSOLUTE = Gauge(
    'bitfinex_btc_transaction_volume_absolute', 'bitfinex_btc_transaction_volume_absolute_gauge')

# Binance Configs
# TODO: Figure out ZEC<->USD as Binance does not provide any pair that includes USD
BINANCE_ZEC_BTC_URL = "https://api.binance.com/api/v1/ticker/24hr?symbol=ZECBTC"
BINANCE_SPOT_PRICE_BTC_PORT = Enum('binance_spot_price_btc_check',
                                   'Binance Spot Price BTC Check', states=['1', '0'])
BINANCE_TRANSACTION_VOLUME_BTC_PORT = Enum(
    'binance_transaction_volume_btc_check', 'Binance Transaction Volume BTC Check', states=['1', '0'])
BINANCE_SPOT_PRICE_MEDIAN_DEVIATION_PORT = Histogram(
    'binance_spot_price_deviation_check', 'Binance Spot Price Deviation Check')
BINANCE_BTC_SPOT_PRICE_DEVIATION_GAUGE = Gauge('binance_btc_spot_price_deviation_gauge',
                                               'binance_btc_spot_price_deviation_gauge gauge')
BINANCE_BTC_SPOT_PRICE_ABSOLUTE = Gauge(
    'binance_btc_spot_price_absolute', 'binance_btc_spot_price_absolute_gauge')
BINANCE_BTC_TRANSACTION_VOLUME_ABSOLUTE = Gauge(
    'binance_btc_transaction_volume_absolute', 'binance_btc_transaction_volume_absolute_gauge')

# Coinbase Configs
# TODO: Figure out ZEC<->BTC as Coinbase does not provide this pair.
COINBASE_ZEC_USD_URI = "https://api.coinbase.com/v2/prices/ZEC-USD/spot"
COINBASE_SPOT_PRICE_USD_PORT = Enum('coinbase_spot_price_usd_check',
                                    'Coinbase Spot Price USD Check', states=['1', '0'])
COINBASE_USD_SPOT_PRICE_DEVIATION_GAUGE = Gauge('coinbase_usd_spot_price_deviation_gauge',
                                                'coinbase_usd_spot_price_deviation_gauge gauge')
COINBASE_USD_SPOT_PRICE_ABSOLUTE = Gauge(
    'coinbase_usd_spot_price_absolute', 'coinbase_usd_spot_price_absolute_gauge')

# Kraken Configs
KRAKEN_ZEC_USD_URL = "https://api.kraken.com/0/public/Ticker?pair=ZECUSD"
KRAKEN_SPOT_PRICE_USD_PORT = Enum('kraken_spot_price_usd_check',
                                  'Kraken Spot Price USD Check', states=['1', '0'])
KRAKEN_TRANSACTION_VOLUME_USD_PORT = Enum(
    'kraken_transaction_volume_usd_check', 'Kraken Transaction Volume USD Check', states=['1', '0'])
KRAKEN_USD_SPOT_PRICE_DEVIATION_GAUGE = Gauge('kraken_usd_spot_price_deviation_gauge',
                                              'kraken_usd_spot_price_deviation_gauge gauge')                                # Gauge Configs for Spot Price Deviation
KRAKEN_USD_SPOT_PRICE_ABSOLUTE = Gauge(
    'kraken_usd_spot_price_absolute', 'kraken_usd_spot_price_absolute_gauge')
KRAKEN_USD_TRANSACTION_VOLUME_ABSOLUTE = Gauge(
    'kraken_usd_transaction_volume_absolute', 'kraken_usd_transaction_volume_absolute_gauge')

# Coinjar Configs
COINJAR_ZEC_BTC_URL = "https://data.exchange.coinjar.com/products/ZECBTC/ticker"
COINJAR_SPOT_PRICE_BTC_PORT = Enum('coinjar_spot_price_btc_check',
                                   'Coinjar Spot Price BTC Check', states=['1', '0'])
COINJAR_TRANSACTION_VOLUME_BTC_PORT = Enum(
    'coinjar_transaction_volume_btc_check', 'Coinjar Transaction Volume BTC Check', states=['1', '0'])
COINJAR_BTC_SPOT_PRICE_DEVIATION_GAUGE = Gauge('coinjar_btc_spot_price_deviation_gauge',
                                               'coinjar_btc_spot_price_deviation_gauge gauge')
COINJAR_BTC_SPOT_PRICE_ABSOLUTE = Gauge(
    'coinjar_btc_spot_price_absolute', 'coinjar_btc_spot_price_absolute_gauge')
COINJAR_BTC_TRANSACTION_VOLUME_ABSOLUTE = Gauge(
    'coinjar_btc_transaction_volume_absolute', 'coinjar_btc_transaction_volume_absolute_gauge')

# Universal configs

USD_EXCHANGE = {
    "Exmo": EXMO_USD_SPOT_PRICE_DEVIATION_GAUGE,
    "Bittrex": BITTREX_USD_SPOT_PRICE_DEVIATION_GAUGE,
    "Gemini": GEMINI_USD_SPOT_PRICE_DEVIATION_GAUGE,
    "Bitfinex": BITFINEX_USD_SPOT_PRICE_DEVIATION_GAUGE,
    "Coinbase": COINBASE_USD_SPOT_PRICE_DEVIATION_GAUGE,
    "Kraken": KRAKEN_USD_SPOT_PRICE_DEVIATION_GAUGE
}

BTC_EXCHANGE = {
    "Exmo": EXMO_BTC_SPOT_PRICE_DEVIATION_GAUGE,
    "Bittrex": BITTREX_BTC_SPOT_PRICE_DEVIATION_GAUGE,
    "Gemini": GEMINI_BTC_SPOT_PRICE_DEVIATION_GAUGE,
    "Bitfinex": BITFINEX_BTC_SPOT_PRICE_DEVIATION_GAUGE,
    "Binance": BINANCE_BTC_SPOT_PRICE_DEVIATION_GAUGE,
    "Coinjar": COINJAR_BTC_SPOT_PRICE_DEVIATION_GAUGE
}

ABSOLUTE_PRICE_USD_EXCHANGE = {
    "Exmo": EXMO_USD_SPOT_PRICE_ABSOLUTE,
    "Bittrex": BITTREX_USD_SPOT_PRICE_ABSOLUTE,
    "Gemini": GEMINI_USD_SPOT_PRICE_ABSOLUTE,
    "Bitfinex": BITFINEX_USD_SPOT_PRICE_ABSOLUTE,
    "Coinbase": COINBASE_USD_SPOT_PRICE_ABSOLUTE,
    "Kraken": KRAKEN_USD_SPOT_PRICE_ABSOLUTE
}

ABSOLUTE_PRICE_BTC_EXCHANGE = {
    "Exmo": EXMO_BTC_SPOT_PRICE_ABSOLUTE,
    "Bittrex": BITTREX_BTC_SPOT_PRICE_ABSOLUTE,
    "Gemini": GEMINI_BTC_SPOT_PRICE_ABSOLUTE,
    "Bitfinex": BITFINEX_BTC_SPOT_PRICE_ABSOLUTE,
    "Binance": BINANCE_BTC_SPOT_PRICE_ABSOLUTE,
    "Coinjar": COINJAR_BTC_SPOT_PRICE_ABSOLUTE
}

ABSOLUTE_TRANSACTION_VOLUME_USD_EXCHANGE = {
    "Exmo": EXMO_USD_TRANSACTION_VOLUME_ABSOLUTE,
    "Bittrex": BITTREX_USD_TRANSACTION_VOLUME_ABSOLUTE,
    "Gemini": GEMINI_USD_TRANSACTION_VOLUME_ABSOLUTE,
    "Bitfinex": BITFINEX_USD_TRANSACTION_VOLUME_ABSOLUTE,
    "Kraken": KRAKEN_USD_TRANSACTION_VOLUME_ABSOLUTE
}

ABSOLUTE_TRANSACTION_VOLUME_BTC_EXCHANGE = {
    "Exmo": EXMO_BTC_TRANSACTION_VOLUME_ABSOLUTE,
    "Bittrex": BITTREX_BTC_TRANSACTION_VOLUME_ABSOLUTE,
    "Gemini": GEMINI_BTC_TRANSACTION_VOLUME_ABSOLUTE,
    "Bitfinex": BITFINEX_BTC_TRANSACTION_VOLUME_ABSOLUTE,
    "Binance": BINANCE_BTC_TRANSACTION_VOLUME_ABSOLUTE,
    "Coinjar": COINJAR_BTC_TRANSACTION_VOLUME_ABSOLUTE
}

MEDIAN_SPOT_PRICE_USD = Gauge(
    'median_spot_price_usd', 'median_spot_price_usd_gauge')
MEDIAN_SPOT_PRICE_BTC = Gauge(
    'median_spot_price_btc', 'median_spot_price_btc_gauge')
