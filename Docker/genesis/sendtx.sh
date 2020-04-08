#!/bin/bash

HASHES='
    769282ab3dee78378d7443fe6c1344c76e718734e7f581961717f12a121a2be8
    83537e56c647fbf0b726286ee08d31f12dba1bf7e50e8119eaffbf48004f237f
    314eb5c181a6f25d200d694622a3b6aa0b5401cd37ed9f99e773caed6b6857cd
    07a3800e41fd88add1bc56cc77bc9b16789a5067d1c292ec7adec5d4c75a330a
    e40d1b1f49d51e26509358c96b7c33eccd08b83b262828a7c9f989131ee7f230
    c0fb5a1c9ffc27d49e3d520a3f325ffb0aabeb55c8664ae068f153155a3ef83f
    6e4952d89c786b8526654535d0445c5e3fd8168aee6d01aced056be616a6561d
    latest_revision
    latest_governance_score
'

# set latest revision before update network proposal enalbed governance SCORE

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
