import numpy as np
import Helper


class ViewPort:
    """Viewport for calculating pixel points in world-space

    Attributes:
        w, h: Width and height, in pixels, of image
        ratio: ratio of width to height, used to keep image from stretching
        forward, up, right: Numpy arrays representing normal vectors for
            conversion from world-space to view-space
        p: Numpy array representing the coordinates of the camera in world-space
        d: Distance from camera to view plane
        zoom: Camera zoom
        c: Center of view plane
        swCorner: Bottom left corner of view plane, basis of all pixel coordinates
    """

    def __init__(self, width, height, viewPt, viewDir, viewUp, viewPortDist, viewZoom):
        self.w = width
        self.h = height
        self.ratio = self.w / self.h
        self.forward = Helper.normalize(np.asfarray(viewDir))
        self.up = Helper.normalize(np.asfarray(viewUp))
        self.right = Helper.normalize(np.cross(self.forward, self.up))
        self.p = np.asfarray(viewPt)
        self.d = viewPortDist
        self.zoom = viewZoom
        self.c = self.p + (self.d * self.forward)
        self.swCorner = self.c - (self.right / self.zoom) / 2.0 - (self.up / self.zoom) / 2.0

    def getPixelCenter(self, r, c):
        return self.swCorner + (c + 0.5) * (self.right / self.w) / self.zoom + (r + 0.5) * (
                    self.up / self.h) / self.zoom

    def getPixelCenterJittered(self, r, c, halton, n):
        return self.swCorner + (c + halton[0][n]) * (self.right / self.w) / self.zoom + (r + halton[1][n]) * (
                    self.up / self.h) / self.zoom
