from SimpleCV import *
import numpy as np
from scipy.signal import sepfir2d, convolve2d, gaussian


def dist2d(p1,p2):
    return math.sqrt((p2[0] - p1[0]) ** 2 +
                     (p2[1] - p1[1]) ** 2) 


def dist3d(p1,p2):
    return math.sqrt((p2[0] - p1[0]) ** 2 +
                     (p2[1] - p1[1]) ** 2 +
                     (p2[2] - p1[2]) ** 2) 


class ImageProcessor(object):
    """SimpleCV image processing module."""
    def __init__(self):
        pass


    def get_led(self,img,size_range,threshold,roi=None):
        """ Returns binarized LED image, location, area """

        binary = img.binarize(thresh=threshold).invert()
        led = img.findBlobsFromMask(binary,minsize=size_range[0],
            maxsize=size_range[1])

        center,area = None,None
        #found an LED
        if led:
            if(len(led)>0): # if we got a blob
                for l in led:
                    new = [l.x,l.y]
                    #print led[-1].isCircle(tolerance=0.25)
                    if roi is None:                           
                        center = new
                        area = l.area()
                        break
                    else:
                        if roi[0]<new[0]<roi[2] and \
                            roi[1]<new[1]<roi[3]:
                            center=new
                            area = l.area()
                            break

        return binary, center, area

    def get_pupil(self, img, size_range, threshold, guess=None):
        #FIND PUPIL

        edges = img.erode(5).edges().dilate()
        
        combined = edges+img

        binary = combined.invert().erode(3).blur().equalize().binarize(
            thresh=threshold).invert()
        binary = binary.morphOpen().morphClose()
        #binary = binary.morphOpen().morphOpen().morphOpen()

        pupil = img.findBlobsFromMask(binary,minsize=size_range[0],
            maxsize=size_range[1])

        center,area = None,None

        if pupil:
            if(len(pupil)>0): # if we got a blob
                center = [pupil[-1].x,pupil[-1].y]
                area = pupil[-1].area()
                #print pupil[-1].isCircle(tolerance=0.3)

        return binary,center,area


    def preprocess(self, img, roi=None, gray=True, blur=0,
        equalize=True,zoom=0):
        #grayscale
        if gray:
            img = img.grayscale()

        #roi?
        if roi:
            img = img.regionSelect(*roi)

        #softwarezoom?
        if zoom>0:
            width,height = img.size()
            img = img.regionSelect(int(width/100*zoom),
                int(height/100*zoom),
                int(width-width/100*zoom),
                int(height-height/100*zoom))
        
        #blur?
        if blur>0:
            img = img.blur(window=(blur, blur))

        #equalize?
        if equalize:
            img = img.equalize()

        return img

    def fast_radial_transform(self, img, radii, alpha, **kwargs):

        #translated from coxlab eyetracker with only minor changes
        #not at all fast...
        #I should try using the woven version

        if not type(img) == np.ndarray:
            img = self.getNumpy(img)[:,:,0]

        gaussian_kernel_cheat = 1.0

        (rows, cols) = img.shape

        #cached sobel?
        use_cached_sobel = False
        cached_mag = None
        cached_x = None
        cached_y = None
        if 'cached_sobel' in kwargs:
            (cached_mag, cached_x, cached_y) = kwargs['cached_sobel']
            (sobel_rows, sobel_cols) = cached_sobel_mag.shape

            if sobel_rows == rows or sobel_cols == cols:
                use_cached_sobel = True

        if use_cached_sobel:
            mag = cached_mag
            imgx = cached_x
            imgy = cached_y
        else:
            (mag, imgx, imgy) = self.sobel3x3_naive(img)

        imgx = imgx / mag
        imgy = imgy / mag

        Ss = list(radii)

        (y,x) = np.mgrid[0:rows,0:cols]

        S = np.zeros_like(img)

        for i,rad in enumerate(radii):

            M = np.zeros_like(img)
            O = np.zeros_like(img)
            F = np.zeros_like(img)

            posx = x + rad * imgx
            posy = y + rad * imgy

            negx = x - rad * imgx
            negy = y - rad * imgy

            kappa = 9.9
            if rad == 1:
                kappa = 8

            posx = posx.round()
            posy = posy.round()
            negx = negx.round()
            negy = negy.round()

            posx[np.where(posx<0)] = 0
            posx[np.where(posx > cols - 1)] = cols - 1
            posy[np.where(posy < 0)] = 0
            posy[np.where(posy > rows - 1)] = rows - 1

            negx[np.where(negx < 0)] = 0
            negx[np.where(negx > cols - 1)] = cols - 1
            negy[np.where(negy < 0)] = 0
            negy[np.where(negy > rows - 1)] = rows - 1            

            for r in range(0, rows):
                for c in range(0, cols):
                    O[posy[r, c], posx[r, c]] += 1
                    O[negy[r, c], negx[r, c]] -= 1

                    M[posy[r, c], posx[r, c]] += mag[r, c]
                    M[negy[r, c], negx[r, c]] -= mag[r, c]

            O[np.where(O > kappa)] = kappa
            O[np.where(O < -kappa)] = -kappa

            F = M / kappa * (abs(O) / kappa) ** alpha

            width = round(gaussian_kernel_cheat * rad)

            if np.mod(width, 2) == 0:
                width += 1
            gauss1d = gaussian(width, 0.25 * rad).astype(np.float32)

            thisS = self.separable_convolution2d(F, gauss1d, gauss1d)
            S += thisS

        S = S / len(radii)

        return S


    def sobel3x3_naive(self, image):
        sobel_x = np.array([[-1., 0., 1.], [-2., 0., 2.], [1., 0., -1]])
        sobel_y = np.array([[1., 2., -1.], [0., 0., 0.], [-1., -2., 1]])
        imgx = convolve2d(image, sobel_x, mode='same', boundary='symm')
        imgy = convolve2d(image, sobel_y, mode='same', boundary='symm')
        mag = np.sqrt(imgx ** 2 + imgy ** 2) + 2e-16
        return (mag, imgx, imgy)

    def separable_convolution2d(self, im, row, col, **kwargs):
        print im.shape
        print row.shape
        print col.shape
        return sepfir2d(np.array(im), row, col)


    def getNumpy(self,img):
        return np.fliplr(np.rot90(img.getNumpy(),3))


if __name__ == '__main__':
    
    import matplotlib.pyplot as plt

    path = r"C:\Users\derricw\Pictures\eye.png"
    img = Image(path)
    ip = ImageProcessor()
    #img = ip.preprocess(img)

    rt = ip.fast_radial_transform(img, [10],1.)

    print rt

    plt.imshow(rt)
    plt.show()
