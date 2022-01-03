import io
import os
import cv2
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
from args import *


def ToPIL(fig):
    buf = io.BytesIO()
    fig.savefig(buf)
    buf.seek(0)
    return Image.open(buf)


def ReadImage(name, isBinary=False, resize=None):
    path = os.path.join(IMAGE_FOLDER, name)
    if isBinary:
        img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
        img = (img == 255) * 1.
    else:
        img = cv2.imread(path)[::-1]
    
    if resize:
        img = cv2.resize(img, (resize, resize), interpolation=cv2.INTER_NEAREST)
    
    return img


def ShowImage(img, isBinary=False):
    if isBinary:
        plt.imshow(img, cmap="gray")
    else:
        plt.imshow(img)

    plt.show()


def ToDistribution(arr):
    w = np.exp(arr - arr.min()) ** 4
    w /= w.sum()
    return w


def IsVectorSame(v0, v1, eps=1e-4):
    d = (((v0 - v1) ** 2).sum()) ** 0.5
    return d <= eps


if __name__ == '__main__':
    a = np.array([1, 2])
    b = np.array([1.00002, 2])
    print(IsVectorSame(a, b))