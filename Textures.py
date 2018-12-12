import numpy as np

import Helper


def default(o, pt):
    return o.material


evenmat = np.asfarray([10, 10, 10])


def grid(obj, pt):
    if np.sum(np.floor(pt)) % 2 == 0:
        return evenmat
    return obj.material
