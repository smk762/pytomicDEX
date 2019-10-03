#!/usr/bin/env python3
import os
import sys
import json
from os.path import expanduser
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'lib'))
try:
  from coinslib import coins, trading_list
except:
  print("coinslib not found! copy mm2coins_example.py and modify as required.")
  sys.exit(0)

home = expanduser("~")

error_events = [
    "StartFailed",
    "NegotiateFailed",
    "TakerFeeValidateFailed",
    "MakerPaymentTransactionFailed",
    "MakerPaymentDataSendFailed",
    "TakerPaymentValidateFailed",
    "TakerPaymentSpendFailed",
    "MakerPaymentRefunded",
    "MakerPaymentRefundFailed"
  ]

# assuming start from DB/%NODE_PUBKEY%/SWAPS/STATS/ directory
def fetch_local_swap_files(node_pubkey):
    print(home+"/pytomicDEX/DB/"+node_pubkey+"/SWAPS/STATS/")
    os.chdir(home+"/pytomicDEX/DB/"+node_pubkey+"/SWAPS/STATS/")
    files_list_tmp = os.listdir("MAKER")
    files_list = []
    for file in files_list_tmp:
        if file[-5:] == '.json':
            files_list.append(file)

    files_content = {}

    # loading files content into files_content dict
    for file in files_list:
        try:
            with open('MAKER/'+file) as json_file:
                swap_uuid = file[:-5]
                data = json.load(json_file)
                files_content[swap_uuid] = data
        except Exception as e:
            print(e)
            print("Broken: " + file)
    return files_content

# filter swaps data for speciifc pair
def pair_filter(data_to_filter, maker_coin, taker_coin):
    swaps_of_pair = {}
    for swap_data in data_to_filter.values():
        try:
            if swap_data["events"][0]["event"]["data"]["taker_coin"] == taker_coin and swap_data["events"][0]["event"]["data"]["maker_coin"] == maker_coin:
                swaps_of_pair[swap_data["events"][0]["event"]["data"]["uuid"]] = swap_data
        except Exception:
            pass
    return swaps_of_pair

# filter for time period
def time_filter(data_to_filter, start_time_stamp, end_time_stamp):
    swaps_for_dates = {}
    for swap_data in data_to_filter.values():
        try:
            if swap_data["events"][0]["timestamp"] >= start_time_stamp and swap_data["events"][0]["timestamp"] <= end_time_stamp:
                swaps_for_dates[swap_data["events"][0]["event"]["data"]["uuid"]] = swap_data
        except Exception as e:
            pass
    return swaps_for_dates

# checking if swap succesfull
def count_successful_swaps(swaps_data):
    fails_info = []
    error_type_counts = {}
    for event in error_events:
        error_type_counts[event] = 0
    successful_swaps_counter = 0
    failed_swaps_counter = 0
    i = 0
    for swap_data in swaps_data.values():
        failed = False
        for event in swap_data["events"]:
            if event["event"]["type"] in error_events:
                error_type_counts[event["event"]["type"]] += 1
                taker_coin = swap_data["events"][0]['event']['data']['taker_coin']
                maker_coin = swap_data["events"][0]['event']['data']['maker_coin']
                taker_pub = swap_data["events"][0]['event']['data']['taker']
                fail_uuid = swap_data['uuid']
                fail_timestamp = event['timestamp']
                fail_error = event["event"]["data"]['error']
                fail_data = {
                    "uuid": fail_uuid,
                    "time": fail_timestamp,
                    "pair": taker_coin+" - "+maker_coin,
                    "taker_pub": taker_pub,
                    "error": fail_error
                }
                fails_info.append(fail_data)
                failed = True
                break
        if failed:
            failed_swaps_counter += 1
        else:
            successful_swaps_counter += 1
    return (failed_swaps_counter, successful_swaps_counter, error_type_counts, fails_info)

# calculate volumes, assumes filtered data for pair
def calculate_trades_volumes(swaps_data):
    maker_coin_volume = 0
    taker_coin_volume = 0
    for swap_data in swaps_data.values():
        try:
            maker_coin_volume += float(swap_data["events"][0]["event"]["data"]["maker_amount"])
            taker_coin_volume += float(swap_data["events"][0]["event"]["data"]["taker_amount"])
        except Exception as e:
            print(swap_data["events"][0])
            print(e)
    return (maker_coin_volume, taker_coin_volume)

node_pubkeys = os.listdir(home+"/pytomicDEX/DB")
for node_pubkey in node_pubkeys:
    print(node_pubkey)
    swap_data = fetch_local_swap_files(node_pubkey)
    for maker in coins:
        for taker in coins:
            if maker != taker:
                swap_count = pair_filter(swap_data, maker, taker)
                if len(swap_count) > 0:
                    print(maker+"-"+taker+": "+str(len(swap_count)))

    swaps = count_successful_swaps(swap_data)
    print("Total successful: "+str(swaps[1]))
    print("Total failed: "+str(swaps[0]))
    print("Error Type Counts: "+str(swaps[2]))
    print("Fail info: "+str(swaps[3]))
            
    volumes = calculate_trades_volumes(swap_data)
    print("Total maker volume: "+str(volumes[0]))
    print("Total taker volume: "+str(volumes[1]))
