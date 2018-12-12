import numpy as np

import Helper
import Complex

class AccelStruct:
    kEpsilon = 0.00001
    m = 2

    def __init__(self):
        self.shape = np.ones(3, dtype=int)
        self.objs = []
        self.g = []
        self.size = np.ones(3, dtype=np.float64)
        self.min = np.array([np.PINF, np.PINF, np.PINF])
        self.max = np.array([np.NINF, np.NINF, np.NINF])

    def add(self, obj):
        if isinstance(obj, Complex.Generic):
            self.objs.extend(obj.f)
        else:
            self.objs.append(obj)
        self.min = np.minimum(obj.min, self.min)
        self.max = np.maximum(obj.max, self.max)

    def append(self, obj):
        self.add(obj)

    def extend(self, objs):
        for obj in objs:
            self.add(obj)

    def calculate(self):
        print("Calculating grid")
        self.max += self.kEpsilon
        self.min -= self.kEpsilon
        w = self.max - self.min
        s = (Helper.mag(w) / len(self.objs)) ** (1.0 / 3.0)
        self.shape = np.floor(w * self.m / s).astype(int) + 1
        print(self.shape)
        self.g = [[[[] for _ in range(self.shape[0])] for _ in range(self.shape[1])] for _ in range(self.shape[2])]
        self.size = w / self.shape
        for obj in self.objs:
            start = np.floor((obj.min - self.min) / self.size).astype(int)
            stop = np.floor((obj.max - self.min) / self.size).astype(int) + 1
            print("Adding object from {} to {}".format(start, stop))
            for i in range(start[0], stop[0]):
                for j in range(start[1], stop[1]):
                    for k in range(start[2], stop[2]):
                        self.g[i][j][k].append(obj)
                        # print("Added object to {}, {}, {}".format(i, j, k))
