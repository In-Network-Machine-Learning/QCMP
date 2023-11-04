#!/usr/bin/env python3
import sys
import argparse
import os
import pandas as pd
import grpc

from scapy.all import *

from scapy.layers.inet import _IPOption_HDR

# Import P4Runtime lib from parent utils dir
# Probably there's a better way of doing this.
sys.path.append(
    os.path.join(os.path.dirname(os.path.abspath(__file__)),
                 '../utils/'))
import p4runtime_lib.bmv2
import p4runtime_lib.helper
from p4runtime_lib.error_utils import printGrpcError
from p4runtime_lib.switch import ShutdownAllSwitchConnections

from q_table import (init_path_weights, readTableRules)


def main(p4info_file_path, bmv2_file_path):
    # Instantiate a P4Runtime helper from the p4info file
    p4info_helper = p4runtime_lib.helper.P4InfoHelper(p4info_file_path)

    # Create a switch connection object for all switches;
    # this is backed by a P4Runtime gRPC connection.
    # Also, dump all P4Runtime messages sent to switch to given txt files.
    s1 = p4runtime_lib.bmv2.Bmv2SwitchConnection(
        name='s1',
        address='127.0.0.1:50051',
        device_id=0,
        proto_dump_file='logs/s1-p4runtime-requests.txt')
    s2 = p4runtime_lib.bmv2.Bmv2SwitchConnection(
        name='s2',
        address='127.0.0.1:50052',
        device_id=1,
        proto_dump_file='logs/s2-p4runtime-requests.txt')
    s3 = p4runtime_lib.bmv2.Bmv2SwitchConnection(
        name='s3',
        address='127.0.0.1:50053',
        device_id=2,
        proto_dump_file='logs/s3-p4runtime-requests.txt')


    # Send master arbitration update message to establish this controller as
    # master (required by P4Runtime before performing any other write operation)
    s1.MasterArbitrationUpdate()
    s2.MasterArbitrationUpdate()
    s3.MasterArbitrationUpdate()


    nhop_dmacs = ["00:00:00:00:01:04", "00:00:00:00:01:05"]
    nhop_ipv4s = ["10.0.2.0", "10.0.3.0"]
    ports = [4, 5]
    init_path_weights(p4info_helper, s1, nhop_dmacs, nhop_ipv4s, ports)

    nhop_dmacs = ["00:00:00:00:02:03", "00:00:00:00:02:04"]
    nhop_ipv4s = ["10.0.4.0", "10.0.5.0"]
    ports = [3, 4]
    init_path_weights(p4info_helper, s2, nhop_dmacs, nhop_ipv4s, ports)

    nhop_dmacs = ["00:00:00:00:03:03", "00:00:00:00:03:04"]
    nhop_ipv4s = ["10.0.4.0", "10.0.5.0"]
    ports = [3, 4]
    init_path_weights(p4info_helper, s3, nhop_dmacs, nhop_ipv4s, ports)

    # Uncomment the following line to read table entries from s1
    # readTableRules(p4info_helper, s1)
    # readTableRules(p4info_helper, s2)
    # readTableRules(p4info_helper, s3)
    # readTableRules(p4info_helper, s4)

    ShutdownAllSwitchConnections()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='P4Runtime Controller')
    parser.add_argument('--p4info', help='p4info proto in text format from p4c',
                        type=str, action="store", required=False,
                        default='./build/load_balance_advanced.p4.p4info.txt')
    parser.add_argument('--bmv2-json', help='BMv2 JSON file from p4c',
                        type=str, action="store", required=False,
                        default='./build/load_balance_advanced.json')
    args = parser.parse_args()

    if not os.path.exists(args.p4info):
        parser.print_help()
        print("\np4info file not found: %s\nHave you run 'make'?" % args.p4info)
        parser.exit(1)
    if not os.path.exists(args.bmv2_json):
        parser.print_help()
        print("\nBMv2 JSON file not found: %s\nHave you run 'make'?" % args.bmv2_json)
        parser.exit(1)
    main(args.p4info, args.bmv2_json)
