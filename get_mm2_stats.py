#!/usr/bin/env python3
from stats_lib import *
try:
  from mm2coins import coins, trading_list
except:
  print("mm2coins.py not found! copy mm2coins_example.py and modify as required.")
  sys.exit(0)
node_pubkeys = os.listdir(home+"/pytomicDEX/DB")
for node_pubkey in node_pubkeys:
    print(node_pubkey)
    swap_data = fetch_local_swap_files(node_pubkey)
    for maker in coins:
        for taker in coins:
            if maker['tag'] != taker['tag']:
                swap_count = pair_filter(swap_data, maker['tag'], taker['tag'])
                if len(swap_count) > 0:
                    print(maker['tag']+"-"+taker['tag']+": "+str(len(swap_count)))

    swaps = count_successful_swaps(swap_data)
    print("Total successful: "+str(swaps[1]))
    print("Total failed: "+str(swaps[0]))
    print("Error Type Counts: "+str(swaps[2]))
    print("Fail info: "+str(swaps[3]))
            
    volumes = calculate_trades_volumes(swap_data)
    print("Total maker volume: "+str(volumes[0]))
    print("Total taker volume: "+str(volumes[1]))
