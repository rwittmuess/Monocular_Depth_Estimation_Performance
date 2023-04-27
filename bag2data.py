# Import Libraries
import rosbag
from sensor_msgs.msg import Image
from PIL import Image
import numpy as np
from matplotlib import pyplot as plt
from bagpy import bagreader
import pandas as pd
import seaborn as sea

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


def ros2numpy(msg_list):
    '''
    Converts a list of 'tmp5k5jvpwx._sensor_msgs__Image' into a list of numpy arrays.
    '''
    np_list = []
    for pic in msg_list:
        np_list.append(np.frombuffer(pic.data, dtype=np.uint8).reshape(pic.height, pic.width))
    return np_list