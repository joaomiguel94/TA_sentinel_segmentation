import numpy as np
from matplotlib import pyplot as plt
#import gdal,sys,cv2
from osgeo import *
from os import walk


def read_image(path):
    bandas = []
    tci = []
    jp2s = []
    for (dirpath, dirnames, filenames) in walk(path):
        jp2s = filenames
        break
    for jp2 in jp2s:
        if 'TCI' in jp2:
            print ("Loading sattelite image...")
            nir_ds = gdal.Open(path + "/" + jp2)
            nir_band = nir_ds.GetRasterBand(1)
            return nir_band.ReadAsArray()

def adaptative_hist_eq (image):
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    return clahe.apply(image)

def detect_white_spots(image):
    #160
    element = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(11,11))
    blur = cv2.GaussianBlur(image,(9,9),0)
    thresh = cv2.threshold(blur, 200, 255, cv2.THRESH_BINARY)[1]
    thresh = cv2.erode(thresh, None, iterations=5)
    thresh = cv2.dilate(thresh, element, iterations=3)
    return 1*(thresh == 255)

def otsu (image):
    ret,img = cv2.threshold(image, 127, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    return img


#processa a imagem para tentar extrair informações de estradas com o algoritmo de Canny
def process_canny(image, equalize, correct, remove_white):
    if (equalize==1): image = adaptative_hist_eq(image)
    if (correct==1): image = gamma_correction(image,2.0)
    if (remove_white==1): image = image*(1-detect_white_spots(image))
    image = cv2.GaussianBlur(np.uint8(image),(5,5),0)
    image = cv2.Canny(np.uint8(image),100,200)
    return image


#processa a imagem para tentar extrair informações de estradas com algoritmos de morfologia matemática
def process_morpholgical(image):
    equalized = adaptative_hist_eq(image)
    gamma_corrected = gamma_correction(equalized,1.5)    
    kernel = np.ones((3,3),np.uint8)
    blurred = cv2.GaussianBlur(gamma_corrected,(5,5),0)
    otsu_image = otsu(blurred)
    eroded = cv2.erode(otsu_image, kernel, iterations=1)
    dilated = cv2.dilate(eroded, kernel, iterations=1)
    return dilated


def gamma_correction(image, gamma):
    invGamma = 1.0 / gamma
    table = np.array([((i / 255.0) ** invGamma) * 255
        for i in np.arange(0, 256)]).astype("uint8")
    return cv2.LUT(image, table)

def segment_roads(image,equalize,correct_gamma,detect_white):
    X,Y = image.shape
    smallx,smally = (round(X/40),round(Y/40))
    for x in range(0,X-smallx,smallx):
        for y in range(0,Y-smally,smally):
            plt.imshow(image[x:x+smallx,y:y+smally],cmap='gray')
            plt.show()
            plt.imshow(process_canny(image[x:x+smallx,y:y+smally],equalize,correct_gamma,detect_white),cmap='gray')
            plt.show()
            



if __name__=="__main__":
    path = "R10m"
    print("Script will proceed with default parameters. Use this way: python canny.py [equalize] [correct_gamma] [detect_white]")
    print("Every value must be 0 or 1.")
    image = read_image(path)
    if (len(sys.argv) == 4):
        equalize = int(sys.argv[1])
        correct_gamma = int(sys.argv[2])
        detect_white = int(sys.argv[3])
    else:
        equalize = 1
        correct_gamma = 1
        detect_white = 1
    segment_roads(np.array(image, dtype='uint8'),equalize,correct_gamma,detect_white)