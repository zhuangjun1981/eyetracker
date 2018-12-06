import os
import cv2
import numpy as np
import matplotlib.pyplot as plt

fn = 'test.avi'
# fn = r"C:\Users\junz\Desktop\141120104947-KSstim-mouse146303-Jun-105-avt.avi"
frame_i = 10

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

np.save('test_img2.npy', frame)