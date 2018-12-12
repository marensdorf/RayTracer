import numpy as np
import math

from primatives.Ray import Ray

np.seterr(divide='ignore', invalid='ignore')
kEpsilon = 0.000001

sampleSize = 4
numSamples = sampleSize ** 2
maxDepth = 4
reflectMult = 1.0
transmitMult = 0.95

# define light properties
lightPower = 0.01

ambientIntensity = 0.6
diffuseIntensity = 0.6
specularIntensity = 0.4

shinyness = 8.0

shadows = True


def mag(v):
    """ Calculate the magnitude of a vector

    Attributes: v: Numpy 1d array representing a vector
    Returns: the magnitude of the vector
    """
    return np.sqrt(v.dot(v))


def areaTriangle(p0, p1, p2):
    """ Calculate the area of a triangle

    Attributes: p0, p1, p2: Numpy arrays representing points of the triangle
    Returns: the total area of the triangle
    """
    return mag(np.cross(p2 - p1, p0 - p1)) / 2.


def normalize(v):
    vLen = mag(v)
    if vLen == 0.:
        return 0.
    else:
        return v / vLen


def translationMatrix(x, y, z):
    return np.array([[1, 0, 0, x],
                     [0, 1, 0, y],
                     [0, 0, 1, z],
                     [0, 0, 0, 1]], dtype=np.float64)


def scaleMatrix(a, b, c):
    return np.array([[a, 0, 0, 0],
                     [0, b, 0, 0],
                     [0, 0, c, 0],
                     [0, 0, 0, 1]], dtype=np.float64)


def rotationMatrix(axis, theta):
    """
    Return the rotation matrix associated with counterclockwise rotation about
    the given axis by theta radians.
    """
    axis = normalize(np.asarray(axis))
    a = math.cos(theta / 2.0)
    b, c, d = -axis * math.sin(theta / 2.0)
    aa, bb, cc, dd = a * a, b * b, c * c, d * d
    bc, ad, ac, ab, bd, cd = b * c, a * d, a * c, a * b, b * d, c * d
    return np.array([[aa + bb - cc - dd, 2 * (bc + ad), 2 * (bd - ac), 0],
                     [2 * (bc - ad), aa + cc - bb - dd, 2 * (cd + ab), 0],
                     [2 * (bd + ac), 2 * (cd - ab), aa + dd - bb - cc, 0],
                     [0, 0, 0, 1]], dtype=np.float64)


def clamp(x, lower, upper):
    return lower if x < lower else (upper if x > upper else x)


def findBVHs(ray, bvh):
    # return 0.0, [bvh]
    t0 = (bvh.min - ray.o) / ray.d
    t1 = (bvh.max - ray.o) / ray.d
    tmin = np.max(np.minimum(t0, t1))
    tmax = np.min(np.maximum(t0, t1))
    if tmin > tmax or tmax < 0.0:
        return 0.0, []

    if bvh.minChild is None:
        return (tmin if tmin > kEpsilon else tmax), [bvh]
    (tleft, left) = findBVHs(ray, bvh.minChild)
    (tright, right) = findBVHs(ray, bvh.maxChild)
    return (tleft, left + right) if tleft < tright else (tright, right + left)


def shadowTrace(ray, accel, timemax):
    # print("Tracing out from {} in direction {}".format(ray.o, ray.d))
    (_, bvhs) = findBVHs(ray, accel.root)

    for bvh in bvhs:
        for o in bvh.objs:
            t = o.intersectRay(ray)
            if t is not None:
                if kEpsilon < t < timemax:
                    return True
    return False


def phongShading(p, obj, ray, objs, lights):
    """ Implements a Phong-style shading function

    Args:
         p: is the intersection point on a surface
         obj: is the object to calculate shading for
         ray: is the ray casted to the point
         objs: objects to check for shadows
         lights: lights to iterate through

    Returns: A tuple representing an RGB color with values in [0,255]
    """
    import Lights
    n = obj.getNormal(p)
    mat = obj.matfunc(obj, p)
    # mat = obj.material
    ambientColor = mat * ambientIntensity
    diffuseColor = mat * diffuseIntensity
    specularColor = mat * specularIntensity
    color = ambientColor
    for l in lights:
        distance = 1.0 if isinstance(l, Lights.DirLight) else mag(l.p - p)
        lightDir = -l.d if isinstance(l, Lights.DirLight) else normalize(l.p - p)
        viewDir = -ray.d

        lightMult = 1.0
        if shadows and isinstance(l, Lights.AreaLight):
            for pt in l.samples:
                if shadowTrace(Ray(p, normalize(pt - p)), objs, mag(pt - p)):
                    lightMult -= 1.0 / numSamples
        if lightMult == 0.0:
            continue
        if shadows and shadowTrace(Ray(p, lightDir), objs, distance):
            continue

        diffuse = clamp(np.dot(n, lightDir), 0.0, 1.0)
        specular = 0.0

        if diffuse > 0.0:
            reflectDir = 2 * (np.dot(lightDir, n)) * n - lightDir
            specAngle = max(np.dot(reflectDir, viewDir), 0.0)
            specular = specAngle ** shinyness

        color += (l.c * lightPower * lightMult / len(lights) / distance) * \
                 ((diffuseColor * diffuse) + (specularColor * specular))
    return color


def rayTrace(ray, accel, lights, row, col, depth, timemin=kEpsilon, timemax=np.inf):
    # print("Tracing out from {} in direction {}".format(ray.o, ray.d))
    if depth < maxDepth:
        (_, bvhs) = findBVHs(ray, accel.root)

        tRet = timemax
        obj = None
        for bvh in bvhs:
            for o in bvh.objs:
                t = o.intersectRay(ray)
                if t is not None:
                    if timemin < t < tRet:
                        tRet = t
                        obj = o
        if obj is not None:
            xp = ray.getPoint(tRet)
            from Lights import AreaLight
            if isinstance(obj, AreaLight):
                return row, col, obj.c
            elif obj.reflect:
                n = obj.getNormal(xp)
                reflectDir = ray.d - 2 * np.dot(ray.d, n) * n
                _, _, c = rayTrace(Ray(xp, reflectDir, ray.eta), accel, lights, row, col, depth + 1)
                if c is None:
                    return row, col, None
                return row, col, reflectMult * c + (1.0 - reflectMult) * phongShading(xp, obj, ray, accel, lights)
            elif obj.transparent:
                n = obj.getNormal(xp)
                nCrossD = np.cross(n, ray.d)
                relEta = ray.eta / obj.eta
                transmitDir = relEta * np.cross(n, np.cross(-n, ray.d)) - n * np.sqrt(1 - relEta * relEta *
                                                                                      np.dot(nCrossD, nCrossD))
                _, _, c = rayTrace(Ray(xp, transmitDir, obj.eta), accel, lights, row, col, depth + 1)
                if c is None:
                    return row, col, None
                return row, col, transmitMult * c + (1.0 - transmitMult) * phongShading(xp, obj, ray, accel, lights)
            else:
                return row, col, phongShading(xp, obj, ray, accel, lights)
    return row, col, None
