"""
eyetracker.py

Allen Institute for Brain Science

@author: junz

@created: Dec 06, 2018

CLI version of the GUI eyetracker.  Used for batch processing.

"""

import os
from . import image_processor as ip

class Eyetracker(object):
    """
    Eyetracking program designed for CLI use.

    Main function is to process a single video and create 1) parameters used as a config file;
    2) annotated .avi movie and 3) an .hdf5 file containing the following:

        1) The pupil/led positions for each frame
        2) The pupil/led areas for each frame
        3) The shape (length of first axis, length of second axis, angle) of pupil for each frame
        4) The shape (length of first axis, length of second axis, angle) of led for each frame
        5) a copy of config
        6) Metadata about the movie file.  Size, length, etc.

    Parameters
    ----------
    video_file : str
        Path to input video
    output_file : str
        Path for output video
    config_file : str
        Path for config file. Default: None
    """

    def __init__(self,
                 input_file_path=None,
                 ):

        if input_file_path is None:
            self.input_file_path = input_file_path
        elif input_file_path[-4:] == '.avi':
            self.input_file_path = os.path.realpath(input_file_path)
            self.load_file(self.input_file_path)
        else:
            raise LookupError('input file should be a .avi movie file.')

    def load_file(self):

        if os.path.isfile(self._data_file_path):
            raise FileExistsError('the .hdf5 data file already exists. Path:\n\t{}'.format(self._data_file_path))

        if os.path.isfile(self._cfg_file_path):
            print('load existing config file.')
        else:
            print('did not find config file. load default config.')
        self.load_cfg()

    def load_cfg(self):

        #todo: finish this
        pass

    @property
    def _data_file_path(self):
        if self.input_file_path is not None:
            return os.path.splitext(self.input_file_path) + '.hdf5'
        else:
            return None

    @property
    def _cfg_file_path(self):
        if self.input_file_path is not None:
            return os.path.splitext(self.input_file_path) + '.cfg'
        else:
            return None