import numpy as np
import Helper
from Textures import default
from primatives.Ray import Ray

UNION = 0
INTERSECTION = 1
DIFFERENCE = 2


def getIntervals(obj, ray):
    t = obj.intersectRay(ray)
    if t is None:
        return []
    nextRay = Ray(ray.getPoint(t), ray.d)
    nextT = obj.intersectRay(nextRay)
    if nextT is None:
        return [(t, t)]  # Rare case of single point of intersection
    return [(t, t + nextT)] + getIntervals(obj, Ray(ray.getPoint(t + nextT), ray.d))


class Node:
    def __init__(self, left, right, operation):
        self.left, self.right = left, right
        self.operation = operation

    def intersectRay(self, ray):
        leftIntervals = getIntervals(self.left, ray)
        rightIntervals = getIntervals(self.right, ray)
        if self.operation == 0:
            if len(leftIntervals) == 0 and len(rightIntervals) == 0:
                return None
            if len(leftIntervals) == 0:
                return rightIntervals[0][0]
            if len(rightIntervals) == 0:
                return leftIntervals[0][0]
            return min(leftIntervals[0][0], rightIntervals[0][0])
        if self.operation == 1:
            if len(leftIntervals) == 0 or len(rightIntervals) == 0:
                return None
            for i in leftIntervals:
                for j in rightIntervals:
                    if max(i[0], j[0]) < min(i[1], j[1]):
                        return max(i[0], j[0])
            return None
        if self.operation == 2:
            if len(leftIntervals) == 0:
                return None
            if len(rightIntervals) == 0:
                return leftIntervals[0][0]
            for i in leftIntervals:
                for j in rightIntervals:
                    if j[1] > i[0]:
                        pass  # TODO
        return None

    def contains(self, pt):
        return self.left.contains(pt) or self.right.contains(pt)

    def getNormal(self, pt):
        if self.left.contains(pt):
            return self.left.getNormal(pt)
        if self.right.contains(pt):
            return self.right.getNormal(pt)
        return None


class CSG:
    def __init__(self, obj):
        self.material, self.matfunc, self.reflect, self.transparent, self.eta, self.min, self.max, self.center = \
            obj.material, obj.matfunc, obj.reflect, obj.transparent, obj.eta, obj.min, obj.max, obj.center
        self.root = obj

    def add(self, obj, operation):
        if self.root is None:
            self.root = Node(obj, obj, operation)
            self.center = obj.center
        else:
            self.root = Node(self.root, obj, operation)
        if operation == 0:
            self.min = np.minimum(self.min, obj.min)
            self.max = np.maximum(self.max, obj.max)
            self.center = (self.center + obj.center) / 2.0
        elif operation == 1:
            self.min = np.maximum(self.min, obj.min)
            self.max = np.minimum(self.max, obj.max)
            self.center = (self.max + self.min) / 2.0

    def intersectRay(self, ray):
        if self.root is None:
            return None
        return self.root.intersectRay(ray)

    def getNormal(self, pt):
        if self.root is None:
            return None
        return self.root.getNormal(pt)
