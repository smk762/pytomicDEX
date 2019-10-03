# pytomicDEX

### A Python TUI for using [Komodo Platform](https://komodoplatform.com/)'s [AtomicDEX](https://atomicdex.io/) from the command line  
*Note: Only tested in Ubuntu 18.04 so far.*  

![pytomicDEX TUI](https://i.imgur.com/eFjW83f.png)

#### Dependancies  
```
pip3 install requests json subprocess  
```  
#### Recommended reading  
https://developers.atomicdex.io/  
https://developers.komodoplatform.com/  
https://komodoplatform.com/atomic-swaps/  

## Setup  

### MM2.json
This file needs to be customised with your own RPC password and wallet passphrase. If you run the TUI without an MM2.json file, a menu option to create one will be available.   
The netid value is set to 9999 by default (used for public beta testing), but can be changed to a different value to allow for testing privately (e.g. between two nodes with a unique shared netid).  
```
cp MM2_example.json MM2.json  
nano MM2.json
```
Update the rpc_password, passphrase, userhome and netid (optional) to custom values.  
`gui` Leave this as the default value `MM2GUI`    
`netid` Defines the network you will trade on. `9999` is being used for beta testing and is the most active.   
To trade directly with someone on a private network, the seller and buyer can set this to a different custom value.  
`rpc_password` Should be at least 12 alphanumeric characters.  
This authenticates the user for communicating with the mm2 daemon.   
`passphrase` This will be used to generate your wallet addresses.   
Should be 12 words minimum, 24 words are recommended.  
You can use Luke Child's https://dogeseed.com/ to generate these words (preferably offline).  
`userhome` Set this to the home folder of the user installing this repo.  
```
{
"gui":"MM2GUI",
"netid":9999,
"rpc_password":"ENTER SECURE RPC PASSWORD",
"passphrase":"ENTER A SECURE PASSPHRASE",
"userhome":"/home/YOURUSERNAME/"
}
```

### lib/coinslib.py  

Contains additional coin parameters to activate them with mm2, defines block explorers, binance trade parameters, and which coins you want to buy/sell using the bot. The default file is populated with 20 mm2 compatible coins, iuncluding those present in the mobile app.   
NOTE: You will also need a copy of the `coins` file from https://github.com/jl777/coins/blob/master/coins  

```
cd ~/pytomicDEX  
wget https://raw.githubusercontent.com/jl777/coins/master/coins  
```

Each coin in coinslib.py needs values as per the examples below:  
`tag` The ticker for the coin. Must be the same as the `name` value in `coins` value.  
`min_swap` Should be higher than the `fee` value in the `coins` file, to ensure you are sending enough funds for a successful transaction.  
`api-id` Used to get current pricing data from the CoinGecko API.   
Should be the same as the `id` value for the coin from  https://www.coingecko.com/api/documentations/v3#/coins/get_coins_list   
NOTE: this feature is not yet fully implemented.   
`activate_with` Defines whether to use a native coin daemon, or an Electrum (SPV) server.   
NOTE: Native mode requires the local chain to be fully sync'd, the deamon running, and the private key for your addresses imported.   
`reserve_balance:` number of coins to keep in MM2 wallet (excess will be sent your to Binance wallet)   
`premium:` Value relative to Binance market rate to setprices as marketmaker. E.g. a value of 1.05 will set your sell price 5% above Binance market price.   
`minQty; maxQty; stepSize:` Values as required for setting orders on Binance, available from https://api.binance.com/api/v1/exchangeInfo   
`bot_sell; bot_buy:` Set to True or False to indicate whether or not you want the bot to buy/sell the coin.   
`electrum` Defines the server and port to use for interacting with mm2 in lite mode.   
Electrum server details can be found at https://github.com/jl777/coins/tree/master/electrums (for Komodo ecosystem coins), and online for external coins (check the coin's website, github or ask the coin community).   
Note the different format that is used for ETH/ERC20 tokens in the examples below.   
`contract` This value is only required for ETH/ERC20 tokens.   
The contract is always `0x8500AFc0bc5214728082163326C2FF0C73f4a871`, which handles atomic swap between ETH/ERC20 tokens and other blockchains.  
ETH/ERC20 tokens can all use the same Electrum SPV servers as each other.   
NOTE: Trading ETH/ERC20 coins requires a sufficient ETH balance in your mm2 ETH address to cover gas fees.   

##### Native example *(needs native daemon installed with a sync'd blockchain)*
```json
    "KMD":{
        "min_swap": 0.01,
        "api-id": "komodo",
        "activate_with":"native",
        "tx_explorer":"https://www.kmdexplorer.io/tx",
        "reserve_balance":1000,
        "premium":1.03,
        "min_swap":0.1,
        "minQty":"0.01000000",
        "maxQty":"90000000.00000000",
        "stepSize":"0.01000000",
        "bot_sell": True,
        "bot_buy": True
    },
```
##### Electrum example
```json
    "KMD":{
        "min_swap": 0.01,
        "api-id": "komodo",
        "activate_with":"electrum",
        "tx_explorer":"https://www.kmdexplorer.io/tx",
        "electrum": [{"url":"electrum1.cipig.net:10001"},
                     {"url":"electrum2.cipig.net:10001"},
                     {"url":"electrum3.cipig.net:10001"}],
        "reserve_balance":1000,
        "premium":1.03,
        "min_swap":0.1,
        "minQty":"0.01000000",
        "maxQty":"90000000.00000000",
        "stepSize":"0.01000000",
        "bot_sell": True,
        "bot_buy": True
    },
```
##### Electrum example for Etherum and ERC20 tokens
```json
    "ETH":{
        "api-id": "ethereum",
        "activate_with":"electrum",
        "min_swap": 0.01,
        "tx_explorer":"https://etherscan.io/tx",
        "electrum": ["http://eth1.cipig.net:8555",
                     "http://eth2.cipig.net:8555",
                     "http://eth3.cipig.net:8555"],
        "contract": "0x8500AFc0bc5214728082163326C2FF0C73f4a871",
        "reserve_balance":2,
        "premium":1.03,
        "min_swap":0.01,
        "minQty":"0.001000000",
        "maxQty":"100000.00000000",
        "stepSize":"0.001000000",
        "bot_sell": True,
        "bot_buy": True
    },
```

### api_keys.json 
This file is needed to get prices from the Binance API, and could also be used to manage deposits and withdrawls between your MM2 wallet and Binance wallets (work in progress).

```json
{
        "binance_key":"YOUR_BINANCE_KEY",
        "binance_secret":"YOUR_BINANCE_SECRET"
}
```
