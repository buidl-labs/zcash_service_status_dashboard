import json
import time
import subprocess
import requests
import linecache
import sys
from prometheus_client import (Enum, Gauge, Histogram, Summary, start_http_server)
from configs.blockchain_explorers_config import *
from self_health_check.utils import send_slack_notification

start_http_server(8095)

def print_exception():
    """returns the line number, line contents and the description of the last exception as a string"""
    exc_type, exc_obj, tb = sys.exc_info()
    f = tb.tb_frame
    lineno = tb.tb_lineno
    filename = f.f_code.co_filename
    linecache.checkcache(filename)
    line = linecache.getline(filename, lineno, f.f_globals)
    return '(LINE {} "{}"): {}'.format(lineno, line.strip(), exc_obj)

def notify_explorer_error(identifier, exception_string):
    send_slack_notification(
        message="Exception occured in {} in blockchain_explorers_health_check.py file. Exception in {}".format(identifier, exception_string))

def block_info(block_hash_or_height, verbose_identifier):
    """gets the block data from zcash-cli and returns a json object"""
    try:
        zcashd_block_data = subprocess.run(["zcash-cli","getblock",str(block_hash_or_height), str(verbose_identifier)], check=True, stdout=subprocess.PIPE, universal_newlines=True, stderr=subprocess.PIPE)
        zcashd_block = json.loads((zcashd_block_data.stdout).strip())
    except:
        exception_string = print_exception()
        notify_explorer_error("ZCASHD", str(exception_string))

    return zcashd_block

def zcashd_fields(last_block_hash_or_height, fields_identifier):
    """returns a list of all the fields to be checked in a block in correct order"""
    zcashd_block = block_info(str(last_block_hash_or_height), "1")
    zcashd_transaction_hashes = []
    for this_transaction in range(len(zcashd_block["tx"])):
        zcashd_transaction_hashes.append(zcashd_block["tx"][this_transaction])
    zcashd_transaction_hashes.sort()
    if fields_identifier == 1:
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
    if fields_identifier == 2:
        zcashd_block_fields =(
            zcashd_block["hash"],
            zcashd_block["size"],
            zcashd_block["height"],
            len(zcashd_block["tx"]),
            zcashd_block["version"],
            zcashd_block["merkleroot"],
            zcashd_block["time"],
            zcashd_block["nonce"],
            zcashd_block["bits"],
            zcashd_block["previousblockhash"],
            zcashd_transaction_hashes
            )

    return zcashd_block_fields

last_block_considered = None
slack_notification_counter = 0

while True:

    #ZCASHD
    try:
        zcashd_blockcount_data = subprocess.run(["zcash-cli","getblockcount"], check=True, stdout=subprocess.PIPE, universal_newlines=True, stderr=subprocess.PIPE)
        zcashd_height = int((zcashd_blockcount_data.stdout).strip())
        zcashd_block_fields = zcashd_fields(str(zcashd_height), 1)
        zcashd_block_fields_second_variation = zcashd_fields(str(zcashd_height), 2)
    except:
        exception_string = print_exception()
        notify_explorer_error("ZCASHD", str(exception_string))
        continue

    if(last_block_considered == zcashd_height):
        time.sleep(5)
        continue

    #ZCHA
    zcha_block_height_not_correct = False
    zcha_block_response = zcha_block = None
    try:
        zcha_block_response = requests.get(url=ZCHA_BLOCK_URL + zcashd_block_fields[0], timeout=20)
        if zcha_block_response.status_code != 200:
            time.sleep(2)
            zcha_block_response = requests.get(url=ZCHA_BLOCK_URL + zcashd_block_fields[0], timeout=20)
        zcha_block = zcha_block_response.json()
        if zcashd_height == zcha_block["height"]:
            set_state = '1'
        else:
            set_state = '0'
            zcha_block_height_not_correct = True
        ZCHA_BLOCK_HEIGHT_PORT.state(set_state)
    
        zcha_transaction_hashes = []

        #zcha only returns a maximum of 20 transactions at a time
        for zcha_requests in range(int(zcha_block["transactions"]/20)+1):
            offset = zcha_requests*20
            zcha_block_transactions_response = requests.get(url=ZCHA_BLOCK_URL + zcashd_block_fields[0] + "/transactions?limit=20&offset={}&sort=index&direction=ascending".format(offset), timeout=5)
            zcha_block_transactions = zcha_block_transactions_response.json()
            for this_transaction in range(zcha_block["transactions"]):
               zcha_transaction_hashes.append(zcha_block_transactions[this_transaction]["hash"])
        zcha_transaction_hashes.sort()
        zcha_block_fields = (
            zcha_block["hash"],
            zcha_block["size"],
            zcha_block["height"],
            zcha_block["transactions"],
            zcha_block["version"],
            zcha_block["merkleRoot"],
            zcha_block["timestamp"],
            zcha_block["nonce"],
            zcha_block["solution"],
            zcha_block["bits"],
            zcha_block["chainWork"],
            zcha_block["prevHash"],
            zcha_transaction_hashes
            )
        if zcha_block_fields == zcashd_block_fields and zcha_block_height_not_correct == False:
            set_state = '1'
        else:
            set_state = '0'
        ZCHA_LAST_BLOCK_CHECK_PORT.state(set_state)

    except:
        ZCHA_BLOCK_HEIGHT_PORT.state('0')
        ZCHA_LAST_BLOCK_CHECK_PORT.state('0')
        if(zcha_block_response == None):
            send_slack_notification(message="zcha_block_response is empty")
        else:
            exception_string = print_exception()
            notify_explorer_error("ZCHA", str(exception_string))
    
    #ZCASHNETWORKINFO
    zcashnetworkinfo_block_height_not_correct = False
    zcashnetworkinfo_block_response = zcashnetworkinfo_block = None
    try:
        zcashnetworkinfo_block_response = requests.get(url=ZCASHNETWORKINFO_BLOCK_URL + zcashd_block_fields[0], timeout=30)
        if zcashnetworkinfo_block_response.status_code != 200:
            time.sleep(5)
            zcashnetworkinfo_block_response = requests.get(url=ZCASHNETWORKINFO_BLOCK_URL+ zcashd_block_fields[0], timeout=15)
        zcashnetworkinfo_block = zcashnetworkinfo_block_response.json()
        if zcashd_height == zcashnetworkinfo_block["height"]:
            set_state = '1'
        else:
            set_state = '0'
            zcashnetworkinfo_block_height_not_correct = True
        ZCASHNETWORKINFO_BLOCK_HEIGHT_PORT.state(set_state)

        zcashnetworkinfo_transaction_hashes = zcashnetworkinfo_block["tx"]
        zcashnetworkinfo_transaction_hashes.sort()
        zcashnetworkinfo_block_fields = (
            zcashnetworkinfo_block["hash"],
            zcashnetworkinfo_block["size"],
            zcashnetworkinfo_block["height"],
            len(zcashnetworkinfo_block["tx"]),
            zcashnetworkinfo_block["version"],
            zcashnetworkinfo_block["merkleroot"],
            zcashnetworkinfo_block["time"],
            zcashnetworkinfo_block["nonce"],
            zcashnetworkinfo_block["solution"],
            zcashnetworkinfo_block["bits"],
            zcashnetworkinfo_block["chainwork"],
            zcashnetworkinfo_block["previousblockhash"],
            zcashnetworkinfo_transaction_hashes
            )

        if zcashnetworkinfo_block_fields == zcashd_block_fields and zcashnetworkinfo_block_height_not_correct == False:
            set_state = '1'
        else:
            set_state = '0'
        ZCASHNETWORKINFO_LAST_BLOCK_CHECK_PORT.state(set_state)
        
    except:
        ZCASHNETWORKINFO_BLOCK_HEIGHT_PORT.state('0')
        ZCASHNETWORKINFO_LAST_BLOCK_CHECK_PORT.state('0')
        if(zcashnetworkinfo_block_response == None):
            send_slack_notification(message="zcashnetworkinfo_block_response is empty")
        else:
            exception_string = print_exception()
            notify_explorer_error("ZCASHNETWORKINFO", str(exception_string))    

    #ZECMATE
    zecmate_block_height_not_correct = False
    zecmate_block_response = zecmate_block = None
    try:
        zecmate_block_response = requests.get(url=ZECMATE_BLOCK_URL + zcashd_block_fields[0], timeout=15)
        if zecmate_block_response.status_code != 200:
            time.sleep(5)
            zecmate_block_response = requests.get(url=ZECMATE_BLOCK_URL+ zcashd_block_fields[0], timeout=15)
        zecmate_block = zecmate_block_response.json()
        if zcashd_height == zecmate_block["height"]:
            set_state = '1'
        else:
            set_state = '0'
            zecmate_block_height_not_correct = True
        ZECMATE_BLOCK_HEIGHT_PORT.state(set_state)

        zecmate_transaction_hashes = zecmate_block["tx"]
        zecmate_transaction_hashes.sort()
        zecmate_block_fields = (
            zecmate_block["hash"],
            zecmate_block["size"],
            zecmate_block["height"],
            len(zecmate_block["tx"]),
            zecmate_block["version"],
            zecmate_block["merkleroot"],
            zecmate_block["time"],
            zecmate_block["nonce"],
            zecmate_block["solution"],
            zecmate_block["bits"],
            zecmate_block["chainwork"],
            zecmate_block["previousblockhash"],
            zecmate_transaction_hashes
            )

        if zecmate_block_fields == zcashd_block_fields and zecmate_block_height_not_correct == False:
            set_state = '1'
        else:
            set_state = '0'
        ZECMATE_LAST_BLOCK_CHECK_PORT.state(set_state)

    except:
        ZECMATE_BLOCK_HEIGHT_PORT.state('0')
        ZECMATE_LAST_BLOCK_CHECK_PORT.state('0')
        if(zecmate_block_response == None):
            send_slack_notification(message="zecmate_block_response is empty")
        else:
            exception_string = print_exception()
            notify_explorer_error("ZECMATE", str(exception_string))  

    #ZCASHFR
    zcashfr_block_height_not_correct = False
    zcashfr_block_response = zcashfr_block = None
    try:
        zcashfr_block_response = requests.get(url=ZCASHFR_BLOCK_URL + zcashd_block_fields[0], timeout=15)
        if zcashfr_block_response.status_code != 200:
            time.sleep(5)
            zcashfr_block_response = requests.get(url=ZCASHFR_BLOCK_URL+ zcashd_block_fields[0], timeout=15)
        zcashfr_block = zcashfr_block_response.json()
        if zcashd_height == zcashfr_block["height"]:
            set_state = '1'
        else:
            set_state = '0'
            zcashfr_block_height_not_correct = True
        ZCASHFR_BLOCK_HEIGHT_PORT.state(set_state)

        zcashfr_transaction_hashes = zcashfr_block["tx"]
        zcashfr_transaction_hashes.sort()
        zcashfr_block_fields = (
            zcashfr_block["hash"],
            zcashfr_block["size"],
            zcashfr_block["height"],
            len(zcashfr_block["tx"]),
            zcashfr_block["version"],
            zcashfr_block["merkleroot"],
            zcashfr_block["time"],
            zcashfr_block["nonce"],
            zcashfr_block["solution"],
            zcashfr_block["bits"],
            zcashfr_block["chainwork"],
            zcashfr_block["previousblockhash"],
            zcashfr_transaction_hashes
            )

        if zcashfr_block_fields == zcashd_block_fields and zcashfr_block_height_not_correct == False:
            set_state = '1'
        else:
            set_state = '0'
        ZCASHFR_LAST_BLOCK_CHECK_PORT.state(set_state)

    except:
        ZCASHFR_BLOCK_HEIGHT_PORT.state('0')
        ZCASHFR_LAST_BLOCK_CHECK_PORT.state('0')
        if(zcashfr_block_response == None):
            send_slack_notification(message="zcashfr_block_response is empty")
             
        else:
            exception_string = print_exception()
            notify_explorer_error("ZCASHFR", str(exception_string))

    #CHAINSO
    chainso_block_height_not_correct = False
    chainso_block_response = chainso_block = None
    try:
        chainso_block_response = requests.get(url=CHAINSO_BLOCK_URL + str(zcashd_block_fields_second_variation[2]), timeout=30)
        if chainso_block_response.status_code != 200:
            time.sleep(5)
            chainso_block_response = requests.get(url=CHAINSO_BLOCK_URL+ str(zcashd_block_fields_second_variation[2]), timeout=10)
        chainso_block = chainso_block_response.json()
        if zcashd_height == chainso_block["data"]["block_no"]:
            set_state = '1'
        else:
            set_state = '0'
            chainso_block_height_not_correct = True
        CHAINSO_BLOCK_HEIGHT_PORT.state(set_state)

        chainso_transaction_hashes = []
        for this_transaction in range(len(chainso_block["data"]["txs"])):
            chainso_transaction_hashes.append(chainso_block["data"]["txs"][this_transaction]["txid"])
        chainso_transaction_hashes.sort()
        chainso_block_fields = (
            chainso_block["data"]["blockhash"],
            chainso_block["data"]["size"],
            chainso_block["data"]["block_no"],
            (len(chainso_block["data"]["txs"])),
            chainso_block["data"]["version"],
            chainso_block["data"]["merkleroot"],
            chainso_block["data"]["time"],
            chainso_block["data"]["nonce"],
            chainso_block["data"]["bits"],
            chainso_block["data"]["previous_blockhash"],
            chainso_transaction_hashes
            )

        if chainso_block_fields == zcashd_block_fields_second_variation and chainso_block_height_not_correct == False:
            set_state = '1'
        else:
            set_state = '0'
        CHAINSO_LAST_BLOCK_CHECK_PORT.state(set_state)

    except:
        CHAINSO_BLOCK_HEIGHT_PORT.state('0')
        CHAINSO_LAST_BLOCK_CHECK_PORT.state('0')
        if(chainso_block_response == None):
            send_slack_notification(message="chainso_block_response is empty")
        else:
            exception_string = print_exception()
            notify_explorer_error("CHAINSO", str(exception_string))

    #NETDNA
    netdna_block_height_not_correct = False
    netdna_block_response = netdna_block = None
    try:
        netdna_block_response = requests.get(url=NETDNA_BLOCK_URL + str(zcashd_block_fields_second_variation[2]), timeout=30)
        if netdna_block_response.status_code != 200:
            time.sleep(5)
            netdna_block_response = requests.get(url=NETDNA_BLOCK_URL+ str(zcashd_block_fields_second_variation[2]), timeout=15)
        netdna_block = netdna_block_response.json()
        if zcashd_height == netdna_block["data"]["block_no"]:
            set_state = '1'
        else:
            set_state = '0'
            netdna_block_height_not_correct = True
        NETDNA_BLOCK_HEIGHT_PORT.state(set_state)

        netdna_transaction_hashes = []
        for this_transaction in range(len(netdna_block["data"]["txs"])):
            netdna_transaction_hashes.append(netdna_block["data"]["txs"][this_transaction]["txid"])
        netdna_transaction_hashes.sort()
        netdna_block_fields = (
            netdna_block["data"]["blockhash"],
            netdna_block["data"]["size"],
            netdna_block["data"]["block_no"],
            (len(netdna_block["data"]["txs"])),
            netdna_block["data"]["version"],
            netdna_block["data"]["merkleroot"],
            netdna_block["data"]["time"],
            netdna_block["data"]["nonce"],
            netdna_block["data"]["bits"],
            netdna_block["data"]["previous_blockhash"],
            netdna_transaction_hashes
            )

        if netdna_block_fields == zcashd_block_fields_second_variation and netdna_block_height_not_correct == False:
            set_state = '1'
        else:
            set_state = '0'
        NETDNA_LAST_BLOCK_CHECK_PORT.state(set_state)

    except:
        NETDNA_BLOCK_HEIGHT_PORT.state('0')
        NETDNA_LAST_BLOCK_CHECK_PORT.state('0')
        if(netdna_block_response == None):
            send_slack_notification(message="netdna_block_response is empty")
        else:
            exception_string = print_exception()
            notify_explorer_error("NETDNA", str(exception_string))

    if(last_block_considered == None):
        last_block_considered = zcashd_height

    elif last_block_considered < zcashd_height:
        last_block_considered+=1

    slack_notification_counter += 1
    print("iteration count = {}    block number = {}".format(slack_notification_counter, zcashd_height))
    if slack_notification_counter%30==0:
        send_slack_notification(
            message="{} iterations of blockchain_explorers_health_check.py done!".format(slack_notification_counter))
