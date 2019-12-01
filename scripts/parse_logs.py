#!/usr/bin/env python3
import json

# Change this to your log filename
logfilename = "my_logs.txt"

with open(logfilename, "r") as f:
    lines = f.readlines()
    x = 0
    for line in lines:
        x += 1
        # Remove log data not during stress test
        if line.find('NoSuchMethodError') == -1 and line.find('JsonRpcError') == -1  and line.find('Transport error') == -1:
                # Get recent swaps json
                if line.find('getRecentSwaps') > -1:
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
