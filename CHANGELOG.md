# ChangeLog - T-Bears

## 1.1.0 - 2018-11-29
* Add test command
* Add SCORE integration test library
* Add -v, --verbose option
* Modify init command to generate test code
* Deprecate samples command

## 1.0.6.2 - 2018-10-19
* Fix configuration file loading bug
* Modify python version requirements to 3.6.5+

## 1.0.6.1 - 2018-10-16
* Fix deploy command bug

## 1.0.6 - 2018-10-12
* Add '--step-limit' option to the 'deploy' and 'transfer' commands
* Support docker image - iconloop/tbears
* Fix minor bugs

## 1.0.5.1 - 2018-09-07
* Remove sanic package from dependencies

## 1.0.5 - 2018-09-06
* '-t' option of the deploy command deprecated. Deploy command supports zip type only.
* Remove runtime warning message of T-Bears block_manager.
* Modify the deploy command. Deploy command can get directory and zip file as a project.
* Fix the transfer command to read 'stepLimit' from the configuration file.
* Add test account 'test1' in genesis block.
* Modify the keystore command to receive the password twice to confirm it.

## 1.0.4 - 2018-08-28
* Change the encryption parameter 'N' of keystore
* Improve IconClient error handling
* Update README.md

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
