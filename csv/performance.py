# This file is part of the Planter extend project: QCMP.
# This program is a free software tool, which does ensemble in-network reinforcement learning for load balancing.
# licensed under Apache-2.0
#
# Utility: This file is used to plot the result from Wireshark
#
# Copyright (c) 2020-2021 Benjamin Rienecker Modified by Changgang Zheng
# Copyright (c) Computing Infrastructure Group, Department of Engineering Science, University of Oxford

import matplotlib.pyplot as plt
import numpy as np
import csv
import pandas as pd

ECMP = '/Users/benjamin/Documents/4YP-INML-RL/load_balancing_advanced_topo/csv/ECMP.csv'
with open(ECMP, mode='r') as file:
    reader = csv.reader(file)
    ECMP_values = []
    for row in reader:
        ECMP_values.append(row[1])
ECMP_values = [int(x) for x in ECMP_values[1:]]

QCMP = '/Users/benjamin/Documents/4YP-INML-RL/load_balancing_advanced_topo/csv/QCMP.csv'
with open(QCMP, mode='r') as file:
    reader = csv.reader(file)
    QCMP_values = []
    for row in reader:
        QCMP_values.append(row[1])
QCMP_values = [int(x) for x in QCMP_values[1:]]

time = [i for i in range(len(ECMP_values))]

ECMP_df = pd.DataFrame({'values': ECMP_values})
ECMP_ma = ECMP_df.rolling(window=10, min_periods=1).mean()

QCMP_df = pd.DataFrame({'values': QCMP_values})
QCMP_ma = QCMP_df.rolling(window=10, min_periods=1).mean()

queue = 0
QCMP_drops = []
for i in QCMP_values:
    queue += 380 - i
    QCMP_drops.append(max(0, queue - 100))
    queue = min(queue, 100)


queue = 0
ECMP_drops = []
for i in ECMP_values:
    queue += 380 - i
    ECMP_drops.append(max(0, queue - 100))
    queue = min(queue, 100)


ECMP_drops_df = pd.DataFrame({'values': ECMP_drops})
ECMP_drops_ma = ECMP_drops_df.rolling(window=10, min_periods=1).mean()

QCMP_drops_df = pd.DataFrame({'values': QCMP_drops})
QCMP_drops_ma = QCMP_drops_df.rolling(window=10, min_periods=1).mean()

fig, ax = plt.subplots(figsize=(14, 6))
ax.set_xlim(left=0, right=500)
ax.set_ylim(bottom=0, top=420)
ax.plot(time, ECMP_ma, color='r', label = "ECMP")
ax.plot(time, QCMP_ma, color='b', label = "QCMP")
ax.plot(time, ECMP_drops_ma, color='r', label = "ECMP Drops", linestyle='--')
ax.plot(time, QCMP_drops_ma, color='b', label = "QCMP Drops", linestyle='--')
ax.legend(loc=4, bbox_to_anchor=(1, 0.1))
ax.set_xlabel('Time (s)')
ax.set_ylabel('Packets per Second')
# plt.show()
plt.savefig('../images/performance.png')

# QCMP_sorted = QCMP_ma.sort_values('values')
# QCMP_cdf = [x/(len(QCMP_sorted.values)-1) for x in range(len(QCMP_sorted.values))]
# QCMP_sorted['cdf'] = QCMP_cdf
#
# ECMP_sorted = ECMP_ma.sort_values('values')
# ECMP_cdf = [x/(len(ECMP_sorted.values)-1) for x in range(len(ECMP_sorted.values))]
# ECMP_sorted['cdf'] = ECMP_cdf
#
# plt.plot(QCMP_sorted.values, QCMP_sorted.cdf, color='b', label = 'QCMP')
# plt.plot(ECMP_sorted.values, QCMP_sorted.cdf, color='r', label = 'ECMP')
#
# plt.axvline(x=252, color='red', linestyle=':')
# plt.axvline(x=351, color='blue', linestyle=':')
#
# plt.axvline(x=380, color='grey', linestyle='--')
# plt.axvline(x=361, color='grey', linestyle='--')
# plt.axhline(y=0.78, color='grey', linestyle='--')
# plt.axhline(y=0.38, color='grey', linestyle='--')
# plt.axhline(y=0.0095, color='grey', linestyle='--')
#
# plt.tick_params(axis='y', left=True, right=False)
# plt.tick_params(axis='x', bottom=True, top=False)
# plt.ylabel('CDF')
# plt.ylim(bottom=0, top=1)
# plt.xlabel('Packets per Second')
# plt.xlim(left=150, right=400)
# plt.legend(loc=2)
#
# ax2 = plt.twinx()
# yticks = [0.010, 0.38, 0.78]
# yticklabels = ['0.010', '0.38', '0.78']
# ax2.set_yticks(yticks)
# ax2.set_yticklabels(yticklabels)
# plt.tick_params(axis='y', left=False, right=True, labelright=True)
#
# ax3 = plt.twiny()
# xticks = [0.844, 0.92]
# xticklabels = ['95%', '100%']
# ax3.set_xticks(xticks)
# ax3.set_xticklabels(xticklabels)
# plt.tick_params(axis='x', bottom=False, top=True, labeltop=True)
#
# # plt.show()
# plt.savefig('../images/cdf.png')
