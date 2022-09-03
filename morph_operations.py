import cv2
import numpy as np


def apply_closing(image_read):
    kernel = np.ones((20, 20), np.uint8)
    # closing
    img_dilatation = dilatation(image_read, kernel)
    img_erosion = erosion(img_dilatation, kernel)

    return img_erosion


def apply_opening(image_read):
    kernel = np.ones((20, 20), np.uint8)
    # opening
    img_erosion = erosion(image_read, kernel)
    img_dilatation = dilatation(img_erosion, kernel)

    return img_dilatation


def dilatation(img, kernel, iterations_number=1):
    dilation_img = cv2.dilate(img, kernel, iterations=iterations_number)
    return dilation_img


def erosion(img, kernel, iterations_number=1):
    erosion_img = cv2.erode(img, kernel, iterations=iterations_number)
    return erosion_img


def opening(img, kernel):
    opening_img = cv2.morphologyEx(img, cv2.MORPH_OPEN, kernel)
    return opening_img


def closing(img, kernel):
    closing_img = cv2.morphologyEx(img, cv2.MORPH_CLOSE, kernel)
    return closing_img
