#AIBS Eyetracking Python Package

Created 10/2/14 by Derric Williams

![Alt text](http://i.imgur.com/U0P8p1p.png)

## Dependencies

[SimpleCV](http://simplecv.org/)

Get the newest version found [here](https://github.com/sightmachine/simplecv)

[OpenCV](http://opencv.org/)

[pyqtgraph](http://www.pyqtgraph.org/) (only used for GUI)

## Installation

Unzip the package and run:

    python setup.py install

### Testing Installation

Run the tests in the "tests" folder, for example:

    python test_all.py

## Usage

### GUI

Run the GUI using:

    python eyetrackergui.py

### CLI

Run the CLI using 

    python eyetracker.py input_file output_file [-c config_file][-a custom_algorithm]

## Known Issues

1. GUI sometimes slows down when playing and processing short videos simultaneously.
1. Import/export of tiff sequences don't do anything yet.
1. If the ROI at startup is too large for the image it currently throws an error until the ROI is resized.
1. This should be considered V0.1 so there will be lots of bugs.  Report them [HERE](http://jira.corp.alleninstitute.org/browse/MPE/component/10422)

![Alt text](http://i.imgur.com/9U5qwAi.gif)
