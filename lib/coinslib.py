coins = {
    "KMD":{
        "min_swap": 0.01,
        "api-id": "komodo",
        "activate_with":"electrum",
        "tx_explorer":"https://www.kmdexplorer.io/tx",
        "electrum": [{"url":"electrum1.cipig.net:10001"},
                     {"url":"electrum2.cipig.net:10001"},
                     {"url":"electrum3.cipig.net:10001"}]
    },
    "DEX":{
        "min_swap": 0.1,
        "api-id": "",
        "activate_with":"electrum",
        "tx_explorer":"https://dex.explorer.dexstats.info/tx",
        "electrum": [{"url":"electrum1.cipig.net:10006"},
                     {"url":"electrum2.cipig.net:10006"},
                     {"url":"electrum3.cipig.net:10006"}]
    },
    "VRSC":{        
        "min_swap": 0.1,
        "activate_with":"electrum",
        "tx_explorer":"https://explorer.veruscoin.io/tx",
        "electrum": [{"url":"el0.vrsc.0x03.services:10000"},
                     {"url":"el1.vrsc.0x03.services:10000"},
                     {"url":"electrum1.cipig.net:10021"},
                     {"url":"electrum2.cipig.net:10021"},
                     {"url":"electrum3.cipig.net:10021"}]
    },
    "BTC":{
        "api-id": "bitcoin",
        "activate_with":"electrum",
        "tx_explorer":"https://explorer.bitcoin.com/bch/tx",
        "electrum": [{"url":"electrum1.cipig.net:10000"},
                     {"url":"electrum2.cipig.net:10000"},
                     {"url":"electrum3.cipig.net:10000"}]
    },
    "BCH":{
        "min_swap": 0.01,
        "activate_with":"electrum",
        "tx_explorer":"https://explorer.bitcoin.com/bch/tx",
        "electrum": [{"url":"bch.imaginary.cash:50001"},
                     {"url":"electroncash.dk:50001"},
                     {"url":"electron-cash.dragon.zone:50001"}]
    },
    "ETH":{
        "api-id": "ethereum",
        "activate_with":"electrum",
        "min_swap": 0.01,
        "tx_explorer":"https://etherscan.io/tx",
        "electrum": ["http://eth1.cipig.net:8555",
                     "http://eth2.cipig.net:8555",
                     "http://eth3.cipig.net:8555"],
        "contract": "0x8500AFc0bc5214728082163326C2FF0C73f4a871"
    },
    "DASH":{
        "api-id": "dash",
        "min_swap": 0.01,
        "activate_with":"electrum",
        "tx_explorer":"https://explorer.dash.org/tx",
        "electrum":  [{"url":"electrum1.cipig.net:10061"},
                      {"url":"electrum2.cipig.net:10061"},
                      {"url":"electrum3.cipig.net:10061"}]
    },
    "LTC":{
        "api-id": "litecoin",
        "min_swap": 0.01,
        "activate_with":"electrum",
        "tx_explorer":"https://live.blockcypher.com/ltc/tx",
        "electrum": [{"url":"electrum-ltc.bysh.me:50001"},
                     {"url":"electrum.ltc.xurious.com:50001"},
                     {"url":"ltc.rentonisk.com:50001"},
                     {"url":"backup.electrum-ltc.org:50001"}]
    },
    "USDC":{
        "min_swap": 0.5,
        "api-id": "usd-coin",
        "activate_with":"electrum",
        "tx_explorer":"https://etherscan.io/tx",
        "electrum": ["http://eth1.cipig.net:8555",
                     "http://eth2.cipig.net:8555",
                     "http://eth3.cipig.net:8555"],
        "contract": "0x8500AFc0bc5214728082163326C2FF0C73f4a871"
    },
    "DOGE":{
        "api-id": "dogecoin",
        "activate_with":"electrum",
        "tx_explorer":"https://live.blockcypher.com/doge/tx",
        "min_swap": 10,
        "electrum": [{"url":"electrum1.cipig.net:10060"},
                     {"url":"electrum2.cipig.net:10060"},
                     {"url":"electrum3.cipig.net:10060"}]
    },
    "DGB":{
        "api-id": "digibyte",
        "min_swap": 10,
        "activate_with":"electrum",
        "tx_explorer":"https://digiexplorer.info/tx",
        "electrum": [{"url":"electrum1.cipig.net:10059"},
                     {"url":"electrum2.cipig.net:10059"},
                     {"url":"electrum3.cipig.net:10059"}]
    },
    "QTUM":{
        "min_swap": 4,
        "activate_with":"electrum",
        "tx_explorer":"https://qtum.info/tx",
        "electrum": [{"url":"s1.qtum.info:50001"},
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
    "RFOX":{
        "min_swap": 5,
        "activate_with":"electrum",
        "tx_explorer":"https://rfox.explorer.dexstats.info/tx",
        "electrum": [{"url":"electrum1.cipig.net:10034"},
                     {"url":"electrum2.cipig.net:10034"},
                     {"url":"electrum3.cipig.net:10034"}]
    },
    "ZILLA":{
        "min_swap": 5,
        "activate_with":"electrum",
        "tx_explorer":"https://zilla.explorer.dexstats.info/tx",
        "electrum": [{"url":"electrum1.cipig.net:10028"},
                     {"url":"electrum2.cipig.net:10028"},
                     {"url":"electrum3.cipig.net:10028"}]
    },
    "RVN":{
        "min_swap": 5,
        "activate_with":"electrum",
        "tx_explorer":"https://ravencoin.network/tx",
        "electrum": [{"url":"electrum1.cipig.net:10051"},
                     {"url":"electrum2.cipig.net:10051"},
                     {"url":"electrum3.cipig.net:10051"}]
    },
    "BAT":{
        "min_swap": 0.5,
        "activate_with":"electrum",
        "api-id": "basic-attention-token",
        "tx_explorer":"https://etherscan.io/tx",
        "electrum": ["http://eth1.cipig.net:8555",
                     "http://eth2.cipig.net:8555",
                     "http://eth3.cipig.net:8555"],
        "contract": "0x8500AFc0bc5214728082163326C2FF0C73f4a871"
    },
    "LINK":{
        "min_swap": 0.5,
        "activate_with":"electrum",
        "api-id": "chainlink",
        "tx_explorer":"https://etherscan.io/tx",
        "electrum": ["http://eth1.cipig.net:8555",
                     "http://eth2.cipig.net:8555",
                     "http://eth3.cipig.net:8555"],
        "contract": "0x8500AFc0bc5214728082163326C2FF0C73f4a871"
    },
    "LABS":{
        "min_swap": 5,
        "activate_with":"electrum",
        "tx_explorer":"https://labs.explorer.dexstats.info/tx",
        "electrum": [{"url":"electrum1.cipig.net:10019"},
                     {"url":"electrum2.cipig.net:10019"},
                     {"url":"electrum3.cipig.net:10019"}]
    },
    "AXE":{
        "min_swap": 1,
        "api-id": "axe",
        "activate_with":"electrum",
        "tx_explorer":"https://etherscan.io/tx",
        "electrum": [{"url":"electrum1.cipig.net:10057"},
                     {"url":"electrum2.cipig.net:10057"},
                     {"url":"electrum3.cipig.net:10057"}]
    },
    "HUSH":{
        "min_swap": 1,
        "api-id": "hush",
        "activate_with":"electrum",
        "tx_explorer":"https://hush3.komodod.com/t",
        "electrum": [{"url":"electrum1.cipig.net:10064"},
                     {"url":"electrum2.cipig.net:10064"},
                     {"url":"electrum3.cipig.net:10064"}]
    }
}

# Input coins you want to trade here. 
# reserve_balance: excess funds will be sent to your Binance wallet
# premium: value relative to binance market rate to setprices as marketmaker.
# min/max/stepsize need to be set from values from 
# https://api.binance.com/api/v1/exchangeInfo
trading_list = {
    "LTC":{
        "reserve_balance":2,
        "premium":1.03,
        "min_swap":0.01,
        "minQty":"0.01000000",
        "maxQty":"100000.00000000",
        "stepSize":"0.01000000"
    },
    "DASH":{
        "reserve_balance":2,
        "premium":1.03,
        "min_swap":0.01,
        "minQty":"0.00100000",
        "maxQty":"900000.00000000",
        "stepSize":"0.00100000"
    },
    "BCH":{
        "reserve_balance":2,
        "premium":1.03,
        "min_swap":0.01,
        "minQty":"0.00001000",
        "maxQty":"900000.00000000",
        "stepSize":"0.00001000"
    },
    "RVN":{
        "reserve_balance":2500,
        "premium":1.03,
        "min_swap":1,
        "minQty":"1.00000000",
        "maxQty":"90000000.00000000",
        "stepSize":"1.00000000"
    },
    "DOGE":{
        "reserve_balance":20000,
        "premium":1.0377,
        "min_swap":10,
        "minQty":"1.00000000",
        "maxQty":"90000000.00000000",
        "stepSize":"1.00000000"
    },
    "QTUM":{
        "reserve_balance":50,
        "premium":1.03,
        "min_swap":3.4,
        "minQty":"0.01000000",
        "maxQty":"10000000.00000000",
        "stepSize":"0.01000000"
    },
    "KMD":{
        "reserve_balance":1000,
        "premium":1.03,
        "min_swap":0.1,
        "minQty":"0.01000000",
        "maxQty":"90000000.00000000",
        "stepSize":"0.01000000"
    },
    "ETH":{
        "reserve_balance":2,
        "premium":1.03,
        "min_swap":0.01,
        "minQty":"0.001000000",
        "maxQty":"100000.00000000",
        "stepSize":"0.001000000"
    },
    "BAT":{
        "reserve_balance":500,
        "premium":1.03,
        "min_swap":1,
        "minQty":"1.00000000",
        "maxQty":"90000000.00000000",
        "stepSize":"1.00000000"
    }
}
Not_on_atomicdex_mobile = {
    "LINK":{
        "reserve_balance":20,
        "premium":1.03,
        "minQty":"1.00000000",
        "maxQty":"90000000.00000000",
        "stepSize":"1.00000000"
    }
}


cointags = []
for coin in coins:
  cointags.append(coin)