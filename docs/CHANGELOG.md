# ChangeLog - tbears

## 0.9.6.1 - 2018-07-31

* Fix configuration file loading bug
* Add commands (lastblock, blockbyhash, blockbyheight)
    * update tbears_tutorial.md
   
## 0.9.6 - 2018-07-27

* Support log rotation with ICON Commons
* Add commands (balance, totalsupply, scoreapi)
    * tbears_tutorial.md is out of date. It will be updated later

## 0.9.5.1 - 2018-07-24

* Improve configuration files
    * check 'Configuration Files' chapter of tbears_tutorial.md

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