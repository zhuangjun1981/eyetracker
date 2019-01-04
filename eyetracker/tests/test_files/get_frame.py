import os
import cv2
import numpy as np
import matplotlib.pyplot as plt

# fn = 'test3.avi'
fn = r"F:\data2\rabies_tracing_project\M417949\2018-12-14-deepscope\videomon\181214-M417949-LSNDGC-110--1.avi"
frame_i = 118288

curr_folder = os.path.dirname(os.path.realpath(__file__))
os.chdir(curr_folder)

cap = cv2.VideoCapture(fn)
print(cap.get(cv2.CAP_PROP_FRAME_COUNT))
cap.set(cv2.CAP_PROP_POS_FRAMES, frame_i - 1)
res, frame = cap.read()

print('res: {}'.format(res))
print('frame type: {}'.format(type(frame)))
print('frame shape: {}'.format(frame.shape))
print('frame dtype: {}'.format(frame.dtype))
plt.imshow(frame)
plt.show()

np.save('test_img3.npy', frame)