# pytomicDEX

### A Python wrapper for using [Komodo Platform](https://komodoplatform.com/)'s [AtomicDEX](https://atomicdex.io/) from the command line  
*Note: Only tested in Ubuntu 18.04 so far.*  

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
This file needs to be customised with your own RPC password and wallet passphrase. 
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
### mm2coins.py  
Contains additional coin parameters to activate them with mm2.  
NOTE: You will also need a copy of the `coins` file from https://github.com/jl777/coins/blob/master/coins  
```
cd ~/pytomicDEX  
wget https://raw.githubusercontent.com/jl777/coins/master/coins  
```
Each coin in mm2coins.py needs values as per the examples below:  
`tag` The ticker for the coin. Must be the same as the `name` value in `coins` value.  
`min_swap` Should be higher than the `fee` value in the `coins` file, to ensure you are sending enough funds for a successful transaction.  
`api-id` Used to get current pricing data from the CoinGecko API.   
Should be the same as the `id` value for the coin from  https://www.coingecko.com/api/documentations/v3#/coins/get_coins_list   
NOTE: this feature is not yet fully implemented.   
`activate_with` Defines whether to use a native coin daemon, or an Electrum (SPV) server.   
NOTE: Native mode requires the local chain to be fully sync'd, the deamon running, and the private key for your addresses imported.   
`electrum` Defines the server and port to use for interacting with mm2 in lite mode.   
Electrum server details can be found at https://github.com/jl777/coins/tree/master/electrums (for Komodo ecosystem coins), and online for external coins (check the coin's website, github or ask the coin community).   
Note the different format that is used for ETH/ERC20 tokens in the examples below.   
`contract` This value is only required for ETH/ERC20 tokens. The contract is always `0x8500AFc0bc5214728082163326C2FF0C73f4a871`, which handles atomic swap between ETH/ERC20 tokens and other blockchains.  
ETH/ERC20 tokens can all use the same Electrum SPV servers as each other.
NOTE: Trading ETH/ERC20 coins requires a sufficient ETH balance in your mm2 ETH address to cover gas fees.   

##### Native example *(needs native daemon installed with a sync'd blockchain)*
```
    {
        'tag': 'KMD',
        'min_swap': 0.01,
        'api-id': 'komodo',
        'activate_with':'native'
    }
```
##### Electrum example
```
    {
        'tag': 'DGB',
        'api-id': 'digibyte',
        'min_swap': 10,
        'activate_with':'electrum',
        'electrum': [{"url":"electrum1.cipig.net:10059"},
                     {"url":"electrum2.cipig.net:10059"},
                     {"url":"electrum3.cipig.net:10059"}]
    }
```
##### Electrum example for Etherum and ERC20 tokens
```
    {
        'tag': 'ETH',
        'api-id': 'ethereum',
        'activate_with':'electrum',
        'min_swap': 0.01,
        'electrum': ["http://eth1.cipig.net:8555",
                     "http://eth2.cipig.net:8555",
                     "http://eth3.cipig.net:8555"],
        'contract': "0x8500AFc0bc5214728082163326C2FF0C73f4a871"
    }
```

## Usage  
### atomicDEX-cli  
Use like `./atomicDEX-cli METHOD [PARAMETERS]`  
If you use `./atomicDEX-cli` without a method, it will list the available methods.  
If you use `./atomicDEX-cli METHOD` for methods that require parameters, it will list the parameters required (and the order they need to be in).  

### mm2lib.py  
Contains functions to translate mm2 curl methods to use the python requests library.   
Not all methods or optional parameters are exposed in the CLI as yet.  
