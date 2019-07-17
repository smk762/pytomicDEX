# pytomicDEX

### A Python wrapper for using [Komodo Platform](https://komodoplatform.com/)'s [AtomicDEX](https://atomicdex.io/) from the command line

See https://developers.atomicdex.io/ for more information

*Note: Only tested in Ubuntu 18.04 so far.*

### MM2.json
This file needs to be customised with your own RPC password and wallet passphrase. 
The netid value is set to 9999 by default (used for public beta testing), but can be changed to a different value to allow for testing privately (e.g. between two nodes with a unique shared netid).

### atomicDEX-cli
Use like `./atomicDEX-cli METHOD [PARAMETERS]`
Supports methods detailed in https://developers.atomicdex.io/basic-docs/atomicdex/atomicdex-api.html

### mm2lib.py
Contains functions to translate mm2 curl methods. Requires python requests library. Not all functions are exposed in the CLI as yet.

### mm2coins.py
Contains additional coin parameters such as electrums and coingecko prices API (not yet exposed to ./atomicDEX-cli)
