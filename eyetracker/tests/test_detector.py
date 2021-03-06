import unittest
import os
import cv2
import numpy as np
import eyetracker.detector as dt
import matplotlib.pyplot as plt

class TestDetector(unittest.TestCase):

    def setUp(self):

        curr_folder = os.path.dirname(os.path.realpath(__file__))
        os.chdir(curr_folder)

    def test_Ellipse(self):
        ell = dt.Ellipse(center=(64.3, 192.2), axes=(22.6, 5.7), angle=45.0)
        mask = ell.get_binary_mask((256, 256))

        assert(mask[64, 192] == 1)
        assert(mask[64, 212] == 0)
        assert(mask[44, 192] == 0)
        assert(mask[78, 178] == 1)
        assert(mask[50, 206] == 1)

        img = cv2.cvtColor(src=mask*255, code=cv2.COLOR_GRAY2BGR)
        img_marked = ell.draw(img=img, color=(0, 255, 0), thickness=1)
        plt.imshow(img_marked)
        plt.colorbar()
        plt.show()

    def test_Ellipse_get_intensity(self):
        img = np.ones((256, 256))
        ell = dt.Ellipse(center=(120.5, 70.8), axes=(22.6, 5.7), angle=25.5)
        int = ell.get_intensity(img)
        assert(int == 1)

    def test_Ellipse_roi(self):
        ell = dt.Ellipse(center=(64.3, 192.2), axes=(22.6, 5.7), angle=45.0)
        mask = ell.get_binary_mask((256, 256))

        roi = [0, 128, 128, 256]
        ell_roi = ell.into_roi(roi)
        mask_roi = ell_roi.get_binary_mask((128, 128))

        assert (mask_roi[64, 64] == 1)
        assert (mask_roi[64, 84] == 0)
        assert (mask_roi[44, 64] == 0)
        assert (mask_roi[78, 50] == 1)
        assert (mask_roi[50, 78] == 1)

        f = plt.figure(figsize=(8, 4))
        ax1 = f.add_subplot(1, 2, 1)
        img_marked = ell.draw(img=cv2.cvtColor(mask * 255, cv2.COLOR_GRAY2BGR), color=(0, 255, 0), thickness=2)
        cv2.rectangle(img_marked, pt1=(roi[2], roi[0]), pt2=(roi[3], roi[1]), color=(255, 0, 0), thickness=2)
        ax1.imshow(img_marked)
        ax1.set_title('full')

        ax2 = f.add_subplot(1, 2, 2)
        img_marked_roi = ell_roi.draw(img=cv2.cvtColor(mask_roi * 255, cv2.COLOR_GRAY2BGR),
                                      color=(0, 255, 0), thickness=2)
        ax2.imshow(img_marked_roi)
        ax2.set_title('roi')
        plt.show()

    def test_PupilLedDetector_detect(self):
        img = np.load(os.path.join('test_files', 'test_img.npy'))
        det = dt.PupilLedDetector(led_roi=(200, 300, 280, 400),
                                  pupil_roi=(100, 350, 200, 500),
                                  led_binary_threshold=200,
                                  led_openclose_iter=1,
                                  led_mask_dilation=20,
                                  pupil_binary_threshold=240,
                                  pupil_openclose_iter=10,
                                  pupil_min_size=500)
        det.load_frame(frame=img)
        det.detect()
        det.show_results()
        plt.show()

    def test_PupilLedDetector_detect2(self):
        img = np.load(os.path.join('test_files', 'test_img2.npy'))
        det = dt.PupilLedDetector(led_roi=(80, 140, 130, 200),
                                  pupil_roi=(0, 240, 0, 320),
                                  led_binary_threshold=250,
                                  led_openclose_iter=1,
                                  pupil_binary_threshold=200,
                                  pupil_openclose_iter=5,
                                  pupil_min_size=500,
                                  led_mask_dilation=20,
                                  pupil_is_equalize=False)
        det.load_frame(frame=img)
        det.detect()
        det.show_results()
        plt.show()

    def test_PupilLedDetector_detect3(self):

        cap = cv2.VideoCapture(os.path.join('test_files', 'test2.avi'))
        cap.set(cv2.CAP_PROP_POS_FRAMES, 35)
        _, frame0 = cap.read()
        cap.set(cv2.CAP_PROP_POS_FRAMES, 36)
        _, frame1 = cap.read()

        det = dt.PupilLedDetector(led_binary_threshold=200,
                                  led_blur=2,
                                  led_mask_dilation=5,
                                  led_max_size=1000.0,
                                  led_min_size=1.0,
                                  led_openclose_iter=1,
                                  led_roi=[209, 293, 224, 321],
                                  pupil_binary_threshold=240,
                                  pupil_blur=2,
                                  pupil_is_equalize=True,
                                  pupil_min_size=500.0,
                                  pupil_openclose_iter=15,
                                  pupil_roi=[102, 352, 131, 431])

        det.load_frame(frame0)
        det.detect(last_pupil=None)

        last_pupil = det.pupil

        det.load_frame(frame1)
        det.detect(last_pupil=None)
        det.show_results()
        plt.show()

        det.detect(last_pupil=last_pupil)
        det.show_results()
        plt.show()

    def test_PupilLedDetector_detect4(self):

        frame3 = np.load(os.path.join('test_files', 'test_img3.npy'))
        det = dt.PupilLedDetector(led_roi=(275, 375, 233, 353),
                                  pupil_roi=(176, 426, 146, 446),
                                  led_binary_threshold=240,
                                  led_openclose_iter=1,
                                  led_mask_dilation=20,
                                  pupil_blur=10,
                                  pupil_binary_threshold=250,
                                  pupil_openclose_iter=5,
                                  pupil_min_size=500,
                                  pupil_is_equalize=True)
        det.load_frame(frame=frame3)
        det.detect()
        det.show_results()
        plt.show()
        source1 = det.pupil_blurred
        th1_o = det.pupil_thresholded

        frame1 = np.load(os.path.join('test_files', 'test_img.npy'))
        det = dt.PupilLedDetector(led_roi=(200, 300, 280, 400),
                                  pupil_roi=(100, 350, 200, 500),
                                  led_binary_threshold=240,
                                  led_openclose_iter=1,
                                  led_mask_dilation=20,
                                  pupil_blur=10,
                                  pupil_binary_threshold=250,
                                  pupil_openclose_iter=10,
                                  pupil_min_size=500,
                                  pupil_is_equalize=True)

        det.load_frame(frame=frame1)
        det.detect()
        det.show_results()
        plt.show()
        source2 = det.pupil_blurred
        th2_o = det.pupil_thresholded

    def test_PupilLedDetector_detect5(self):

        frame4 = np.load(os.path.join('test_files', 'test_img4.npy'))
        det = dt.PupilLedDetector(led_roi=[220, 291, 295, 362],
                                  pupil_roi=[157, 333, 241, 439],
                                  led_binary_threshold=200,
                                  led_openclose_iter=5,
                                  led_mask_dilation=20,
                                  pupil_blur=10,
                                  pupil_binary_threshold=180,
                                  pupil_openclose_iter=10,
                                  pupil_min_size=500,
                                  pupil_is_equalize=True)

        det.load_frame(frame=frame4)
        det.detect()
        det.show_results()
        plt.show()

        # th1 = cv2.adaptiveThreshold(src=source1,
        #                             maxValue=255,
        #                             adaptiveMethod=cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        #                             thresholdType=cv2.THRESH_BINARY,
        #                             blockSize=33,
        #                             C=0)
        #
        # th2 = cv2.adaptiveThreshold(src=source2,
        #                             maxValue=255,
        #                             adaptiveMethod=cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        #                             thresholdType=cv2.THRESH_BINARY,
        #                             blockSize=33,
        #                             C=0)
        #
        # f = plt.figure(figsize=(10, 5))
        # f.suptitle('adaptive thr')
        # ax1 = f.add_subplot(121)
        # ax1.imshow(th1, cmap='gray')
        # ax1.set_axis_off()
        # ax2 = f.add_subplot(122)
        # ax2.imshow(th2, cmap='gray')
        # ax2.set_axis_off()
        #
        # f2 = plt.figure(figsize=(10, 5))
        # f2.suptitle('global thr')
        # ax3 = f2.add_subplot(121)
        # ax3.imshow(th1_o, cmap='gray')
        # ax3.set_axis_off()
        # ax4 = f2.add_subplot(122)
        # ax4.imshow(th2_o, cmap='gray')
        # ax4.set_axis_off()
        # plt.show()

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
        # print(len(contours))

        # cv2.drawContours(image=img, contours=contours, contourIdx=-1, color=(0, 255, 0), thickness=3)

        ellipse = cv2.fitEllipse(contours[0])
        # print(ellipse)
        cv2.ellipse(img, ellipse, (0, 255, 0), 3)



        cv2.imshow('test', img)
        cv2.waitKey(0)

        cv2.destroyAllWindows()