#!/usr/bin/env python3
import os
import sys
import grpc
import math
import numpy as np

from scapy.all import *
from scapy.layers.inet import _IPOption_HDR

sys.path.append(
    os.path.join(os.path.dirname(os.path.abspath(__file__)),
                 '../utils/'))
import p4runtime_lib.bmv2
import p4runtime_lib.helper

from q_table import (path_stats,
                     q_table)

old_paths = [path_stats([0, 0], [50, 50]), path_stats([0, 0], [50, 50]), path_stats([0, 0], [50, 50])]

class SwitchTrace(Packet):
    fields_desc = [ IntField("swid", 0),
                  IntField("qdepth", 0)]
    def extract_padding(self, p):
                return "", p

class IPOption_MRI(IPOption):
    name = "MRI"
    option = 31
    fields_desc = [ _IPOption_HDR,
                    FieldLenField("length", None, fmt="B",
                                  length_of="swtraces",
                                  adjust=lambda pkt,l:l*2+4),
                    ShortField("count", 0),
                    PacketListField("swtraces",
                                   [],
                                   SwitchTrace,
                                   count_from=lambda pkt:(pkt.count*1)) ]

def runthat(switch_q_table, switch, mri, path_dicts, counter, index1, index2, index3, diff_switches, nhop_dmacs, nhop_ipv4s, ports, reset_params):
    # index1 : index for where switch queue data is stored in path_dicts (list of dicts)
    # index2 : which switch trace contains the queue length
    # index3 : swid for path defining switch

    switch_q_table.update_parameters()
    queue_length = mri.swtraces[index2].qdepth
        # print(mri.swtraces[i].swid, mri.swtraces[i].qdepth)
    if mri.swtraces[index3].swid == diff_switches[0]:
        path_dicts[index1]['path1'] = int(queue_length/2)
        counter[index1][0] += 1
    elif mri.swtraces[index3].swid == diff_switches[1]:
        path_dicts[index1]['path2'] = int(queue_length/2)
        counter[index1][1] += 1

    if 3 in counter[index1]:
        zero_indices = [i for i, x in enumerate(counter[index1]) if x == 0]
        for index in zero_indices:
            path_dicts[index1]["path{0}".format(index + 1)] = 100 # max queue length

    if len(path_dicts[index1]) == 2:
        global old_paths
        # print(path_dict)

        new_paths = path_stats([path_dicts[index1]['path1'], path_dicts[index1]['path2']])
        switch_q_table.update_q_table(switch_q_table.parameters['LEARNING_RATE'], switch_q_table.parameters['DISCOUNT'], old_paths[index1], new_paths)
        # print(q_table)
        new_paths.get_next_action(switch_q_table, switch_q_table.parameters['epsilon'])
        new_paths.get_new_weights(old_paths[index1], switch_q_table.parameters['action_weight'])
        new_paths.get_reward(old_paths[index1])
        print('s{0}'.format(index1+1), new_paths.path_weights, new_paths.action, new_paths.path_queues[::-1])


        p4info_file_path = os.path.join(os.getcwd(), 'build/load_balance_advanced.p4.p4info.txt')
        p4info_helper = p4runtime_lib.helper.P4InfoHelper(p4info_file_path)

        switch.MasterArbitrationUpdate()

        new_paths.change_path_weights(old_paths[index1], p4info_helper, switch, nhop_dmacs, nhop_ipv4s, ports)

        switch.shutdown()

        switch_q_table.reset_parameters(new_paths, reset_params[index1])

        old_paths[index1] = new_paths
        path_dicts[index1].clear()
        for i in range(len(counter[index1])):
            counter[index1][i] = 0


def handle_pkt(pkt, s1_q_table, s2_q_table, s3_q_table, path_dicts, counter, reset_params):

    # pkt.show2()
    if pkt[IP]:

        mri=pkt[IP][IPOption_MRI]
        path_len = len(mri.swtraces)

        if path_len == 3:

            s1 = p4runtime_lib.bmv2.Bmv2SwitchConnection(
                name='s1',
                address='127.0.0.1:50051',
                device_id=0)

            nhop_dmacs = ["00:00:00:00:01:04", "00:00:00:00:01:05"]
            nhop_ipv4s = ["10.0.2.0", "10.0.3.0"]
            ports = [4, 5]
            diff_switches = [2, 3]

            runthat(s1_q_table, s1, mri, path_dicts, counter, 0, 2, 1, diff_switches, nhop_dmacs, nhop_ipv4s, ports, reset_params)

        else:
            if mri.swtraces[3].swid == 2:
                s2 = p4runtime_lib.bmv2.Bmv2SwitchConnection(
                    name='s2',
                    address='127.0.0.1:50052',
                    device_id=1)

                nhop_dmacs = ["00:00:00:00:02:03", "00:00:00:00:02:04"]
                nhop_ipv4s = ["10.0.4.0", "10.0.5.0"]
                ports = [3, 4]
                diff_switches = [4, 5]

                runthat(s2_q_table, s2, mri, path_dicts, counter, 1, 3, 2, diff_switches, nhop_dmacs, nhop_ipv4s, ports, reset_params)

            elif mri.swtraces[3].swid == 3:
                s3 = p4runtime_lib.bmv2.Bmv2SwitchConnection(
                    name='s3',
                    address='127.0.0.1:50053',
                    device_id=2)

                nhop_dmacs = ["00:00:00:00:03:03", "00:00:00:00:03:04"]
                nhop_ipv4s = ["10.0.4.0", "10.0.5.0"]
                ports = [3, 4]
                diff_switches = [4, 5]

                runthat(s3_q_table, s3, mri, path_dicts, counter, 2, 3, 2, diff_switches, nhop_dmacs, nhop_ipv4s, ports, reset_params)


    else:
        print("cannot find IP header in the packet")

    sys.stdout.flush()

def main():
    s1_q_table = q_table()
    s2_q_table = q_table()
    s3_q_table = q_table()
    s1_path_dict = {}
    s2_path_dict = {}
    s3_path_dict = {}
    path_dicts = [s1_path_dict, s2_path_dict, s3_path_dict]
    counter = [[0, 0], [0, 0], [0, 0]]
    reset_params = [[],[],[]]
    iface = 's1-eth3'
    print("sniffing on %s" % iface)
    sys.stdout.flush()
    sniff(filter="ip", iface = iface,
          prn = lambda x: handle_pkt(x, s1_q_table, s2_q_table, s3_q_table, path_dicts, counter, reset_params))

if __name__ == '__main__':
    main()
