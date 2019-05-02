#!/bin/bash

HASHES='
    769282ab3dee78378d7443fe6c1344c76e718734e7f581961717f12a121a2be8
    c033fdb276cd5521ec28a36626ff2f110baabe79508950c8c91088dd5166fc38
    b80df81fcc5c02fd799b2806789830cfcc25ef69498695df9792386728b9beab
    30450a8b86515c84c0e158923262e7bd2f5348973fce4b2e308268086efcb88b
'

PWD=$(dirname $0)
KEYSTORE=$PWD/keystore_test1
PASSWORD=test1_Account

service rabbitmq-server start
tbears start

function deploy() {
    tbears deploy $1.zip -c $1.json -k $KEYSTORE -p $PASSWORD
}

function sendtx() {
    tbears sendtx -k $KEYSTORE -p $PASSWORD $1.json
}

for h in $HASHES; do
    tx=$PWD/$h
    grep deploy $tx.json > /dev/null
    if [[ $? -eq 0 ]]; then
        deploy $tx
    else
        sendtx $tx
    fi
    sleep 3
done
