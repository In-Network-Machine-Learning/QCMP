# This file is part of the Planter extend project: QCMP.
# This program is a free software tool, which does ensemble in-network reinforcement learning for load balancing.
# licensed under Apache-2.0
#
# Utility: This file is used to send telemetry traffic
#
# Copyright (c) 2020-2021 Benjamin Rienecker Modified by Changgang Zheng
# Copyright (c) Computing Infrastructure Group, Department of Engineering Science, University of Oxford

#!/usr/bin/env python3
import random
import socket
import sys
from time import sleep

from scapy.all import *
from scapy.layers.inet import _IPOption_HDR

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

class SourceRoute(Packet):
   fields_desc = [ BitField("bos", 0, 1),
                   BitField("port", 0, 15)]

bind_layers(Ether, SourceRoute, type=0x1234)
bind_layers(SourceRoute, SourceRoute, bos=0)
bind_layers(SourceRoute, IP, bos=1)

def main():

    iface = 'eth0'

    print("sending on interface %s" % (iface))

    path1_ports = [3, 3, 4, 3]
    path2_ports = [4, 3, 4, 3]
    while True:
        for path in (path1_ports, path2_ports):
            i = 0
            pkt =  Ether(src=get_if_hwaddr(iface), dst='ff:ff:ff:ff:ff:ff');
            for p in path:
                try:
                    pkt = pkt / SourceRoute(bos=0, port=int(p))
                    i = i+1
                except ValueError:
                    pass
            if pkt.haslayer(SourceRoute):
                pkt.getlayer(SourceRoute, i).bos = 1 # set final hop bos = 1

            pkt = pkt /IP(dst='0.0.0.0', options = IPOption_MRI(count=0,
                swtraces=[]))

            # pkt.show2()
            sendp(pkt, iface=iface, verbose=False)
        sleep(0.5)


if __name__ == '__main__':
    main()
