import os
import cv2
import numpy as np
import matplotlib.pyplot as plt

# fn = 'test3.avi'
fn = r"Z:\chandelier_cell_project\M447219\2019-06-25-deepscope\videomon\190625-M447219-UCSLFC-110--1.avi"
frame_i = 105

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

np.save('test_img4.npy', frame)