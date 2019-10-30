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

def notify_metric_explorer_error(identifier, exception_string):
    send_slack_notification(
    	message="Exception occured in {} in blockchain_explorers_health_check.py file. Exception in {}".format(identifier, exception_string))

def block_info(block_hash_or_height, verbose_identifier):
    """gets the block data from zcash-cli and returns a json object"""
    try:
        zcashd_block_data = subprocess.run(["zcash-cli","getblock",block_hash_or_height, verbose_identifier], check=True, stdout=subprocess.PIPE, universal_newlines=True, stderr=subprocess.PIPE)
    except:
        exception_string = print_exception()
        notify_metric_explorer_error("ZCASHD", str(exception_string))

    zcashd_block = json.loads((zcashd_block_data.stdout).strip())
    return zcashd_block

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

last_block_considered = None
slack_notification_counter = 0

while True:

	#ZCASHD
    try:
        zcashd_blockcount_data = subprocess.run(["zcash-cli","getblockcount"], check=True, stdout=subprocess.PIPE, universal_newlines=True, stderr=subprocess.PIPE)
    	zcashd_height = int((zcashd_blockcount_data.stdout).strip())
    	zcashd_block_fields = zcashd_fields(zcashd_height)
    except:
        exception_string = print_exception()
        notify_metric_explorer_error("ZCASHD", str(exception_string))
        pass

    if(last_block_considered == zcashd_height):
    	time.sleep(5)
    	continue

    #ZCHA
    zcha_block_response = zcha_block = None
    try:
    	zcha_block_response = requests.get(url=ZCHA_BLOCK_URL + zcashd_block_fields["hash"], timeout=5)
    	zcha_block = zcha_block_response.json()
        if zcha_block["error"] == "Block not found.":
        	time.sleep(5)
        	zcha_block_response = requests.get(url=ZCHA_BLOCK_URL + zcashd_block_fields["hash"], timeout=5)
        	zcha_block = zcha_block_response.json()
        if zcashd_height == zcha_block["height"]:
            set_state = '1'
        else:
        	set_state = '0'
        ZCHA_BLOCK_HEIGHT_PORT.state(set_state)
    
    	zcha_transaction_hashes = []

    	#zcha only returns a maximum of 20 transactions at a time
       	for zcha_requests in range(int(zcha_block["transactions"]/20)+1):
       	    offset = zcha_requests*20
           	zcha_block_transactions_response = requests.get(url=ZCHA_BLOCK_URL + zcha_last_block_hash + "/transactions?limit=20&offset={}&sort=index&direction=ascending".format(offset), timeout=5)
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
       	if zcha_block_fields == zcashd_block_fields:
       	    set_state = '1'
       	else:
          	set_state = '0'
        ZCHA_LAST_BLOCK_CHECK_PORT.state(set_state)
    except:
    	if(zcha_block_response == None):
    		send_slack_notification(message="zcha_block_response is empty")	
    	else:	
        	exception_string = print_exception()
        	notify_metric_explorer_error("ZCHA", str(exception_string))
    
    if(last_block_considered == None):
    	last_block_considered = zcashd_height

    elif last_block_considered < zcashd_height:
    	last_block_considered+=1

    slack_notification_counter += 1
    print(slack_notification_counter)
    if slack_notification_counter % 30 == 0:
        send_slack_notification(
            message="{} iterations of blockchain explorer/metrics done!".format(slack_notification_counter))
