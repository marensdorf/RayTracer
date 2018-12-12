import numpy as np
import Helper
from Textures import default


class Triangle:
    """ Simple geometric triangle

    Attributes:
        kEpsilon: floating value used for allowable error in equality tests
        a, b, c: Numpy arrays representing points of the triangle
        n: Numpy array representing unit normal vector
        area: Total area of triangle
        min, max: Numpy arrays with mimimum and maximum points, used to speed up intersect calculation
        mat: Tuple representing an RGB color with values in [0,255] (default: Green)
    """
    kEpsilon = Helper.kEpsilon

    def __init__(self, a, b, c, mat=None, reflect=False, transparent=False, eta=1.0, matfunc=None):
        """Initializes triangle attributes"""
        if mat is None:
            mat = [0, 255, 0]
        if matfunc is None:
            matfunc = default
        self.a = np.asfarray(a)
        self.b = np.asfarray(b)
        self.c = np.asfarray(c)
        self.n = Helper.normalize(np.cross((self.b - self.a), (self.c - self.a)))
        self.d = np.dot(self.n, self.a)
        self.area = Helper.areaTriangle(self.a, self.b, self.c)
        self.material = np.asarray(mat)
        self.min = np.array([a, b, c]).min(axis=0)
        self.max = np.array([a, b, c]).max(axis=0)
        self.center = (self.a + self.b + self.c)/3
        self.reflect, self.transparent, self.eta, self.matfunc = reflect, transparent, eta, matfunc

    def intersectRay(self, ray):
        """ Determine if a ray intersects the triangle
            Returns: the parameter t for the intersection point to the ray
                     origin. Returns a value of None for no intersection
        """
        # Ray Tracing from the Ground Up, pg. 367
        a, b, c, d = self.a[0] - self.b[0], self.a[0] - self.c[0], ray.d[0], self.a[0] - ray.o[0]
        e, f, g, h = self.a[1] - self.b[1], self.a[1] - self.c[1], ray.d[1], self.a[1] - ray.o[1]
        i, j, k, L = self.a[2] - self.b[2], self.a[2] - self.c[2], ray.d[2], self.a[2] - ray.o[2]

        m, n, p = f * k - g * j, h * k - g * L, f * L - h * j
        q, s = g * i - e * k, e * j - f * i

        denom = a * m + b * q + c * s
        if denom < self.kEpsilon:
            return None

        inv_denom = 1.0 / denom

        e1 = d * m - b * n - c * p
        beta = e1 * inv_denom

        if beta < 0.0:
            return None

        r = e * L - h * i
        e2 = a * n + d * q + c * r
        gamma = e2 * inv_denom

        if gamma < 0.0:
            return None

        if beta + gamma > 1.0:
            return None

        e3 = a * p - b * r + d * s
        t = e3 * inv_denom

        if t < self.kEpsilon:
            return None

        return t

    def getNormal(self, p):
        return self.n
