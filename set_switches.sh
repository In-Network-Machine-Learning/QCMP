#!/bin/bash
python3 initiate_rules.py

simple_switch_CLI --thrift-port 9090 <<< 'set_queue_depth 200'
simple_switch_CLI --thrift-port 9090 <<< 'set_queue_rate 297 4'
simple_switch_CLI --thrift-port 9090 <<< 'set_queue_rate 103 5'

simple_switch_CLI --thrift-port 9091 <<< 'set_queue_depth 200'
simple_switch_CLI --thrift-port 9091 <<< 'set_queue_rate 293 3'
simple_switch_CLI --thrift-port 9091 <<< 'set_queue_rate 18 4'

simple_switch_CLI --thrift-port 9092 <<< 'set_queue_depth 200'
simple_switch_CLI --thrift-port 9092 <<< 'set_queue_rate 60 3'
simple_switch_CLI --thrift-port 9092 <<< 'set_queue_rate 48 4'

python3 receive_queues.py
