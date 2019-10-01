#!/usr/bin/env python3
import os
import sys
import json
import time
import requests
import subprocess
from os.path import expanduser
from . import coinslib, rpclib, binance_api

explorers = {
    "KMD":"https://www.kmdexplorer.io/tx",
}

def colorize(string, color):

        colors = {
                'black':'\033[30m',
                'red':'\033[31m',
                'green':'\033[32m',
                'orange':'\033[33m',
                'blue':'\033[34m',
                'purple':'\033[35m',
                'cyan':'\033[36m',
                'lightgrey':'\033[37m',
                'darkgrey':'\033[90m',
                'lightred':'\033[91m',
                'lightgreen':'\033[92m',
                'yellow':'\033[93m',
                'lightblue':'\033[94m',
                'pink':'\033[95m',
                'lightcyan':'\033[96m',
        }
        if color not in colors:
                return string
        else:
                return colors[color] + string + '\033[0m'

hl = colorize("|", 'lightblue')

def wait_continue(msg=''):
        return input(colorize(msg+"Press [Enter] to continue...", 'orange'))

def exit():
        while True:
                q = input(colorize("Stop Marketmaker 2? (y/n): ", 'orange'))
                if q == 'y' or q == 'Y':
                        stop_mm2()
                        sys.exit()
                elif q == 'n' or q == 'N':
                        sys.exit()
                else:
                        print(colorize("Invalid response, use [Y/y] or [N/n]...", 'red'))

## MM2 management
def start_mm2(logfile='mm2_output.log'):
        mm2_output = open(logfile,'w+')
        subprocess.Popen(["./mm2"], stdout=mm2_output, stderr=mm2_output, universal_newlines=True)
        msg = "Marketmaker 2 starting. Use 'tail -f "+logfile+"' for mm2 console messages. "
        time.sleep(1)
        wait_continue(msg)

def stop_mm2(node_ip, user_pass):
        params = {'userpass': user_pass, 'method': 'stop'}
        try:
                r = requests.post(node_ip, json=params)
                msg = "MM2 stopped. "
        except:
                msg = "MM2 was not running. "
        wait_continue(msg)

def activate_all(node_ip, user_pass):
    for coin in coinslib.coins:
        if coinslib.coins[coin]['activate_with'] == 'native':
            r = rpclib.enable(node_ip, user_pass, coin)
            print("Activating "+coin+" in native mode")
        else:
            r = rpclib.electrum(node_ip, user_pass, coin)
            print("Activating "+coin+" with electrum")

def validate_selection(interrogative, selection_list):
        while True:
                index = int(input(colorize(interrogative, 'orange')))-1
                try:
                        selected = selection_list[index]
                        return selected
                except:
                        print(colorize("Invalid selection, must be number between 1 and "+str(len(selection_list)), 'red'))
                        pass

def select_coin(interrogative, coin_list):
        i = 1
        row = ''
        for coin in coin_list:
                if i < 10:
                        row += '{:<14}'.format(" ["+str(i)+"] "+coin)
                else:
                        row += '{:<14}'.format("["+str(i)+"] "+coin)
                if len(row) > 64:
                        print(colorize(row, 'blue'))
                        row = ''
                i += 1
        selection = validate_selection(interrogative, coin_list)
        return selection


def show_orderbook_pair(node_ip, user_pass):
        coin_status = rpclib.check_coins_status(node_ip, user_pass)
        active_coins = coin_status[3]
        base = select_coin("Select coin to buy: ", active_coins)
        rel = select_coin("Select coin to sell: ", active_coins)
        orderbook = rpclib.orderbook(node_ip, user_pass, base, rel).json()
        pair_data = rpclib.build_coins_data([base,rel])
        pair_orderbook_table(node_ip, user_pass, orderbook, pair_data)

def pair_orderbook_table(node_ip, user_pass, orderbook, pair_data):
        total_btc_val = 0
        base = list(pair_data.keys())[0]
        rel = list(pair_data.keys())[1]
        try:
                balance_data = my_balance('http://127.0.0.1:7783', userpass, rel).json()
                addr = balance_data['address']
        except:
                addr = ''
                pass
        try:
                row = "-"*177
                print("    "+row)
                print(
                        "    |"+'{:^10}'.format('ORDER NUM')+hl+'{:^14}'.format('PAIR')+hl+'{:^18}'.format('VOLUME')+hl \
                        +'{:^18}'.format('PRICE (USD)')+hl+'{:^18}'.format('PRICE (AUD)')+hl \
                        +'{:^18}'.format('PRICE (BTC)')+hl+'{:^18}'.format('PRICE ('+rel+')')+hl \
                        +'{:^18}'.format('MM2 RATE')+hl+'{:^18}'.format('MARKET RATE')+hl \
                        +'{:^16}'.format('DIFFERENTIAL')+hl    \
                        )
                print("    "+row)
                try:
                        market_rate = pair_data[base]['BTC_price']/pair_data[rel]['BTC_price']
                except:
                        market_rate = 0
                pair = rel+"/"+base
                btc_price = pair_data[rel]['BTC_price']
                aud_price = pair_data[rel]['AUD_price']
                usd_price = pair_data[rel]['USD_price']
                if len(orderbook['bids']) > 0:
                        i = 1
                        for bid in orderbook['bids']:
                                if bid['address'] == addr:
                                        highlight = '\033[94m'
                                else:
                                        highlight = '\033[0m'
                                price = str(bid['price'])
                                volume = str(bid['maxvolume'])
                                if market_rate != 0:
                                        differential = float(market_rate)/float(price)-1
                                else:
                                        differential = 0
                                diff_pct = str(differential*100)[:5]+"%"
                                if differential < 0:
                                        differential = colorize('{:^16}'.format(str(diff_pct)[:8]), 'green')
                                elif differential > 0.07:
                                        differential = colorize('{:^16}'.format(str(diff_pct)[:8]), 'red')
                                else:
                                        differential = colorize('{:^16}'.format(str(diff_pct)[:8]), 'default')
                                rel_price = float(price)
                                print(highlight+"    |"+'{:^10}'.format("["+str(i)+"]")+hl+'{:^14}'.format(pair)+hl+'{:^18}'.format(volume[:14])+hl \
                                                     +'{:^18}'.format("$"+str(usd_price)[:14])+hl+'{:^18}'.format("$"+str(aud_price)[:14])+hl \
                                                     +'{:^18}'.format(str(btc_price)[:14])+hl+'{:^18}'.format(str(rel_price)[:14])+hl \
                                                     +'{:^18}'.format(str(price)[:14])+hl+'{:^18}'.format(str(market_rate)[:14])+hl \
                                                     +str(differential)+"\033[0m"+hl \
                                                     )
                                i += 1
                                print("    "+row)
                        while True:
                                bal = rpclib.my_balance(node_ip, user_pass, rel).json()['balance']
                                print(colorize("Your "+rel+" balance: "+str(bal), 'green'))
                                q = input(colorize("Select an order number to start a trade, [C]reate one manually, or [E]xit to menu: ", 'orange'))
                                if q == 'e' or q == 'E':
                                        break
                                elif q == 'c' or q == 'C':
                                        while True:
                                                outcome = create_buy(node_ip, user_pass, base, rel)
                                                if outcome == 'back to menu':
                                                        break
                                        break
                                else:
                                        try:
                                                selected = orderbook['bids'][int(q)-1]
                                                while True:
                                                        try:
                                                                buy_num = float(input(colorize("How many "+base+" to buy at "+selected['price'][:6]+"? (max. "+str(selected['maxvolume'])[:6]+"): ", 'orange')))
                                                                if buy_num > selected['maxvolume']:
                                                                        print(colorize("Can't buy more than max volume! Try again..." , 'red'))
                                                                else:
                                                                        while True:
                                                                                q = input(colorize("Confirm buy order, "+str(buy_num)+" "+base+" for "+str(float(price)*buy_num)+" "+rel+" (y/n): ",'orange'))
                                                                                if q == 'Y' or q == 'y':
                                                                                        resp = rpclib.buy(node_ip, user_pass, base, rel, buy_num, price).json()
                                                                                        if 'error' not in resp:
                                                                                                print(colorize("Order submitted!", 'green'))
                                                                                        else:
                                                                                                print(resp)
                                                                                        wait_continue()
                                                                                        return 'back to menu'
                                                                                elif q == 'N' or q == 'n':
                                                                                        return 'back to menu'
                                                                                else:
                                                                                        print(colorize("Invalid selection, must be [Y/y] or [N/n]. Try again...", 'red'))
                                                        except Exception as e:
                                                                print(e)
                                                                pass
                                                break
                                        except:
                                                print(colorize("Invalid selection, must be [E/e] or a number between 1 and "+str(len(orderbook['bids'])), 'red'))
                                                pass
                else:
                        print("    |"+'{:^10}'.format("[*]")+hl+'{:^14}'.format(pair)+hl+'{:^18}'.format(0)+hl \
                                             +'{:^18}'.format("$"+str(usd_price)[:14])+hl+'{:^18}'.format("$"+str(aud_price)[:14])+hl \
                                             +'{:^18}'.format(str(btc_price)[:14])+hl+'{:^18}'.format(str(market_rate)[:14])+hl \
                                             +'{:^18}'.format(str('-')[:14])+hl+'{:^18}'.format(str(market_rate)[:14])+hl \
                                             +'{:^18}'.format(str('-')+"\033[0m")+"    |" \
                                             )
                        print("    "+row)
                        q = input(colorize("No orders in orderbook for "+base+"/"+rel+"! Create one manually? (y/n): ", 'red'))
                        while True:
                                if q == 'N' or q == 'n':
                                        break
                                if q == 'Y' or q == 'y':
                                        while True:
                                                outcome = create_buy(node_ip, user_pass, base, rel)
                                                if outcome == 'back to menu':
                                                        break
                                        break
        except Exception as e:
                print("Orderbooks error: "+str(e))
                pass

def create_buy(node_ip, user_pass, base, rel):
        try:
                rel_bal = rpclib.my_balance(node_ip, user_pass, rel).json()['balance']
                rel_price = float(input(colorize("What "+rel+" price?: ", 'orange')))
                max_vol = float(rel_bal)/rel_price
                buy_num = float(input(colorize("How many "+base+" to buy? (max. "+'{:^6}'.format(str(max_vol))+"): ", 'orange')))
                if buy_num > max_vol:
                        print(colorize("Can't buy more than max volume! Try again..." , 'red'))
                else:
                        while True:
                                q = input(colorize("Confirm setprice order, "+str(buy_num)+" "+base+" for "+str(float(rel_price)*buy_num)+" "+rel+" (y/n): ",'orange'))
                                if q == 'Y' or q == 'y':
                                        resp = rpclib.buy(node_ip, user_pass, base, rel, buy_num, rel_price).json()
                                        if 'error' in resp:
                                                print(colorize("Setprice Error: "+str(resp), 'red'))
                                        else:
                                                print(colorize("Order submitted!", 'green'))
                                        wait_continue()
                                        return 'back to menu'
                                elif q == 'N' or q == 'n':
                                        return 'back to menu'
                                else:
                                        print(colorize("Invalid selection, must be [Y/y] or [N/n]. Try again...", 'red'))
        except Exception as e:
                print("Create setprice error: "+str(e))
                wait_continue()
                return 'back to menu'


def my_orders_table(node_ip, user_pass, my_orders):
        if len(my_orders['maker_orders']) + len(my_orders['maker_orders']) == 0:
                print(colorize("You have no pending orders!", 'red'))
                wait_continue()
                return 'back to menu'
        coins_data = rpclib.build_coins_data()
        total_btc_val = 0
        my_order_list = []
        try:
                row = colorize("-"*174, 'blue')
                print("    "+row)
                print(
                        "    |"+'{:^11}'.format("ORDER NUM")+hl+'{:^14}'.format('ORDER TYPE')+hl \
                        +'{:^14}'.format('PAIR')+hl+'{:^18}'.format('VOLUME')+hl \
                        +'{:^18}'.format('PRICE (USD)')+hl+'{:^18}'.format('PRICE (AUD)')+hl \
                        +'{:^18}'.format('PRICE (BTC)')+hl+'{:^18}'.format('MY PRICE')+hl \
                        +'{:^18}'.format('MARKET RATE')+hl \
                        +'{:^16}'.format('DIFFERENTIAL')+hl    \
                        )
                print("    "+row)
                i = 1
                for order in my_orders['maker_orders']:
                        my_order_list.append(my_orders['maker_orders'][order])
                        order_type = "MAKER"
                        base = my_orders['maker_orders'][order]['base']
                        rel = my_orders['maker_orders'][order]['rel']
                        price = my_orders['maker_orders'][order]['price']
                        volume = my_orders['maker_orders'][order]['available_amount']
                        try:
                                market_rate = coins_data[base]['BTC_price']/coins_data[rel]['BTC_price']
                        except:
                                market_rate = 0
                        pair = rel+"/"+base
                        btc_price = coins_data[rel]['BTC_price']
                        aud_price = coins_data[rel]['AUD_price']
                        usd_price = coins_data[rel]['USD_price']
                        if market_rate != 0:
                                differential = float(price)/float(market_rate)-1
                        else:
                                differential = 0
                        diff_pct = str(differential*100)[:5]+"%"
                        if differential < 0:
                                differential = colorize('{:^16}'.format(str(diff_pct)[:8]), 'green')
                        elif differential > 0.07:
                                differential = colorize('{:^16}'.format(str(diff_pct)[:8]), 'red')
                        else:
                                differential = colorize('{:^16}'.format(str(diff_pct)[:8]), 'default')
                        rel_price = float(price)
                        print(colorize("    "+hl+'{:^11}'.format("["+str(i)+"]")+hl+'{:^14}'.format(order_type)+hl \
                                             +'{:^14}'.format(pair)+hl+'{:^18}'.format(volume[:14])+hl \
                                             +'{:^18}'.format("$"+str(usd_price)[:14])+hl+'{:^18}'.format("$"+str(aud_price)[:14])+hl \
                                             +'{:^18}'.format(str(btc_price)[:14])+hl+'{:^18}'.format(str(rel_price)[:14])+hl \
                                             +'{:^18}'.format(str(market_rate)[:14])+hl \
                                             +str(differential)+hl, 'blue') \
                                 )
                        i += 1
                        print("    "+row)
                for order in my_orders['taker_orders']:
                        my_order_list.append(my_orders['taker_orders'][order])
                        order_type = "TAKER"
                        base = my_orders['taker_orders'][order]['request']['base']
                        rel = my_orders['taker_orders'][order]['request']['rel']
                        base_amount = my_orders['taker_orders'][order]['request']['base_amount']
                        rel_amount = my_orders['taker_orders'][order]['request']['rel_amount']
                        price = float(rel_amount)/float(base_amount)
                        volume = base_amount
                        try:
                            market_rate = coins_data[base]['BTC_price']/coins_data[rel]['BTC_price']
                        except:
                            market_rate = 0
                        pair = rel+"/"+base
                        btc_price = coins_data[rel]['BTC_price']
                        aud_price = coins_data[rel]['AUD_price']
                        usd_price = coins_data[rel]['USD_price']
                        if market_rate != 0:
                            differential = float(market_rate)/float(price)-1
                        else:
                            differential = 0
                        diff_pct = str(differential*100)[:5]+"%"
                        if differential < 0:
                            differential = colorize('{:^16}'.format(str(diff_pct)[:8]), 'green')
                        elif differential > 0.07:
                            differential = colorize('{:^16}'.format(str(diff_pct)[:8]), 'red')
                        else:
                            differential = colorize('{:^16}'.format(str(diff_pct)[:8]), 'default')
                        rel_price = float(price)
                        print(colorize("    "+hl+'{:^11}'.format("["+str(i)+"]")+hl+'{:^14}'.format(order_type)+hl \
                                             +'{:^14}'.format(pair)+hl+'{:^18}'.format(volume[:14])+hl \
                                             +'{:^18}'.format("$"+str(usd_price)[:14])+hl+'{:^18}'.format("$"+str(aud_price)[:14])+hl \
                                             +'{:^18}'.format(str(btc_price)[:14])+hl+'{:^18}'.format(str(rel_price)[:14])+hl \
                                             +'{:^18}'.format(str(market_rate)[:14])+hl \
                                             +str(differential)+hl, 'blue') \
                                 )
                        i += 1
                        print("    "+row)
                while True:
                        q = input(colorize("Select an order number to cancel a trade, Cancel [A]ll trades, or [E]xit to menu: ", 'orange'))
                        if q == 'e' or q == 'E':
                                break
                        elif q == 'a' or q == 'A':
                                resp = rpclib.cancel_all(node_ip, user_pass).json()
                                print(colorize("All orders cancelled!","orange"))
                                break
                        else:
                                try:
                                        selected = my_order_list[int(q)-1]
                                        base = selected['base']
                                        rel = selected['rel']
                                        resp = rpclib.cancel_pair(node_ip, user_pass, base, rel).json()
                                        print(colorize("Order #"+q+" ("+base+"/"+rel+") cancelled!","orange"))
                                        break
                                except:
                                        print(colorize("Invalid selection, must be [E/e] or a number between 1 and "+str(len(orderbook['bids'])), 'red'))
                                        pass

                                
        except Exception as e:
                print("Orders error: "+str(e))
                pass        
        wait_continue()

def show_orders(node_ip, user_pass):
        resp = rpclib.my_orders(node_ip, user_pass).json()
        my_orders_table(node_ip, user_pass, resp['result'])

def show_balances_table(node_ip, user_pass):
        coin_status = rpclib.check_coins_status(node_ip, user_pass)
        coin_data = rpclib.build_coins_data(coinslib.coins)
        active_coins = coin_status[3]
        if len(active_coins) == 0:
                msg = colorize("No coins activated!", 'red')
                wait_continue()
        trading_coins = coin_status[4]
        btc_total = 0
        usd_total = 0
        aud_total = 0
        header = hl+'{:^7}'.format('COIN')+hl+'{:^50}'.format('ADDRESS (green = bot trading)')+hl \
                            +'{:^11}'.format('BALANCE')+hl+'{:^11}'.format('BTC PRICE')+hl \
                            +'{:^11}'.format('BTC VALUE')+hl+'{:^11}'.format('USD PRICE')+hl \
                            +'{:^11}'.format('USD VALUE')+hl+'{:^11}'.format('AUD PRICE')+hl \
                            +'{:^11}'.format('AUD VALUE')+hl
        table_dash = "-"*144
        print(colorize(" "+table_dash, 'lightblue'))
        print(colorize(" "+header, 'lightblue'))
        print(colorize(" "+table_dash, 'lightblue'))
        for coin in coin_data:
                if coin in active_coins:
                        try:
                                balance_data = rpclib.my_balance(node_ip, user_pass, coin).json()
                                addr = balance_data['address']
                                bal = float(balance_data['balance'])
                        except:
                                addr = "RPC timed out!"
                                bal = 0
                                pass
                        btc_price = coin_data[coin]['BTC_price']
                        btc_val = btc_price*bal
                        btc_total += btc_val
                        usd_price = coin_data[coin]['USD_price']
                        usd_val = usd_price*bal
                        usd_total += usd_val
                        aud_price = coin_data[coin]['AUD_price']
                        aud_val = aud_price*bal
                        aud_total += aud_val
                        if coin not in trading_coins:
                                row = hl+'{:^7}'.format(coin)+hl+'{:^50}'.format(addr)+hl \
                                                             +'{:^11}'.format(str(bal)[:9])+hl \
                                                             +'{:^11}'.format(str(btc_price)[:9])+hl+'{:^11}'.format(str(btc_val)[:9])+hl \
                                                             +'{:^11}'.format(str(usd_price)[:9])+hl+'{:^11}'.format(str(usd_val)[:9])+hl \
                                                             +'{:^11}'.format(str(aud_price)[:9])+hl+'{:^11}'.format(str(aud_val)[:9])+hl
                                print(colorize(" "+row, 'lightblue'))
                        else:
                                row = hl+colorize('{:^7}'.format(coin),'green')+hl+colorize('{:^50}'.format(addr),'green')+hl \
                                                             +colorize('{:^11}'.format(str(bal)[:9]),'green')+hl \
                                                             +colorize('{:^11}'.format(str(btc_price)[:9]),'green')+hl+colorize('{:^11}'.format(str(btc_val)[:9]),'green')+hl\
                                                             +colorize('{:^11}'.format(str(usd_price)[:9]),'green')+hl+colorize('{:^11}'.format(str(usd_val)[:9]),'green')+hl\
                                                             +colorize('{:^11}'.format(str(aud_price)[:9]),'green')+hl+colorize('{:^11}'.format(str(aud_val)[:9]),'green')+hl
                                print(colorize(" "+row, 'lightblue'))
        print(colorize(" "+table_dash, 'lightblue')) 
        row = hl+'{:^70}'.format(' ')+hl \
                     +'{:^11}'.format('TOTAL BTC')+hl+'{:^11}'.format(str(btc_total)[:9])+hl \
                     +'{:^11}'.format('TOTAL USD')+hl+'{:^11}'.format(str(usd_total)[:9])+hl \
                     +'{:^11}'.format('TOTAL AUD')+hl+'{:^11}'.format(str(aud_total)[:9])+hl
        print(colorize(" "+row, 'lightblue'))
        print(colorize(" "+table_dash+"\n\n", 'lightblue'))
        while True:
                outcome = withdraw_tui(node_ip, user_pass, active_coins)
                if outcome == 'back to menu':
                        break

def withdraw_tui(node_ip, user_pass, active_coins):
                q = input(colorize("[W]ithdraw funds, or [E]xit to menu: ", 'orange'))
                if q == 'e' or q == 'E':
                        return 'back to menu'
                elif q == 'w' or q == 'W':
                        while True:
                                cointag = select_coin("Select coin to withdraw funds: ", active_coins)
                                address = input(colorize("Enter destination "+cointag+" address: ",'orange'))
                                amount = input(colorize("Enter amount to send: ",'orange'))
                                resp = rpclib.withdraw(node_ip, user_pass, cointag, address, amount).json()
                                if 'error' in resp:
                                        if resp['error'].find("Invalid Address") > 0:
                                                print(colorize("Invalid address! Try again...", 'red'))
                                        elif resp['error'].find("Not sufficient balance") > 0:
                                                print(colorize("Insufficient balance! Try again...", 'red'))
                                        else:
                                                print(colorize("Error: "+str(resp['error']), 'red'))
                                else:
                                        txid = rpclib.send_raw_transaction(node_ip, user_pass, cointag, resp['tx_hex']).json()
                                        if 'tx_hash' in txid:
                                                print(colorize("Withdrawl successful! TXID: ["+txid['tx_hash']+"]", 'green'))
                                                try:
                                                    print(colorize("Track transaction status at ["+coinslib.coins[cointag]['tx_explorer']+"/"+txid['tx_hash']+"]", 'cyan'))
                                                except:
                                                    print(colorize("Track transaction status at ["+txid['tx_hash']+"]", 'cyan'))
                                                    pass
                                                break
                                        else:
                                                print(colorize("Error: "+str(txid), 'red'))
                                                break
                else:
                        print(colorize("Invalid selection, must be [E/e] or [W/w]! Try again...", 'red'))
                        return 'try again'

def show_recent_swaps(node_ip, user_pass, swapcount=50):
    coins_data = rpclib.build_coins_data()
    header_list = []
    swap_json = []
    error_events = ['StartFailed', 'NegotiateFailed', 'TakerFeeValidateFailed',
                                    'MakerPaymentTransactionFailed', 'MakerPaymentDataSendFailed',
                                    'TakerPaymentValidateFailed', 'TakerPaymentSpendFailed', 
                                    'MakerPaymentRefunded', 'MakerPaymentRefundFailed']
    swap_status = "Success" 
    recent_swaps = rpclib.my_recent_swaps(node_ip, user_pass, swapcount).json()
    swap_list = recent_swaps['result']['swaps']
    for swap in swap_list:
        swap_data = swap['events'][0]
        maker_coin = swap_data['event']['data']['maker_coin']
        maker_amount = swap_data['event']['data']['maker_amount']
        taker_coin = swap_data['event']['data']['taker_coin']
        taker_amount = swap_data['event']['data']['taker_amount']
        timestamp = int(int(swap_data['timestamp'])/1000)
        human_time = time.ctime(timestamp)
        if maker_coin not in header_list:
            header_list.append(maker_coin)
        if taker_coin not in header_list:
            header_list.append(taker_coin)
        rate = float(maker_amount)/float(taker_amount)
        swap_str = str(maker_amount)+" "+maker_coin+" for "+str(taker_amount)+" "+taker_coin+" ("+str(rate)+")"
        for event in swap['events']:
            if event['event']['type'] in error_events:
                swap_status = "Failed ("+event['event']['type']+")"
                break
            else:
                swap_status = "Success ("+event['event']['type']+")"
        swap_json.append({"result":swap_status,
                                        "time":human_time,
                                        "maker_coin":maker_coin,
                                        "maker_amount":maker_amount,
                                        "taker_coin":taker_coin,
                                        "taker_amount":taker_amount
                    })
    delta = {}
    header = "|"+'{:^26}'.format("TIME")+"|"+'{:^36}'.format("RESULT")+"|"
    for coin in header_list:
        header += '{:^14}'.format(coin)+"|"
        delta[coin] = 0
    table_dash = "-"*len(header)
    print(" "+table_dash)
    print(" "+header)
    print(" "+table_dash)
    for swap in swap_json:
        row_str = "|"+'{:^26}'.format(swap['time'])+"|"
        row_str += '{:^36}'.format(swap['result'])+"|"
        for coin in header_list:
            if coin == swap['maker_coin']:
                row_str += '\033[91m'+'{:^14}'.format(swap['maker_amount'][:12])+'\033[0m'+"|"
                delta[coin] -= float(swap['maker_amount'])
            elif coin == swap['taker_coin']:
                row_str += '\033[92m'+'{:^14}'.format(swap['taker_amount'][:12])+'\033[0m'+"|"
                delta[coin] += float(swap['taker_amount'])
            else:
                row_str += '{:^14}'.format('-')+"|"
        print(" "+row_str)
    delta_row = "|"+'{:^63}'.format("TOTAL")+"|"
    btc_row = "|"+'{:^63}'.format("BTC")+"|"
    usd_row = "|"+'{:^63}'.format("USD")+"|"
    aud_row = "|"+'{:^63}'.format("AUD")+"|"
    table_dash = "-"*(len(delta_row)+(len(header_list)+1)*15)
    btc_sum = 0
    usd_sum = 0
    aud_sum = 0
    for delta_coin in delta:
        for header_coin in header_list:
            if delta_coin == header_coin:
                if float(delta[header_coin]) > 0:
                    highlight = '\033[92m'
                else:
                    highlight = '\033[91m'
                btc_price = coins_data[header_coin]['BTC_price']*delta[header_coin]
                usd_price = coins_data[header_coin]['USD_price']*delta[header_coin]
                aud_price = coins_data[header_coin]['AUD_price']*delta[header_coin]
                btc_sum += btc_price
                usd_sum += usd_price
                aud_sum += aud_price
                delta_row += highlight+'{:^14}'.format(str(delta[header_coin])[:12])+'\033[0m'+"|"
                btc_row += highlight+'{:^14}'.format(str(btc_price)[:12])+'\033[0m'+"|"
                usd_row += highlight+'{:^14}'.format("$"+str(usd_price)[:10])+'\033[0m'+"|"
                aud_row += highlight+'{:^14}'.format("$"+str(aud_price)[:10])+'\033[0m'+"|"
    delta_row += '{:^14}'.format("TOTAL")+"|"
    btc_row += '{:^14}'.format(str(btc_sum)[:12])+"|"
    usd_row += '{:^14}'.format("$"+str(usd_sum)[:10])+"|"
    aud_row += '{:^14}'.format("$"+str(aud_sum)[:10])+"|"

    print(" "+table_dash)
    print(" "+delta_row)
    print(" "+table_dash)
    print(" "+btc_row)
    print(" "+table_dash)
    print(" "+usd_row)
    print(" "+table_dash)
    print(" "+aud_row)
    print(" "+table_dash)
    #calculate in / out value
    wait_continue()

def recover_swap(node_ip, user_pass):
    uuid = input(colorize("Enter stuck swap UUID: ", 'orange'))
    print(uuid)
    resp = rpclib.recover_stuck_swap(node_ip, user_pass, uuid).json()
    print(resp)
    wait_continue()

def show_failed_swaps(node_ip, user_pass, swapcount=50):
    header_list = []
    swap_json = []
    failed_swaps = []
    error_events = ['StartFailed', 'NegotiateFailed', 'TakerFeeValidateFailed',
                                    'MakerPaymentTransactionFailed', 'MakerPaymentDataSendFailed',
                                    'TakerPaymentValidateFailed', 'TakerPaymentSpendFailed', 
                                    'MakerPaymentRefundFailed']
    recent_swaps = rpclib.my_recent_swaps(node_ip, user_pass, swapcount).json()
    swap_list = recent_swaps['result']['swaps']
    for swap in swap_list:
        for event in swap['events']:
            if event['event']['type'] in error_events:
                failed_swaps.append(swap)
                break
    failed_swaps_summary = {}
    for swap in failed_swaps:
        timestamps_list = []
        errors_list = []
        failed_swap_json = {}
        swap_type = swap['type']
        uuid = swap['uuid']
        failed_swap_json.update({'swap_type':swap_type})
        failed_swap_json.update({'uuid':uuid})
        for event in swap['events']:
            event_type = event['event']['type']
            event_timestamp = event['timestamp']
            timestamps_list.append({event_type:event_timestamp})
            if event['event']['type'] in error_events:
                error = str(event['event']['data'])
                errors_list.append({event_type:error})
            if event['event']['type'] == 'Started':
                failed_swap_json.update({'lock_duration':event['event']['data']['lock_duration']})
                failed_swap_json.update({'taker_coin':event['event']['data']['taker_coin']})
                failed_swap_json.update({'taker_pub':event['event']['data']['taker']})
                failed_swap_json.update({'maker_coin':event['event']['data']['maker_coin']})
                failed_swap_json.update({'maker_pub':event['event']['data']['my_persistent_pub']})
            if 'data' in event['event']:
                if 'maker_payment_locktime' in event['event']['data']:
                    failed_swap_json.update({'maker_locktime':event['event']['data']['maker_payment_locktime']})
                if 'taker_payment_locktime' in event['event']['data']:
                    failed_swap_json.update({'taker_locktime':event['event']['data']['taker_payment_locktime']})
            if event['event']['type'] == 'Finished':
                failed_swap_json.update({'timestamps_list':timestamps_list})
                failed_swap_json.update({'errors':errors_list})
                failed_swaps_summary[uuid] = failed_swap_json

    header = hl+'{:^7}'.format('NUM')+hl+'{:^40}'.format('UUID')+hl+'{:^7}'.format('TYPE')+hl \
                        +'{:^25}'.format('FAIL EVENT')+hl+'{:^23}'.format('ERROR')+hl \
                        +'{:^7}'.format('TAKER')+hl+'{:^7}'.format('MAKER')+hl \
                        +'{:^66}'.format('TAKER PUB')+hl
    table_dash = "-"*191
    print(colorize(" "+table_dash, 'lightblue'))
    print(colorize(" "+header, 'lightblue'))
    print(colorize(" "+table_dash, 'lightblue'))
    i = 1
    for uuid in failed_swaps_summary:
        swap_summary = failed_swaps_summary[uuid]
        for error in swap_summary['errors']:
            #swap_time = swap_summary['timestamps_list'][0][1]-swap_summary['timestamps_list'][0][0]
            start_time = list(swap_summary['timestamps_list'][0].values())[0]
            end_time = list(swap_summary['timestamps_list'][-1].values())[0]
            swap_time = ((end_time - start_time)/1000)/60
            taker_pub = swap_summary['taker_pub']
            taker_coin = swap_summary['taker_coin']
            maker_coin = swap_summary['maker_coin']
            if str(error).find('overwinter') > 0:
                error_type = "tx-overwinter-active"
            elif str(error).find('timeout') > 0:
                error_type = "timeout"
            else:
                error_type = "other"
            row = hl+'{:^7}'.format("["+str(i)+"]")+hl+'{:^40}'.format(uuid)+hl+'{:^7}'.format(str(swap_type))+hl \
                        +'{:^25}'.format(str(list(error.keys())[0]))+hl+'{:^23}'.format(error_type)+hl \
                        +'{:^7}'.format(taker_coin)+hl+'{:^7}'.format(maker_coin)+hl \
                        +'{:^66}'.format(taker_pub)+hl
            print(colorize(" "+row, 'lightblue'))
            print(colorize(" "+table_dash, 'lightblue'))
            #print(error)
        i += 1
    while True:
        q = input(colorize("Enter a swap number to view events log, or [E]xit to menu: ", 'orange'))
        if q == 'e' or q == 'E':
            return 'back to menu'
        else:        
            try:
                swap = failed_swaps[int(q)-1]
                for event in swap['events']:
                    print(colorize("["+event['event']['type']+"]", 'green'))
                    if event['event']['type'] in error_events:
                        print(colorize(str(event), 'red'))
                    else:
                        print(colorize(str(event), 'blue'))
            except Exception as e:
                print(colorize("Invalid selection, must be [E/e] or a number between 1 and "+str(len(failed_swaps)), 'red'))
                pass

    wait_continue()