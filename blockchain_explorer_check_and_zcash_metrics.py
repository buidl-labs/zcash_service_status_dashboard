import json
import time
import subprocess
import requests
import linecache
import sys
from prometheus_client import (Enum, Gauge, Histogram, Summary, start_http_server)
from blockchain_explorer_and_metrics_config import *
from self_health_check.utils import send_slack_notification

start_http_server(8093)

def print_exception():
    """returns the line number, line contents and the description of the last exception as a string"""
    exc_type, exc_obj, tb = sys.exc_info()
    f = tb.tb_frame
    lineno = tb.tb_lineno
    filename = f.f_code.co_filename
    linecache.checkcache(filename)
    line = linecache.getline(filename, lineno, f.f_globals)
    return '(LINE {} "{}"): {}'.format(lineno, line.strip(), exc_obj)

def notify_metric_explorer_error(identifier, exception_string):
    send_slack_notification(
        message="Exception occured in {} in blockchain_explorer/metric file. Exception in {}".format(
            identifier, exception_string
        )
    )

def block_info(block_hash_or_height, verbose_identifier):
    """gets the block data from zcash-cli and returns a json object"""
    try:
        zcashd_block_data = subprocess.run(["zcash-cli","getblock",block_hash_or_height, verbose_identifier], check=True, stdout=subprocess.PIPE, universal_newlines=True, stderr=subprocess.PIPE)
    except:
        exception_string = print_exception()
        notify_metric_explorer_error("ZCASHD", str(exception_string))

    zcashd_block = json.loads((zcashd_block_data.stdout).strip())
    return zcashd_block

def transaction_type_check(block_hash_or_height):
    """counts the number of transparent and shielded transactions in a block and returns a tuple"""
    block_data = block_info(block_hash_or_height, "2")
    shielded_counter = 0
    transparent_counter = 0
    for this_transaction in range(len(block_data["tx"])):
        if not (block_data["tx"][this_transaction]["vjoinsplit"] or block_data["tx"][this_transaction]["vShieldedOutput"] or block_data["tx"][this_transaction]["vShieldedSpend"]):
            #if all three fields are empty than the transaction is transparent
            transparent_counter+=1
        else:
            shielded_counter+=1
    return(transparent_counter, shielded_counter)

def zcashd_fields(last_block_hash_or_height):
    """returns a list of all the fields to be checked in a block in correct order"""
    zcashd_block = block_info(last_block_hash_or_height, "1")
    zcashd_transaction_hashes = []
    for this_transaction in range(len(zcashd_block["tx"])):
        zcashd_transaction_hashes.append(zcashd_block["tx"][this_transaction])
    zcashd_transaction_hashes.sort()
    zcashd_block_fields =(
        zcashd_block["hash"],
        zcashd_block["size"],
        zcashd_block["height"],
        len(zcashd_block["tx"]),
        zcashd_block["version"],
        zcashd_block["merkleroot"],
        zcashd_block["time"],
        zcashd_block["nonce"],
        zcashd_block["solution"],
        zcashd_block["bits"],
        zcashd_block["chainwork"],
        zcashd_block["previousblockhash"],
        zcashd_transaction_hashes
        )
    return zcashd_block_fields

try:
    last_block_transactions_checked_data = subprocess.run(["zcash-cli","getblockcount"], check=True, stdout=subprocess.PIPE, universal_newlines=True, stderr=subprocess.PIPE)
except:
        exception_string = print_exception()
        notify_metric_explorer_error("ZCASHD", str(exception_string))
last_block_considered = int((last_block_transactions_checked_data.stdout).strip())

slack_notification_counter = 0
while True:

    zcha_network_response = None
    try:
        zcha_network_response = requests.get(url = ZCHA_NETWORK_URL, timeout = 5)
    except:
        exception_string = print_exception()
        notify_metric_explorer_error("ZCHA NETWORK URL RESPONSE", str(exception_string))
        pass

    #ZCASHD
    try:
        zcashd_blockcount_data = subprocess.run(["zcash-cli","getblockcount"], check=True, stdout=subprocess.PIPE, universal_newlines=True, stderr=subprocess.PIPE)
    except:
        exception_string = print_exception()
        notify_metric_explorer_error("ZCASHD", str(exception_string))
        pass
    try:
        zcashd_blockchain_info = subprocess.run(["zcash-cli","getblockchaininfo"], check=True, stdout=subprocess.PIPE, universal_newlines=True, stderr=subprocess.PIPE)
    except:
        exception_string = print_exception()
        notify_metric_explorer_error("ZCASHD", str(exception_string))
        pass

    #ZCHA
    #TODO - check for none values
    #this way has its drawbacks - if two or more blocks get mined in 30 secs (the time.sleep() value), this will only check the last block
    zcha_last_block_hash = zcha_last_block_response = None
    try:
        zcashd_height = int((zcashd_blockcount_data.stdout).strip())
        zcha_network_data = zcha_network_response.json()
        zcha_block_height = int(zcha_network_data['blockNumber'])
        zcha_last_block_hash = zcha_network_data['blockHash']
        if zcha_block_height == zcashd_height:
            set_state = '1'
        else:
            set_state = '0'
        ZCHA_BLOCK_HEIGHT_PORT.state(set_state)
    except:
        exception_string = print_exception()
        notify_metric_explorer_error("ZCHA", str(exception_string))
    
    try:
        zcha_last_block_response = requests.get(url=ZCHA_BLOCK_URL + zcha_last_block_hash, timeout=5)
    except:
        exception_string = print_exception()
        notify_metric_explorer_error("ZCHA", str(exception_string))

    zcha_last_block = zcha_last_block_response.json()
    zcha_transaction_hashes = []
    #zcha only returns a maximum of 20 transactions at a time
    
    try:
        for zcha_requests in range(int(zcha_last_block["transactions"]/20)+1):
            offset = zcha_requests*20
            zcha_block_transactions_response = requests.get(url=ZCHA_BLOCK_URL + zcha_last_block_hash + "/transactions?limit=20&offset={}&sort=index&direction=ascending".format(offset), timeout=5)
            zcha_block_transactions = zcha_block_transactions_response.json()
            for this_transaction in range(zcha_last_block["transactions"]):
                zcha_transaction_hashes.append(zcha_block_transactions[this_transaction]["hash"])
        zcha_transaction_hashes.sort()
        zcashd_block_fields = zcashd_fields(str(zcha_block_height))
        zcha_block_fields = (
            zcha_last_block["hash"],
            zcha_last_block["size"],
            zcha_last_block["height"],
            zcha_last_block["transactions"],
            zcha_last_block["version"],
            zcha_last_block["merkleRoot"],
            zcha_last_block["timestamp"],
            zcha_last_block["nonce"],
            zcha_last_block["solution"],
            zcha_last_block["bits"],
            zcha_last_block["chainWork"],
            zcha_last_block["prevHash"],
            zcha_transaction_hashes
            )
        if zcha_block_fields == zcashd_block_fields:
            set_state = '1'
        else:
            set_state = '0'
        ZCHA_LAST_BLOCK_CHECK_PORT.state(set_state)

    except:
        exception_string = print_exception()
        notify_metric_explorer_error("ZCHA", str(exception_string))

    #METRICS
    try:
        zcashd_blockchain_info_data = json.loads((zcashd_blockchain_info.stdout).strip())
        if zcashd_blockchain_info_data["valuePools"][0]["monitored"] == True:
            sprout_value_pool = float(zcashd_blockchain_info_data["valuePools"][0]["chainValue"])
            SPROUT_VALUE_POOL_GAUGE.set(sprout_value_pool)
        else:
             send_slack_notification("zcashd node reindex required")
        if zcashd_blockchain_info_data["valuePools"][1]["monitored"] == True:
            sapling_value_pool = float(zcashd_blockchain_info_data["valuePools"][1]["chainValue"])
            SAPLING_VALUE_POOL_GAUGE.set(sapling_value_pool)
        else:
             send_slack_notification("zcashd node reindex required")
    except:
        exception_string = print_exception()
        notify_metric_explorer_error("value pool metric", str(exception_string))

    try:    
        zcash_difficulty = float(zcashd_blockchain_info_data["difficulty"])
        ZCASH_DIFFICULTY_GAUGE.set(zcash_difficulty)
    except:
        exception_string = print_exception()
        notify_metric_explorer_error("zcash difficulty metric", str(exception_string))

    try:
        zcashd_height = int((zcashd_blockcount_data.stdout).strip())
        if slack_notification_counter == 0:
            #in the first iteration, last_block_considered = zcashd_height, so the loop will not run
            first_iteration = True
        while (last_block_considered < zcashd_height or first_iteration == True):
            #using this loop so that no block's transactions remain uncounted
            if first_iteration == True:
                first_iteration = False
            else:
                last_block_considered+=1
            count_of_type_of_transactions = transaction_type_check(str(last_block_considered))
            transparent_transactions_in_block = count_of_type_of_transactions[0]
            TRANSPARENT_TRANSACTIONS_IN_BLOCK_GAUGE.set(transparent_transactions_in_block)
            shielded_transactions_in_block = count_of_type_of_transactions[1]
            SHIELDED_TRANSACTIONS_IN_BLOCK_GAUGE.set(shielded_transactions_in_block)
            time.sleep(5) #prometheus scrapes every 5 seconds, making sure every block gets counted
    except:
        exception_string = print_exception()
        notify_metric_explorer_error("transaction count metric", str(exception_string))

    slack_notification_counter += 1
    print(slack_notification_counter)
    if slack_notification_counter % 30 == 0:
        send_slack_notification(
            message="{} iterations of blockchain explorer/metrics done!".format(slack_notification_counter))
    time.sleep(30)
