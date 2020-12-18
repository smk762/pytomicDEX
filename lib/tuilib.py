#!/usr/bin/env python3
import os
import sys
import json
import time
import requests
import subprocess
from os.path import expanduser
from . import coinslib, rpclib, binance_api
from decimal import Decimal, ROUND_DOWN

import bitcoin
from bitcoin.wallet import P2PKHBitcoinAddress
from bitcoin.core import x
from bitcoin.core import CoreMainParams

class CoinParams(CoreMainParams):
    MESSAGE_START = b'\x24\xe9\x27\x64'
    DEFAULT_PORT = 7770
    BASE58_PREFIXES = {'PUBKEY_ADDR': 60,
                       'SCRIPT_ADDR': 85,
                       'SECRET_KEY': 188}
bitcoin.params = CoinParams

def get_radd_from_pub(pub):
    try:
        taker_addr = str(P2PKHBitcoinAddress.from_pubkey(x("02"+pub)))
    except:
        taker_addr = pub
    return str(taker_addr)

cwd = os.getcwd()
script_path = sys.path[0]
home = expanduser("~")

ignored_addresses = ['RDbAXLCmQ2EN7daEZZp7CC9xzkcN8DfAZd', '']

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
                return str(string)
        else:
                return colors[color] + str(string) + '\033[0m'

hl = colorize("|", 'lightblue')

def wait_continue(msg=''):
    input(colorize(msg+"Press [Enter] to continue...", 'orange'))

def create_MM2_json():
    data = {}
    rpc_pass = input(colorize("Enter an RPC password: ", 'orange'))
    netid = input(colorize("Enter a NET ID (default = 9999): ", 'orange'))
    userhome = expanduser("~")
    passphrase = input(colorize("Enter a wallet seed: ", 'orange'))
    data.update({"gui":"MM2GUI"})
    data.update({"rpc_password":rpc_pass})
    data.update({"netid":int(netid)})
    data.update({"userhome":userhome})
    data.update({"passphrase":passphrase})
    with open('MM2.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(colorize("MM2.json file created!", 'green'))
    wait_continue()


## MM2 management
def start_mm2(logfile='mm2_output.log'):
        if os.path.isfile('mm2'):
            mm2_output = open(logfile,'w+')
            subprocess.Popen(["./mm2"], stdout=mm2_output, stderr=mm2_output, universal_newlines=True)
            msg = "Marketmaker 2 starting. Use 'tail -f "+logfile+"' for mm2 console messages. "
            time.sleep(1)
            wait_continue(msg)
        else:
            print(colorize("\nmm2 binary not found in "+script_path+"!", 'red'))
            print(colorize("See https://developers.komodoplatform.com/basic-docs/atomicdex/atomicdex-setup/get-started-atomicdex.html for install instructions.", 'orange'))
            print(colorize("Exiting...\n", 'blue'))
            sys.exit()        

def stop_mm2(node_ip, user_pass):
        params = {'userpass': user_pass, 'method': 'stop'}
        try:
            r = requests.post(node_ip, json=params)
            msg = "MM2 stopped. "
        except:
            msg = "MM2 was not running. "
        wait_continue(msg)


def exit(node_ip, user_pass):
    mm2_active = rpclib.get_status(node_ip, user_pass)[1]
    if mm2_active:
        while True:
            q = input(colorize("Cancel all orders (y/n)? ", 'orange'))
            if q == 'n' or q == 'N':
                break
            elif q == 'y' or q == 'Y':
                resp = rpclib.cancel_all(node_ip, user_pass).json()
                print(colorize("All orders cancelled!","orange"))
                break
            else:        
                print(colorize("Invalid response, must be [Y/y] or [N/n]", 'red'))
                pass
        while True:
            q = input(colorize("Stop Marketmaker 2? (y/n): ", 'orange'))
            if q == 'y' or q == 'Y':
                stop_mm2(node_ip, user_pass)
                print(colorize("Goodbye!", 'blue'))
                sys.exit()
            elif q == 'n' or q == 'N':
                sys.exit()
            else:
                print(colorize("Invalid response, use [Y/y] or [N/n]...", 'red'))
    else:
        print(colorize("Goodbye!", 'blue'))
        sys.exit()

def activate_all(node_ip, user_pass):
    for coin in coinslib.coins:
        if coinslib.coins[coin]['activate_with'] == 'native':
            r = rpclib.enable(node_ip, user_pass, coin)
            print(r.json())
            print(colorize("Activating "+coin+" in native mode", 'cyan'))
        else:
            r = rpclib.electrum(node_ip, user_pass, coin)
            print(r.json())
            print(colorize("Activating "+coin+" with electrum", 'cyan'))

def validate_selection(interrogative, selection_list):
    while True:
        index = int(input(colorize(interrogative, 'orange')))-1
        try:
            selected = selection_list[index]
            return selected
        except:
            print(colorize("Invalid selection, must be number between 1 and "+str(len(selection_list)), 'red'))
            pass

def select_coin(interrogative, coin_list, ignore=[]):
    i = 1
    row = ''
    coin_list.sort()
    for coin in ignore:
        coin_list.remove(coin)
    for coin in coin_list:
        if i < 10:
            row += '{:<14}'.format(" ["+str(i)+"] "+coin)
        else:
            row += '{:<14}'.format("["+str(i)+"] "+coin)
        if len(row) > 64 or i == len(coin_list):
            print(colorize(row, 'blue'))
            row = ''
        i += 1
    selection = validate_selection(interrogative, coin_list)
    return selection

def pair_orderbook_table(node_ip, user_pass, base, rel, coins_data='', no_stop=False):
    if not no_stop:
        print(colorize('Getting orderbook...', 'cyan'))
    orderbook = rpclib.orderbook(node_ip, user_pass, base, rel).json()
    if coins_data == '':
        coins_data = rpclib.build_coins_data(node_ip, user_pass, [base,rel])
    try:
        balance_data = rpclib.my_balance(node_ip, user_pass, base).json()
        addr = balance_data['address']
    except Exception as e:
        addr = ''
        pass
    row = "-"*175 
    orderbook_trim = []
    header_row =  hl+'{:^10}'.format('ORDER NUM')+hl+'{:^14}'.format('PAIR')+hl+'{:^16}'.format('VOLUME'+" ("+base+")")+hl \
            +'{:^18}'.format('PRICE (USD)')+hl \
            +'{:^36}'.format('SELLER ADDRESS')+hl+'{:^18}'.format('PRICE ('+rel+')')+hl \
            +'{:^18}'.format('MM2 RATE')+hl+'{:^18}'.format('MARKET RATE')+hl \
            +'{:^16}'.format('DIFFERENTIAL')+hl
    if not no_stop:
        print("    "+row)
        print("    "+header_row)
        print("    "+row)
    elif 'asks' in orderbook and len(orderbook['asks']) == 0 and no_stop:
        return []
    try:
        market_rate = coins_data[base]['BTC_price']/coins_data[rel]['BTC_price']
    except:
        market_rate = 0
    pair = rel+"/"+base
    try:
        btc_price = coins_data[base]['BTC_price']
        aud_price = coins_data[base]['AUD_price']
        usd_price = coins_data[base]['USD_price']
        price_source = coins_data[base]['price_source']
        if 'asks' in orderbook and len(orderbook['asks']) > 0:
            i = 1
            for bid in orderbook['asks']:
                if bid['address'] != addr:
                    orderbook_trim.append(bid)
                    bid['price'] = str(round(float(bid['price']),7))
                    price = str(bid['price'])
                    volume = str(bid['maxvolume'])
                    if market_rate != 0:
                        differential = float(price)/float(market_rate)-1
                    else:
                        differential = 0
                    diff_pct = str(differential*100)[:5]+"%"
                    if differential < 0:
                        diff_pct = colorize('{:^16}'.format(str(diff_pct)[:8]), 'green')
                    elif differential > 0.07:
                        diff_pct = colorize('{:^16}'.format(str(diff_pct)[:8]), 'red')
                    else:
                        diff_pct = colorize('{:^16}'.format(str(diff_pct)[:8]), 'default')
                    rel_price = float(price)
                    if not no_stop:
                        print("    "+hl+'{:^10}'.format("["+str(i)+"]")+hl+'{:^14}'.format(pair)+hl+'{:^16}'.format(volume[:10])+hl \
                                     +'{:^18}'.format("$"+str(usd_price)[:14])+hl \
                                     +'{:^36}'.format(str(bid['address']))+hl+'{:^18}'.format(str(rel_price)[:14])+hl \
                                     +'{:^18}'.format(str(price)[:14])+hl+'{:^18}'.format(str(market_rate)[:14])+hl \
                                     +str(diff_pct)+"\033[0m"+hl \
                                     )
                        i += 1
                        print("    "+row)
                    elif differential < 0:
                        print("    "+row)
                        print("    "+header_row)
                        print("    "+row)
                        print("    "+hl+'{:^10}'.format("["+str(i)+"]")+hl+'{:^14}'.format(pair)+hl+'{:^16}'.format(volume[:10])+hl \
                                     +'{:^18}'.format("$"+str(usd_price)[:14])+hl \
                                     +'{:^36}'.format(str(bid['address']))+hl+'{:^18}'.format(str(rel_price)[:14])+hl \
                                     +'{:^18}'.format(str(price)[:14])+hl+'{:^18}'.format(str(market_rate)[:14])+hl \
                                     +str(diff_pct)+"\033[0m"+hl \
                                     )
                        i += 1
                        print("    "+row)
                else:
                    orderbook_trim.append(bid)
                    price = str(bid['price'])
                    volume = str(bid['maxvolume'])
                    if market_rate != 0:
                        differential = float(price)/float(market_rate)-1
                    else:
                        differential = 0
                    diff_pct = str(differential*100)[:5]+"%"
                    if differential < 0:
                        diff_pct = colorize('{:^16}'.format(str(diff_pct)[:8]), 'green')
                    elif differential > 0.07:
                        diff_pct = colorize('{:^16}'.format(str(diff_pct)[:8]), 'red')
                    else:
                        diff_pct = colorize('{:^16}'.format(str(diff_pct)[:8]), 'default')
                    rel_price = float(price)
                    print("    "+hl+'{:^10}'.format("["+str(i)+"]")+hl+'{:^14}'.format(pair)+hl+'{:^16}'.format(volume[:10])+hl \
                                 +'{:^18}'.format("$"+str(usd_price)[:14])+hl \
                                 +colorize('{:^36}'.format("YOUR ORDER"), 'cyan')+hl+'{:^18}'.format(str(rel_price)[:14])+hl \
                                 +'{:^18}'.format(str(price)[:14])+hl+'{:^18}'.format(str(market_rate)[:14])+hl \
                                 +str(diff_pct)+"\033[0m"+hl \
                                 )
                    i += 1
                    print("    "+row)

        elif not no_stop:
            print("    "+hl+'{:^10}'.format("[*]")+hl+'{:^14}'.format(pair)+hl+'{:^16}'.format("-")+hl \
                         +'{:^18}'.format("$"+str(usd_price)[:14])+hl \
                         +'{:^36}'.format(str("-"))+hl+'{:^18}'.format(str(market_rate)[:14])+hl \
                         +'{:^18}'.format(str('-'))+hl+'{:^18}'.format(str(market_rate)[:14])+hl \
                         +'{:^18}'.format(str('-')+"\033[0m")+hl \
                         )
            print("    "+row)
            while True:
                q = input(colorize("No orders in orderbook for "+base+"/"+rel+"! Create one manually? (y/n): ", 'orange'))
                if q == 'N' or q == 'n':
                    return 'back to menu'
                elif q == 'Y' or q == 'y':
                    while True:
                        outcome = create_buy(node_ip, user_pass, base, rel)
                        if outcome == 'back to menu':
                            break
                    break
                else:
                    print(colorize("Enter [Y/y] or [N/n] only, try again... ", 'red'))
    except Exception as e:
        print("Orderbook error: "+str(e))
        pass
    return orderbook_trim

def rat_float(rat):
    numerator = rat[0]
    denominator = rat[1]
    if numerator[0] == -1:
        numerator = numerator[1]*-1
    else:
        numerator = numerator[1]
    print(numerator)
    if denominator[0] == -1:
        denominator = denominator[1]*-1
    else:
        denominator = denominator[1]
    print(denominator)
    fee = numerator[0]/denominator[0]
    return fee


def show_orderbook_pair(node_ip, user_pass, base='', rel=''):
    coin_status = rpclib.check_coins_status(node_ip, user_pass)
    active_coins = coin_status[3]
    if base == '':
        base = select_coin("Select coin to buy: ", active_coins)
    if rel == '':
        rel = select_coin("Select coin to sell: ", active_coins, [base])
    # todo: ignore orders set by user
    try:
        orderbook = pair_orderbook_table(node_ip, user_pass, base, rel)
        while True:
            if orderbook == 'back to menu':
                return 'back to menu'
            bal = rpclib.my_balance(node_ip, user_pass, rel).json()['balance']
            print(colorize("Your "+rel+" balance: "+str(bal), 'green'))
            q = input(colorize("Select an order number to start a trade, [R]efresh orderbook, [C]reate one manually, or [E]xit to menu: ", 'orange'))
            if q == 'e' or q == 'E':
                break
            if q == 'R' or q == 'r':
                orderbook = pair_orderbook_table(node_ip, user_pass, base, rel)
            elif q == 'c' or q == 'C':
                while True:
                    outcome = create_buy(node_ip, user_pass, base, rel)
                    if outcome == 'back to menu':
                        break
                break
            else:
                try:
                    selected = orderbook[int(q)-1]
                    price = float(selected['price'])
                    while True:
                        try:
                            fee = rpclib.get_fee(node_ip, user_pass, rel).json()['result']['amount']
                            print(fee)
                            fee = rat_float(fee)
                            print(fee)
                            print(bal)
                            max_afforded_val = ((float(bal)-float(fee)*2)/price)*0.99
                            volume = float(selected['maxvolume'])
                            if volume > max_afforded_val:
                                max_vol = max_afforded_val
                            else:
                                max_vol = volume
                            max_vol = Decimal(Decimal(max_vol).quantize(Decimal('.001'), rounding=ROUND_DOWN))
                            buy_num = float(input(colorize("How many "+base+" to buy at "+str(price)+"? (max. "+str(max_vol)+"): ", 'orange')))
                            if buy_num > max_afforded_val:
                                    print(colorize("Can't buy more than max affordable volume! Try again..." , 'red'))
                            else:
                                while True:
                                    q = input(colorize("Confirm buy order, "+str(buy_num)+" "+base+" for "+str(price*buy_num)+" "+rel+" (y/n): ",'orange'))
                                    if q == 'Y' or q == 'y':
                                        resp = rpclib.buy(node_ip, user_pass, base, rel, buy_num, price).json()
                                        if 'error' not in resp:
                                            input(colorize("Order submitted! Press [Enter] to continue...", 'green'))
                                        else:
                                            print(resp)
                                            input(colorize("Press [Enter] to continue...", 'orange'))
                                        break
                                    elif q == 'N' or q == 'n':
                                        break
                                    else:
                                        print(colorize("Invalid selection, must be [Y/y] or [N/n]. Try again...", 'red'))
                                break
                        except Exception as e:
                            print(e)
                            pass
                    break
                except Exception as e:
                    print(e)
                    print(colorize("Invalid selection, must be [E/e] or a number between 1 and "+str(len(orderbook)), 'red'))
                    pass
    except Exception as e:
        print("Orderbooks error: "+str(e))
        pass
        wait_continue()

def create_buy(node_ip, user_pass, base, rel):
    try:
        rel_bal = rpclib.my_balance(node_ip, user_pass, rel).json()['balance']
        rel_price = float(input(colorize("What "+rel+" price?: ", 'orange')))
        rel_price = round(rel_price,7)
        max_vol = float(rel_bal)/rel_price
        max_vol = round(max_vol,7)
        buy_num = float(input(colorize("How many "+base+" to buy? (max. "+'{:^8}'.format(str(max_vol))+"): ", 'orange')))
        buy_num = round(buy_num,7)
        if buy_num > max_vol:
            print(colorize("Can't buy more than max volume! Try again..." , 'red'))
        else:
            while True:
                q = input(colorize("Confirm buy order, "+str(buy_num)+" "+base+" for "+str(float(rel_price)*buy_num)+" "+rel+" (y/n): ",'orange'))
                if q == 'Y' or q == 'y':
                    resp = rpclib.buy(node_ip, user_pass, base, rel, buy_num, rel_price).json()
                    if 'error' in resp:
                        print(colorize("Buy Error: "+str(resp), 'red'))
                    else:
                        print(colorize("Order submitted!", 'green'))
                    wait_continue()
                    return 'back to menu'
                elif q == 'N' or q == 'n':
                    return 'back to menu'
                else:
                    print(colorize("Invalid selection, must be [Y/y] or [N/n]. Try again...", 'red'))
    except Exception as e:
        print("Create buy error: "+str(e))
        wait_continue()
        return 'back to menu'


def show_orders_table(node_ip, user_pass, coins_data='', bot=False):
    my_current_orders = rpclib.my_orders(node_ip, user_pass).json()['result']
    num_orders = len(my_current_orders['maker_orders']) + len(my_current_orders['taker_orders'])
    if num_orders == 0:
        print(colorize("You have no pending orders!", 'red'))
        if not bot:
            wait_continue()
            return 'back to menu'
    if coins_data == '':
        coins_data = rpclib.build_coins_data(node_ip, user_pass)
    total_btc_val = 0
    my_order_list = []
    try:
        row = colorize("-"*174, 'blue')
        print("    "+row)
        print(
                hl+'{:^11}'.format("ORDER NUM")+hl+'{:^14}'.format('ORDER TYPE')+hl \
                +'{:^14}'.format('PAIR')+hl+'{:^18}'.format('VOLUME')+hl \
                +'{:^18}'.format('PRICE (USD)')+hl+'{:^18}'.format('PRICE (AUD)')+hl \
                +'{:^18}'.format('PRICE (BTC)')+hl+'{:^18}'.format('MY PRICE')+hl \
                +'{:^18}'.format('MARKET RATE')+hl \
                +'{:^16}'.format('DIFFERENTIAL')+hl    \
                )
        print("    "+row)
        i = 1
        for order in my_current_orders['maker_orders']:
            my_order_list.append(my_current_orders['maker_orders'][order])
            order_type = "MAKER"
            base = my_current_orders['maker_orders'][order]['base']
            rel = my_current_orders['maker_orders'][order]['rel']
            price = my_current_orders['maker_orders'][order]['price']
            volume = my_current_orders['maker_orders'][order]['available_amount']
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
            price_source = coins_data[base]['price_source']
            btc_price = str(btc_price)
            if price_source == 'binance':
                btc_price = colorize('{:^18}'.format(str(btc_price)), 'yellow')
            elif price_source == 'coingecko':
                btc_price = colorize('{:^18}'.format(str(btc_price)), 'pink')
            elif price_source == 'mm2_orderbook':
                btc_price = colorize('{:^18}'.format(str(btc_price)), 'cyan')
            #print(price_source)
            #print(btc_price)
            rel_price = float(price)
            print(colorize("    "+hl+'{:^11}'.format("["+str(i)+"]")+hl+'{:^14}'.format(order_type)+hl \
                                 +'{:^14}'.format(pair)+hl+'{:^18}'.format(volume[:14])+hl \
                                 +'{:^18}'.format("$"+str(usd_price)[:14])+hl+'{:^18}'.format("$"+str(aud_price)[:14])+hl \
                                 +'{:^18}'.format(str(btc_price))+hl+'{:^18}'.format(str(rel_price)[:14])+hl \
                                 +'{:^18}'.format(str(market_rate)[:14])+hl \
                                 +str(differential)+hl, 'blue') \
                     )
            i += 1
            print("    "+row)
        for order in my_current_orders['taker_orders']:
            my_order_list.append(my_current_orders['taker_orders'][order])
            order_type = "TAKER"
            base = my_current_orders['taker_orders'][order]['request']['base']
            rel = my_current_orders['taker_orders'][order]['request']['rel']
            base_amount = my_current_orders['taker_orders'][order]['request']['base_amount']
            rel_amount = my_current_orders['taker_orders'][order]['request']['rel_amount']
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
            price_source = coins_data[base]['price_source']
            btc_price = str(btc_price)
            if price_source == 'binance':
                btc_price = colorize('{:^18}'.format(str(btc_price)), 'yellow')
            elif price_source == 'coingecko':
                btc_price = colorize('{:^18}'.format(str(btc_price)), 'pink')
            elif price_source == 'mm2_orderbook':
                btc_price = colorize('{:^18}'.format(str(btc_price)), 'cyan')
            rel_price = float(price)
            print(colorize("    "+hl+'{:^11}'.format("["+str(i)+"]")+hl+'{:^14}'.format(order_type)+hl \
                                 +'{:^14}'.format(pair)+hl+'{:^18}'.format(volume[:14])+hl \
                                 +'{:^18}'.format("$"+str(usd_price)[:14])+hl+'{:^18}'.format("$"+str(aud_price)[:14])+hl \
                                 +'{:^18}'.format(str(btc_price))+hl+'{:^18}'.format(str(rel_price)[:14])+hl \
                                 +'{:^18}'.format(str(market_rate)[:14])+hl \
                                 +str(differential)+hl, 'blue') \
                     )
            i += 1
            print("    "+row)
        if not bot:
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
                        print(selected)
                        order_uuid = selected['uuid']
                        resp = rpclib.cancel_uuid(node_ip, user_pass, order_uuid).json()
                        print(colorize("Order #"+q+" cancelled!","orange"))
                        break
                    except:
                        print(colorize("Invalid selection, must be [E/e] or a number between 1 and "+str(len(my_order_list)), 'red'))
                        pass                        
    except Exception as e:
        print("Orders error: "+str(e))
        pass
    if not bot:        
        wait_continue()

def show_balances_table(node_ip, user_pass, coins_data='', bot=False):
        coin_status = rpclib.check_coins_status(node_ip, user_pass)
        active_coins = coin_status[3]
        if coins_data == '':
            coins_data = rpclib.build_coins_data(node_ip, user_pass, list(coinslib.coins.keys()))
        if len(active_coins) == 0:
            msg = colorize("No coins activated!", 'red')
            if not bot:
                wait_continue()
            #TODO: add highlights for bot buy/sell
        btc_total = 0
        usd_total = 0
        aud_total = 0
        header = hl+'{:^10}'.format('COIN')+hl+'{:^50}'.format('ADDRESS (green = bot trading)')+hl \
                            +'{:^11}'.format('BALANCE')+hl+'{:^16}'.format('BTC PRICE')+hl \
                            +'{:^11}'.format('BTC VALUE')+hl+'{:^11}'.format('USD PRICE')+hl \
                            +'{:^11}'.format('USD VALUE')+hl+'{:^11}'.format('AUD PRICE')+hl \
                            +'{:^11}'.format('AUD VALUE')+hl
        table_dash = "-"*152
        print(colorize(" "+table_dash, 'lightblue'))
        print(colorize(" "+header, 'lightblue'))
        print(colorize(" "+table_dash, 'lightblue'))
        for coin in coins_data:
            if coin in active_coins:
                try:
                    balance_data = rpclib.my_balance(node_ip, user_pass, coin).json()
                    addr = balance_data['address']
                    bal = float(balance_data['balance'])
                except Exception as e:
                    addr = "RPC timed out! "+str(e)
                    bal = 0
                    pass
                btc_price = 0
                btc_val = 0
                usd_price = 0
                usd_val = 0
                aud_price = 0
                aud_val = 0
                try:
                    if coin in coins_data:
                        btc_price = float(coins_data[coin]['BTC_price'])
                        btc_val = btc_price*bal
                        usd_price = coins_data[coin]['USD_price']
                        usd_val = usd_price*bal
                        aud_price = coins_data[coin]['AUD_price']
                        aud_val = aud_price*bal
                except Exception as e:
                    pass
                    '''
                    # some coins only returning btc price
                    print(coin)
                    print(coins_data[coin])
                    print(e)
                    '''
                btc_total += btc_val
                usd_total += usd_val
                aud_total += aud_val
                price_source = coins_data[coin]['price_source']
                if price_source == 'binance':
                    btc_price = colorize('{:^16}'.format(str(btc_price)[:8]), 'yellow')
                elif price_source == 'coingecko':
                    btc_price = colorize('{:^16}'.format(str(btc_price)[:8]), 'pink')
                elif price_source == 'mm2_orderbook':
                    btc_price = colorize('{:^16}'.format(str(btc_price)[:8]), 'cyan')
                if coin not in coinslib.trading_list:
                    row = hl+'{:^10}'.format(coin)+hl+'{:^50}'.format(addr)+hl \
                                                 +'{:^11}'.format(str(bal)[:9])+hl \
                                                 +'{:^16}'.format(str(btc_price))+hl+'{:^11}'.format(str(btc_val)[:9])+hl \
                                                 +'{:^11}'.format(str(usd_price)[:9])+hl+'{:^11}'.format(str(usd_val)[:9])+hl \
                                                 +'{:^11}'.format(str(aud_price)[:9])+hl+'{:^11}'.format(str(aud_val)[:9])+hl
                    print(colorize(" "+row, 'lightblue'))
                else:
                    row = hl+colorize('{:^10}'.format(coin),'green')+hl+colorize('{:^50}'.format(addr),'green')+hl \
                                                 +colorize('{:^11}'.format(str(bal)[:9]),'green')+hl \
                                                 +colorize('{:^16}'.format(str(btc_price)),'green')+hl+colorize('{:^11}'.format(str(btc_val)[:9]),'green')+hl\
                                                 +colorize('{:^11}'.format(str(usd_price)[:9]),'green')+hl+colorize('{:^11}'.format(str(usd_val)[:9]),'green')+hl\
                                                 +colorize('{:^11}'.format(str(aud_price)[:9]),'green')+hl+colorize('{:^11}'.format(str(aud_val)[:9]),'green')+hl
                    print(colorize(" "+row, 'lightblue'))
        print(colorize(" "+table_dash, 'lightblue')) 
        row = hl+'{:^78}'.format(' ')+hl \
                     +'{:^11}'.format('TOTAL BTC')+hl+'{:^11}'.format(str(btc_total)[:9])+hl \
                     +'{:^11}'.format('TOTAL USD')+hl+'{:^11}'.format(str(usd_total)[:9])+hl \
                     +'{:^11}'.format('TOTAL AUD')+hl+'{:^11}'.format(str(aud_total)[:9])+hl
        print(colorize(" "+row, 'lightblue'))
        print(colorize(" "+table_dash+"\n\n", 'lightblue'))
        if not bot:
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
            amount = input(colorize("Enter amount to send, or [A] for all: ",'orange'))
            if amount == 'A' or amount == 'a':
                resp = rpclib.withdraw_all(node_ip, user_pass, cointag, address).json()
            else:
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
                    if address.startswith('0x'):
                        txid_str = '0x'+txid['tx_hash']
                    else:
                        txid_str = txid['tx_hash']
                    print(colorize("Withdrawl successful! TXID: ["+txid_str+"]", 'green'))
                    try:
                        print(colorize("Track transaction status at ["+coinslib.coins[cointag]['tx_explorer']+"/"+txid_str+"]", 'cyan'))
                    except:
                        pass
                    break
                else:
                    print(colorize("Error: "+str(txid), 'red'))
                    break
    else:
        print(colorize("Invalid selection, must be [E/e] or [W/w]! Try again...", 'red'))
        return 'try again'


def show_pending_swaps(node_ip, user_pass, swapcount=50):
    header_list = []
    swap_json = []
    pending_swaps = []
    error_events = ['StartFailed', 'NegotiateFailed', 'TakerFeeValidateFailed',
                                    'MakerPaymentTransactionFailed', 'MakerPaymentDataSendFailed',
                                    'TakerPaymentValidateFailed', 'TakerPaymentSpendFailed', 
                                    'MakerPaymentRefundFailed']
    recent_swaps = rpclib.my_recent_swaps(node_ip, user_pass, swapcount).json()
    swap_list = recent_swaps['result']['swaps']
    for swap in swap_list:
        ignore = False
        for event in swap['events']:
            if event['event']['type'] in error_events or event['event']['type'] == 'Finished':
                ignore = True
        if not ignore:
            pending_swaps.append(swap)
    if len(pending_swaps) > 0:
        pending_swaps_summary = {}
        for swap in pending_swaps:
            try:
                pending_swap_json = {}
                swap_type = swap['type']
                swap_info = swap['my_info']
                uuid = swap['uuid']
                pending_swap_json.update({'swap_type':swap_type})
                pending_swap_json.update({'uuid':uuid})
                if swap_type == 'Taker':
                    pending_swap_json.update({'taker_amount':swap_info['my_amount'][:8]})
                    pending_swap_json.update({'taker_coin':swap_info['my_coin']})
                    pending_swap_json.update({'maker_amount':swap_info['other_amount'][:8]})
                    pending_swap_json.update({"maker_coin":swap_info['other_coin']})
                else:
                    pending_swap_json.update({'maker_amount':swap_info['my_amount'][:8]})
                    pending_swap_json.update({'maker_coin':swap_info['my_coin']})
                    pending_swap_json.update({'taker_amount':swap_info['other_amount'][:8]})
                    pending_swap_json.update({"taker_coin":swap_info['other_coin']})
                for event in swap['events']:
                    pending_swap_json.update({"last_event":event['event']['type']})
                pending_swaps_summary[uuid] = pending_swap_json
            except:
                pass

        header = hl+'{:^7}'.format('NUM')+hl+'{:^40}'.format('UUID')+hl+'{:^12}'.format('TYPE')+hl \
                            +'{:^34}'.format('CURRENT EVENT')+hl \
                            +'{:^12}'.format('TAKER COIN')+hl+'{:^12}'.format('TAKER VAL')+hl \
                            +'{:^12}'.format('MAKER COIN')+hl+'{:^12}'.format('MAKER VAL')+hl
        table_dash = "-"*150
        print(colorize(" "+table_dash, 'lightblue'))
        print(colorize(" "+header, 'lightblue'))
        print(colorize(" "+table_dash, 'lightblue'))
        i = 1
        for uuid in pending_swaps_summary:
            swap_summary = pending_swaps_summary[uuid]
            row = hl+'{:^7}'.format("["+str(i)+"]")+hl+'{:^40}'.format(uuid)+hl+'{:^12}'.format(swap_summary['swap_type'])+hl \
                        +'{:^34}'.format(swap_summary['last_event'])+hl \
                        +'{:^12}'.format(swap_summary['taker_coin'])+hl+'{:^12}'.format(swap_summary['taker_amount'])+hl \
                        +'{:^12}'.format(swap_summary['maker_coin'])+hl+'{:^12}'.format(swap_summary['maker_amount'])+hl
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
                    swap = pending_swaps[int(q)-1]
                    for event in swap['events']:
                        print(colorize("["+event['event']['type']+"]", 'green'))
                        print(colorize(str(event), 'blue'))
                        print()
                except Exception as e:
                    print(colorize("Invalid selection, must be [E/e] or a number between 1 and "+str(len(pending_swaps)), 'red'))
                    pass
    else:
        print(colorize("You have no pending swaps in your history!", 'orange'))
    wait_continue()

def swaps_info(node_ip, user_pass, swapcount=250):
    recent_swaps = rpclib.my_recent_swaps(node_ip, user_pass, swapcount).json()
    swap_list = recent_swaps['result']['swaps']
    swap_json = []
    num_finished = 0
    num_in_progress = 0
    num_failed = 0
    num_swaps = 0
    header_list = []
    if len(swap_list) > 0:
        error_events = ['StartFailed', 'NegotiateFailed', 'TakerFeeValidateFailed',
                                        'MakerPaymentTransactionFailed', 'MakerPaymentDataSendFailed',
                                        'TakerPaymentValidateFailed', 'TakerPaymentSpendFailed', 
                                        'MakerPaymentRefunded', 'MakerPaymentRefundFailed']
        for swap in swap_list:
            try:
                taker_addr = ''
                maker_coin = ''
                maker_amount = 0
                taker_coin = ''
                taker_amount = 0
                role = swap['type']
                swap_data = swap['events'][0]
                if 'maker_coin' in swap_data['event']['data']:
                    maker_coin = swap_data['event']['data']['maker_coin']
                    if maker_coin not in header_list:
                        header_list.append(maker_coin)
                if 'maker_amount' in swap_data['event']['data']:
                    maker_amount = swap_data['event']['data']['maker_amount']
                if 'taker_coin' in swap_data['event']['data']:
                    taker_coin = swap_data['event']['data']['taker_coin']
                    if taker_coin not in header_list:
                        header_list.append(taker_coin)
                if 'taker_amount' in swap_data['event']['data']:
                    taker_amount = swap_data['event']['data']['taker_amount']
                timestamp = int(int(swap_data['timestamp'])/1000)
                human_time = time.ctime(timestamp)
                for event in swap['events']:
                    if event['event']['type'] == 'Started':
                        if 'taker' in swap_data['event']['data']:
                            taker_pub = swap_data['event']['data']['taker']
                            taker_addr = get_radd_from_pub(taker_pub)
                        else: 
                            taker_pub = swap_data['event']['data']['maker']
                            taker_addr = get_radd_from_pub(taker_pub)
                    if event['event']['type'] in error_events:
                        swap_status = event['event']['type']
                        break
                    else:
                        swap_status = event['event']['type']
                if taker_addr not in ignored_addresses:
                    swap_json.append({"result":swap_status,
                                                "time":human_time,
                                                "role":role,
                                                "maker_coin":maker_coin,
                                                "maker_amount":maker_amount,
                                                "taker_coin":taker_coin,
                                                "taker_amount":taker_amount
                            })
            except Exception as e:
                print(e)
                pass
        num_swaps = len(swap_json)
        for swap in swap_json:
            if swap['result'] == 'Finished':
                num_finished += 1
            elif swap['result'].find('Failed') != -1:
                num_failed += 1
            else:
                num_in_progress += 1
    return swap_json, num_swaps, num_finished, num_failed, num_in_progress, header_list

def show_recent_swaps(node_ip, user_pass, swapcount=50, coins_data='', bot=False):
    print(colorize("Getting swaps info...", 'cyan'))
    swap_info = swaps_info(node_ip, user_pass)
    swap_json = swap_info[0]
    header_list = swap_info[5]
    if len(swap_json) > 0:
        if coins_data == '':
            coins_data = rpclib.build_coins_data(node_ip, user_pass) 
        delta = {}
        header = "|"+'{:^14}'.format("TIME")+"|"+'{:^8}'.format("RESULT")+"|"+'{:^7}'.format("ROLE")+"|"
        for coin in header_list:
            header += '{:^8}'.format(coin)+"|"
            delta[coin] = 0
        table_dash = "-"*len(header)
        print(" "+table_dash)
        print(" "+header)
        print(" "+table_dash)
        for swap in swap_json:
            role = swap['role']
            time_str = swap['time'][:-8]
            time_str = time_str[4:]
            row_str = "|"+'{:^14}'.format(time_str)+"|"
            if swap['result'].find('Failed') > 0:
                highlight = 'red'
                result = 'FAILED'
            elif swap['result'].find('Finished') > -1:
                highlight = 'green'
                result = 'FINISHED'
            else:
                highlight = 'orange'
                result = 'PENDING'
            result = colorize('{:^8}'.format(result), highlight)+"|"
            row_str += result
            row_str += '{:^7}'.format(role)+"|"
            for coin in header_list:
                if role == 'Maker':
                    if coin == swap['maker_coin']:
                        swap_amount = float(swap['maker_amount'])*-1
                    elif coin == swap['taker_coin']:
                        swap_amount = float(swap['taker_amount'])
                    else:
                        swap_amount = 0
                elif role == 'Taker':
                    if coin == swap['taker_coin']:
                        swap_amount = float(swap['taker_amount'])*-1
                    elif coin == swap['maker_coin']:
                        swap_amount = float(swap['maker_amount'])
                    else:
                        swap_amount = 0
                if result.find('Failed') == -1:
                    delta[coin] += swap_amount
                if swap_amount < 0:
                    row_str += colorize('{:^8}'.format(str(swap_amount)[:6]), 'red')+"|"
                elif swap_amount > 0:
                    row_str += colorize('{:^8}'.format(str(swap_amount)[:6]), 'green')+"|"
                else:
                    row_str += colorize('{:^8}'.format('-'), 'darkgrey')+"|"
            print(" "+row_str)
        delta_row = "|"+'{:^31}'.format("TOTAL")+"|"
        btc_row = "|"+'{:^31}'.format("BTC")+"|"
        usd_row = "|"+'{:^31}'.format("USD")+"|"
        aud_row = "|"+'{:^31}'.format("AUD")+"|"
        table_dash = "-"*(len(delta_row)+(len(header_list)+1)*9)
        btc_sum = 0
        usd_sum = 0
        aud_sum = 0
        for delta_coin in delta:
            try:
                for header_coin in header_list:
                    if delta_coin == header_coin:
                        btc_price = coins_data[header_coin]['BTC_price']*delta[header_coin]
                        usd_price = coins_data[header_coin]['USD_price']*delta[header_coin]
                        aud_price = coins_data[header_coin]['AUD_price']*delta[header_coin]
                        btc_sum += btc_price
                        usd_sum += usd_price
                        aud_sum += aud_price
                        if float(delta[header_coin]) > 0:
                            highlight = 'green'
                        else:
                            highlight = 'red'
                        delta_row += colorize('{:^8}'.format(str(delta[header_coin])[:6]),highlight)+"|"
                        btc_row += colorize('{:^8}'.format(str(btc_price)[:6]),highlight)+"|"
                        usd_row += colorize('{:^8}'.format("$"+str(usd_price)[:5]),highlight)+"|"
                        aud_row += colorize('{:^8}'.format("$"+str(aud_price)[:5]),highlight)+"|"
            except:
                pass
        delta_row += '{:^8}'.format("TOTAL")+"|"
        btc_row += '{:^8}'.format(str(btc_sum)[:6])+"|"
        usd_row += '{:^8}'.format("$"+str(usd_sum)[:5])+"|"
        aud_row += '{:^8}'.format("$"+str(aud_sum)[:5])+"|"

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
    else:
        print(colorize("You have no swaps in your history!", 'orange'))
    if not bot:
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
    if len(failed_swaps) > 0:
        failed_swaps_summary = {}
        for swap in failed_swaps:
            try:
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
                        if 'taker' in event['event']['data']:
                            taker_pub = event['event']['data']['taker']
                            taker_addr = get_radd_from_pub(taker_pub)
                        else: 
                            taker_pub = event['event']['data']['maker']
                            taker_addr = get_radd_from_pub(taker_pub)
                        failed_swap_json.update({'lock_duration':event['event']['data']['lock_duration']})
                        failed_swap_json.update({'taker_coin':event['event']['data']['taker_coin']})
                        failed_swap_json.update({'taker_addr':taker_addr})
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
                        if taker_addr not in ignored_addresses:
                            failed_swaps_summary[uuid] = failed_swap_json
            except Exception as e:
                print("swap summary error: "+str(e))
                pass

        header = hl+'{:^7}'.format('NUM')+hl+'{:^40}'.format('UUID')+hl+'{:^7}'.format('TYPE')+hl \
                            +'{:^28}'.format('FAIL EVENT')+hl+'{:^23}'.format('ERROR')+hl \
                            +'{:^7}'.format('TAKER')+hl+'{:^7}'.format('MAKER')+hl \
                            +'{:^66}'.format('TAKER RADD')+hl
        table_dash = "-"*194
        print(colorize(" "+table_dash, 'lightblue'))
        print(colorize(" "+header, 'lightblue'))
        print(colorize(" "+table_dash, 'lightblue'))
        i = 1
        for uuid in failed_swaps_summary:
            swap_summary = failed_swaps_summary[uuid]
            for error in swap_summary['errors']:
                taker_addr = ''
                taker_coin = ''
                maker_coin = ''
                #swap_time = swap_summary['timestamps_list'][0][1]-swap_summary['timestamps_list'][0][0]
                start_time = list(swap_summary['timestamps_list'][0].values())[0]
                end_time = list(swap_summary['timestamps_list'][-1].values())[0]
                swap_time = ((end_time - start_time)/1000)/60
                if 'taker_addr' in swap_summary:
                    taker_addr = swap_summary['taker_addr']
                if 'taker_coin' in swap_summary:
                    taker_coin = swap_summary['taker_coin']
                if 'maker_coin' in swap_summary:
                    maker_coin = swap_summary['maker_coin']
                if str(error).find('overwinter') > 0:
                    error_type = "tx-overwinter-active"
                elif str(error).find('timeout') > 0:
                    error_type = "timeout"
                else:
                    error_type = "other"
                row = hl+'{:^7}'.format("["+str(i)+"]")+hl+'{:^40}'.format(uuid)+hl+'{:^7}'.format(str(swap_type))+hl \
                            +'{:^28}'.format(str(list(error.keys())[0]))+hl+'{:^23}'.format(error_type)+hl \
                            +'{:^7}'.format(taker_coin)+hl+'{:^7}'.format(maker_coin)+hl \
                            +'{:^66}'.format(taker_addr)+hl
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
    else:
        print(colorize("You have no failed swaps in your history!", 'orange'))
    wait_continue()

def run_tradebot(node_ip, user_pass, refresh_mins=20):
    while True:
        try:
            coins_data = rpclib.build_coins_data(node_ip, user_pass, list(coinslib.coins.keys()))
            submit_bot_trades(node_ip, user_pass, coins_data)
            show_orders_table(node_ip, user_pass, coins_data, True)
            show_balances_table(node_ip, user_pass, coins_data, True)
            show_recent_swaps(node_ip, user_pass, 50, coins_data, True)
            for i in range(refresh_mins):
                time_left = refresh_mins-i
                print(str(time_left)+"min until refresh..." )
                print("Exit bot with [CTRL-C]" )
                time.sleep(60)
        except KeyboardInterrupt:
            break
    while True:
        q = input(colorize("Cancel all orders (y/n)? ", 'orange'))
        if q == 'n' or q == 'N':
            break
        elif q == 'y' or q == 'Y':
            resp = rpclib.cancel_all(node_ip, user_pass).json()
            print(colorize("All orders cancelled!","orange"))
            break
        else:        
            print(colorize("Invalid selection, must be [Y/y] or [N/n]", 'red'))
            pass

def get_btc_price(cointag):
    if cointag == 'BTC':
        return 1
    if cointag == 'BCH':
        btc_price = binance_api.get_price('BCHABCBTC')
    else:
        btc_price = binance_api.get_price(cointag+'BTC')
    if 'price' in btc_price:
        return btc_price['price']
    else:
        return 0

def get_binance_addr(cointag):
    try:
        if cointag == "BCH":
            deposit_addr = binance_api.get_deposit_addr(cointag+"ABC")
        else:
            deposit_addr = binance_api.get_deposit_addr(cointag)
    except:
        deposit_addr == ''
        pass
    return deposit_addr

def binance_account_info(node_ip='', user_pass='', base='', bal=0, base_addr='', coins_data='', bot=False):
    if base == '':
        coinslist = coinslib.cointags
        coins_data = rpclib.build_coins_data(node_ip, user_pass)
    else:
        coinslist = [base]
    for base in coinslist:
        try:
            account_info = binance_api.get_account_info()
            usd_price = coins_data[base]['USD_price']
            binance_balances = account_info['balances']
            atomicDEX_reserve = coinslib.coins[base]['reserve_balance']
            if bot:
                for item in binance_balances:
                    if item['asset'] == base:
                        binance_balance = float(item['free'])
                        print(base+" balance on Binance is: "+str(binance_balance))
                        print(base+" balance on AtomicDEX is: "+str(bal))
                        print(base+" reserve for AtomicDEX is: "+str(atomicDEX_reserve))
                        break
                    else:
                        binance_balance = 0
                try:
                    if bal > atomicDEX_reserve*1.2 and base not in ['RICK','MORTY']:
                        qty = bal - atomicDEX_reserve
                        bal = bal - qty
                        deposit_addr = get_binance_addr(base)
                        withdraw_tx = rpclib.withdraw(node_ip, user_pass, base, deposit_addr['address'], qty).json()
                        print("Sending "+str(qty)+" "+base+" to Binance address "+deposit_addr['address'])
                        send_resp = rpclib.send_raw_transaction(node_ip, user_pass, base, withdraw_tx['tx_hex']).json()
                        if 'tx_hash' in send_resp:
                            txid_str = send_resp['tx_hash']
                            print(colorize("Track transaction status at ["+coinslib.coins[base]['tx_explorer']+"/"+txid_str+"]", 'cyan'))
                        else:
                            print("Response: "+str(send_resp))                
                    elif bal < atomicDEX_reserve*0.9 and base not in ['RICK','MORTY']:
                        qty = atomicDEX_reserve - bal
                        if base_addr != '':
                            if qty > binance_balance:
                                qty = binance_balance
                            qty = round(float(qty), 8)
                            if binance_balance >= qty and qty > 0:
                                print("Withdrawing "+str(qty)+" of "+str(binance_balance)+" "+base+" from Binance to address "+base_addr)
                                if base == "BCH":
                                    withdraw_tx = binance_api.withdraw(base+"ABC", base_addr, qty)
                                else:
                                    withdraw_tx = binance_api.withdraw(base, base_addr, qty)
                                print(withdraw_tx)
                            else:
                                print("Binance balance "+str(binance_balance)+" too low to reach AtomicDEX reserve "+str(atomicDEX_reserve)+" ...")
                                pass
                except Exception as e:
                    print(deposit_addr)
                    print(e)
                    print('Binance deposit/withdraw failed')
                    pass
            else:
                for item in binance_balances:
                    if item['asset'] == base:
                        binance_balance = float(item['free'])
                        print(base+" balance on Binance is: "+str(binance_balance))
                        break
                    else:
                        binance_balance = 0
        except Exception as e:
            print(e)
            input(colorize("Press [Enter] to continue...", 'orange'))
            pass
    if not bot:
        input(colorize("Press [Enter] to continue...", 'orange'))
    return bal

def submit_bot_trades(node_ip, user_pass, coins_data):
    swaps_in_progress = 0
    for base in coinslib.sell_list:
        try:
            balance_data = rpclib.my_balance(node_ip, user_pass, base).json()
            base_addr = balance_data['address']
            total_bal = float(balance_data['balance'])
            locked_bal = float(balance_data['locked_by_swaps'])
            bal = total_bal - locked_bal
        except:
            print("my_balance failed!")
            print(balance_data)
            base_addr = ''
            bal = 0
            pass
        bal = binance_account_info(node_ip, user_pass, base, bal, base_addr, coins_data, True)
        my_current_orders = rpclib.my_orders(node_ip, user_pass).json()['result']
        for rel in coinslib.buy_list:
            if rel != base:
                if 'override_KMD_buy_price' in coinslib.coins[rel]:
                    rel_btc_price = float(get_btc_price('KMD'))*float(coinslib.coins[rel]['override_KMD_buy_price'])
                else:
                    rel_btc_price = get_btc_price(rel)
                if rel_btc_price != 0 or rel in ['RICK', 'MORTY']:
                    trade_vol=bal*0.97
                    for order in my_current_orders['maker_orders']:
                        if base == my_current_orders['maker_orders'][order]['base'] and rel == my_current_orders['maker_orders'][order]['rel']:
                            started_swaps = my_current_orders['maker_orders'][order]['started_swaps']
                            swaps_in_progress = len(started_swaps)
                            if swaps_in_progress > 0:
                                print(str(swaps_in_progress)+" x "+base+" to "+rel+" swaps in order!")
                                for swap_uuid in started_swaps:
                                    swap_data = rpclib.my_swap_status(node_ip, user_pass, swap_uuid).json()
                                    for event in swap_data['result']['events']:
                                        if event['event']['type'] == 'Finished':
                                            print(swap_uuid+" finished")
                                            swaps_in_progress -= 1;
                    if swaps_in_progress == 0:
                        if 'override_KMD_sell_price' in coinslib.coins[base]:
                            base_btc_price = float(get_btc_price('KMD'))*float(coinslib.coins[base]['override_KMD_sell_price'])
                        else:
                            base_btc_price = get_btc_price(base)
                        if base_btc_price != 0 or base in ['RICK', 'MORTY']:
                            if base == 'BTC':
                                rel_price = 1
                            else:
                                base_price = base_btc_price
                            if rel == 'BTC':
                                rel_price = 1
                            else:
                                rel_price = rel_btc_price
                            if base not in ['RICK', 'MORTY'] and rel not in ['RICK', 'MORTY']:
                                pair_price = float(base_price)/float(rel_price)
                            else:
                                pair_price = 1
                            try:
                                min_swap = coinslib.coins[base]['min_swap']
                            except:
                                min_swap = 0
                            if trade_vol > min_swap:
                                if base in ['RICK', 'MORTY'] or rel in ['RICK', 'MORTY']:
                                    if base in ['RICK', 'MORTY'] and rel in ['RICK', 'MORTY']:
                                        trade_price = 1.762
                                        resp = rpclib.setprice(node_ip, user_pass, base, rel, trade_vol, trade_price).json()
                                        print(colorize("Setprice order: "+str(trade_vol)[:8]+" "+base+" for "+str(trade_price*trade_vol)[:8]+" "+rel+" submitted...","red"))
                                        time.sleep(0.1)
                                else:
                                    if 'premium' in coinslib.coins[base]:
                                        trade_price = pair_price*coinslib.coins[base]['premium']
                                    else:
                                        trade_price = pair_price*1.05
                                    resp = rpclib.setprice(node_ip, user_pass, base, rel, trade_vol, trade_price).json()
                                    print(colorize("Setprice order: "+str(trade_vol)[:8]+" "+base+" for "+str(trade_price*trade_vol)[:8]+" "+rel+" submitted...","cyan"))
                                    time.sleep(0.1)
                        else:
                            print(colorize("Unable to get price for "+base+", skipping...", 'cyan'))
                else:
                    print(colorize("Unable to get price for "+rel+", skipping...", 'cyan'))
    # TODO: Detect swaps in progress, and make sure to not cancel with new swap.