#
#  Create Yolo Data for MVTec Metal Nut Data
#  - Find images on disk
#  - Read mask files
#  - Find Contours in mask files
#  - Write Yolo annotaions file
#


import cv2
import numpy as np
import time
import sys
import shutil
import os

from pathlib import Path
from random import shuffle


#
# Global vars
#

# Optionally add image without scratch or bent 
# To-do: Check if accuracy and false positives is better
add_good = True
add_color = True

test_set_size = 0.2

# Source data
path_mask = '../data/metal_nut/ground_truth/'
path_test = '../data/metal_nut/test/'

# Destination paths
path_data = 'data/'
path_yolo = 'data/metal_yolo/'

Path(path_yolo).mkdir(parents=True, exist_ok=True)

#
# Find Images on local disk and return a list with a label and path incl filename
#

def find_images(path):

    image_list = []

    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith("png") or file.endswith("jpg"):
                image_meta =  {"label": "good", "path": "data/0.png" }
                ipath = os.path.join(root, file)
                label = os.path.basename(root).replace(" ", "-").lower()
                image_meta["label"] = label
                image_meta["path"] = ipath
                # print(label, ipath)
                image_list.append(image_meta)
    return image_list




# Get a list of images
image_list = []      
image_list = find_images(path_test)

print(f"Toal number of images: {len(image_list)}")

#
# We just use two classes/lables: scratch and bent
#
labels = {
  "scratch": "0",
  "bent": "1"
}

#
# Create classes.txt
#

f = open(path_yolo + "classes.txt", "w")
for k in labels.keys():
    f.write(f'{k}\n')
f.close

#
#  Create Yolo files
#  - Copy image to Yolo directory
#  - Create Yolo annotation from mask files
#


for image_meta in image_list:

    # Set source image path and destination path 
    im_path = image_meta['path']
    dest_path = path_yolo + image_meta["label"] + "-" + os.path.basename(im_path)
    txt_p = dest_path.replace(".png", ".txt").replace(".jpg", ".txt")


    
    if image_meta["label"] in list(labels.keys()):

        # Copy file
        # print(f'COPY:{im_path}:{dest_path}')
        shutil.copyfile(im_path, dest_path)


        # Set Mask and annotation (txt) filepath
        mask_p = im_path.replace("test", "ground_truth").replace(".png", "_mask.png")
        
        # Create the Yolo annonation
        f = open(txt_p, "w")

        # print(image_meta,mask_p, txt_p)
        
        # Read images
        frame_mask = cv2.imread(mask_p)
        frame = cv2.imread(im_path)

        # Get image height and width
        height = frame.shape[0]
        width = frame.shape[1]

        # Convert mask to gray and find contours
        gray=cv2.cvtColor(frame_mask, cv2.COLOR_BGR2GRAY)
        contours,hierarchy = cv2.findContours(gray,cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for cnt in contours:
            area = cv2.contourArea(cnt)

            if area>400:
                
                peri = cv2.arcLength(cnt,True)
                approx = cv2.approxPolyDP(cnt,0.02*peri,True)
                x, y, w, h = cv2.boundingRect(approx)
                #print(f'x:{x}, y:{y}, w:{w}, h:{h}')

                # Convert x,y,w,h to normalized center in x, center in y, w, h
                norm_center_x = ( x + w/2 ) / width
                norm_center_y = ( y + h/2 ) / height
                norm_w = w / width
                norm_h = h / height
                print(f'{image_meta["label"]} - center_x:{norm_center_x}, center_y:{norm_center_y}, norm_w:{norm_w}, norm_h:{norm_h}')
                f.write(f'{labels[image_meta["label"]]} {norm_center_x} {norm_center_y} {norm_w} {norm_h}\n')

        f.close()
    else:
        if image_meta["label"] == "good" and add_good or image_meta["label"] == "color" and add_color:
            print(f'Add {image_meta["label"]} to output without annoations')
            shutil.copyfile(im_path, dest_path)
            # Create empty annotation file
            f = open(txt_p, "w")            
            f.write(f'\n')
            f.close()





#
# Create train.txt and test.txt
#


file_list = []
for file in os.listdir(path_yolo):
    if file.endswith("png") or file.endswith("jpg"):
        file_list.append(f"{path_yolo}{file}")

shuffle(file_list)


middle_index =  int(len(file_list)*test_set_size)

train = file_list[middle_index:]
test = file_list[:middle_index]


f = open(path_data + "train.txt", "w")
for t in train:
    f.write(f'{t}\n')
f.close

f = open(path_data + "test.txt", "w")
for t in test:
    f.write(f'{t}\n')
f.close

