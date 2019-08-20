#!/usr/bin/env python3
import os
from os.path import expanduser
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'applibs'))
import mm2lib

home = expanduser("~")
mm2_path = home+'/pytomicDEX'

try:
    mm2lib.my_balance('http://127.0.0.1:7783', mm2lib.userpass, 'KMD')
except:
    os.chdir(mm2_path)
    mm2lib.start_mm2()
    pass
coins_data = mm2lib.build_coins_data(mm2lib.coins)

mm2lib.recent_swaps_table("http://127.0.0.1:7783", mm2lib.userpass, coins_data)
