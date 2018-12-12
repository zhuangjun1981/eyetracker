"""
eyetracker.py

Allen Institute for Brain Science

@author: junz

@created: Dec 06, 2018

CLI version of the GUI eyetracker.  Used for batch processing.

"""

import sys
import os
import numpy as np
import cv2
from . import image_processor as ip
import yaml

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
            self.clear()
        elif input_movie_path[-4:] == '.avi':
            self.load_file(input_movie_path)
        else:
            raise LookupError('input file should be a .avi movie file.')

    def clear(self):
        self.input_movie_path = None
        self.input_movie = None
        self.frame_num = None
        self.frame_shape = None
        self.pupil_positions = None
        self.pupil_shape = None
        self.led_positions = None
        self.led_shape = None
        self.output_movie = None

    def load_file(self, input_movie_path):

        if self.input_movie_path is not None:
            msg_str = 'Eyetracker is already loaded with a movie. ' \
                        '\n{}\n\nDo you want to reload? (y/n)\n'.format(self.input_movie_path)
            msg = input(msg_str)
            while True:
                if msg == 'y':
                    break
                elif msg == 'n':
                    return
                else:
                    msg = input(msg_str)

        self.input_movie_path = os.path.realpath(input_movie_path)

        if os.path.isfile(self._data_file_path):
            raise FileExistsError('the .hdf5 data file already exists. Path:\n\t{}'.format(self._data_file_path))

        self.load_cfg()
        self.input_movie = cv2.VideoCapture(self.input_movie_path)
        self.frame_num = int(self.input_movie.get(cv2.CAP_PROP_FRAME_COUNT))
        # print(type(self.frame_num))
        # print(self.frame_num)
        if self.frame_num > 0:
            self.frame_shape = (int(self.input_movie.get(cv2.CAP_PROP_FRAME_WIDTH)),
                                int(self.input_movie.get(cv2.CAP_PROP_FRAME_HEIGHT)))
            # print(self.frame_shape)

            self.pupil_positions = np.zeros((self.frame_num, 2), dtype=np.float32)
            self.pupil_positions[:] = np.nan
            self.pupil_shape = np.zeros((self.frame_num, 3), dtype=np.float32)
            self.pupil_shape[:] = np.nan
            self.led_positions = np.zeros((self.frame_num, 2), dtype=np.float32)
            self.led_positions[:] = np.nan
            self.led_shape = np.zeros((self.frame_num, 3), dtype=np.float32)
            self.led_shape[:] = np.nan

            self.output_movie = cv2.VideoWriter(filename=self._output_movie_path,
                                                fourcc=cv2.VideoWriter_fourcc(*FOURCC),
                                                fps=FPS,
                                                frameSize=self.frame_shape)
        else:
            print('No frames in video file: \n{}\n Do nothing.'.format(self.input_movie_path))
            self.input_movie.release()
            self.clear()

    def load_cfg(self):

        if os.path.isfile(self._cfg_file_path):
            print('load existing config file.')
            with open(self._cfg_file_path, 'r') as cfg_f:
                params = yaml.load(cfg_f)
            self.detector = ip.PupilLedDetector()
            self.detector.load_parameters(**params)
        else:
            print('did not find config file. load default config.')
            self.detector = ip.PupilLedDetector()

        print(self.detector.string)

    def process_file(self):

        for frame_i in range(self.frame_num):

            self.input_movie.set(cv2.CAP_PROP_POS_FRAMES, frame_i)
            _, curr_frame = self.input_movie.read()

            if frame_i == 0:
                self.detector.load_first_frame(frame=curr_frame)
            else:
                self.detector.load_next_frame(frame=curr_frame)

            self.detector.detect()

            if self.detector.led is not None:
                self.led_positions[frame_i, :] = self.detector.led.center
                self.led_shape[frame_i, :] = [self.detector.led.axes[0],
                                              self.detector.led.axes[1],
                                              self.detector.led.angle]

            if self.detector.pupil is not None:
                self.pupil_positions[frame_i, :] = self.detector.pupil.center
                self.pupil_shape[frame_i, :] = [self.detector.pupil.axes[0],
                                                self.detector.pupil.axes[1],
                                                self.detector.pupil.angle]

            self.output_movie.write(self.detector.annotated)

        self.output_movie.release()

        self._save_cfg()
        self._save_hdf5()
        self.clear()

    def _save_cfg(self):

        if os.path.isfile(self._cfg_file_path):
            print('Overwriting existing config file: \n{}'.format(self._cfg_file_path))
            os.remove(self._cfg_file_path)

        param_dict = self.detector.get_parameter_dict()
        print(param_dict)
        with open(self._cfg_file_path, 'w') as cfg_f:
            yaml.dump(param_dict, cfg_f)

    def _save_hdf5(self):
        #todo: finish this!
        pass

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