#!/usr/bin/env python3
import os
import sys
import json
import time
import requests
import subprocess
from subprocess import Popen
from os.path import expanduser
from lib import coinslib

# Get and set config
cwd = os.getcwd()
home = expanduser("~")
mm2_path= home+"/pytomicDEX"
mm2log_path= home+"/pytomicDEX/logs"

orderbook_json = '/var/www/html/json/mm2_orderbook.json'
orderbook_json2 = '/var/www/html/json/mm2_orderbook2.json'

def get_modified_time(file):
    #return time.ctime(os.path.getmtime(file))
    return os.path.getmtime(file)

with open(mm2_path+"/MM2.json") as j:
  mm2json = json.load(j)

gui = mm2json['gui']
netid = mm2json['netid']
passphrase = mm2json['passphrase']
user_pass = mm2json['rpc_password']
rpc_password = mm2json['rpc_password']
node_ip = "http://127.0.0.1:7783"

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

def start_mm2(logfile):
  mm2_output = open(logfile,'w+')
  os.chdir(mm2_path)
  Popen(["./mm2"], stdout=mm2_output, stderr=mm2_output, universal_newlines=True)
  print("Marketmaker 2 started. Use 'tail -f "+logfile+"' for mm2 console messages")
  os.chdir(cwd)

  
def activate_all(node_ip, user_pass):
    for coin in coinslib.coins:
        if coinslib.coins[coin]['activate_with'] == 'native':
            r = enable(node_ip, user_pass, coin)
        else:
            r = electrum(node_ip, user_pass, coin)


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

def orderbook(node_ip, user_pass, base, rel):
    params = {'userpass': user_pass,
              'method': 'orderbook',
              'base': base, 'rel': rel,}
    r = requests.post(node_ip, json=params)
    return r

def get_orders_json(node_ip, user_pass, coins):
    orders = []
    ask_json = []
    bid_json = []
    for base in coins:
        for rel in coins:
            if base != rel:
                orderbook_response = orderbook(node_ip, user_pass, base, rel).json()
                orders.append(orderbook_response)
    for pair in orders:
        if len(pair['asks']) > 0:
            baserel = pair['rel']+"/"+pair['base']
            print(baserel)
            for ask in pair['asks']:
                print(str(ask['price'])[:12]+" "+pair['rel']+" per "+pair['base']+" ("+str(ask['maxvolume'])+" "+pair['base']+" available)")
                baserel = pair['base']+"/"+pair['rel']
                ask_json.append({"pair":baserel, "price":str(str(ask['price'])[:12]+" "+pair['rel']), "volume":str(str(ask['maxvolume'])+" "+pair['base'])})
           # for bid in pair['bids']:
            #    print(str(bid['price'])+" "+pair['base']+" per "+pair['rel']+" ("+str(bid['maxvolume'])+" available)")
             #   bid_json.append({"baserel":baserel, "price":bid['price'], "volume":str(bid['maxvolume'])})
    return ask_json, bid_json

mm2_running = check_mm2_status(node_ip, user_pass)

if mm2_running:
    orderbook = get_orders_json(node_ip, user_pass, coinslib.coins)
    table_data = orderbook[0]+orderbook[1]
else:
    start_mm2('mm2.log')
    time.sleep(10)
    activate_all(node_ip, user_pass)
    orderbook = get_orders_json(node_ip, user_pass, coinslib.coins)
    table_data = orderbook[0]+orderbook[1]
    pass
table_json = str(table_data).replace("'",'"')
print(table_json)
jsonfile = orderbook_json
if os.path.isfile(orderbook_json2):
    pass
else:
    jsonfile = orderbook_json2
try:
    if os.path.isfile(orderbook_json2):
        print(get_modified_time(orderbook_json))
        print(get_modified_time(orderbook_json2))
        if get_modified_time(orderbook_json) > get_modified_time(orderbook_json2):
            jsonfile = orderbook_json2
except Exception as e:
    jsonfile = orderbook_json
    print(e)
    pass
print(jsonfile)
with open(jsonfile, "w+") as f:
    f.write(str(table_json))
