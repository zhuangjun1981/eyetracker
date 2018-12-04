'''
module to detect pupil and LED reflection
'''

import numpy as np
import cv2


def apply_roi(img, roi):
    """
    :param img: 2d array
    :param roi: [min_height, max_height, min_width, max_width]
    :return: cropped image defined by roi
    """
    return img[roi[0]:roi[1], roi[2]:roi[3]]


def get_abs_position(pos, roi):
    """ Converts an ROI position to the position within the full img. """
    if roi:
        return int(pos[0]+roi[0]), int(pos[1]+roi[1])
    else:
        return pos


def get_relative_position(pos, roi):
    """ Converts an image position to a position within an ROI. """
    if roi:
        return int(pos[0]-roi[0]), int(pos[1]-roi[1])
    else:
        return pos


def dist2d(p1, p2):
    """ Returns the distance between two 2d points """
    return np.sqrt((p2[0] - p1[0]) ** 2 +
                   (p2[1] - p1[1]) ** 2)


class Ellipse(object):

    def __init__(self, center, axes, angle):
        """
        ellipse object to mark pupil and LED

        :param center: tuple of two positive floats, (center height, center width)
        :param axes: tuple of two positive floats, (length of first axis, length of second axis)
        :param angle: float, degree, clockwise rotation of first axis
        """
        self.center = center
        self.axes = axes
        self.angle = angle

    def get_area(self):
        return np.pi * self.axes[0] * self.axes[1]

    def get_binary_mask(self, shape):
        """
        :param shape: tuple of 2 positive integers (height, width)
        :return: binary mask of the ellipse with given shape
        """
        mask = np.zeros(shape=shape, dtype=np.uint8)
        mask = cv2.ellipse(mask,
                           center=(int(self.center[0]), int(self.center[1])),
                           axes=(int(self.axes[0]), int(self.axes[1])),
                           angle=self.angle,
                           startAngle=0,
                           endAngle=360,
                           color=1,
                           thickness=-1)
        return mask

    def get_intensity(self, img):
        """
        :param img: 2d gray scale image
        :return: mean intensity of ellipse
        """

        if len(img.shape) != 2:
            raise ValueError('input image should be 2d array.')

        mask = self.get_binary_mask(img.shape)
        return np.mean(img[mask])


class PupilLedDetector(object):

    def __init__(self):

        # # some stuff we want to track between frames
        # self.last_pupil = None  # ellipse object
        # self.last_led = None  # ellipse object
        # self.last_pupil_velocity = (0, 0)

        # # ----------------------------------------------------------------------
        # # images we want to track for displaying intermediate processing steps
        # self.original = None
        #
        # self.led_region = None
        # self.led_thresholded = None
        # self.led_blurred = None
        # self.led_openclosed = None
        # self.led_contoured = None  # cropped shape
        # self.led_annotated = None  # original shape
        #
        # self.pupil_region = None  # after masking LED
        # self.pupil_thresholded = None  # intensity reversed
        # self.pupil_blurred = None
        # self.pupil_openclosed = None
        # self.pupil_contoured = None  # cropped shape, with LED annotation
        # self.pupil_annotated = None  # original shape, with LED annotation

        # ----------------------------------------------------------------------
        # some stuff we want to allow the user to tweak
        # pupil
        self.pupil_roi = None
        self.pupil_binary_thresh = 210
        self.pupil_blur = 2
        self.pupil_openclose = 4
        self.pupil_min_size = 100

        # led
        self.led_roi = None
        self.led_binary_thresh = 200
        self.led_blur = 2
        self.led_openclose = 4
        self.led_min_size = 1
        self.led_max_size = 200
        self.led_mask_dilation = 5

        # preprocessing
        self.equalize = True

        self.clear()

    def clear(self):
        """
        clear processing results of current frame, but keep frame history information
        """
        # ----------------------------------------------------------------------
        # images we want to track for displaying intermediate processing steps
        self.original = None
        self.preprocessed = None

        self.led_region = None
        self.led_thresholded = None
        self.led_blurred = None
        self.led_openclosed = None
        self.led_contoured = None  # cropped shape
        self.led_annotated = None  # original shape

        self.pupil_region = None  # after masking LED
        self.pupil_thresholded = None  # intensity reversed
        self.pupil_blurred = None
        self.pupil_openclosed = None
        self.pupil_contoured = None  # cropped shape, with LED annotation
        self.pupil_annotated = None  # original shape, with LED annotation

    def clear_all(self):
        """
        clear all frame information, only keep processing parameters
        """
        self.clear()

        # some stuff we want to track between frames
        self.last_pupil = None  # ellipse object
        self.last_led = None  # ellipse object
        self.last_pupil_velocity = (0, 0)

    def _find_led(self):
        self.led_region = apply_roi(self.preprocessed, self.led_roi)
        _, self.led_thresholded = cv2.threshold(src=self.led_region, thresh=self.led_binary_thresh, maxval=255,
                                                type=cv2.THRESH_BINARY)
        self.led_blurred = cv2.blur(src=self.led_thresholded, ksize=(self.led_blur, self.led_blur))
        led_openclose_ker = np.ones((self.led_openclose, self.led_openclose), dtype=np.uint8)
        self.led_openclosed= cv2.morphologyEx(self.led_blurred, cv2.MORPH_OPEN, kernel=led_openclose_ker)
        self.led_openclosed = cv2.morphologyEx(self.led_openclosed, cv2.MORPH_CLOSE, kernel=led_openclose_ker)
        _, led_cons, _ = cv2.findContours(image=self.led_openclosed,
                                          mode=cv2.RETR_TREE,
                                          method=cv2.CHAIN_APPROX_SIMPLE)
        print('number of led contours: {}'.format(len(led_cons)))
        led_ell = cv2.fitEllipse(led_cons[0])
        # opencv fitEllipse give the center as (x, y) needs to be swapped to (height, width)
        led_center = get_abs_position((led_ell[0][1], led_ell[0][0]), self.led_roi)

        led = Ellipse(center=led_center, axes=led_ell[1], angle=led_ell[2])
        if led.get_area() < self.led_min_size or led.get_area() > self.led_max_size:
            return None
        else:
            # here: do a lot of things
            pass

    def _find_pupil(self):
        pass

    def _pre_process(self):

        self.preprocessed = cv2.cvtColor(self.original, code=cv2.COLOR_BGR2GRAY)
        if self.equalize:
            self.preprocessed = cv2.equalizeHist(self.preprocessed)

    def process_frame(self, img):

        self.original = img
        self._pre_process()
        self._find_led()
        self._find_pupil()





