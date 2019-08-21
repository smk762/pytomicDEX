# Input coins you want to activate in MM2 Here
coins = [    
    {
        'tag': 'KMD',
        'min_swap': 0.01,
        'api-id': 'komodo',
        'activate_with':'electrum',
        'electrum': [{"url":"electrum1.cipig.net:10001"},
                     {"url":"electrum2.cipig.net:10001"},
                     {"url":"electrum3.cipig.net:10001"}]
    },
    {
        'tag': 'VRSC',
        'min_swap': 0.1,
        'activate_with':'electrum',
        'electrum': [{"url":"el0.vrsc.0x03.services:10000"},
                     {"url":"el1.vrsc.0x03.services:10000"},
                     {"url":"electrum1.cipig.net:10021"},
                     {"url":"electrum2.cipig.net:10021"},
                     {"url":"electrum3.cipig.net:10021"}]
    },
    {
        'tag': 'BTC',
        'api-id': 'bitcoin',
        'activate_with':'electrum',
        'electrum': [{"url":"electrum1.cipig.net:10000"},
                     {"url":"electrum2.cipig.net:10000"},
                     {"url":"electrum3.cipig.net:10000"}]
    },
    {
        'tag': 'BCH',
        'min_swap': 0.01,
        'activate_with':'electrum',
        'electrum': [{"url":"bch.imaginary.cash:50001"},
                     {"url":"electroncash.dk:50001"},
                     {"url":"electron-cash.dragon.zone:50001"}]
    },
    {
        'tag': 'ETH',
        'api-id': 'ethereum',
        'activate_with':'electrum',
        'min_swap': 0.01,
        'electrum': ["http://eth1.cipig.net:8555",
                     "http://eth2.cipig.net:8555",
                     "http://eth3.cipig.net:8555"],
        'contract': "0x8500AFc0bc5214728082163326C2FF0C73f4a871"
    },
    {
        'tag': 'DASH',
        'api-id': 'dash',
        'min_swap': 0.01,
        'activate_with':'electrum',
        'electrum':  [{"url":"electrum1.cipig.net:10061"},
                      {"url":"electrum2.cipig.net:10061"},
                      {"url":"electrum3.cipig.net:10061"}]
    },
    {
        'tag': 'LTC',
        'api-id': 'litecoin',
        'min_swap': 0.01,
        'activate_with':'electrum',
        'electrum': [{"url":"electrum-ltc.bysh.me:50001"},
                     {"url":"electrum.ltc.xurious.com:50001"},
                     {"url":"ltc.rentonisk.com:50001"},
                     {"url":"backup.electrum-ltc.org:50001"}]
    },
    {
        'tag': 'USDC',
        'min_swap': 0.5,
        'api-id': 'usd-coin',
        'activate_with':'electrum',
        'electrum': ["http://eth1.cipig.net:8555",
                     "http://eth2.cipig.net:8555",
                     "http://eth3.cipig.net:8555"],
        'contract': "0x8500AFc0bc5214728082163326C2FF0C73f4a871"
    },
    {
        'tag': 'DOGE',
        'api-id': 'dogecoin',
        'activate_with':'electrum',
        'min_swap': 10,
        'electrum': [{"url":"electrum1.cipig.net:10060"},
                     {"url":"electrum2.cipig.net:10060"},
                     {"url":"electrum3.cipig.net:10060"}]
    },
    {
        'tag': 'DGB',
        'api-id': 'digibyte',
        'min_swap': 10,
        'activate_with':'electrum',
        'electrum': [{"url":"electrum1.cipig.net:10059"},
                     {"url":"electrum2.cipig.net:10059"},
                     {"url":"electrum3.cipig.net:10059"}]
    },
    {
        'tag': 'QTUM',
        'min_swap': 5,
        'activate_with':'electrum',
        'electrum': [{"url":"s1.qtum.info:50001"},
                     {"url":"s2.qtum.info:50001"},
                     {"url":"s3.qtum.info:50001"},
                     {"url":"s4.qtum.info:50001"},
                     {"url":"s5.qtum.info:50001"},
                     {"url":"s6.qtum.info:50001"},
                     {"url":"s7.qtum.info:50001"},
                     {"url":"s8.qtum.info:50001"},
                     {"url":"s9.qtum.info:50001"}
                     ]
    },
    {
        'tag': 'RFOX',
        'min_swap': 5,
        'activate_with':'electrum',
        'electrum': [{"url":"electrum1.cipig.net:10034"},
                     {"url":"electrum2.cipig.net:10034"},
                     {"url":"electrum3.cipig.net:10034"}]
    },

    {
        'tag': 'ZILLA',
        'min_swap': 5,
        'activate_with':'electrum',
        'electrum': [{"url":"electrum1.cipig.net:10028"},
                     {"url":"electrum2.cipig.net:10028"},
                     {"url":"electrum3.cipig.net:10028"}]
    },

    {
        'tag': 'RVN',
        'min_swap': 5,
        'activate_with':'electrum',
        'electrum': [{"url":"electrum1.cipig.net:10051"},
                     {"url":"electrum2.cipig.net:10051"},
                     {"url":"electrum3.cipig.net:10051"}]
    },
    {
        'tag': 'BAT',
        'min_swap': 0.5,
        'activate_with':'electrum',
        'api-id': 'basic-attention-token',
        'electrum': ["http://eth1.cipig.net:8555",
                     "http://eth2.cipig.net:8555",
                     "http://eth3.cipig.net:8555"],
        'contract': "0x8500AFc0bc5214728082163326C2FF0C73f4a871"
    },
    {
        'tag': 'RICK',
        'min_swap': 1,
        'activate_with':'electrum',
        'electrum': [{"url":"electrum1.cipig.net:10017"},
                     {"url":"electrum2.cipig.net:10017"},
                     {"url":"electrum3.cipig.net:10017"}]
    },
    {
        'tag': 'MORTY',
        'min_swap': 1,
        'activate_with':'electrum',
        'electrum': [{"url":"electrum1.cipig.net:10018"},
                     {"url":"electrum2.cipig.net:10018"},
                     {"url":"electrum3.cipig.net:10018"}]
    },
    {
        'tag': 'LABS',
        'min_swap': 5,
        'activate_with':'electrum',
        'electrum': [{"url":"electrum1.cipig.net:10019"},
                     {"url":"electrum2.cipig.net:10019"},
                     {"url":"electrum3.cipig.net:10019"}]
    }
]

# Input coins you want to trade here. 
# reserve_balance: excess funds will be sent to your Binance wallet
# premium: value relative to binance market rate to setprices as marketmaker.
# min/max/stepsize need to be set from values from https://api.binance.com/api/v1/exchangeInfo
trading_list = {
    "LTC":{
        "reserve_balance":2,
        "premium":1.0777,
        "minQty":"0.01000000",
        "maxQty":"100000.00000000",
        "stepSize":"0.01000000"
    },
    "DASH":{
        "reserve_balance":2,
        "premium":1.0777,
        "minQty":"0.00100000",
        "maxQty":"900000.00000000",
        "stepSize":"0.00100000"
    },
    "BCH":{
        "reserve_balance":2,
        "premium":1.0777,
        "minQty":"0.00001000",
        "maxQty":"900000.00000000",
        "stepSize":"0.00001000"
    },
    "RVN":{
        "reserve_balance":2500,
        "premium":1.0777,
        "minQty":"1.00000000",
        "maxQty":"90000000.00000000",
        "stepSize":"1.00000000"
    },
    "DOGE":{
        "reserve_balance":20000,
        "premium":1.0777,
        "minQty":"1.00000000",
        "maxQty":"90000000.00000000",
        "stepSize":"1.00000000"
    },
    "QTUM":{
        "reserve_balance":50,
        "premium":1.0777,
        "minQty":"0.01000000",
        "maxQty":"10000000.00000000",
        "stepSize":"0.01000000"
    },
    "KMD":{
        "reserve_balance":1000,
        "premium":1.0777,
        "minQty":"0.01000000",
        "maxQty":"90000000.00000000",
        "stepSize":"0.01000000"
    },
    "ETH":{
        "reserve_balance":2,
        "premium":1.0777,
        "minQty":"0.001000000",
        "maxQty":"100000.00000000",
        "stepSize":"0.001000000"
    },
}