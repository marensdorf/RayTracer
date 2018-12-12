import time
from PIL import Image
import concurrent.futures

import Halton
from BVH import AccelStruct
from Blobby import BlobbyParticles
from Textures import *
from primatives.Plane import Plane
from primatives.Ray import Ray
from Complex import *
from Lights import *
from ViewPort import ViewPort
from tqdm import tqdm

from primatives.Sphere import Sphere


def run(frame, viewPt, *particles):
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
    BlobbyParticles(o, [255, 0, 0], 0.1, *particles)
    # for p in particles:
    #     o.add(Sphere(2.0, p, mat=[255, 0, 0]))
    o.add(Plane([0, 0, 0], [0, 1, 0], mat=[250, 250, 250], minimum=[-10, -10, -10], maximum=[10, 10, 10], matfunc=grid))
    o.add(
        Plane([0, 0, -3], [0, 0, 1], mat=[250, 250, 250], minimum=[-10, -10, -10], maximum=[10, 10, 10], matfunc=grid))
    lights.append(PointLight([0, 10, 2]))
    viewDir = [0, 0, -1]
    viewUp = [0, 1, 0]
    viewPortDist = 1.0
    viewZoom = 0.5

    # create a viewport and image
    v = ViewPort(256, 256, viewPt, viewDir, viewUp, viewPortDist, viewZoom)
    a = np.zeros((v.h, v.w, 3))
    o.calculate()
    print("Total time to setup objects: {:.3}s".format(time.time() - timeStart))
    timeStart = time.time()
    with concurrent.futures.ThreadPoolExecutor() as e:
        futures = []
        for row in range(v.h):
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
    im.save('images/frame{0:04d}.bmp'.format(frame))
    # im.show()


if __name__ == '__main__':
    np.set_printoptions(precision=3)
    np.seterr(divide='ignore', invalid='ignore')

    gravity = 40.0
    framerate = 30.0
    seconds = 12.5
    frametime = 1.0 / framerate

    p1 = np.asfarray([-1.821, 3.712, 0.])
    p2 = np.asfarray([1.821, 4.288, 0.])
    v1 = np.asfarray([-1.737, 1.374, 0.])
    v2 = -v1
    vPt = np.asfarray([0, 3, 6])
    viewDir = np.asfarray([0, 0, -1])

    lastframe = time.time()
    for i in tqdm(range(247, int(seconds * framerate))):
        time.sleep(0.1)
        print('Frame: ' + str(i))
        print(p1, end='\t')
        print(v1)
        print(p2, end='\t')
        print(v2)
        run(i, vPt, p1, p2)
        p1 += v1 * frametime
        p2 += v2 * frametime

        p1top2 = p2 - p1
        distsq = p1top2.dot(p1top2)
        a1 = Helper.normalize(p1top2) * gravity / distsq
        a2 = -a1
        v1 += a1 * frametime
        v2 += a2 * frametime

        print('Frame calculated in {0:.3f}s'.format(time.time() - lastframe))
        lastframe = time.time()
        time.sleep(0.1)
