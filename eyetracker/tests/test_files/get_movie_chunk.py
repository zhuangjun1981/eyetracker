import os
import cv2
import numpy as np
import matplotlib.pyplot as plt

fn = r"F:\data2\rabies_tracing_project\M360495\2018-03-23-deepscope-reanalysis" \
     r"\video_mon\180323-M360495-CombinedStimuli-100-0.avi"
frame_range = [5800, 5900]

curr_folder = os.path.dirname(os.path.realpath(__file__))
os.chdir(curr_folder)

cap = cv2.VideoCapture(fn)
print(cap.get(cv2.CAP_PROP_FRAME_COUNT))
frame_shape = (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
               int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))

vw = cv2.VideoWriter(filename=os.path.join(curr_folder, 'test2.avi'),
                     fourcc=cv2.VideoWriter_fourcc(*'XVID'),
                     fps=30.,
                     frameSize=frame_shape)

for frame_i in range(frame_range[0], frame_range[1]):
    print('writing frame {}'.format(frame_i))
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_i)
    res, frame = cap.read()
    vw.write(frame)

cap.release()
vw.release()