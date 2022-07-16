import pydicom 
import matplotlib.pyplot as plt 
from scipy.misc import imsave
import numpy as np
import os 


def Dcm2jpg(file_path):
  #Get all picture names
  c = []
  names =  os.listdir (file_path)
  #Separate the file names in the folder from the. DCM following them
  for name in names:
    index = name.rfind('.')
    name = name[:index]
    c.append(name)

  for files in c :
    picture_path = file_path+files+".dcm"
    out_path = "ct_images_output/"+files+".jpg"
    ds = pydicom.read_file(picture_path)
    img = ds.pixel_array # extracting image information
    imsave(out_path, img)
  
  print('all is changed')
      
Dcm2jpg("./ct_images/")