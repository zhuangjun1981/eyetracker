import os
import cv2
import numpy as np
import matplotlib.pyplot as plt

fn = r"F:\data2\rabies_tracing_project\M417949\2018-12-14-deepscope\videomon\181214-M417949-LSNDGC-110--1.avi"
frame_range = [117220, 117380]

curr_folder = os.path.dirname(os.path.realpath(__file__))
os.chdir(curr_folder)

cap = cv2.VideoCapture(fn)
print(cap.get(cv2.CAP_PROP_FRAME_COUNT))
frame_shape = (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
               int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))

vw = cv2.VideoWriter(filename=os.path.join(curr_folder, 'test3.avi'),
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