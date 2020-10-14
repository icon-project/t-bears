#!/bin/python

import os
import pika
from time import sleep

AMQ_HOST = os.environ.get("AMQ_HOST", "127.0.0.1")
MAX_RETRIES = int(os.environ.get("AMQ_HOST_MAX_RETRIES", 5))
DELAY = int(os.environ.get("AMQ_HOST_RETRY_DELAY", 1))

retry_count = 1

print(f"Checking connection to AMQ: {AMQ_HOST}")

while True:
    try:
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                AMQ_HOST, blocked_connection_timeout=1, retry_delay=0, socket_timeout=1
            )
        )
        print("AMQ is available")
        exit(0)
    except Exception as e:
        print(f"Retrying after {DELAY}s ...")
        sleep(DELAY)
        retry_count += 1
        if retry_count > MAX_RETRIES:
            print(f"Could not connect to AMQ after {MAX_RETRIES} retries")
            exit(99)
        continue
