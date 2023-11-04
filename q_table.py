#!/usr/bin/env python3
import numpy as np
import math

class q_table():
    def __init__(self):
        self.q_table = self.init_q_table()
        self.parameters = {'LEARNING_RATE': 0.2,
                        'DISCOUNT': 0.1,
                        'epsilon': 0.4,
                        'action_weight': 5,
                        'pkt_counter': 0}

    def init_q_table(self):
        actions = ('updown', 'downup', 'no_change')
        q_table = np.random.rand(len(actions), 11, 11) * 0.1 - 0.05
        q_table = np.round(q_table, decimals=3)
        return q_table

    def update_q_table(self, LEARNING_RATE, DISCOUNT, old_paths, new_paths):
        # Calculate new Q-value
        indices = [old_paths.action, math.ceil(min(10, old_paths.path_queues[0] / 10)), math.ceil(min(10, old_paths.path_queues[1] / 10))]
        max_future_q = np.argmax(self.q_table[:, indices[1], indices[2]])
        current_q = self.q_table[indices[0], indices[1], indices[2]]
        new_q = (1 - LEARNING_RATE)* current_q + LEARNING_RATE * (old_paths.reward + DISCOUNT * max_future_q)
        new_q = np.round(max(-1, min(new_q, 1)), decimals=3)
        self.q_table[indices[0], indices[1], indices[2]] = new_q
        # print(current_q, new_q)

    def update_parameters(self):
        self.parameters['pkt_counter'] += 1
        if self.parameters['pkt_counter'] % 80 == 0:
            if self.parameters['epsilon'] > 0.1:
                self.parameters['epsilon'] = np.round(self.parameters['epsilon'] - 0.1, decimals=1) # [0.4, 0.3, 0.2, 0.1]
            if self.parameters['LEARNING_RATE'] > 0.05:
                self.parameters['LEARNING_RATE'] *= 0.85
            if self.parameters['action_weight'] > 1:
                self.parameters['action_weight'] = math.ceil(self.parameters['action_weight'] * 0.5) # [5, 3, 2, 1]
            print(self.parameters)

    def reset_parameters(self, path, reset_params):
        reset_params.append(path.path_queues)
        if len(reset_params) == 10:
            if (all(lst[0] > 98 for lst in reset_params) and all(lst[1] < 2 for lst in reset_params)) or (all(lst[1] > 98 for lst in reset_params) and all(lst[0] < 2 for lst in reset_params)):
                self.parameters['LEARNING_RATE'] = 0.1
                self.parameters['epsilon'] = 0.2
                self.parameters['action_weight'] = 5
                self.parameters['pkt_counter'] = 0
                print('PARAMETERS HAVE BEEN RESET!!!')
                reset_params.clear()
        if len(reset_params) == 10:
            reset_params.pop(0)

class path_stats():
    def __init__(self, path_queues, path_weights=0):
        self.path_queues = path_queues
        self.path_weights = path_weights
        self.action = 2
        self.reward = 0

    def weighted_average(self):
        queue_difference = abs(self.path_queues[0]-self.path_queues[1])
        weight_avg_queue = sum([self.path_queues[i] * self.path_weights[i] for i in range(len(self.path_weights))]) / sum(self.path_weights)
        return (-queue_difference + 50) + weight_avg_queue

    def get_next_action(self, table, epsilon):
        if np.random.random() < epsilon:
            self.action = np.random.choice(np.arange(3))
        else:
            # print(q_table[:, math.ceil(paths.path_queues[0] / 10), math.ceil(paths.path_queues[1] / 10)])
            self.action = np.argmax(table.q_table[:, math.ceil(min(10, self.path_queues[0] / 10)), math.ceil(min(10, self.path_queues[1] / 10))])

    def get_new_weights(self, old_paths, action_weight):
        if self.action == 2:
            self.path_weights = old_paths.path_weights
        elif self.action == 0:
            weights = [old_paths.path_weights[0] + action_weight, old_paths.path_weights[1] - action_weight]
            weights = [max(0, min(num, 100)) for num in weights]
            self.path_weights = weights
        elif self.action == 1:
            weights = [old_paths.path_weights[0] - action_weight, old_paths.path_weights[1] + action_weight]
            weights = [max(0, min(num, 100)) for num in weights]
            self.path_weights = weights

    def get_reward(self, old_paths):
    # Calculate reward
        old_average = old_paths.weighted_average()
        new_average = self.weighted_average()
        if new_average < old_average - 0.5:
            self.reward = 1
        elif new_average > old_average + 0.5:
            self.reward = -1
        else:
            self.reward = 0
        # print(old_average, new_average, new_paths.reward)

    def change_path_weights(self, old_paths, p4info_helper, ingress_sw, nhop_dmacs, nhop_ipv4s, ports):
        if self.path_weights[0] > old_paths.path_weights[0]:
            for i in range(old_paths.path_weights[0], self.path_weights[0]):
                update_path_weights(p4info_helper, ingress_sw=ingress_sw, value=i,
                    nhop_dmac=nhop_dmacs[0], nhop_ipv4=nhop_ipv4s[0], port=ports[0])
        elif self.path_weights[0] < old_paths.path_weights[0]:
            for i in range(self.path_weights[0], old_paths.path_weights[0]):
                update_path_weights(p4info_helper, ingress_sw=ingress_sw, value=i,
                    nhop_dmac=nhop_dmacs[1], nhop_ipv4=nhop_ipv4s[1], port=ports[1])

def init_path_weights(p4info_helper, ingress_sw, nhop_dmacs, nhop_ipv4s, ports):
    for i in range(50):
        write_path_weights(p4info_helper, ingress_sw=ingress_sw, value=i,
            nhop_dmac=nhop_dmacs[0], nhop_ipv4=nhop_ipv4s[0], port=ports[0])
    for i in range(50, 100):
        write_path_weights(p4info_helper, ingress_sw=ingress_sw, value=i,
            nhop_dmac=nhop_dmacs[1], nhop_ipv4=nhop_ipv4s[1], port=ports[1])

def write_path_weights(p4info_helper, ingress_sw, value, nhop_dmac, nhop_ipv4, port):
    # Create table entry
    table_entry = p4info_helper.buildTableEntry(
        table_name="MyIngress.ecmp_nhop",
        match_fields={
            "meta.ecmp_select": (value),
        },
        action_name="MyIngress.set_nhop",
        action_params={
            "nhop_dmac": nhop_dmac,
            "nhop_ipv4": nhop_ipv4,
            "port": port,
        })
    ingress_sw.WriteTableEntry(table_entry)
    # print("Installed ingress tunnel rule on %s" % ingress_sw.name)

def update_path_weights(p4info_helper, ingress_sw, value, nhop_dmac, nhop_ipv4, port):
    # Modify table entry
    table_entry = p4info_helper.buildTableEntry(
        table_name="MyIngress.ecmp_nhop",
        match_fields={
            "meta.ecmp_select": (value),
        },
        action_name="MyIngress.set_nhop",
        action_params={
            "nhop_dmac": nhop_dmac,
            "nhop_ipv4": nhop_ipv4,
            "port": port,
        })
    ingress_sw.ModifyTableEntry(table_entry)
    # print("Installed ingress tunnel rule on %s" % ingress_sw.name)

def readTableRules(p4info_helper, sw):
    """
    Reads the table entries from all tables on the switch.
    :param p4info_helper: the P4Info helper
    :param sw: the switch connection
    """
    print('\n----- Reading tables rules for %s -----' % sw.name)
    for response in sw.ReadTableEntries():
        for entity in response.entities:
            entry = entity.table_entry
            # TODO For extra credit, you can use the p4info_helper to translate
            #      the IDs in the entry to names
            print(entry)
            print('-----')
