import json
import time
from statistics import median
import requests
from prometheus_client import (Enum, Gauge, Histogram, Summary, start_http_server)
from configs.exchanges_config import *
from self_health_check.utils import send_slack_notification
start_http_server(8093)


def notify_driver_health_check_issue(exception):
    try:
        send_slack_notification(message="Some issue in driver_health_check!")
        send_slack_notification(message=str(exception))
    except Exception:
        pass


def notify_exchange_error(exchange, exception):
    try:
        send_slack_notification(message="Something wrong or mismatching in {}'s response -> {}".format(exchange, exception))
    except Exception:
        pass


slack_notification_counter = 0
while True:
    # get the response for all exchanges asap, all at once to avoid time difference
    exmo_response = bittrex_spot_price_zec_usd_response = \
        bittrex_spot_price_zec_btc_response = bittrex_transaction_volume_response = gemini_zec_usd_response = \
        gemini_zec_btc_response = bitfinex_zec_usd_response = bitfinex_zec_btc_response = \
        binance_zec_btc_response = coinbase_zec_usd_response = \
        kraken_zec_usd_response = coinjar_zec_btc_response = None
    try:
        exmo_response = requests.get(url=EXMO_URL, timeout=5)
    except Exception as e:
        notify_driver_health_check_issue(e)
        pass
    
    try:
        bittrex_spot_price_zec_usd_response = requests.get(
            url=BITTREX_ZEC_USD_SPOT_PRICE_URL, timeout=5)
    except Exception as e:
        notify_driver_health_check_issue(e)
        pass
    try:
        bittrex_spot_price_zec_btc_response = requests.get(
            url=BITTREX_ZEC_BTC_SPOT_PRICE_URL, timeout=5)
    except Exception as e:
        notify_driver_health_check_issue(e)
        pass
    try:
        bittrex_transaction_volume_response = requests.get(
            url=BITTREX_TRANSACTION_VOLUME_URL, timeout=5)
    except Exception as e:
        notify_driver_health_check_issue(e)
        pass
    try:
        gemini_zec_usd_response = requests.get(
            url=GEMINI_ZEC_USD_URL, timeout=5)
    except Exception as e:
        notify_driver_health_check_issue(e)
        pass
    try:
        gemini_zec_btc_response = requests.get(
            url=GEMINI_ZEC_BTC_URL, timeout=5)
    except Exception as e:
        notify_driver_health_check_issue(e)
        pass
    try:
        bitfinex_zec_usd_response = requests.get(
            url=BITFINEX_ZEC_USD_URL, timeout=5)
    except Exception as e:
        notify_driver_health_check_issue(e)
        pass
    try:
        bitfinex_zec_btc_response = requests.get(
            url=BITFINEX_ZEC_BTC_URL, timeout=5)
    except Exception as e:
        notify_driver_health_check_issue(e)
        pass
    try:
        binance_zec_btc_response = requests.get(
            url=BINANCE_ZEC_BTC_URL, timeout=5)
    except Exception as e:
        notify_driver_health_check_issue(e)
        pass
    try:
        coinbase_zec_usd_response = requests.get(url=COINBASE_ZEC_USD_URI, timeout=5, headers={
            'AUTHORIZATION': 'Bearer abd90df5f27a7b170cd775abf89d632b350b7c1c9d53e08b340cd9832ce52c2c'})
    except Exception as e:
        notify_driver_health_check_issue(e)
        pass
    try:
        kraken_zec_usd_response = requests.get(
            url=KRAKEN_ZEC_USD_URL, timeout=5)
    except Exception as e:
        notify_driver_health_check_issue(e)
        pass
    try:
        coinjar_zec_btc_response = requests.get(
            url=COINJAR_ZEC_BTC_URL, timeout=5)
    except Exception as e:
        notify_driver_health_check_issue(e)
        pass

    # Exmo
    try:
        exmo_data = exmo_response.json()
        # setting transaction volume in USD
        exmo_usd_transaction_volume = exmo_data['ZEC_USD']['vol_curr']
        # setting zec_usd spot price
        exmo_usd_spot_price = float(exmo_data['ZEC_USD']['last_trade'])
        # setting transaction volume in BTC
        exmo_btc_transaction_volume = exmo_data['ZEC_BTC']['vol_curr']
        # setting zec_btc spot price
        exmo_btc_spot_price = float(exmo_data['ZEC_BTC']['last_trade'])
        # plotting usd and btc transaction volume and spot price
        if exmo_usd_transaction_volume == 0:
            set_state = '0'
        else:
            set_state = '1'
        EXMO_TRANSACTION_VOLUME_USD_PORT.state(set_state)
        if exmo_btc_transaction_volume == 0:
            set_state = '0'
        else:
            set_state = '1'
        EXMO_TRANSACTION_VOLUME_BTC_PORT.state(set_state)
        if exmo_usd_spot_price == 0:
            set_state = '0'
        else:
            set_state = '1'
        EXMO_SPOT_PRICE_USD_PORT.state(set_state)
        if exmo_btc_spot_price == 0:
            set_state = '0'
        else:
            set_state = '1'
        EXMO_SPOT_PRICE_BTC_PORT.state(set_state)
    except Exception as e:
        if exmo_response is None:
            send_slack_notification(message="Exmo response is None!")
        else:
            notify_exchange_error("Exmo", str(e))

    # Bittrex
    try:
        bittrex_spot_price_zec_btc_data = bittrex_spot_price_zec_btc_response.json()
        bittrex_btc_spot_price = float(
            bittrex_spot_price_zec_btc_data['result']['Last'])
        bittrex_spot_price_zec_usd_data = bittrex_spot_price_zec_usd_response.json()
        bittrex_usd_spot_price = float(
            bittrex_spot_price_zec_usd_data['result']['Last'])
        bittrex_transaction_volume_data = bittrex_transaction_volume_response.json()
        for obj in bittrex_transaction_volume_data:
            if obj["symbol"] == "ZEC-USD":
                bittrex_usd_transaction_volume = obj['volume']
                if bittrex_usd_transaction_volume == 0:
                    set_state = '0'
                else:
                    set_state = '1'
                BITTREX_TRANSACTION_VOLUME_USD_PORT.state(set_state)
            if obj["symbol"] == "ZEC-BTC":
                bittrex_btc_transaction_volume = obj['volume']
                if bittrex_btc_transaction_volume == 0:
                    set_state = '0'
                else:
                    set_state = '1'
                BITTREX_TRANSACTION_VOLUME_BTC_PORT.state(set_state)
        if bittrex_usd_spot_price == 0:
            set_state = '0'
        else:
            set_state = '1'
        BITTREX_SPOT_PRICE_USD_PORT.state(set_state)
        if bittrex_btc_spot_price == 0:
            set_state = '0'
        else:
            set_state = '1'
        BITTREX_SPOT_PRICE_BTC_PORT.state(set_state)
    except Exception as e:
        notify_exchange_error("Bitrex", str(e))

    # Gemini
    try:
        gemini_zec_usd_data = gemini_zec_usd_response.json()
        gemini_zec_btc_data = gemini_zec_btc_response.json()
        gemini_usd_spot_price = float(gemini_zec_usd_data['last'])
        gemini_btc_spot_price = float(gemini_zec_btc_data['last'])
        gemini_usd_transaction_volume = gemini_zec_usd_data['volume']['ZEC']
        gemini_btc_transaction_volume = gemini_zec_btc_data['volume']['ZEC']
        if gemini_usd_spot_price == 0:
            set_state = '0'
        else:
            set_state = '1'
        GEMINI_SPOT_PRICE_USD_PORT.state(set_state)
        if gemini_btc_spot_price == 0:
            set_state = '0'
        else:
            set_state = '1'
        GEMINI_SPOT_PRICE_BTC_PORT.state(set_state)
        if gemini_usd_transaction_volume == 0:
            set_state = '0'
        else:
            set_state = '1'
        GEMINI_TRANSACTION_VOLUME_USD_PORT.state(set_state)
        if gemini_btc_transaction_volume == 0:
            set_state = '0'
        else:
            set_state = '1'
        GEMINI_TRANSACTION_VOLUME_BTC_PORT.state(set_state)
    except Exception as e:
        notify_exchange_error("Gemini", str(e))

    # Bitfinex
    try:
        bitfinex_zec_usd_data = bitfinex_zec_usd_response.json()
        bitfinex_zec_btc_data = bitfinex_zec_btc_response.json()
        bitfinex_usd_spot_price = float(bitfinex_zec_usd_data[0][-4])
        bitfinex_btc_spot_price = float(bitfinex_zec_btc_data[0][-4])
        bitfinex_usd_transaction_volume = bitfinex_zec_usd_data[0][-3]
        bitfinex_btc_transaction_volume = bitfinex_zec_btc_data[0][-3]
        if bitfinex_usd_spot_price == 0:
            set_state = '0'
        else:
            set_state = '1'
        BITFINEX_SPOT_PRICE_USD_PORT.state(set_state)
        if bitfinex_btc_spot_price == 0:
            set_state = '0'
        else:
            set_state = '1'
        BITFINEX_SPOT_PRICE_BTC_PORT.state(set_state)
        if bitfinex_usd_transaction_volume == 0:
            set_state = '0'
        else:
            set_state = '1'
        BITFINEX_TRANSACTION_VOLUME_USD_PORT.state(set_state)
        if bitfinex_btc_transaction_volume == 0:
            set_state = '0'
        else:
            set_state = '1'
        BITFINEX_TRANSACTION_VOLUME_BTC_PORT.state(set_state)
    except Exception as e:
        notify_exchange_error("Bitfinex", str(e))

    # Binance
    try:
        binance_zec_btc_data = binance_zec_btc_response.json()
        binance_btc_spot_price = float(binance_zec_btc_data['lastPrice'])
        binance_btc_transaction_volume = float(binance_zec_btc_data['volume'])
        if binance_btc_spot_price == 0:
            set_state = '0'
        else:
            set_state = '1'
        BINANCE_SPOT_PRICE_BTC_PORT.state(set_state)
        if binance_btc_transaction_volume == 0:
            set_state = '0'
        else:
            set_state = '1'
        BINANCE_TRANSACTION_VOLUME_BTC_PORT.state(set_state)
    except Exception as e:
        notify_exchange_error("Binance", str(e))

    # Coinbase
    try:
        coinbase_zec_usd_data = coinbase_zec_usd_response.json()['data']
        coinbase_usd_spot_price = float(coinbase_zec_usd_data['amount'])
        if coinbase_usd_spot_price == 0:
            set_state = '0'
        else:
            set_state = '1'
        COINBASE_SPOT_PRICE_USD_PORT.state(set_state)
    except Exception as e:
        notify_exchange_error("Coinbase", str(e))

    # Kraken
    try:
        kraken_zec_usd_data = kraken_zec_usd_response.json()[
            'result']['XZECZUSD']
        kraken_usd_spot_price = float(kraken_zec_usd_data['c'][0])
        kraken_usd_transaction_volume = float(kraken_zec_usd_data['v'][1])
        if kraken_usd_spot_price == 0:
            set_state = '0'
        else:
            set_state = '1'
        KRAKEN_SPOT_PRICE_USD_PORT.state(set_state)
        if kraken_usd_transaction_volume == 0:
            set_state = '0'
        else:
            set_state = '1'
        KRAKEN_TRANSACTION_VOLUME_USD_PORT.state(set_state)
    except Exception as e:
        notify_exchange_error("Kraken", str(e))

    # Coinjar
    try:
        coinjar_zec_btc_data = coinjar_zec_btc_response.json()
        coinjar_btc_spot_price = float(coinjar_zec_btc_data['last'])
        coinjar_btc_transaction_volume = float(coinjar_zec_btc_data['volume'])
        if coinjar_btc_spot_price == 0:
            set_state = '0'
        else:
            set_state = '1'
        COINJAR_SPOT_PRICE_BTC_PORT.state(set_state)
        if coinjar_btc_transaction_volume == 0:
            set_state = '0'
        else:
            set_state = '1'
        COINJAR_TRANSACTION_VOLUME_BTC_PORT.state(set_state)
    except Exception as e:
        notify_exchange_error("Coinjar", str(e))

    spot_price_usd = [exmo_usd_spot_price,
                      bittrex_usd_spot_price, gemini_usd_spot_price, bitfinex_usd_spot_price, kraken_usd_spot_price]
    spot_price_btc = [exmo_btc_spot_price,
                      bittrex_btc_spot_price, gemini_btc_spot_price, bitfinex_btc_spot_price, binance_btc_spot_price]
    spot_price_median_usd = median(spot_price_usd)
    spot_price_median_btc = median(spot_price_btc)
    MEDIAN_SPOT_PRICE_USD.set(spot_price_median_usd)
    MEDIAN_SPOT_PRICE_BTC.set(spot_price_median_btc)

    # Create a config of exchange: price for many use-cases
    spot_price_usd_all_exchanges = {
        "Exmo": exmo_usd_spot_price,
        "Bittrex": bittrex_usd_spot_price,
        "Gemini": gemini_usd_spot_price,
        "Bitfinex": bitfinex_usd_spot_price,
        "Coinbase": coinbase_usd_spot_price,
        "Kraken": kraken_usd_spot_price
    }
    spot_price_btc_all_exchanges = {
        "Exmo": exmo_btc_spot_price,
        "Bittrex": bittrex_btc_spot_price,
        "Gemini": gemini_btc_spot_price,
        "Bitfinex": bitfinex_btc_spot_price,
        "Binance": binance_btc_spot_price,
        "Coinjar": coinjar_btc_spot_price
    }
    for exchange_usd_price in spot_price_usd_all_exchanges.keys():
        change_percentage = abs(
            spot_price_usd_all_exchanges[exchange_usd_price] - spot_price_median_usd) / spot_price_median_usd * 100.0
        USD_EXCHANGE[exchange_usd_price].set(change_percentage)
        ABSOLUTE_PRICE_USD_EXCHANGE[exchange_usd_price].set(
            spot_price_usd_all_exchanges[exchange_usd_price])
    for exchange_btc_price in spot_price_btc_all_exchanges.keys():
        change_percentage = abs(
            spot_price_btc_all_exchanges[exchange_btc_price] - spot_price_median_btc) / spot_price_median_btc * 100.0
        BTC_EXCHANGE[exchange_btc_price].set(change_percentage)
        ABSOLUTE_PRICE_BTC_EXCHANGE[exchange_btc_price].set(
            spot_price_btc_all_exchanges[exchange_btc_price])

    # transaction volume
    transaction_volume_usd_all_exchanges = {
        "Exmo": exmo_usd_transaction_volume,
        "Bittrex": bittrex_usd_transaction_volume,
        "Gemini": gemini_usd_transaction_volume,
        "Bitfinex": bitfinex_usd_transaction_volume,
        "Kraken": kraken_usd_transaction_volume
    }
    transaction_volume_btc_all_exchanges = {
        "Exmo": exmo_btc_transaction_volume,
        "Bittrex": bittrex_btc_transaction_volume,
        "Gemini": gemini_btc_transaction_volume,
        "Bitfinex": bitfinex_btc_transaction_volume,
        "Binance": binance_btc_transaction_volume,
        "Coinjar": coinjar_btc_transaction_volume
    }
    for transaction_volume_usd in transaction_volume_usd_all_exchanges.keys():
        ABSOLUTE_TRANSACTION_VOLUME_USD_EXCHANGE[transaction_volume_usd].set(
            transaction_volume_usd_all_exchanges[transaction_volume_usd])

    for transaction_volume_btc in transaction_volume_btc_all_exchanges.keys():
        ABSOLUTE_TRANSACTION_VOLUME_BTC_EXCHANGE[transaction_volume_btc].set(
            transaction_volume_btc_all_exchanges[transaction_volume_btc]
        )
    print(slack_notification_counter)
    slack_notification_counter += 1
    if slack_notification_counter % 100 == 0:
        send_slack_notification(
            message="{} iterations of exchanges health checks done!".format(slack_notification_counter))
    time.sleep(15)
