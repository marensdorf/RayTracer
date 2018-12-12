

class Object:
    def __init__(self, *args, **kwargs):
        for arg in kwargs:
            self.arg = kwargs[arg]

    def intersectRay(self, r):
        return None

    def getNormal(self, pt):
        return self.n

    def getMat(self, pt):
        return self.matfunc(self, pt)
