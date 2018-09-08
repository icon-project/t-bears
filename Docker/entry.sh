#!/bin/bash

service rabbitmq-server start

tbears genconf
tbears start

exec /bin/bash
