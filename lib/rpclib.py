#!/usr/bin/env python3
import os
import sys
import json
import time
import requests
import subprocess
from os.path import expanduser
from . import coinslib, tuilib, binance_api

cwd = os.getcwd()
home = expanduser("~")

#TODO: change this to match python methods
def help_mm2(node_ip, user_pass):
    params = {'userpass': user_pass, 'method': 'help'}
    r = requests.post(node_ip, json=params)
    return r.text

def check_mm2_status(node_ip, user_pass):
    try: 
        help_mm2(node_ip, user_pass)
        return True
    except Exception as e:
        return False

def my_orders(node_ip, user_pass):
    params = {'userpass': user_pass, 'method': 'my_orders',}
    r = requests.post(node_ip, json=params)
    return r

def orderbook(node_ip, user_pass, base, rel):
    params = {'userpass': user_pass,
              'method': 'orderbook',
              'base': base, 'rel': rel,}
    r = requests.post(node_ip, json=params)
    return r

def check_active_coins(node_ip, user_pass, cointag_list):
    active_cointags = []
    for cointag in cointag_list:
        try:
            # Dirty way to detect activation (rel is checked first by mm2)
            resp = orderbook(node_ip, user_pass, 'XXXX', cointag).json()
            if resp['error'] == 'Base coin is not found or inactive':
                active_cointags.append(cointag)
        except Exception as e:
            #print(e)
            pass
    return active_cointags 

def check_coins_status(node_ip, user_pass):
    if os.path.exists(cwd+"/coins") is False:
        print(tuilib.colorize("\n'coins' file not found in "+os.getcwd()+"!",'red'))
        print(tuilib.colorize("Use 'wget https://raw.githubusercontent.com/jl777/coins/master/coins' to download.", 'orange'))
        print(tuilib.colorize("Exiting...\n", 'blue'))
        sys.exit()
    elif os.path.exists(cwd+"/api_keys.json") is False:
        print(tuilib.colorize("\n'api_keys.json' file not found in "+os.getcwd()+"!",'red'))
        print(tuilib.colorize("Use 'cp api_keys_example.json api_keys.json' to copy it.", 'orange'))
        print(tuilib.colorize("You can leave the values blank, or input your own Binance API keys", 'orange'))
        print(tuilib.colorize("Exiting...\n", 'blue'))
        sys.exit()     
    else:
        cointag_list = []
        for coin in coinslib.coins:
            cointag_list.append(coin)
        num_all_coins = len(cointag_list)
        active_coins = check_active_coins(node_ip, user_pass, cointag_list)
        num_active_coins = len(active_coins)
        msg = str(num_active_coins)+"/"+str(num_all_coins)+" coins active"
        if num_active_coins == 0:
            color = 'red'
            all_active = False
        elif num_active_coins < len(coinslib.coins):
            color = 'yellow'
            all_active = False
        else:
            color = 'green'
            all_active = True
        return msg, color, all_active, active_coins

def get_status(node_ip, user_pass):
    mm2_active = check_mm2_status(node_ip, user_pass)
    if mm2_active:
        mm2_msg = tuilib.colorize("[MM2 active]", 'green')
    else:
        mm2_msg = tuilib.colorize("[MM2 disabled]", 'red')
    coins_status = check_coins_status(node_ip, user_pass)
    my_current_orders = my_orders(node_ip, user_pass).json()['result']
    num_orders = len(my_current_orders['maker_orders']) + len(my_current_orders['taker_orders'])
    coin_msg = tuilib.colorize("["+coins_status[0]+"]", coins_status[1])
    status_msg = mm2_msg+"   "+coin_msg
    return status_msg, mm2_active, coins_status[2], coins_status[3], num_orders

def enable(node_ip, user_pass, cointag, tx_history=True):
    coin = coinslib.coins[cointag]
    params = {'userpass': user_pass,
              'method': 'enable',
              'coin': cointag,
              'mm2':1,  
              'tx_history':tx_history,}
    r = requests.post(node_ip, json=params)
    return r

def electrum(node_ip, user_pass, cointag, tx_history=True):
    coin = coinslib.coins[cointag]
    if 'contract' in coin:
        params = {'userpass': user_pass,
                  'method': 'enable',
                  'urls':coin['electrum'],
                  'coin': cointag,
                  'swap_contract_address': coin['contract'],
                  'mm2':1,
                  'tx_history':tx_history,}
    else:
        params = {'userpass': user_pass,
                  'method': 'electrum',
                  'servers':coin['electrum'],
                  'coin': cointag,
                  'mm2':1,
                  'tx_history':tx_history,}
    r = requests.post(node_ip, json=params)
    return r

def buy(node_ip, user_pass, base, rel, basevolume, relprice):
    params ={'userpass': user_pass,
             'method': 'buy',
             'base': base,
             'rel': rel,
             'volume': basevolume,
             'price': relprice,}
    r = requests.post(node_ip,json=params)
    return r    

def my_balance(node_ip, user_pass, cointag):
    params = {'userpass': user_pass,
              'method': 'my_balance',
              'coin': cointag,}
    r = requests.post(node_ip, json=params)
    return r


def cancel_all(node_ip, user_pass):
    params = {'userpass': user_pass,
              'method': 'cancel_all_orders',
              'cancel_by': {"type":"All"},}
    r = requests.post(node_ip,json=params)
    return r

def cancel_pair(node_ip, user_pass, base, rel):
    params = {'userpass': user_pass,
              'method': 'cancel_all_orders',
              'cancel_by': {
                    "type":"Pair",
                    "data":{"base":base,"rel":rel},
                    },}
    r = requests.post(node_ip,json=params)
    return r

def setprice(node_ip, user_pass, base, rel, basevolume, relprice, trademax=False, cancel_previous=True):
    params = {'userpass': user_pass,
              'method': 'setprice',
              'base': base,
              'rel': rel,
              'volume': basevolume,
              'price': relprice,
              'max':trademax,
              'cancel_previous':cancel_previous,}
    r = requests.post(node_ip, json=params)
    return r

def recover_stuck_swap(node_ip, user_pass, uuid):
    params = {'userpass': user_pass,
              'method': 'recover_funds_of_swap',
              'params': {'uuid':uuid}
              }
    r = requests.post(node_ip, json=params)
    return r    

def withdraw(node_ip, user_pass, cointag, address, amount):
    params = {'userpass': user_pass,
              'method': 'withdraw',
              'coin': cointag,
              'to': address,
              'amount': amount,}
    r = requests.post(node_ip, json=params)
    return r 

def withdraw_all(node_ip, user_pass, cointag, address):
    params = {'userpass': user_pass,
              'method': 'withdraw',
              'coin': cointag,
              'to': address,
              'max': True}
    r = requests.post(node_ip, json=params)
    return r 

def send_raw_transaction(node_ip, user_pass, cointag, rawhex):
    params = {'userpass': user_pass,
              'method': 'send_raw_transaction',
              'coin': cointag, "tx_hex":rawhex,}
    r = requests.post(node_ip, json=params)
    return r

def my_recent_swaps(node_ip, user_pass, limit=10, from_uuid=''):
    if from_uuid=='':
        params = {'userpass': user_pass,
                  'method': 'my_recent_swaps',
                  'limit': int(limit),}
        
    else:
        params = {'userpass': user_pass,
                  'method': 'my_recent_swaps',
                  "limit": int(limit),
                  "from_uuid":from_uuid,}
    r = requests.post(node_ip,json=params)
    return r

def build_coins_data(cointag_list=''):
    if cointag_list == '':
        cointag_list = coinslib.cointags
    coins_data = {}
    cointags = []
    gecko_ids = []
    print(tuilib.colorize('Getting prices from Binance...', 'cyan'))
    for coin in cointag_list:
      coins_data[coin] = {}
      cointags.append(coin)
      coins_data[coin]['BTC_price'] = float(tuilib.get_btc_price(coin))
      time.sleep(0.05)
    # Get Coingecko API ids
    print(tuilib.colorize('Getting prices from CoinGecko...', 'cyan'))
    gecko_coins_list = requests.get(url='https://api.coingecko.com/api/v3/coins/list').json()
    for gecko_coin in gecko_coins_list:
      if gecko_coin['symbol'].upper() in cointags:
        # override to avoid batcoin
        if gecko_coin['symbol'].upper() == 'BAT':
          coins_data[gecko_coin['symbol'].upper()]['gecko_id'] = 'basic-attention-token'
          gecko_ids.append('basic-attention-token')
        else:
          coins_data[gecko_coin['symbol'].upper()]['gecko_id'] = gecko_coin['id']
          gecko_ids.append(gecko_coin['id'])

    # Get fiat price on Coingecko
    gecko_prices = gecko_fiat_prices(",".join(gecko_ids), 'usd,aud,btc').json()
    for coin_id in gecko_prices:
      for coin in coins_data:
        if 'gecko_id' in coins_data[coin]:
          if coins_data[coin]['gecko_id'] == coin_id:
            coins_data[coin]['AUD_price'] = gecko_prices[coin_id]['aud']
            coins_data[coin]['USD_price'] = gecko_prices[coin_id]['usd']
            if coins_data[coin]['BTC_price'] == 0:
              coins_data[coin]['BTC_price'] = gecko_prices[coin_id]['btc']
        else:
          coins_data[coin]['AUD_price'] = 0
          coins_data[coin]['USD_price'] = 0
    return coins_data

def gecko_fiat_prices(gecko_ids, fiat):
    url = 'https://api.coingecko.com/api/v3/simple/price'
    params = dict(ids=str(gecko_ids),vs_currencies=fiat)
    r = requests.get(url=url, params=params)
    return r

def my_swap_status(node_ip, user_pass, swap_uuid):
    params = {'userpass': user_pass,
              'method': 'my_swap_status',
              'params': {"uuid": swap_uuid},}
    r = requests.post(node_ip,json=params)
    return r

def get_unfinished_swaps(node_ip, user_pass):
    unfinished_swaps = []
    unfinished_swap_uuids = []
    recent_swaps = my_recent_swaps(node_ip, user_pass, 50).json()
    for swap in recent_swaps['result']['swaps']:
        swap_events = []
        for event in swap['events']:
            swap_events.append(event['event']['type'])
        if 'Finished' not in swap_events:
            unfinished_swaps.append(swap)
            unfinished_swap_uuids.append(swap['uuid'])
    return unfinished_swap_uuids, unfinished_swaps
