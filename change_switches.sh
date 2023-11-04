#!/bin/bash
sleep 100

simple_switch_CLI --thrift-port 9090 <<< 'set_queue_rate 154 4'
simple_switch_CLI --thrift-port 9090 <<< 'set_queue_rate 246 5'

simple_switch_CLI --thrift-port 9091 <<< 'set_queue_rate 53 3'
simple_switch_CLI --thrift-port 9091 <<< 'set_queue_rate 108 4'

simple_switch_CLI --thrift-port 9092 <<< 'set_queue_rate 87 3'
simple_switch_CLI --thrift-port 9092 <<< 'set_queue_rate 171 4'

sleep 100

simple_switch_CLI --thrift-port 9090 <<< 'set_queue_rate 330 4'
simple_switch_CLI --thrift-port 9090 <<< 'set_queue_rate 70 5'

simple_switch_CLI --thrift-port 9091 <<< 'set_queue_rate 99 3'
simple_switch_CLI --thrift-port 9091 <<< 'set_queue_rate 247 4'

simple_switch_CLI --thrift-port 9092 <<< 'set_queue_rate 65 3'
simple_switch_CLI --thrift-port 9092 <<< 'set_queue_rate 8 4'

sleep 100

simple_switch_CLI --thrift-port 9090 <<< 'set_queue_rate 181 4'
simple_switch_CLI --thrift-port 9090 <<< 'set_queue_rate 219 5'

simple_switch_CLI --thrift-port 9091 <<< 'set_queue_rate 60 3'
simple_switch_CLI --thrift-port 9091 <<< 'set_queue_rate 130 4'

simple_switch_CLI --thrift-port 9092 <<< 'set_queue_rate 166 3'
simple_switch_CLI --thrift-port 9092 <<< 'set_queue_rate 63 4'

sleep 100

simple_switch_CLI --thrift-port 9090 <<< 'set_queue_rate 54 4'
simple_switch_CLI --thrift-port 9090 <<< 'set_queue_rate 346 5'

simple_switch_CLI --thrift-port 9091 <<< 'set_queue_rate 4 3'
simple_switch_CLI --thrift-port 9091 <<< 'set_queue_rate 52 4'

simple_switch_CLI --thrift-port 9092 <<< 'set_queue_rate 221 3'
simple_switch_CLI --thrift-port 9092 <<< 'set_queue_rate 142 4'

sleep 100
