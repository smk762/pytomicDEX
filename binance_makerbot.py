#!/usr/bin/env python3
import os
from os.path import expanduser
import sys
import time
import binance_api
import mm2lib

home = expanduser("~")
mm2_path = home+'/pytomicDEX'

trading_coins = list(mm2lib.trading_list.keys())
accepted_coins = trading_coins[:]
accepted_coins.append('BTC')
try:
    mm2lib.my_balance('http://127.0.0.1:7783', mm2lib.userpass, 'KMD')
except:
    os.chdir(mm2_path)
    mm2lib.start_mm2('mm2.log')
    pass

mm2lib.activate_all('http://127.0.0.1:7783', mm2lib.userpass, mm2lib.coins)

while True:
    coins_data = mm2lib.build_coins_data(mm2lib.coins)
    mm2lib.show_balances_table(coins_data, trading_coins)
    mm2lib.recent_swaps_table("http://127.0.0.1:7783", mm2lib.userpass, 50, coins_data)
    my_orders = mm2lib.my_orders('http://127.0.0.1:7783', mm2lib.userpass).json()
    for base in mm2lib.trading_list:
        balance_data = mm2lib.my_balance('http://127.0.0.1:7783', mm2lib.userpass, base).json()
        base_addr = balance_data['address']
        bal = float(balance_data['balance'])
        if base == 'BCH':
            base_btc_price = binance_api.get_price('BCHABCBTC')
        else:
            base_btc_price = binance_api.get_price(base+'BTC')
        if bal > mm2lib.trading_list[base]['reserve_balance']*1.2:
            qty = bal - mm2lib.trading_list[base]['reserve_balance']
            bal = bal - qty
            # Send Funds to Binance
            if base == "BCH":
                deposit_addr = binance_api.get_deposit_addr(base+"ABC")
            else:
                deposit_addr = binance_api.get_deposit_addr(base)
            withdraw_tx = mm2lib.withdraw("http://127.0.0.1:7783", mm2lib.userpass, base, deposit_addr['address'], qty).json()
            send_resp = mm2lib.send_raw_transaction("http://127.0.0.1:7783", mm2lib.userpass, base, withdraw_tx['tx_hex']).json()
            print("Sent "+str(qty)+" "+base+" to Binance address "+deposit_addr['address'])
            print("TXID: "+send_resp['tx_hash'])
        elif bal < mm2lib.trading_list[base]['reserve_balance']*0.8:
            qty = mm2lib.trading_list[base]['reserve_balance'] - bal
            if base == "BCH":
                withdraw_tx = binance_api.withdraw(base+"ABC", base_addr, qty)
            else:
                withdraw_tx = binance_api.withdraw(base, base_addr, qty)
            print(withdraw_tx)
        for rel in accepted_coins:
            if rel != base:
                if rel == 'BCH':
                    rel_btc_price = binance_api.get_price('BCHABCBTC')
                elif rel == 'BTC':
                    rel_btc_price = 1
                else:
                    rel_btc_price = binance_api.get_price(rel+'BTC')
                trade_vol=bal*0.99
                for order in my_orders['result']['maker_orders']:
                    if base == my_orders['result']['maker_orders'][order]['base'] and rel == my_orders['result']['maker_orders'][order]['rel']:
                        started_swaps = my_orders['result']['maker_orders'][order]['started_swaps']
                        swaps_in_progress = len(started_swaps)
                        if swaps_in_progress > 0:
                            print(str(swaps_in_progress)+" x "+base+" to "+rel+" swaps in order!")
                            for swap_uuid in started_swaps:
                                swap_data = mm2lib.my_swap_status('http://127.0.0.1:7783', mm2lib.userpass, swap_uuid).json()
                                for event in swap_data['result']['events']:
                                    if event['event']['type'] == 'Finished':
                                        print(swap_uuid+" finished")
                                        swaps_in_progress -= 1;
                if swaps_in_progress == 0:
                    if base == 'BTC':
                        rel_price = 1
                    else:
                        base_price = base_btc_price['price']
                    if rel == 'BTC':
                        rel_price = 1
                    else:
                        rel_price = rel_btc_price['price']
                    pair_price = float(base_price)/float(rel_price)
                    resp = mm2lib.setprice('http://127.0.0.1:7783', mm2lib.userpass, base, rel, trade_vol, pair_price*mm2lib.trading_list[base]['premium']).json()
                    time.sleep(1)
    
    total_btc_val = mm2lib.orderbooks('http://127.0.0.1:7783', mm2lib.userpass, mm2lib.coins, coins_data)
    print("Combined Orderbook Value (BTC): "+str(total_btc_val))
    total_usd_val = total_btc_val * coins_data['BTC']['USD_price']
    total_aud_val = total_btc_val * coins_data['BTC']['AUD_price']
    print("Combined Orderbook Value (USD): $"+str(total_usd_val))
    print("Combined Orderbook Value (AUD): $"+str(total_aud_val))
    time.sleep(300)
    # TODO: Detect swaps in progress, and make sure to not cancel with new swap.