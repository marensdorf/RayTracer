import numpy as np
import scipy.interpolate as interp

import Helper


def default(o, pt):
    return o.material


otherMat = np.asfarray([10, 10, 10])


def grid(obj, pt):
    if np.sum(np.floor(pt)) % 2 == 0:
        return otherMat
    return obj.material


randomSize = 256
mask = randomSize - 1
np.random.seed(123456)
xs = np.arange(randomSize)
randomTable = np.random.random(randomSize) * 2.0 - 1.0
cs = interp.CubicSpline(xs, randomTable)


zoom = 100.0


def perm(x):
    return int(x * zoom) & mask


def index(pt):
    return perm(pt[0] + perm(pt[1] + perm(pt[2])))


def noise(x):
    return Helper.clamp(cs(x % randomSize), -1.0, 1.0)


fractalOctaves = 5
fractalRange = 2 * (1 - 0.5 ** (fractalOctaves - 1))


def fractalSum(x, func):
    amplitude = 1.0
    frequency = 1.0
    ret = 0.0
    for i in range(fractalOctaves):
        ret += amplitude * func(frequency * x)
        amplitude *= 0.5
        frequency *= 2.0
    return (ret + fractalRange) / (2 * fractalRange)


def noiseTexture(obj, pt):
    return Helper.lerp(otherMat, obj.material, fractalSum(index(pt), noise))


a = 3.0
marbleScale = 3.0


def marbleTexture(obj, pt):
    return Helper.lerp(otherMat, obj.material,
                       0.5 * (1.0 + np.sin(marbleScale * pt[1] + a * fractalSum(index(pt), noise))))
