import numpy as np

import Complex


class Node:
    leafSize = 1

    def __init__(self, objs=None):
        if objs is None:
            objs = []
        self.objs = objs
        self.minChild = None
        self.maxChild = None
        self.min = np.array([np.PINF, np.PINF, np.PINF])
        self.max = np.array([np.NINF, np.NINF, np.NINF])

    def calc(self):
        # print("Calculating node with length {}".format(len(self.objs)))

        # Calc min and max
        for obj in self.objs:
            self.min = np.minimum(obj.min, self.min)
            self.max = np.maximum(obj.max, self.max)

        # Sort objs into correct order
        splitAxis = np.argmax(self.max - self.min)
        self.objs.sort(key=lambda e: e.center[splitAxis])

        # Split if more than leafSize objects
        if len(self.objs) > self.leafSize:
            h = int(len(self.objs) / 2)
            self.minChild = Node(self.objs[:h])
            self.maxChild = Node(self.objs[h:])
            self.minChild.calc()
            self.maxChild.calc()


class AccelStruct:
    def __init__(self):
        self.root = Node()

    def add(self, obj):
        if isinstance(obj, Complex.Generic):
            self.root.objs.extend(obj.f)
        else:
            self.root.objs.append(obj)

    def append(self, obj):
        self.add(obj)

    def extend(self, objs):
        for obj in objs:
            self.add(obj)

    def calculate(self):
        self.root.calc()
