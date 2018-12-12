from Complex import Mesh
import numpy as np


def parse(fileName, mat=np.array([150, 150, 150]), transform=np.identity(4, dtype=np.float64)):
    f = open(fileName, "r")
    fl = f.readlines()
    m = Mesh(mat, transform)
    for line in fl:
        words = line.split(" ")
        if len(words) == 0:
            continue
        if words[0][0] == 'v':
            m.addVertex(float(words[1]), float(words[2]), float(words[3]))
            continue
        if words[0][0] == 'f':
            m.addFace(int(words[1]), int(words[2]), int(words[3]))
            continue
        print("Unknown line: \"" + line + "\"")  # error case
    return m
