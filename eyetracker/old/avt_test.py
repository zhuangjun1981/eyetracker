from toolbox.Cameras.avt import Camera
import cv2
import time
import numpy as np

cam = Camera(0)

movie = cv2.VideoWriter("C:/test.avi", cv2.cv.FOURCC(*'MPEG'), 30.0,
                        (250,250), isColor=False)
intervals = []

for i in range(120):
    t = time.clock()
    img = cam.getImage(20)
    if img is None:
        print "NONE"
    #cv2.imshow("test", img)
    #movie.write(img)
    intervals.append(time.clock()-t)
    time.sleep(0.001)

print np.array(intervals, dtype=np.float32)

movie.release()
cam.release()
