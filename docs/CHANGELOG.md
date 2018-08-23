# ChangeLog - tbears

## 1.0.3 - 2018-08-24
* Add interactive mode. Activate with 'console' command
* Add '-p' option to 'deploy' command. Now can enter keystore file password as argument.
* Add block manager. 
* Rename tbears_tutorial.md to README.md

## 1.0.0 - 2018-08-15
* Tbears service support 'call', 'sendtx' and 'genconf' command
    * call : Send icx_call request
    * sendtx : Send icx_sendTransaction request
    * genconf : Generate tbears configuration files. (tbears_server_config.json, tbears_cli_config.json)

## 0.9.8 - 2018-08-09
* Tbears service support 'lastblock', 'blockbyhash' and 'blockbyheight' command
    * Can query block information on tbears service now
* Proofread tbears_tutorial.md

## 0.9.7 - 2018-08-03
* Fix the bug that '-a' option of start command does not work
* Exception logs are saved separately

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
