import json
import time
import subprocess
import requests
import linecache
import sys
from prometheus_client import (Enum, Gauge, Histogram, Summary, start_http_server)
from configs.metrics_config import *
from self_health_check.utils import send_slack_notification

start_http_server(8094)

last_block_considered = None

def print_exception():
    """returns the line number, line contents and the description of the last exception as a string"""
    exc_type, exc_obj, tb = sys.exc_info()
    f = tb.tb_frame
    lineno = tb.tb_lineno
    filename = f.f_code.co_filename
    linecache.checkcache(filename)
    line = linecache.getline(filename, lineno, f.f_globals)
    return '(LINE {} "{}"): {}'.format(lineno, line.strip(), exc_obj)

def notify_metric_error(identifier, exception_string):
    send_slack_notification(
        message="Exception occured in {} in metrics.py Exception in {}".format(identifier, exception_string))

def block_info(block_hash_or_height, verbose_identifier):
    """gets the block data from zcash-cli and returns a json object"""
    try:
        zcashd_block_data = subprocess.run(["zcash-cli","getblock",block_hash_or_height, verbose_identifier], check=True, stdout=subprocess.PIPE, universal_newlines=True, stderr=subprocess.PIPE)
    except:
        exception_string = print_exception()
        notify_metric_error("ZCASHD", str(exception_string))

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

try:
    last_block_transactions_checked_data = subprocess.run(["zcash-cli","getblockcount"], check=True, stdout=subprocess.PIPE, universal_newlines=True, stderr=subprocess.PIPE)
    last_block_considered = int((last_block_transactions_checked_data.stdout).strip())
except:
        exception_string = print_exception()
        notify_metric_error("ZCASHD", str(exception_string))

slack_notification_counter = 0
while True:

    #ZCASHD
    try:
        zcashd_blockcount_data = subprocess.run(["zcash-cli","getblockcount"], check=True, stdout=subprocess.PIPE, universal_newlines=True, stderr=subprocess.PIPE)
    except:
        exception_string = print_exception()
        notify_metric_error("ZCASHD", str(exception_string))
        pass
    try:
        zcashd_blockchain_info = subprocess.run(["zcash-cli","getblockchaininfo"], check=True, stdout=subprocess.PIPE, universal_newlines=True, stderr=subprocess.PIPE)
    except:
        exception_string = print_exception()
        notify_metric_error("ZCASHD", str(exception_string))
        pass

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
        notify_metric_error("value pool metric", str(exception_string))

    try:    
        zcash_difficulty = float(zcashd_blockchain_info_data["difficulty"])
        ZCASH_DIFFICULTY_GAUGE.set(zcash_difficulty)
    except:
        exception_string = print_exception()
        notify_metric_error("zcash difficulty metric", str(exception_string))

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
            BLOCK_HEIGHT_GAUGE.set(last_block_considered)
            time.sleep(5) #prometheus scrapes every 5 seconds, making sure every block gets counted
    except:
        exception_string = print_exception()
        notify_metric_error("transaction count metric", str(exception_string))

    slack_notification_counter += 1
    print(slack_notification_counter)
    if slack_notification_counter % 30 == 0:
        send_slack_notification(message="{} iterations of metrics.py done!".format(slack_notification_counter))
    time.sleep(20)
