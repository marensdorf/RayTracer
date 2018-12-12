import numpy as np

from primatives.Parallelogram import Parallelogram
from primatives.Triangle import Triangle
from primatives.Rectangle import Rectangle


class Generic:
    def __init__(self):
        self.f = []

    def add(self, other):
        if isinstance(other, Generic):
            self.f.extend(other.f)
        else:
            self.f.append(other)


class Mesh(Generic):
    """ Simple geometric triangular mesh

    Attributes:
        v: Array of 3d points representing vertices of the mesh
        f: Array of Triangles constructed using vertices in v
        min, max: Numpy arrays with mimimum and maximum values of the mesh, used to speed up intersect calculation
        mat: Tuple representing an RGB color with values in [0,255] (default: Gray)
        t: Numpy matrix used to calculate transformations of the mesh
    """

    def __init__(self, mat=None, transform=np.identity(4, dtype=np.float64)):
        super().__init__()
        if mat is None:
            mat = [150, 150, 150]
        self.v = [np.array([0, 0, 0])]  # Initialize with 0-point because faces in obj files are indexed from 1
        self.material = np.array(mat)
        self.t = transform
        self.min = np.array([np.PINF, np.PINF, np.PINF])
        self.max = np.array([np.NINF, np.NINF, np.NINF])

    def addVertex(self, x, y, z):
        v = (np.dot(self.t, np.array([x, y, z, 1.0])))[:-1]
        self.min = np.minimum(v, self.min)
        self.max = np.maximum(v, self.max)
        self.v.append(v)

    def addFace(self, index0, index1, index2):
        self.add(Triangle(self.v[index0], self.v[index1], self.v[index2], self.material))


class RectFace(Generic):
    def __init__(self, a, b, c, mat=None):
        if mat is None:
            mat = [150, 150, 150]
        super().__init__()
        self.add(Parallelogram(a, b, c, mat=mat))  # front-facing
        # self.add(Parallelogram(a, c, b, mat=mat))  # back-facing


class Box(Generic):
    def __init__(self, p, a, b, c, mat=None):
        if mat is None:
            mat = [150, 150, 150]
        super().__init__()
        self.a = np.asfarray(a)
        self.b = np.asfarray(b)
        self.c = np.asfarray(c)
        self.p = np.asfarray(p)
        self.add(RectFace(p, self.p+b, self.p+a, mat=mat))
        self.add(RectFace(p, self.p+a, self.p+c, mat=mat))
        self.add(RectFace(p, self.p+c, self.p+b, mat=mat))
        p2 = self.p + self.a + self.b + self.c
        self.add(RectFace(p2, p2-a, p2-b, mat=mat))
        self.add(RectFace(p2, p2-c, p2-a, mat=mat))
        self.add(RectFace(p2, p2-b, p2-c, mat=mat))


class AABox(Box):
    def __init__(self, p, size, mat=None):
        if mat is None:
            mat = [150, 150, 150]
        super().__init__(p, [size[0], 0, 0], [0, 0, size[2]], [0, size[1], 0], mat=mat)
