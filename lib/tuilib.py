#!/usr/bin/env python3
import os
import sys
import json
import time
import requests
import subprocess
from os.path import expanduser
from . import coinslib, rpclib, binance_api

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
        print("  "+row)
        print(
            "  |"+'{:^10}'.format('ORDER NUM')+"|"+'{:^14}'.format('PAIR')+"|"+'{:^18}'.format('VOLUME')+"|" \
            +'{:^18}'.format('PRICE (USD)')+"|"'{:^18}'.format('PRICE (AUD)')+"|" \
            +'{:^18}'.format('PRICE (BTC)')+"|"'{:^18}'.format('PRICE ('+rel+')')+"|" \
            +'{:^18}'.format('MM2 RATE')+"|"+'{:^18}'.format('MARKET RATE')+"|" \
            +'{:^16}'.format('DIFFERENTIAL')+"|"  \
            )
        print("  "+row)
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
                print(highlight+"  |"+'{:^10}'.format("["+str(i)+"]")+"|"+'{:^14}'.format(pair)+"|"+'{:^18}'.format(volume[:14])+"|" \
                           +'{:^18}'.format("$"+str(usd_price)[:14])+"|"+'{:^18}'.format("$"+str(aud_price)[:14])+"|" \
                           +'{:^18}'.format(str(btc_price)[:14])+"|"+'{:^18}'.format(str(rel_price)[:14])+"|" \
                           +'{:^18}'.format(str(price)[:14])+"|"+'{:^18}'.format(str(market_rate)[:14])+"|" \
                           +str(differential)+"\033[0m"+"|" \
                           )
                i += 1
                print("  "+row)
            while True:
                bal = rpclib.my_balance(node_ip, user_pass, rel).json()['balance']
                print(colorize("Your "+rel+" balance: "+str(bal), 'green'))
                q = input(colorize("Select an order number to start a trade, or [E]xit to menu: ", 'orange'))
                if q == 'e' or q == 'E':
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
                                            print(resp)
                                            print(colorize("Order submitted!", 'green'))
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
            print("  |"+'{:^10}'.format("[*]")+"|"+'{:^14}'.format(pair)+"|"+'{:^18}'.format(0)+"|" \
                       +'{:^18}'.format("$"+str(usd_price)[:14])+"|"+'{:^18}'.format("$"+str(aud_price)[:14])+"|" \
                       +'{:^18}'.format(str(btc_price)[:14])+"|"+'{:^18}'.format(str(market_rate)[:14])+"|" \
                       +'{:^18}'.format(str('-')[:14])+"|"+'{:^18}'.format(str(market_rate)[:14])+"|" \
                       +'{:^18}'.format(str('-')+"\033[0m")+"  |" \
                       )
            print("  "+row)
            q = input(colorize("No orders in orderbook for "+base+"/"+rel+"! Create one manually? (y/n): ", 'red'))
            while True:
                if q == 'N' or q == 'n':
                    break
                if q == 'Y' or q == 'y':
                    try:
                        base_bal = rpclib.my_balance(node_ip, user_pass, base).json()['balance']
                        print(colorize("Available "+rel+" balance: "+str(base_bal), 'green'))
                        base_price = float(input(colorize("What "+base+" price?: ", 'orange')))
                        max_vol = float(base_bal)/base_price
                        buy_num = float(input(colorize("How many "+rel+" to buy? (max. "+'{:^6}'.format(str(max_vol))+": ", 'orange')))
                        if buy_num > max_vol:
                            print(colorize("Can't buy more than max volume! Try again..." , 'red'))
                        else:
                            while True:
                                q = input(colorize("Confirm setprice order, "+str(buy_num)+" "+rel+" for "+str(float(base_price)*buy_num)+" "+base+" (y/n): ",'orange'))
                                if q == 'Y' or q == 'y':
                                    resp = rpclib.setprice(node_ip, user_pass, base, rel, buy_num, base_price).json()
                                    print(resp)
                                    print(colorize("Order submitted!", 'green'))
                                    wait_continue()
                                    return 'back to menu'
                                elif q == 'N' or q == 'n':
                                    return 'back to menu'
                                else:
                                    print(colorize("Invalid selection, must be [Y/y] or [N/n]. Try again...", 'red'))
                    except Exception as e:
                        print(e)
                        pass
    except Exception as e:
        print("Orderbooks error: "+str(e))
        pass    
    wait_continue()

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
        print("  "+row)
        print(
            "  |"+'{:^11}'.format("ORDER NUM")+"|"+'{:^14}'.format('ORDER TYPE')+"|" \
            +'{:^14}'.format('PAIR')+"|"+'{:^18}'.format('VOLUME')+"|" \
            +'{:^18}'.format('PRICE (USD)')+"|"'{:^18}'.format('PRICE (AUD)')+"|" \
            +'{:^18}'.format('PRICE (BTC)')+"|"'{:^18}'.format('MY PRICE')+"|" \
            +'{:^18}'.format('MARKET RATE')+"|" \
            +'{:^16}'.format('DIFFERENTIAL')+"|"  \
            )
        print("  "+row)
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
            print(colorize("  |"+'{:^11}'.format("["+str(i)+"]")+"|"+'{:^14}'.format(order_type)+"|" \
                       +'{:^14}'.format(pair)+"|"+'{:^18}'.format(volume[:14])+"|" \
                       +'{:^18}'.format("$"+str(usd_price)[:14])+"|"+'{:^18}'.format("$"+str(aud_price)[:14])+"|" \
                       +'{:^18}'.format(str(btc_price)[:14])+"|"+'{:^18}'.format(str(rel_price)[:14])+"|" \
                       +'{:^18}'.format(str(market_rate)[:14])+"|" \
                       +str(differential)+"|", 'blue') \
                 )
            i += 1
            print("  "+row)
        for order in my_orders['taker_orders']:
            my_order_list.append(my_orders['taker_orders'][order])
            order_type = "TAKER"
            base = my_orders['taker_orders'][order]['base']
            rel = my_orders['taker_orders'][order]['rel']
            price = my_orders['taker_orders'][order]['price']
            volume = my_orders['taker_orders'][order]['available_amount']
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
            print("  |"+'{:^10}'.format("["+str(i)+"]")+"|"+'{:^14}'.format(order_type)+"|" \
                       +'{:^14}'.format(pair)+"|"+'{:^18}'.format(volume[:14])+"|" \
                       +'{:^18}'.format("$"+str(usd_price)[:14])+"|"+'{:^18}'.format("$"+str(aud_price)[:14])+"|" \
                       +'{:^18}'.format(str(btc_price)[:14])+"|"+'{:^18}'.format(str(rel_price)[:14])+"|" \
                       +"|"+'{:^18}'.format(str(market_rate)[:14])+"|" \
                       +str(differential)+"|" \
                 )
            i += 1
            print("  "+row)
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
    header = "|"+'{:^7}'.format('COIN')+"|"+'{:^50}'.format('ADDRESS')+"|" \
              +'{:^11}'.format('BALANCE')+"|"+'{:^11}'.format('BTC PRICE')+"|" \
              +'{:^11}'.format('BTC VALUE')+"|"+'{:^11}'.format('USD PRICE')+"|" \
              +'{:^11}'.format('USD VALUE')+"|"+'{:^11}'.format('AUD PRICE')+"|" \
              +'{:^11}'.format('AUD VALUE')+"|"
    table_dash = "-"*len(header)
    print(" "+table_dash)  
    print(" "+header)
    print(" "+table_dash)  
    for coin in coin_data:
        if coin in active_coins:
            balance_data = rpclib.my_balance(node_ip, user_pass, coin).json()
            coin = balance_data['coin']
            addr = balance_data['address']
            bal = float(balance_data['balance'])
            btc_price = coin_data[coin]['BTC_price']
            btc_val = btc_price*bal
            btc_total += btc_val
            usd_price = coin_data[coin]['USD_price']
            usd_val = usd_price*bal
            usd_total += usd_val
            aud_price = coin_data[coin]['AUD_price']
            aud_val = aud_price*bal
            aud_total += aud_val
            if coin in trading_coins:
                highlight = '\033[94m'
            else:
                highlight = '\033[0m'      
            row = highlight+"|"+'{:^7}'.format(coin)+"|"+'{:^50}'.format(addr)+"|" \
                           +'{:^11}'.format(str(bal)[:9])+"|" \
                           +'{:^11}'.format(str(btc_price)[:9])+"|"+'{:^11}'.format(str(btc_val)[:9])+"|"\
                           +'{:^11}'.format(str(usd_price)[:9])+"|"+'{:^11}'.format(str(usd_val)[:9])+"|"\
                           +'{:^11}'.format(str(aud_price)[:9])+"|"+'{:^11}'.format(str(aud_val)[:9])+"|"
            print(" "+row)
    print(" "+table_dash)  
    row = "|"+'{:^70}'.format(' ')+"|" \
           +'{:^11}'.format('TOTAL BTC')+"|"+'{:^11}'.format(str(btc_total)[:9])+"|"\
           +'{:^11}'.format('TOTAL USD')+"|"+'{:^11}'.format(str(usd_total)[:9])+"|"\
           +'{:^11}'.format('TOTAL AUD')+"|"+'{:^11}'.format(str(aud_total)[:9])+"|"
    print(" "+row)
    print(" "+table_dash+"\n\n")
    wait_continue()