# This file is part of the Planter extend project: QCMP.
# This program is a free software tool, which does ensemble in-network reinforcement learning for load balancing.
# licensed under Apache-2.0
#
# Copyright (c) 2020-2021 Benjamin Rienecker Modified by Changgang Zheng
# Copyright (c) Computing Infrastructure Group, Department of Engineering Science, University of Oxford

import numpy as np

s1_1 = np.random.randint(400)
s1_2 = 400 - s1_1

s2_1 = np.random.randint(int(s1_1*1.05))
s2_2 = int(s1_1*1.05) - s2_1

s3_1 = np.random.randint(int(s1_2*1.05))
s3_2 = int(s1_2*1.05) - s3_1

print(s1_1, s1_2, s2_1, s2_2, s3_1, s3_2)
