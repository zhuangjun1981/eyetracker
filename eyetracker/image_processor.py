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
        return int(pos[0]+roi[0]), int(pos[1]+roi[2])
    else:
        return pos


def get_relative_position(pos, roi):
    """ Converts an image position to a position within an ROI. """
    if roi:
        return int(pos[0]-roi[0]), int(pos[1]-roi[2])
    else:
        return pos


def dist2d(p1, p2):
    """ Returns the distance between two 2d points """
    return np.sqrt((p2[0] - p1[0]) ** 2 +
                   (p2[1] - p1[1]) ** 2)


def get_circularity(contour):
    """
    given a contour detected by cv2.findContours, return the circular index of this contour

    circular index = 4 * pi * area / (perimeter ** 2)

    :param contour: list of (x, y) points from a contour.

    :return: float, circular index (0: not circle at all, line, 1: perfect circle)
    """

    area = cv2.contourArea(contour)
    peri = cv2.arcLength(contour,True) # get perimeter
    return 4 * np.pi * area / (peri ** 2)


class Ellipse(object):

    def __init__(self, center, axes, angle):
        """
        ellipse object to mark pupil and LED

        :param center: tuple of two positive floats, (center height, center width)
        :param axes: tuple of two positive floats, (length of first axis, length of second axis)
        :param angle: float, degree, counterclockwise rotation of first axis, from right direction
        """
        self.center = center
        self.axes = axes
        self.angle = angle

    def get_cv2_ellips(self):
        """
        :return: the ellipse in opencv3 format for drawing
        """
        # return ((int(round(self.center[1])), int(round(self.center[0]))),
        #         (int(round(self.axes[0])), int(round(self.axes[1]))),
        #         -self.angle, 0, 360)
        return ((int(self.center[1]), int(self.center[0])),
                (int(self.axes[0]), int(self.axes[1])),
                -self.angle, 0, 360)

    def get_area(self):
        return np.pi * self.axes[0] * self.axes[1]

    def get_binary_mask(self, shape):
        """
        :param shape: tuple of 2 positive integers (height, width)
        :return: binary mask of the ellipse with given shape
        """
        mask = np.zeros(shape=shape, dtype=np.uint8)
        ell_cv2 = self.get_cv2_ellips()
        mask = cv2.ellipse(mask, center=ell_cv2[0], axes=ell_cv2[1], angle=ell_cv2[2], startAngle=0, endAngle=360,
                           color=1, thickness=-1)
        return mask.astype(np.uint8)

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

    def draw(self, img, color=(0, 255, 0), thickness=3):

        ell_cv2 = self.get_cv2_ellips()
        img_marked = cv2.ellipse(img=img, center=ell_cv2[0], axes=ell_cv2[1], angle=ell_cv2[2], startAngle=ell_cv2[3],
                                 endAngle=ell_cv2[4], color=color, thickness=thickness)
        return img_marked

    @staticmethod
    def from_cv2_box(box):
        """
        get Ellipse object from cv2 rotated rectangle object (from cv2.fitEllipse() function)
        """
        center = (box[0][1], box[0][0])
        axes = (box[1][0] / 2., box[1][1] / 2.)
        angle = -box[2]
        return Ellipse(center=center, axes=axes, angle=angle)


class PupilLedDetector(object):

    def __init__(self,
                 is_equalize=True,
                 led_roi=None,
                 pupil_roi=None,
                 led_binary_threshold=230,
                 pupil_binary_threshold=210,
                 led_blur=2,
                 pupil_blur=2,
                 led_openclose_iter=1,
                 pupil_openclose_iter=4,
                 led_min_size=1,
                 pupil_min_size=200,
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
        self.annotated = np.array(frame)

    def load_first_frame(self, frame):
        self.clear_all()
        self.original = frame
        self.annotated = np.array(frame)

    def _find_led(self):

        # the following imaging processing steps could be simplified
        self.led_region = apply_roi(self.preprocessed, self.led_roi)
        self.led_blurred = cv2.blur(src=self.led_region, ksize=(self.led_blur, self.led_blur))
        _, self.led_thresholded = cv2.threshold(src=self.led_blurred, thresh=self.led_binary_thresh, maxval=255,
                                                type=cv2.THRESH_BINARY)
        led_openclose_ker = np.ones((self.led_openclose_iter, self.led_openclose_iter), dtype=np.uint8)
        self.led_openclosed = cv2.morphologyEx(src=self.led_thresholded, op=cv2.MORPH_OPEN, kernel=led_openclose_ker)
        self.led_openclosed = cv2.morphologyEx(src=self.led_openclosed, op=cv2.MORPH_CLOSE, kernel=led_openclose_ker)
        _, led_cons, _ = cv2.findContours(image=self.led_openclosed,
                                          mode=cv2.RETR_TREE, method=cv2.CHAIN_APPROX_SIMPLE)
        print('number of led contours: {}'.format(len(led_cons)))

        self.led_contoured = cv2.drawContours(image=cv2.cvtColor(src=self.led_openclosed, code=cv2.COLOR_GRAY2BGR),
                                              contours=led_cons, contourIdx=-1, color=(255, 0, 0), thickness=1)
        led = self._filter_led_contour(led_cons)

        if led:
            self.led = led.outof_roi(self.led_roi)
            self.annotated = self.led.draw(img=self.annotated, color=(255, 0, 0), thickness=2)
            return True
        else:
            return False

    def _find_pupil(self):

        self.pupil_region = apply_roi(self.preprocessed, self.pupil_roi)
        self.pupil_blurred = cv2.blur(src=self.pupil_region, ksize=(self.pupil_blur, self.pupil_blur))
        self.pupil_blurred = 255 - self.pupil_blurred
        _, self.pupil_thresholded = cv2.threshold(src=self.pupil_blurred, thresh=self.pupil_binary_thresh,
                                                  maxval=255, type=cv2.THRESH_BINARY)
        pupil_openclose_ker = np.ones((self.pupil_openclose_iter, self.pupil_openclose_iter), dtype=np.uint8)
        self.pupil_openclosed = cv2.morphologyEx(src=self.pupil_thresholded, op=cv2.MORPH_OPEN,
                                                 kernel=pupil_openclose_ker)
        self.pupil_openclosed = cv2.morphologyEx(src=self.pupil_openclosed, op=cv2.MORPH_CLOSE,
                                                 kernel=pupil_openclose_ker)
        _, pupil_cons, _ = cv2.findContours(image=self.pupil_openclosed, mode=cv2.RETR_TREE,
                                            method=cv2.CHAIN_APPROX_SIMPLE)



        pupil, pupil_cons = self._filter_pupil_contour(pupil_cons)

        if pupil_cons:
            self.pupil_contoured = cv2.drawContours(image=cv2.cvtColor(src=self.pupil_openclosed, code=cv2.COLOR_GRAY2BGR),
                                                    contours=pupil_cons, contourIdx=-1, color=(0, 255, 0), thickness=1)

        if pupil:
            self.pupil = pupil.outof_roi(self.pupil_roi)
            self.annotated = self.pupil.draw(img=self.annotated, color=(0, 255, 0), thickness=2)
            return True
        else:
            return False

    def _filter_led_contour(self, cons):
        """
        for each detected potential led contour, first pick contours with at least 5 points,
        then pick the roundest one

        :param cons: detected led contours
        :return: Ellipse object of detected led, None if not detected
        """

        if cons:

            cons_filtered = np.array([con for con in cons if con.shape[0] >= 5])

            if len(cons_filtered) == 0: # no LED contours can be fit to ellipse by cv2
                return None
            else: # there are LED contours can be fit to ellipse, pick the biggest one
                ells = [Ellipse.from_cv2_box(cv2.fitEllipse(con)) for con in cons_filtered]
                areas = [ell.get_area() for ell in ells]
                area = np.max(areas)

                if area >= self.led_min_size and area <= self.led_max_size:
                    return ells[int(np.argmax(areas))]
                else: # picked LED does not meet size criteria
                    return None
        else:
            return None

    def _mask_led(self, cons):
        """
        for each detected potential pupil contour, mask out the shape of led

        :param cons: detected pupil contours
        """

        if self.led is None:
            return cons
        else:
            led_mask = self.led.into_roi(self.pupil_roi).get_binary_mask(self.preprocessed.shape)
            led_mask_kern = np.ones((self.led_mask_dilation, self.led_mask_dilation), dtype=np.uint8)
            led_mask = cv2.dilate(src=led_mask, kernel=led_mask_kern, iterations=1)

            new_cons = []

            # print(cons[0].shape)

            # this may be slow
            for con in cons:
                new_con = []
                for point in con:
                    if led_mask[point[0, 1], point[0, 0]] == 0:
                        new_con.append(point)
                if new_con:
                    new_cons.append(np.array(new_con))

                    # img = cv2.cvtColor(np.array(self.pupil_region), cv2.COLOR_GRAY2BGR)
                    # cv2.drawContours(image=img, contours=[con], contourIdx=0, color=(255, 0, 0), thickness=2)
                    # cv2.drawContours(image=img, contours=[np.array(new_con)], contourIdx=0, color=(0, 255, 0),
                    #                  thickness=2)
                    # f = plt.figure()
                    # ax = f.add_subplot(111)
                    # ax.imshow(img)
                    # plt.show()

            return new_cons

    def _filter_pupil_contour(self, cons):
        """
        for each detected potential pupil contour after LED masking, pick the
        roundest one and the one closest to the pupil from last frame

        :param cons: detected pupil contours
        :return: Ellipse object of detected pupil, None if not detected
                 contours filtered by size, None if not detected
        """

        cons_masked = self._mask_led(cons)

        if cons_masked:

            cons_filtered = np.array([con for con in cons_masked if con.shape[0] >= 5])

            if len(cons_filtered) == 0: # no pupil contours can be fit to ellipse by cv2
                return None, None
            else: # there are contours that can be fit to ellipse
                ells = [Ellipse.from_cv2_box(cv2.fitEllipse(con)) for con in cons_filtered]
                areas = [ell.get_area() for ell in ells]
                size_ind = [i for i, area in enumerate(areas) if area >= self.pupil_min_size]
                ells_area = [ells[i] for i in size_ind]
                cons_area = [cons_filtered[i] for i in size_ind]
                circ_area = [get_circularity(con) for con in cons_area]

                if not ells: # no pupil ellipse bigger than self.pupil_min_size
                    return None, None
                else:
                    if self.last_pupil: # there is last pupil pick the closest one
                        dises = [dist2d(ell.center, self.last_pupil.center) for ell in ells_area]
                        return ells_area[int(np.argmin(dises))]
                    else: # no last pupil information pick the roundest one
                        return ells_area[int(np.argmax(circ_area))], cons_area

        else: # no pupil contours after led masking
            return None, None

    def _pre_process(self):

        self.preprocessed = cv2.cvtColor(self.original, code=cv2.COLOR_BGR2GRAY)
        if self.is_equalize:
            self.preprocessed = cv2.equalizeHist(self.preprocessed)

    def detect(self):
        self._pre_process()
        is_led = self._find_led()

        if is_led:
            is_pupil = self._find_pupil()

            if is_pupil:
                return True
            else:
                return False
        return False

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

        ax9 = f.add_subplot(3, 4, 9)
        if self.pupil_blurred is not None:
            ax9.imshow(self.pupil_blurred, vmin=0, vmax=255, cmap='gray')
        ax9.set_axis_off()
        ax9.set_title('pupil blurred')

        ax10 = f.add_subplot(3, 4, 10)
        if self.pupil_thresholded is not None:
            ax10.imshow(self.pupil_thresholded, vmin=0, vmax=255, cmap='gray')
        ax10.set_axis_off()
        ax10.set_title('pupil thresholded')

        ax11 = f.add_subplot(3, 4, 11)
        if self.pupil_openclosed is not None:
            ax11.imshow(self.pupil_openclosed, vmin=0, vmax=255, cmap='gray')
        ax11.set_axis_off()
        ax11.set_title('pupil openclosed')

        ax12 = f.add_subplot(3, 4, 12)
        if self.pupil_contoured is not None:
            ax12.imshow(self.pupil_contoured)
        ax12.set_axis_off()
        ax12.set_title('pupil contoured')









