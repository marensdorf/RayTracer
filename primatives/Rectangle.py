import numpy as np
import Helper

""" NOTICE: DEPRECATED, DON'T USE UNTIL FIXED """


class Rectangle:
    """ Simple geometric rectangle

    Attributes:
        kEpsilon: floating value used for allowable error in equality tests
        pt: Origin point of the rectangle, where edges originate from
        a, b: Numpy arrays representing edges of the rectangle
        n: Numpy array representing unit normal vector
        mat: Tuple representing an RGB color with values in [0,255] (default: Blue)
    """
    kEpsilon = Helper.kEpsilon

    def __init__(self, pt, a, b, mat=None):
        """Initializes triangle attributes"""
        if mat is None:
            mat = [0, 0, 255]
        self.pt = np.asfarray(pt)
        self.a = np.asfarray(a)
        self.b = np.asfarray(b)
        self.aa = np.dot(self.a, self.a)
        self.bb = np.dot(self.b, self.b)
        self.n = Helper.normalize(np.cross(self.a, self.b))
        self.material = np.asarray(mat)
        self.min = np.array([self.pt, self.pt + self.a, self.pt + self.b, self.pt + self.a + self.b]).min(axis=0)
        self.max = np.array([self.pt, self.pt + self.a, self.pt + self.b, self.pt + self.a + self.b]).max(axis=0)
        self.center = self.pt + (self.a / 2) + (self.b / 2)

    def intersectRay(self, ray):
        """ Determine if a ray intersects the rectangle
            Returns: the parameter t for the intersection point to the ray
                     origin. Returns a value of None for no intersection
        """
        # Ray Tracing from the Ground Up, pg. 370
        t = np.dot(self.pt - ray.o, self.n) / np.dot(ray.d, self.n)
        if t < self.kEpsilon:
            return None

        pt = ray.getPoint(t)
        d = pt - self.pt

        ddota = np.dot(d, self.a)
        if ddota < 0.0 or ddota > self.aa:
            return None

        ddotb = np.dot(d, self.b)
        if ddotb < 0.0 or ddotb > self.bb:
            return None

        return t

    def getNormal(self, p):
        return self.n

    def sample(self, n):
        """ Generate n^2 samples of rectangle """
        ret = []
        for i in range(n):
            for j in range(n):
                ret.append(self.pt + ((0.5 + i) / n * self.a) + ((0.5 + j) / n * self.b))
        return ret
