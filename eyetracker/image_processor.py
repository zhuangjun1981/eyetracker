'''
module to detect pupil and LED reflection
'''

import numpy as np
import cv2
import matplotlib.pyplot as plt


def apply_roi(img, roi):
    """
    :param img: 2d array
    :param roi: [min_height, max_height, min_width, max_width]
    :return: cropped image defined by roi
    """
    if roi:
        return img[roi[0]:roi[1], roi[2]:roi[3]]
    else:
        return img


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

    def into_roi(self, roi):
        """
        :return: new Ellipse object with roi coordinates from full frame coordinates
        """
        return Ellipse(center=get_relative_position(self.center, roi),
                       axes=self.axes,
                       angle=self.angle)

    def outof_roi(self, roi):
        """
        :return: new Ellipse object with full frame coordinates from roi coordinates
        """
        return Ellipse(center=get_abs_position(self.center, roi),
                       axes=self.axes,
                       angle=self.angle)

    def get_cv2_ellips(self):
        return ((int(self.center[0]), int(self.center[1])), (int(self.axes[0]), int(self.axes[1])), self.angle, 0, 360)


class PupilLedDetector(object):

    def __init__(self,
                 is_equalize=True,
                 led_roi=None,
                 pupil_roi=None,
                 led_binary_threshold=230,
                 pupil_binary_threshold=210,
                 led_blur=2,
                 pupil_blur=2,
                 led_openclose_iter=4,
                 pupil_openclose_iter=4,
                 led_min_size=1,
                 pupil_min_size=100,
                 led_max_size=1000,
                 led_mask_dilation=5,
                 ):

        # # some stuff we want to track between frames
        # self.last_pupil = None  # ellipse object
        # self.last_pupil_intensity = None
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
        #
        # self.led = None # ellipse object in whole frame
        # self.pupil = None # ellipse object in whole frame

        # ----------------------------------------------------------------------
        # some stuff we want to allow the user to tweak

        # preprocessing
        # self.is_equalize = is_equalize
        #
        # # pupil
        # self.pupil_roi = pupil_roi
        # self.pupil_binary_thresh = pupil_binary_threshold
        # self.pupil_blur = pupil_blur
        # self.pupil_openclose_iter = pupil_openclose_iter
        # self.pupil_min_size = pupil_min_size
        #
        # # led
        # self.led_roi = led_roi
        # self.led_binary_thresh = led_binary_threshold
        # self.led_blur = led_blur
        # self.led_openclose_iter = led_openclose_iter
        # self.led_min_size = led_min_size
        # self.led_max_size = led_max_size
        # self.led_mask_dilation = led_mask_dilation

        self.load_parameters(is_equalize=is_equalize, led_roi=led_roi, pupil_roi=pupil_roi,
                             led_binary_threshold=led_binary_threshold,
                             pupil_binary_threshold=pupil_binary_threshold, led_blur=led_blur,
                             pupil_blur=pupil_blur, led_openclose_iter=led_openclose_iter,
                             pupil_openclose_iter=pupil_openclose_iter, led_min_size=led_min_size,
                             pupil_min_size=pupil_min_size, led_max_size=led_max_size,
                             led_mask_dilation=led_mask_dilation)

        self.clear_all()

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


        self.pupil_region = None  # after masking LED
        self.pupil_thresholded = None  # intensity reversed
        self.pupil_blurred = None
        self.pupil_openclosed = None
        self.pupil_contoured = None  # cropped shape, with LED annotation

        self.annotated = None  # original shape, with LED annotation

        self.led = None # ellipse object in whole frame
        self.pupil = None # ellipse object in whole frame

    def clear_all(self):
        """
        clear all frame information, only keep processing parameters
        """
        self.clear()

        # some stuff we want to track between frames
        self.last_pupil = None  # ellipse object
        # self.last_pupil_intensity = None
        self.last_led = None  # ellipse object
        # self.last_pupil_velocity = (0, 0) # not used

    def load_parameters(self, is_equalize, led_roi, pupil_roi, led_binary_threshold, pupil_binary_threshold, led_blur,
                        pupil_blur, led_openclose_iter, pupil_openclose_iter, led_min_size, pupil_min_size,
                        led_max_size, led_mask_dilation):
        # preprocessing
        self.is_equalize = is_equalize

        # pupil
        self.pupil_roi = pupil_roi
        self.pupil_binary_thresh = pupil_binary_threshold
        self.pupil_blur = pupil_blur
        self.pupil_openclose_iter = pupil_openclose_iter
        self.pupil_min_size = pupil_min_size

        # led
        self.led_roi = led_roi
        self.led_binary_thresh = led_binary_threshold
        self.led_blur = led_blur
        self.led_openclose_iter = led_openclose_iter
        self.led_min_size = led_min_size
        self.led_max_size = led_max_size
        self.led_mask_dilation = led_mask_dilation

        self.clear()

    def load_next_frame(self, frame):
        """
        load next frame, keep processing history
        :return:
        """
        self.last_led = self.led
        self.last_pupil = self.pupil
        self.clear()
        self.original = frame

    def load_first_frame(self, frame):
        self.clear_all()
        self.original = frame

    def _find_led(self):
        self.led_region = apply_roi(self.preprocessed, self.led_roi)
        self.led_blurred = cv2.blur(src=self.led_region, ksize=(self.led_blur, self.led_blur))
        _, self.led_thresholded = cv2.threshold(src=self.led_blurred, thresh=self.led_binary_thresh, maxval=255,
                                                type=cv2.THRESH_BINARY)
        led_openclose_ker = np.ones((self.led_openclose_iter, self.led_openclose_iter), dtype=np.uint8)
        self.led_openclosed= cv2.morphologyEx(self.led_thresholded, cv2.MORPH_OPEN, kernel=led_openclose_ker)
        self.led_openclosed = cv2.morphologyEx(self.led_openclosed, cv2.MORPH_CLOSE, kernel=led_openclose_ker)
        _, led_cons, _ = cv2.findContours(image=self.led_openclosed,
                                          mode=cv2.RETR_TREE,
                                          method=cv2.CHAIN_APPROX_SIMPLE)
        print('number of led contours: {}'.format(len(led_cons)))

        self.led_contoured = cv2.drawContours(image=cv2.cvtColor(src=self.led_openclosed, code=cv2.COLOR_GRAY2BGR),
                                              contours=led_cons, contourIdx=-1, color=(255, 0, 0), thickness=2)

        # print('\n'.join([str(con) for con in led_cons]))
        led_ell = cv2.fitEllipse(led_cons[0])
        # opencv fitEllipse give the center as (x, y) needs to be swapped to (height, width)
        led_center = get_abs_position((led_ell[0][1], led_ell[0][0]), self.led_roi)

        led = Ellipse(center=led_center, axes=led_ell[1], angle=led_ell[2])

        if led.get_area() < self.led_min_size or led.get_area() > self.led_max_size:
            self.led = None
            return False
        else:
            # here: do a lot of things
            self.led = led.outof_roi(self.led_roi)
            print(self.led.center)
            self.annotated = np.array(self.original)
            cv2.ellipse(img=self.annotated, center=(int(self.led.center[0]), int(self.led.center[1])),
                        axes=(int(self.led.axes[0]), int(self.led.axes[1])), angle=self.led.angle, startAngle=0,
                        endAngle=360, color=(255, 255, 0), thickness=2)
            return True

    def _find_pupil(self):
        self.pupil = None
        pass

    def _pre_process(self):

        self.preprocessed = cv2.cvtColor(self.original, code=cv2.COLOR_BGR2GRAY)
        if self.is_equalize:
            self.preprocessed = cv2.equalizeHist(self.preprocessed)

    def detect(self):

        self._pre_process()
        is_led = self._find_led()

        if is_led:
            is_pupil = self._find_pupil()
        else:
            self.pupil = None

    def show_results(self):

        f = plt.figure(figsize=(12, 9))

        ax1 = f.add_subplot(3, 4, 1)
        if self.original is not None:
            to_show = np.array(self.original)
            if self.led_roi is not None:
                to_show = cv2.rectangle(img=to_show, pt1=(self.led_roi[2], self.led_roi[0]),
                                        pt2=(self.led_roi[3], self.led_roi[1]), color=(255, 0, 0),
                                        thickness=3)
            if self.pupil_roi is not None:
                to_show = cv2.rectangle(img=to_show, pt1=(self.pupil_roi[2], self.pupil_roi[0]),
                                        pt2=(self.pupil_roi[3], self.pupil_roi[1]), color=(0, 255, 0),
                                        thickness=3)
            ax1.imshow(to_show)
        ax1.set_title('original')
        ax1.set_axis_off()

        ax2 = f.add_subplot(3, 4, 2)
        if self.preprocessed is not None:
            ax2.imshow(self.preprocessed, cmap='gray', vmin=0, vmax=255)
        ax2.set_title('preprocessed')
        ax2.set_axis_off()

        ax4 = f.add_subplot(3, 4, 4)
        if self.annotated is not None:
           ax4.imshow(self.annotated)
        ax4.set_title('annotated')
        ax4.set_axis_off()

        ax5 = f.add_subplot(3, 4, 5)
        if self.led_blurred is not None:
            ax5.imshow(self.led_blurred, vmin=0, vmax=255, cmap='gray')
        ax5.set_axis_off()
        ax5.set_title('led blurred')

        ax6 = f.add_subplot(3, 4, 6)
        if self.led_thresholded is not None:
            ax6.imshow(self.led_thresholded, vmin=0, vmax=1, cmap='gray')
        ax6.set_axis_off()
        ax6.set_title('led thresholded')

        ax7 = f.add_subplot(3, 4, 7)
        if self.led_openclosed is not None:
            ax7.imshow(self.led_openclosed, vmin=0, vmax=1, cmap='gray')
        ax7.set_axis_off()
        ax7.set_title('led openclosed')

        ax8 = f.add_subplot(3, 4, 8)
        if self.led_contoured is not None:
            ax8.imshow(self.led_contoured)
        ax8.set_axis_off()
        ax8.set_title('led contoured')









