from tqdm import tqdm
import cv2

if __name__ == '__main__':
    for i in tqdm(range(375)):
        img = cv2.imread('images/frame{0:04d}.bmp'.format(i))
        dst = cv2.fastNlMeansDenoisingColored(img, None, 10, 10, 7, 21)
        cv2.imwrite('denoisedImages/frame{0:04d}.bmp'.format(i), dst)
