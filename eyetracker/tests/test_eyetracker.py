import unittest
import os
from .. import eyetracker as ec

class TestImageProcessor(unittest.TestCase):

    def setUp(self):

        curr_folder = os.path.dirname(os.path.realpath(__file__))
        os.chdir(curr_folder)

    def test_process_file(self):
        mov_path = os.path.join('test_files', 'test.avi')
        tracker = ec.Eyetracker()
        tracker.load_file(mov_path)
        output_movie_path = tracker._output_movie_path
        output_config_path = tracker._cfg_file_path
        output_hdf5_path = tracker._data_file_path
        tracker.process_file()
        # os.remove(output_movie_path)
        # os.remove(output_config_path)
        # os.remove(output_hdf5_path)