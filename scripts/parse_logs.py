#!/usr/bin/env python3
import os
import sys
import json

# Change this to your log filename
try: 
    logfilename = sys.argv[1]
except:
    print("use like: parse_logs.py logfile.log")

if not os.path.isdir("MAKER"):
    os.makedirs("MAKER")
if not os.path.isdir("TAKER"):
    os.makedirs("TAKER")

with open(logfilename, "r") as f:
    lines = f.readlines()
    for line in lines:
        # Remove log data not during stress test
        if line.find('getRecentSwaps') > -1:
            print(line)
            try:
                swap_json = " ".join(line.split(" ")[3:])[1:]
                swap_results = json.loads(swap_json)['result']['swaps']
                for swap in swap_results: 
                    if swap['type'] == 'Taker':
                        folder = "TAKER"
                    elif swap['type'] == 'Maker':
                        folder = "MAKER"
                    uuid = swap['uuid']
                    with open(folder+"/"+uuid+".json", "w") as j:
                        print("writing "+folder+"/"+uuid+".json")
                        j.write(json.dumps(swap))
            except json.decoder.JSONDecodeError:
                pass
