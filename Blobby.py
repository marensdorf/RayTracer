import numpy as np
from math import exp

from Helper import mag, clamp
from MarchingCube import Polygonise

a = 0.75
b = 0.30
threshold = a / 2.0


def getVal(r):
    val = a * exp(-b * r ** 2.)
    # val = 0. if b <= r \
    #     else (3. * a / 2.) * (1. - r / b) ** 2. if b / 3. <= r \
    #     else a * (1. - 3. * r ** 2. / b ** 2.)
    # val = a * (1. - (4. * r ** 6.) / (9. * b ** 6.)
    #            + (17. * r ** 4.) / (9. * b ** 4.)
    #            + (22. * r ** 2.) / (9. * b ** 2.)) if r <= 1.0 / b else 0.0
    return val


class Cube(object):
    def __init__(self, pt, size, mat):
        self.p = np.zeros((8, 3))
        self.p[0] = pt
        self.p[1] = pt + [size[0], 0, 0]
        self.p[2] = pt + [size[0], size[1], 0]
        self.p[3] = pt + [0, size[1], 0]
        self.p[4] = pt + [0, 0, size[2]]
        self.p[5] = pt + [size[0], 0, size[2]]
        self.p[6] = pt + [size[0], size[1], size[2]]
        self.p[7] = pt + [0, size[1], size[2]]
        self.mat = mat
        self.val = np.zeros(8, dtype=np.float64)

    def __repr__(self):
        return "[{:.2f},{:.2f},{:.2f}] - {:.3f}".format(self.p[0][0], self.p[0][1], self.p[0][2], self.val[0])


class BlobbyParticles:
    def __init__(self, objs, mat, size, *particles):
        self.objs = objs
        self.mat = mat
        self.cubeSize = np.full((3,), size)
        self.particles = np.array(particles)
        self.min = self.particles.min(axis=0) - (2. * a)
        self.max = self.particles.max(axis=0) + (2. * a)
        self.shape = ((self.max - self.min) / self.cubeSize).astype(int)

        self.cubes = np.empty(self.shape, dtype=object)
        self.vals = np.zeros(self.shape + 1, dtype=np.float64)

        print(self.min)
        print(self.max)

        self.generate()

    def generate(self):
        for x, y, z in np.ndindex(*self.shape):
            for p in self.particles:
                self.vals[x, y, z] += getVal(mag((self.min + (self.cubeSize * [x, y, z])) - p))
        for x, y, z in np.ndindex(*self.shape):
            self.cubes[x, y, z] = Cube(self.min + (self.cubeSize * [x, y, z]), self.cubeSize, self.mat)
            self.cubes[x, y, z].val += [self.vals[x, y, z], self.vals[x + 1, y, z], self.vals[x + 1, y + 1, z],
                                        self.vals[x, y + 1, z], self.vals[x, y, z + 1], self.vals[x + 1, y, z + 1],
                                        self.vals[x + 1, y + 1, z + 1], self.vals[x, y + 1, z + 1]]
            Polygonise(self.cubes[x, y, z], self.objs)
