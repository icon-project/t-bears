# ChangeLog - tbears

## 0.9.5 - 2018-07-20

* Use ICON common package for configuration file and logging module
* Improve the output message of deploy command
    * Success response : print transaction hash in response
    * Error response : print response message
* Add command
    * txresult : Get transaction result by transaction hash
    * transfer: Transfer ICX coin
* Add network ID
    *  Check icx_sendTransaction method parameter 'nid' of tbears JSON-RPC API document
    * 'Add -n', '--nid' option on deploy command.