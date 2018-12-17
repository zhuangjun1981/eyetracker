import unittest
import os
import eyetracker.tracker as ec
import time

class TestImageProcessor(unittest.TestCase):

    def setUp(self):
        pass

    def test_process_file(self):
        curr_folder = os.path.dirname(os.path.realpath(__file__))
        os.chdir(curr_folder)
        mov_path = os.path.join('test_files', 'test.avi')
        tracker = ec.Eyetracker()
        tracker.load_file(mov_path)
        output_movie_path = tracker._output_movie_path
        output_config_path = tracker._cfg_file_path
        output_hdf5_path = tracker._data_file_path
        tracker.process_movie()
        os.remove(output_movie_path)
        os.remove(output_config_path)
        os.remove(output_hdf5_path)

    def test_processing_cli(self):
        curr_folder = os.path.dirname(os.path.realpath(__file__))
        os.chdir(curr_folder)
        mov_path = os.path.join(curr_folder, 'test_files', 'test.avi')
        eyetracker_path = os.path.join(os.path.dirname(curr_folder), 'tracker.py')
        import sys
        cmd = "start {} {} {}".format(sys.executable,
                                      eyetracker_path,
                                      mov_path)
        os.system(cmd)
        time.sleep(5)
        output_yml_path = os.path.splitext(mov_path)[0] + '_output.yml'
        output_hdf_path = os.path.splitext(mov_path)[0] + '_output.hdf5'
        output_mov_path = os.path.splitext(mov_path)[0] + '_output.avi'
        os.remove(output_yml_path)
        os.remove(output_hdf_path)
        os.remove(output_mov_path)

if __name__ == '__main__':
    test = TestImageProcessor()
    test.test_process_file()