#!/usr/bin/env python
"""
image_processing.py

Allen Institute for Brain Science

@author: derricw

Created on Sep 1, 2014

Derric's new eyetracking algorithm.

Used by eyetracker.py and eyetrackergui.py

"""

import cv2
import os
import math


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
    return math.sqrt((p2[0] - p1[0]) ** 2 +
                     (p2[1] - p1[1]) ** 2)


#@timeit
def filter_features(featureset, ideal=None):
    """
    Returns the best match to the ideal.

    Uses position, radius, and circle distance to score features and return
        the one with the minimum score.

    TODO: Make this not garbage.

    """
    if ideal is None:
        return featureset[-1]
    scores = []
    pos0 = ideal.centroid()
    rad0 = ideal.radius()
    circle0 = ideal.circleDistance()
    for feature in featureset:
        pos1 = feature.centroid()
        rad1 = feature.radius()
        circle1 = feature.circleDistance()
        dpos = dist2d(pos0, pos1)
        drad = abs(rad0-rad1)
        dcircle = abs(circle0-circle1)
        scores.append(dpos+drad+dcircle)
    return featureset[scores.index(min(scores))]


class ImageProcessor(object):
    """ Processes an img of a mouse eye."""
    def __init__(self):

        super(ImageProcessor, self).__init__()

        #options from constructor
        self.pupil_roi = None
        self.led_roi = None
        #self.img_type = img_type

        #some stuff we want to track between frames
        self.last_pupil = None
        self.last_led = None

        self.last_pupil_velocity = (0, 0)
        #self.last_led_velocity = (0, 0)  #probably not necessary

        #----------------------------------------------------------------------
        #images we want to track for displaying intermediate processing steps
        self.original = None
        self.pupil_region = None
        self.led_region = None
        self.eroded = None
        self.edges = None
        self.combined = None
        self.pupil_binary = None
        self.led_binary = None

        #----------------------------------------------------------------------
        #some stuff we want to allow the user to tweak
        # pupil
        self.pupil_blur = 2
        self.pupil_dilate = 4
        self.pupil_erode = 5
        self.mask_circle_thickness = 40
        self.pupil_binary_thresh = 210
        self.pupil_min_size = 100
        # led
        self.led_binary_thresh = 200
        self.led_min_size = 1
        self.led_mask_circle_thickness = 5
        # preprocessing
        self.equalize = False

    #@timeit
    def find_pupil(self, img):
        """
        Finds a pupil in an image.
        """
        # get roi from original img
        if self.pupil_roi is not None:
            try:
                self.pupil_region = img.regionSelect(*self.pupil_roi)  # should this be here?
                if self.pupil_region is None:
                    #some versions of SimpleCV don't error, they return none.
                    self.pupil_region = img
            except:
                self.pupil_region = img
                print("Pupil ROI outside image.")
        else:
            self.pupil_region = img
        if self.last_led:
            led_pos = get_abs_position(self.last_led.centroid(), self.led_roi)
            led_radius = self.last_led.radius()
            if self.last_pupil:
                color = self.last_pupil.meanColor()
                color = (int(color[0]), int(color[1]), int(color[2]))
            else:
                #guess the last color
                color = (0, 0, 0)
            self.pupil_region.drawCircle(get_relative_position(led_pos,
                                                               self.pupil_roi),
                                         led_radius+self.led_mask_circle_thickness,
                                         color=color,
                                         thickness=-1)
        #erode image to remove small speckle
        self.eroded = self.pupil_region.applyLayers().morphClose().blur(
            self.pupil_blur).erode(self.pupil_erode).blur(
            self.pupil_blur).morphClose()

        #find edges and make em thick
        self.edges = self.eroded.edges().dilate(self.pupil_dilate)
        self.combined = self.edges+self.eroded
        if self.last_pupil:
            #interpolate movement here
            #should happen here when this is a class
            try:
                self.combined.drawCircle(self.last_pupil.centroid(),
                                         self.last_pupil.radius()-1,
                                         color=(0, 0, 0),
                                         thickness=-1)
                self.combined.drawCircle(self.last_pupil.centroid(),
                                         self.last_pupil.radius()+10,
                                         color=(255, 255, 255),
                                         thickness=5)
                self.combined.drawCircle(self.last_pupil.centroid(),
                                         self.last_pupil.radius()+50,
                                         color=(255, 255, 255),
                                         thickness=self.mask_circle_thickness)
            except ValueError as e:
                print("Couldn't draw mask circle. Adjust the size:", e)

        self.pupil_binary = self.combined.applyLayers().invert().binarize(
            self.pupil_binary_thresh).invert()

        blobs = self.pupil_region.findBlobsFromMask(self.pupil_binary,
                                                    minsize=self.pupil_min_size)
        if blobs:
            pupil = filter_features(blobs, self.last_pupil)
            self.last_pupil = pupil
            return pupil
        else:
            return None

    def find_led(self, img):
        #if there is an ROI
        if self.led_roi is not None:
            try:
                self.led_region = img.regionSelect(*self.led_roi)
                #some versions of SimpleCV don't error they return None
                if self.led_region is None:
                    self.led_region = img
            except:
                #some versions error
                self.led_region = img
                print("LED ROI outside IMG")
        #No ROI
        else:
            self.led_region = img
        self.led_binary = self.led_region.binarize(self.led_binary_thresh).invert()
        blobs = self.led_region.findBlobsFromMask(self.led_binary)
        if blobs:
            led = blobs[-1]  # filter features not really necessary
            self.last_led = led
            return led
        else:
            return None

    def preprocess(self, img):
        """
        Preprocessing step.
        """
        img = img.grayscale()
        if self.equalize:
            img = img.equalize()
        return img

    def get_led_pos(self):
        return get_abs_position(self.last_led.centroid(), self.led_roi)

    def get_pupil_pos(self):
        return get_abs_position(self.last_pupil.centroid(), self.pupil_roi)

    def set_pupil_roi(self, x0, y0, x1, y1):
        self.pupil_roi = (x0, y0, x1, y1)

    def set_led_roi(self, x0, y0, x1, y1):
        self.led_roi = (x0, y0, x1, y1)


def main():

    pass


if __name__ == "__main__":
    main()
