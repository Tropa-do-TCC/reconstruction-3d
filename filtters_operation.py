import cv2


def gaussian_filter(img):
    gaussian = cv2.GaussianBlur(img, (7, 7), 0)
    return gaussian


def blur_filter(img):
    blur = cv2.blur(img, (7, 7))
    return blur
