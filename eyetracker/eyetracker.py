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

    Main function is to process a single video and create 1) parameters used as a .yml config file;
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
        Path to input video
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

    def load_cfg(self):

        if os.path.isfile(self._cfg_file_path):
            print('load existing config file.')
        else:
            print('did not find config file. load default config.')

        #todo: finish this
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