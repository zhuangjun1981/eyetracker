import unittest
import os
import cv2
import numpy as np
from .. import image_processor as ip

class TestImageProcessor(unittest.TestCase):

    def setUp(self):

        curr_folder = os.path.dirname(os.path.realpath(__file__))
        os.chdir(curr_folder)

    def test_temp(self):

        mov_path = os.path.join('test_files', 'test.avi')
        vc = cv2.VideoCapture(mov_path)
        res, img = vc.read()
        print(img.shape)
        img = img[120:330, 200:500, :]
        img_g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        img_g = cv2.equalizeHist(img_g)

        img_g = 255 - img_g

        ret, thresh = cv2.threshold(img_g, 250, 255, cv2.THRESH_BINARY)

        thresh = cv2.blur(src=thresh, ksize=(2, 2))
        kernel = np.ones((4, 4), dtype=np.uint8)
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel=kernel)
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel=kernel)
        img2, contours, hierarchy = cv2.findContours(image=thresh, mode=cv2.RETR_TREE, method=cv2.CHAIN_APPROX_SIMPLE)

        # edges = cv2.Canny(image=img_g, threshold1=1000, threshold2=5000, apertureSize=5)
        # img2, contours, hierarchy = cv2.findContours(image=edges, mode=cv2.RETR_TREE, method=cv2.CHAIN_APPROX_SIMPLE)
        print(len(contours))

        # cv2.drawContours(image=img, contours=contours, contourIdx=-1, color=(0, 255, 0), thickness=3)

        ellipse = cv2.fitEllipse(contours[0])
        print(ellipse)
        cv2.ellipse(img, ellipse, (0, 255, 0), 3)



        cv2.imshow('test', img)
        cv2.waitKey(0)

        cv2.destroyAllWindows()

    def test_Ellipse_get_binary_mask(self):
        import matplotlib.pyplot as plt
        ell = ip.Ellipse(center=(120.5, 70.8), axes=(22.6, 5.7), angle=25.5)
        mask = ell.get_binary_mask((256, 256))
        plt.imshow(mask)
        plt.colorbar()
        plt.show()

    def test_Ellipse_get_intensity(self):
        img = np.ones((256, 256))
        ell = ip.Ellipse(center=(120.5, 70.8), axes=(22.6, 5.7), angle=25.5)
        int = ell.get_intensity(img)
        assert(int == 1)