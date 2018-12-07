"""
eyetracker.py

Allen Institute for Brain Science

@author: junz

@created: Dec 06, 2018

CLI version of the GUI eyetracker.  Used for batch processing.

"""

import os
import numpy as np
import cv2
from . import image_processor as ip

FOURCC = 'XVID'
FPS = 30

class Eyetracker(object):
    """
    Eyetracking program designed for CLI use.

    Main function is to process a single input_movie and create 1) parameters used as a .yml config file;
    2) annotated .avi movie and 3) an .hdf5 file containing the following:

        1) The pupil/led positions for each frame
        2) The pupil/led areas for each frame
        3) The shape (length of first axis, length of second axis, angle) of pupil for each frame
        4) The shape (length of first axis, length of second axis, angle) of led for each frame
        5) a copy of config
        6) Metadata about the movie file.  Size, length, etc.

    all three files should have same file name and live in the same folder as input movie file.

    Parameters
    ----------
    input_movie_path : str
        Path to input input_movie
    """

    def __init__(self,
                 input_movie_path=None,
                 ):

        if input_movie_path is None:
            self.input_movie_path = input_movie_path
        elif input_movie_path[-4:] == '.avi':
            self.input_movie_path = os.path.realpath(input_movie_path)
            self.load_file()
        else:
            raise LookupError('input file should be a .avi movie file.')

    def load_file(self):

        if os.path.isfile(self._data_file_path):
            raise FileExistsError('the .hdf5 data file already exists. Path:\n\t{}'.format(self._data_file_path))

        self.load_cfg()
        self.input_movie = cv2.VideoCapture(self.input_movie_path)
        self.frame_num = self.input_movie.get(cv2.CAP_PROP_FRAME_COUNT)
        self.frame_shape = (self.input_movie.get(cv2.CAP_PROP_FRAME_HEIGHT),
                            self.input_movie.get(cv2.CAP_PROP_FRAME_WIDTH))

        pupil_positions = np.zeros((self.frame_num), 2)
        pupil_positions[:] = np.nan
        pupil_shape = np.zeros((self.frame_num), 3)
        pupil_shape[:] = np.nan
        led_positions = np.zeros((self.frame_num), 2)
        led_positions[:] = np.nan
        led_shape = np.zeros((self.frame_num), 3)
        led_shape[:] = np.nan

        self.output_movie = cv2.VideoWriter(filename=self._output_movie_path,
                                            fourcc=cv2.VideoWriter_fourcc(*FOURCC),
                                            fps=FPS,
                                            frameSize=self.frame_shape)

    def load_cfg(self):

        if os.path.isfile(self._cfg_file_path):
            print('load existing config file.')
            # todo: finish this
        else:
            print('did not find config file. load default config.')
            self.detector = ip.PupilLedDetector()

    @property
    def _data_file_path(self):
        if self.input_movie_path is not None:
            return os.path.splitext(self.input_movie_path)[0] + '_output.hdf5'
        else:
            return None

    @property
    def _cfg_file_path(self):
        if self.input_movie_path is not None:
            return os.path.splitext(self.input_movie_path)[0] + '_output.yml'
        else:
            return None

    @property
    def _output_movie_path(self):
        if self.input_movie_path is not None:
            return os.path.splitext(self.input_movie_path)[0] + '_output.avi'
        else:
            return None