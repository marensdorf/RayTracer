import numpy as np

import Helper
from primatives.Parallelogram import Parallelogram


class PointLight:
    def __init__(self, pt, lightColor=None):
        if lightColor is None:
            lightColor = [255, 255, 255]
        self.p = np.asarray(pt, dtype=np.float64)
        self.c = np.asarray(lightColor)


class DirLight:
    def __init__(self, d, lightColor=None):
        if lightColor is None:
            lightColor = [255, 255, 255]
        self.d = Helper.normalize(d)
        self.c = np.asarray(lightColor)


class AreaLight(Parallelogram):
    def __init__(self, pt, a, b, objs, lightColor=None):
        if lightColor is None:
            lightColor = [255, 255, 255]
        super().__init__(pt, a, b, mat=lightColor)
        self.c = np.asarray(lightColor)
        self.p = self.center
        self.samples = self.sample(Helper.sampleSize)
        objs.add(self)
