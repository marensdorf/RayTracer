import time
from PIL import Image
import concurrent.futures

import Halton
from BVH import AccelStruct
from Blobby import BlobbyParticles
from CSG import CSG
from Textures import *
from primatives.Plane import Plane
from primatives.Ray import Ray
from Complex import *
from Lights import PointLight, DirLight, AreaLight
from ViewPort import ViewPort
from tqdm import tqdm

from primatives.Sphere import Sphere


resolution = 400


def run():
    timeStart = time.time()
    perspective = True
    jittering = False
    numJitters = 8
    jitterArray = Halton.halton_sequence(numJitters, 2)

    o = AccelStruct()
    lights = []

    # OBJ file
    # m = Parser.parse("meshes/dragon.obj", transform=np.dot(Helper.scaleMatrix(0.7, 0.7, 0.7),
    #                                                        Helper.translationMatrix(1.25, 1.25, 1.75)))
    # print(m.min)
    # print(m.max)
    # o.add(m)

    # Cornell Box
    # o.add(RectFace([0, 0, 0], [550, 0, 0], [0, 0, 550], mat=[250, 250, 250]))  # floor
    # o.add(RectFace([0, 550, 0], [0, 550, 550], [550, 550, 0], mat=[250, 250, 250]))  # ceiling
    # o.add(RectFace([0, 0, 550], [550, 0, 550], [0, 550, 550], mat=[250, 250, 250]))  # back wall
    # o.add(RectFace([0, 0, 0], [0, 0, 550], [0, 550, 0], mat=[0, 250, 0]))  # right wall
    # o.add(RectFace([550, 0, 0], [550, 550, 0], [550, 0, 550], mat=[250, 0, 0]))  # left wall
    # o.add(Box([130, 0, 65], [160, 0, 49], [-49, 0, 160], [0, 165, 0], mat=[255, 255, 255]))  # short box
    # o.add(Box([265, 0, 296], [158, 0, -49], [49, 0, 158], [0, 330, 0], mat=[255, 255, 255]))  # tall box
    # # lights.append(AreaLight([213, 549, 227], [343, 549, 227], [213, 549, 332], o))
    # lights.append(PointLight([300, 540, 200]))
    # viewPt = np.array([278.0, 273.0, -800.0])
    # viewDir = Helper.normalize(np.array([0.0, 0.0, 1.0]))
    # viewUp = Helper.normalize(np.array([0.0, 1.0, 0.0]))
    # viewPortDist = 1.0
    # viewZoom = 1.5

    # Blobby
    # BlobbyParticles(o, [255, 0, 0], 0.1, *particles)
    # for p in particles:
    #     o.add(Sphere(2.0, p, mat=[255, 0, 0]))

    # Textures
    # o.add(Plane([0, 0, 0], [0, 1, 0], mat=[250, 250, 250], minimum=[-10, -10, -10], maximum=[10, 10, 10], matfunc=grid))
    # o.add(
    #     Plane([0, 0, -3], [0, 0, 1], mat=[250, 250, 250], minimum=[-10, -10, -10], maximum=[10, 10, 10], matfunc=grid))
    o.add(Sphere(2.0, [-3, 1, -1], mat=[50, 130, 250], matfunc=marbleTexture))

    # CSG
    c = CSG(Sphere(3.0, [0, 3, 0], mat=[250, 0, 0], matfunc=grid))
    c.add(Sphere(3.0, [1, 3, 0]), 1)
    # c.add(Sphere(3.0, [0.5, 0, 0]), 1)
    o.add(c)

    lights.append(PointLight([0, 10, 2]))
    viewPt = [0, 2, 6]
    viewDir = [0, 0, -1]
    viewUp = [0, 1, 0]
    viewPortDist = 1.0
    viewZoom = 0.5

    # create a viewport and image
    v = ViewPort(resolution, resolution, viewPt, viewDir, viewUp, viewPortDist, viewZoom)
    a = np.zeros((v.h, v.w, 3))
    o.calculate()
    print("Total time to setup objects: {:.3}s".format(time.time() - timeStart))
    timeStart = time.time()
    with concurrent.futures.ThreadPoolExecutor() as e:
        futures = []
        for row in tqdm(range(v.h)):
            for col in range(v.w):
                if jittering:
                    for n in range(numJitters):
                        ray = Ray(v.getPixelCenterJittered(col, row, jitterArray, n), viewDir)
                        if perspective:
                            ray.d = Helper.normalize(ray.o - viewPt)

                        futures.append(e.submit(Helper.rayTrace, ray, o, lights, row, col, 0))
                else:
                    ray = Ray(v.getPixelCenter(col, row), viewDir)
                    if perspective:
                        ray.d = Helper.normalize(ray.o - viewPt)

                    futures.append(e.submit(Helper.rayTrace, ray, o, lights, row, col, 0))
        with tqdm(total=v.h * v.w * numJitters if jittering else v.h * v.w) as pbar:
            for future in concurrent.futures.as_completed(futures):
                (row, col, color) = future.result()
                pbar.update()
                if color is not None:
                    if jittering:
                        a[row, col] += color / numJitters
                    else:
                        a[row, col] = color

    timeEnd = time.time()
    time.sleep(0.1)
    print("Total time to compute ray trace on {:} pixels: {:.4}s".format(v.w * v.h, timeEnd - timeStart))
    print("Average time to compute each pixel: {:.3}ms".format(1000.0 * (timeEnd - timeStart) / (v.w * v.h)))
    # a *= 255.0/a.max()
    im = Image.new("RGB", (v.w, v.h))
    pix = im.load()
    for row in range(v.h):
        for col in range(v.w):
            pix[row, (v.w - 1) - col] = tuple(a[row, col].astype(int))
    im.save('out.bmp')
    # im.show()


if __name__ == '__main__':
    np.set_printoptions(precision=4)
    np.seterr(divide='ignore', invalid='ignore')

    run()
