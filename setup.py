from setuptools import find_packages, setup
from eyetracker import __version__, __author__

setup(name="eyetracker",
      version=__version__,
      description="software annotating eye pupil from movie",
      author=__author__,
      author_email="junz@alleninstitute.org",
      url="https://github.com/zhuangjun1981/eyetracker",
      packages=find_packages(),
      requires=[], #['cv2', 'numpy', 'pyqtgraph', 'PyQt4', 'SimpleCV'],
      include_package_data=True,
      package_data={
          "": ['*.png', '*.ico', '*.jpeg', '*.jpg' '*.ui'],
                    },
      platforms='windows',
      classifiers=['Programming Language :: Python',
                   'Development Status :: 4 - Beta',
                   'Natural Language :: English',
                   'Operating System :: OS Independent',]
      )
