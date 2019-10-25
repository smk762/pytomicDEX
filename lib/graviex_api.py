#!/usr/bin/env python3
import hashlib
import hmac
import urllib2
import urllib
import time
import ssl

try:
    with open(sys.path[0]+"/api_keys.json") as keys_j:
        keys_json = json.load(keys_j)
except FileNotFoundError:
    print("You need api_keys.json file in PytomicDEX directory")
    print("Check api_keys_example.json, create file and run me again")
    exit()

access_key = keys_json['graviex_key']
secret_key = keys_json['graviex_secret']
base_url = 'https://graviex.net/api/v2'

# https://graviex.net/documents/api_v2
# https://graviex.net/api/v2/order_book.json?market=labskmd
# https://graviex.net/api/v2/order_book.json?market=labsbtc
# https://graviex.net/api/v2/deposit_address.json

get_endpoints = []
post_endpoints = []

# 0. making ssl context - verify should be turned off
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def build_query(method, endpoint, params=''):
	epoch_time = str(int(time.time()))+'000'
	request = 'access_key='+access_key+'&tonce='+epoch_time+params
	message = method+'|'+endpoint+'|'+request
    signature = hmac.new(secret_key,message,hashlib.sha256).hexdigest()
    if method == 'GET':
  	    query = base_url+"/"+endpoint+'?'+request+'&signature='+signature
    	content = urllib2.urlopen(query, context=ctx).read()
    elif method == 'POST':
    	query = base_url+"/"+endpoint+'?'+request
    	result = urllib2.Request(query, urllib.urlencode({'signature' : signature}))
    	content = urllib2.urlopen(result, context=ctx).read()
    print(content)
