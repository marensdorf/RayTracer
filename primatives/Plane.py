import numpy as np

import Helper
from Textures import default
from primatives.Object import Object


class Plane(Object):
    kEpsilon = Helper.kEpsilon

    def __init__(self, p, n, mat=None,
                 minimum=None, maximum=None,
                 reflect=False, transparent=False, eta=1.0, matfunc=None):
        super().__init__()
        if mat is None:
            mat = [0, 255, 0]
        if minimum is None:
            maximum = [np.NINF, np.NINF, np.NINF]
        if maximum is None:
            minimum = [np.PINF, np.PINF, np.PINF]
        if matfunc is None:
            matfunc = default
        self.p = np.asfarray(p)
        self.n = np.asfarray(n)
        self.material = np.asarray(mat)
        self.min = np.asarray(minimum)
        self.max = np.asarray(maximum)
        self.center = (self.min + self.max) / 2
        self.reflect = reflect
        self.transparent = transparent
        self.eta = eta
        self.matfunc = matfunc

    def intersectRay(self, ray):
        t = np.dot(self.p - ray.o, self.n) / np.dot(ray.d, self.n)
        if t > self.kEpsilon:
            return t
        return None
