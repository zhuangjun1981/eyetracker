import unittest
import os
import eyetracker.tracker as et
import time

class TestImageProcessor(unittest.TestCase):

    def setUp(self):
        pass

    def test_process_file(self):
        curr_folder = os.path.dirname(os.path.realpath(__file__))
        os.chdir(curr_folder)
        mov_path = os.path.join('test_files', 'test.avi')
        tracker = et.Eyetracker()
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

    def test_processing_with_and_without_history(self):
        curr_folder = os.path.dirname(os.path.realpath(__file__))
        os.chdir(curr_folder)
        mov_path = os.path.join(curr_folder, 'test_files', 'test2.avi')
        tracker = et.Eyetracker(input_movie_path=mov_path)

        params = {'led_binary_threshold': 200,
                  'led_blur':2,
                  'led_mask_dilation':5,
                  'led_max_size':1000.0,
                  'led_min_size':1.0,
                  'led_openclose_iter':1,
                  'led_roi':[213, 281, 226, 317],
                  'pupil_binary_threshold':230,
                  'pupil_blur':2,
                  'pupil_is_equalize':True,
                  'pupil_min_size':500.0,
                  'pupil_openclose_iter':10,
                  'pupil_roi':[149, 331, 155, 397]}

        tracker.detector.load_parameters(**params)

        tracker.process_movie(is_with_history=True)

        output_yml_path = os.path.splitext(mov_path)[0] + '_output.yml'
        output_hdf_path = os.path.splitext(mov_path)[0] + '_output.hdf5'
        output_mov_path = os.path.splitext(mov_path)[0] + '_output.avi'


        # os.remove(output_yml_path)
        # os.remove(output_hdf_path)
        # os.remove(output_mov_path)

if __name__ == '__main__':
    test = TestImageProcessor()
    test.test_process_file()