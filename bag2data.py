# Import Libraries
import rosbag
from sensor_msgs.msg import Image
from PIL import Image
import numpy as np
from matplotlib import pyplot as plt
from bagpy import bagreader
import pandas as pd
import seaborn as sea

import cv2
import os

def getImageData(bag, img_topic = '/d455/infra1/image_rect_raw'):
    '''
    First part inspired by: http://wiki.ros.org/rosbag/Code%20API 

    location_bag_file   - Path to the .bag file. 
                          If it is in the same directory just the name of the bag file.
    img_topic           - ROS topic of the camera.
                          Can be found out using: getTopics(location_bag_file)
    '''
    #bag = rosbag.Bag(location_bag_file)
    image_data = []
    for topic, msg, t in bag.read_messages(topics=[img_topic]):
        image_data.append(msg)
    #bag.close()
    return image_data


def ros_IMG_2numpy(msg_list):
    '''
    Converts a list of 'sensor_msgs_Image' into a list of numpy arrays.
    '''
    np_list = []
    for pic in msg_list:
        np_list.append(np.frombuffer(pic.data, dtype=np.uint8).reshape(pic.height, pic.width))
    return np_list

def getDepthData(bag, img_topic = '/d455/depth/image_rect_raw'):
    '''
                              TODO:

    First part inspired by: http://wiki.ros.org/rosbag/Code%20API 

    bag_file            - .bag file. 
                          If it is in the same directory just the name of the bag file.
    img_topic           - ROS depth-topic of the camera.
    '''
    image_data = []
    for topic, msg, t in bag.read_messages(topics=[img_topic]):
        image_data.append(msg)
    bag.close()
    return image_data


def ros_DEPTH_2numpy(msg_list):
    '''
    Converts a list of 'sensor_msgs_Image' into a list of numpy arrays.
    '''
    np_list = []
    for pic in msg_list:
        np_list.append(np.frombuffer(pic.data, dtype=np.uint16).reshape(pic.height, pic.width))
    return np_list


def load_images_from_folder(folder):
    images = []
    for filename in os.listdir(folder):
        img = cv2.imread(os.path.join(folder,filename))
        if img is not None:
            img = img[:, :, 0]     # TODO: make it dynamic
            images.append(img)
    return images


# def dispDepthImg(msg):
#     '''
#     TODO: Description
#     '''
#     #(480, 848, 2)

#     #print(msg.data.shape)

#     im = np.frombuffer(msg.data, dtype=np.uint16).reshape(msg.height, msg.width)
#     img1 = Image.fromarray(im)
#     np_img = np.array(img1)
#     center_depth = np_img[int(msg.height*0.5),int(msg.width*0.5)] *0.001 # *0.001 to get from mm -> m
#     print("Depth in the middle of the image: ", print(center_depth))
#     plt.imshow(img1,cmap='gray')
#     plt.show()