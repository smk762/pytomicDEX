#!/usr/bin/env python3
import os
import sys
import json
import time
import requests
import subprocess
from os.path import expanduser
from lib import rpclib, tuilib, coinslib
import binance_api

# Get and set config
cwd = os.getcwd()
home = expanduser("~")
with open(cwd+"/MM2.json") as j:
  mm2json = json.load(j)

gui = mm2json['gui']
netid = mm2json['netid']
passphrase = mm2json['passphrase']
userpass = mm2json['rpc_password']
rpc_password = mm2json['rpc_password']
local_ip = "http://127.0.0.1:7783"

mm2_main = {}
mm2_main['header'] = "\
          _                  _      _____  ________   __  \n\
     /\  | |                (_)    |  __ \|  ____\ \ / /  \n\
    /  \ | |_ ___  _ __ ___  _  ___| |  | | |__   \ V /   \n\
   / /\ \| __/ _ \| '_ ` _ \| |/ __| |  | |  __|   > <    \n\
  / ____ \ || (_) | | | | | | | (__| |__| | |____ / . \   \n\
 /_/    \_\__\___/|_| |_| |_|_|\___|_____/|______/_/ \_\  \n\
 \n\
 "
                                                                                                              
mm2_main['menu'] = [
    # TODO: Have to implement here native oracle file uploader / reader, should be dope
    # TODO: data publisher / converter for different types
    {"Stop MarketMaker 2": tuilib.stop_mm2},
    {"Activate coins": tuilib.activate_all},
    {"Show balances table": tuilib.show_balances_table}
    
]
mm2_main['author'] = '{:^55}'.format('Welcome to the AtomicDEX TUI v0.1 by Thorn Mennet')

ip_user_params_list = ["Stop MarketMaker 2", "View/withdraw balances", "Activate coins", "View/buy from orderbook", "View/cancel my orders"]
def main():
    menu = mm2_main
    while True:
        os.system('clear')
        print(tuilib.colorize(menu['header'], 'lightgreen'))
        print(tuilib.colorize(menu['author'], 'cyan'))
        status = rpclib.get_status(local_ip, userpass)
        print(status[0])
        # Build Menu
        if status[1] is False:
            menuItems = [{"Start MarketMaker 2": tuilib.start_mm2}]
        else:
            menuItems = [{"Stop MarketMaker 2": tuilib.stop_mm2}]
            if status[2] is False:
                menuItems.append({"Activate coins": tuilib.activate_all})
            if len(status[3]) > 0:
                menuItems.append({"View/withdraw balances": tuilib.show_balances_table})
                menuItems.append({"View/buy from orderbook": tuilib.show_orderbook_pair})
                menuItems.append({"View/cancel my orders": tuilib.show_orders})

        menuItems.append({"Exit TUI": tuilib.exit})
        print("\n")
        for item in menuItems:
            print(tuilib.colorize("[" + str(menuItems.index(item)) + "] ", 'blue') + tuilib.colorize(list(item.keys())[0],'blue'))
        choice = input(tuilib.colorize("Select menu option: ", 'orange'))
        try:
            if int(choice) < 0:
                raise ValueError
            # Call the matching function
            if list(menuItems[int(choice)].keys())[0] == "Exit TUI":
                list(menuItems[int(choice)].values())[0]()
            elif list(menuItems[int(choice)].keys())[0].find('Menu') != -1:
                submenu(list(menuItems[int(choice)].values())[0])
            elif list(menuItems[int(choice)].keys())[0] in ip_user_params_list:
                list(menuItems[int(choice)].values())[0](local_ip, userpass)
            else:
                list(menuItems[int(choice)].values())[0]()
        except (ValueError, IndexError):
            pass

if __name__ == "__main__":
    while True:
        os.system('clear')
        print("\n\n")
        with (open("lib/logo.txt", "r")) as logo:
            for line in logo:
                parts = line.split(' ')
                row = ''
                for part in parts:
                    if part.find('.') == -1:
                        row += tuilib.colorize(part, 'blue')
                    else:
                        row += tuilib.colorize(part, 'black')
                print(row, end='')
                #print(line, end='')
                time.sleep(0.04)
            time.sleep(0.4)
        print("\n")
        break
    main()
