"""
eyetracker.py

Allen Institute for Brain Science

@author: derricw

@created: Oct 3 2014

CLI version of the GUI eyetracker.  Used for batch processing.

"""

import sys
import os
import argparse
import ConfigParser
import h5py
import datetime
import numpy as np
import cv2

from image_processor import ImageProcessor


class Eyetracker(object):
    """
    Eyetracking program designed for CLI use.

    Main function is to process a single input_movie and create either an AVI of the
        output or an HDF5 that contains:

        1) The pupil/led positions for each frame
        2) The pupil area for each frame
        3) The frame intervals recorded in the movie's accompanying text file
        4) The image_processor configuration that generated the position data
        5) Metadata about the movie file.  Size, length, etc.
        6) A binary copy of the movie file.

    Parameters
    ----------
    video_file : str
        Path to input input_movie
    output_file : str
        Path for output input_movie
    config_file : str
        Path for config file. Default: None
    custom_algorithm : str
        Path for custom_algorithm. Default: None

    """

    def __init__(self,
                 video_file,
                 output_file,
                 config_file=None,
                 custom_algorithm=None,
                 ):

        super(Eyetracker, self).__init__()

        self.video_file = video_file
        self.output_file = output_file
        self.config_file = config_file
        self.custom_algorithm = custom_algorithm
        self.read_video(self.video_file)

        if custom_algorithm:
            import imp
            ip = imp.load_source('image_processor', custom_algorithm)
            self.image_processor = ip.ImageProcessor()
        else:
            self.image_processor = ImageProcessor()

        self.avi_output = None
        self.hdf5_output = None

        self.led_pos = (0, 0)
        self.pupil_pos = (0, 0)
        self.pupil_area = 0
        self.azimuth = 0.0
        self.zenith = 0.0

        if config_file:
            self.config = self._read_config(config_file)
            self._apply_config(self.config)
        else:
            #perhaps one is saved for this input_movie
            filename, ext = os.path.splitext(self.video_file)
            try:
                self.config = self._read_config(filename+".cfg")
                self._apply_config(self.config)
            except Exception as e:
                #no configuration found, so we guess or automatically do it
                raise IOError("No config file found for this input_movie. %s" % e)

        filename, ext = os.path.splitext(self.output_file)

        # if ext in ['.avi', '.mpeg', '.mp4', '.mpg']:
        #     #check output file type
        #     self._avi_setup()
        # elif ext in ['.h5', '.hdf5']:
        #     self._hdf5_setup()
        #     # hacky way to save annotated avi file when asked to save .h5
        #     self._avi_setup()

        if ext in ['.h5', '.hdf5']:
            self._hdf5_setup()
            self._avi_setup()
        else:
            raise IOError("Output file type not supported...")

    def read_video(self, video_file):
        self.video = VirtualCamera(video_file, 'input_movie')
        self.frame_size = self.video.getImage().size()


        if isinstance(self.video, VirtualCamera):
            # camera is SimpleCV VirtualCamera
            self.no_frames = cv2.cv.GetCaptureProperty(self.video.capture, cv2.cv.CV_CAP_PROP_FRAME_COUNT)
            self.fps = cv2.cv.GetCaptureProperty(self.video.capture, cv2.cv.CV_CAP_PROP_FPS)
        elif isinstance(self.video, cv2.VideoCapture):
            # camera is cv2 VideoCapture
            self.no_frames = self.video.get(cv2.cv.CV_CAP_PROP_FRAME_COUNT)
            self.fps = self.video.get(cv2.cv.CV_CAP_PROP_FRAME_FPS)
        else:
            raise RuntimeError("Unknown camera type? Can't get avi length.")

        print("\nloaded input_movie: {}".format(os.path.realpath(video_file)))
        print("frame size: {}".format(self.frame_size))
        print("frame rate: {}".format(self.fps))
        print("number of frames: {}\n".format(self.no_frames))

    def process_video(self):
        ip = self.image_processor

        print("*"*40)
        print("\nProcessing: %s\nSaving as: %s\n" % (self.video_file,
              self.output_file))
        print("*"*40)
        print("")

        frame_no = 1
        led_positions = []
        pupil_positions = []
        pupil_area = []

        self.video = VirtualCamera(self.video_file, 'input_movie')

        while True:
            frame = self.video.getImage()
            if frame.size() != self.frame_size:
                print("Finished!")
                break

            # print(frame)
            frame = ip.preprocess(frame)
            self.led = ip.find_led(frame)
            self.pupil = ip.find_pupil(frame)
            if self.pupil:
                self.pupil_pos = ip.get_pupil_pos()
                self.pupil_area = self.pupil.area()
            if self.led:
                self.led_pos = ip.get_led_pos()
            led_positions.append(self.led_pos)
            pupil_positions.append(self.pupil_pos)
            pupil_area.append(self.pupil_area)

            # ##TODO: Move this to IP
            if self.led:
                frame.drawCircle(self.led_pos,
                                 self.led.radius(),
                                 color=(255, 0, 0),
                                 thickness=min(self.led.radius(), 2))
            if self.pupil:
                frame.drawCircle(self.pupil_pos,
                                 self.pupil.radius(),
                                 color=(0, 255, 0),
                                 thickness=min(self.pupil.radius(), 2))
            try:
                frame = frame.applyLayers()
            except Exception as e:
                print("Couldn't apply layers:", e)
            if self.avi_output:
                frame.save(self.avi_output)
            sys.stdout.write("\rFinished frame: %i, %i%% complete..." % (frame_no,
                100.0*frame_no/self.no_frames))
            sys.stdout.flush()
            frame_no += 1

        #save the pupil and led data sets
        if self.hdf5_output:
            #save eye data
            print("Saving eye data...")
            led_data = np.array(led_positions, dtype=np.int16)
            self.hdf5_output.create_dataset("led_positions", data=led_data)
            pupil_data = np.array(pupil_positions, dtype=np.int16)
            self.hdf5_output.create_dataset("pupil_positions", data=pupil_data)
            pupil_area_data = np.array(pupil_area, dtype=np.int32)
            self.hdf5_output.create_dataset("pupil_area", data=pupil_area_data)

            #save configuration
            if self.config:
                print("Saving configuration...")
                config = np.string_(str(self.config))
                self.hdf5_output.create_dataset("config", data=config)

            #save input_movie metadata
            meta = {
                "width": self.frame_size[0],
                "height": self.frame_size[1],
                "frames": frame_no,
                "fps": self.fps,
                "filename": self.video_file,
                "processed_on": str(datetime.datetime.now())
            }

            meta = np.string_(str(meta))
            self.hdf5_output.create_dataset("video_metadata", data=meta)

            #save input_movie ??? Does this work?  doesn't error...
            # try:
            #     print("Saving copy of the input_movie...")
            #     with open(self.video_file, 'rb') as f:
            #         binary_data = f.read()
            #         vbuffer = np.string_(binary_data)
            #         ds = self.hdf5_output.create_dataset("movie", data=vbuffer)
            # except MemoryError:
            #     print("WARNING: Not enough ram to save movie in HDF5.")

            #save frame intervals
            # try:
            #     print("Saving frame intervals...")
            #     filename, ext = os.path.splitext(self.video_file)
            #     frame_interval_path = filename+".txt"
            #     with open(frame_interval_path, 'r') as f:
            #         intervals_str = f.readlines()
            #         intervals_flt = [float(interval) for interval in intervals_str]
            #         frame_intervals = np.diff(np.array(intervals_flt,
            #                                            dtype=np.float64))
            #         self.hdf5_output.create_dataset("frame_intervals",
            #                                         data=frame_intervals)
            # except Exception as e:
            #     print("Error saving frame intervals.", type(e), e)

            #save custom algorithm
            if self.custom_algorithm:
                np_string = np.string_(self.custom_algorithm)
                self.hdf5_output.create_dataset("custom_algorithm",
                                                data=np_string)

            self.hdf5_output.close()

    def _read_config(self, config_file):
        video_config = ConfigParser.RawConfigParser()
        video_config.read(config_file)
        config = {}
        for (k, v) in video_config.items("Eyetracker"):
            config[k] = eval(v)
        # If calibration was saved
        # for (k, v) in video_config.items("Calibration"):
        #     config[k] = eval(v)
        return config

    def _apply_config(self, config):
        print("Loading configuration:", config)
        for k, v in config.iteritems():
            setattr(self.image_processor, k, v)

    def _hdf5_setup(self):
        print("\nCreating HDF5 file at %s" % self.output_file)
        self.hdf5_output = h5py.File(self.output_file, 'w')

        print("Estimating input file length..")
        self.no_frames = self.get_avi_length()
        print("Approximately %i frames..." % self.no_frames)

    def _avi_setup(self):

        output_fn, _ = os.path.splitext(self.output_file)

        self.avi_output = VideoStream(output_fn + '.avi', fps=self.fps,
                                      framefill=False)
        self.avi_output.fourcc = cv.CV_FOURCC(*"XVID")

    def get_avi_length(self):
        """
        Gets the avi length.
        """
        import cv2
        if isinstance(self.video, VirtualCamera):
            # camera is SimpleCV VirtualCamera
            length = cv2.cv.GetCaptureProperty(self.video.capture, cv2.cv.CV_CAP_PROP_FRAME_COUNT)
        elif isinstance(self.video, cv2.VideoCapture):
            # camera is cv2 VideoCapture
            length = self.video.get(cv2.cv.CV_CAP_PROP_FRAME_COUNT)
        else:
            raise RuntimeError("Unknown camera type? Can't get avi length.")
        return length


def main():
    try:
        parser = argparse.ArgumentParser(
            description='Tracks eye and pupil position in image.')
        parser.add_argument('infile',
                            nargs='?',
                            type=str)
        parser.add_argument('outfile',
                            nargs='?',
                            type=str)
        parser.add_argument('-c',
                            type=str,
                            help='Config file path.',
                            default="")
        parser.add_argument('-a',
                            type=str,
                            help='Custom Algorithm',
                            default="")
        args = parser.parse_args()
        args = vars(args)

        # print(args)

        if args['infile']:
            infile = args['infile']
            _,in_ext = os.path.splitext(infile)
            in_ext = in_ext.lower()
            ## TODO: check input file type
            if args['outfile']:
                outfile = args['outfile']
                _,out_ext = os.path.splitext(outfile)
                out_ext = out_ext.lower()
                if args['c']:
                    config_file = args['c']
                else:
                    config_file = None
                if args['a']:
                    custom_algorithm = args['a']
                else:
                    custom_algorithm = None
                et = Eyetracker(infile, outfile, config_file, custom_algorithm)
                et.process_video()
                #raw_input("Processing completed without errors. Press enter to close...")
    except Exception as e:
        print(type(e), e)
        input("Processing completed with errors. Press enter to close...")


def get_zenith(displacement_y_pix, mm_per_pix, eyeball_radius_mm=1.65):
    return np.arcsin((displacement_y_pix * mm_per_pix) / eyeball_radius_mm)

def get_azimuth(displacement_x_pix, mm_per_pix, eyeball_radius_mm=1.65):
    return -np.arcsin((displacement_x_pix * mm_per_pix) / np.sqrt())


if __name__ == '__main__':
    main()
