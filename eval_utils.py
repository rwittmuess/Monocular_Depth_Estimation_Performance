#
#
#   Helper Functions for eval_performance
#
#
#
#


import os
import rosbag
import pickle
import matplotlib.pyplot as plt
import numpy as np


# # Import Libraries
# import rosbag
# from sensor_msgs.msg import Image
# from PIL import Image
# import numpy as np
# from matplotlib import pyplot as plt
# from bagpy import bagreader
# import pandas as pd
# import seaborn as sea
# import cv2
# import os



def check_bag_file(bag_file_name):
    if bag_file_name.endswith(".bag"):
        test_run = bag_file_name[:-4]  # remove ".bag" from the end of the filename
    else:
        raise ValueError("File extension must be .bag")

    print('In this run of the script we are investigating bag-file \'' + test_run + '\'.')
    print('In case the analysis has already been performed and data has been saved, the saved data will be used to save computational time.')
    # print('\n')
    return test_run



def load_pickle(data_filename):
    try:
        with open(data_filename, 'rb') as file:
            data = pickle.load(file)
            file.close()
            # print('\'data\' loaded.')
            
    except FileNotFoundError:
        # If the file doesn't exist, create it with some initial data
        data = {}
        with open(data_filename, 'wb') as file:
            pickle.dump(data, file, pickle.HIGHEST_PROTOCOL)
        file.close()
        # print('Created \'data\'.')

    # print('\n')
    return data



def get_image_data(bag_file_name,topic_cam1,topic_cam2):    
    bag = rosbag.Bag(os.path.join('drone_data', bag_file_name))

    # get data from rosbag
    image_data_infra1_np, height, width = extract_image_data(bag, topic_cam1)
    image_data_infra2_np, height, width = extract_image_data(bag, topic_cam2)

    print("The bags contain", len(image_data_infra1_np), "and", len(image_data_infra2_np), "frames for the given topics.")

    # print('\n')
    return image_data_infra1_np, image_data_infra2_np, height, width



def get_depth_data(bag_file_name,topic_depth):
    '''
    First part inspired by: http://wiki.ros.org/rosbag/Code%20API 
    '''
    bag = rosbag.Bag(os.path.join('drone_data', bag_file_name))

    # get data from rosbag
    depth_measurement_images = extract_depth_data(bag, topic_depth)

    return depth_measurement_images



def update_data(topic, data_filename, test_run, model_type, newData):
    data = load_pickle(data_filename)

    if test_run in data:
        print('\'Data\' already contains data for \'' +  test_run + '\'.')
        if model_type in data[test_run]:
            print('\'Data\' also already contains data for \'' + model_type + '\'.')
            if topic in data[test_run][model_type]:
                if len(data[test_run][model_type][topic]) != len(newData):
                    data[test_run][model_type][topic] = newData
                    print('Added \'' + topic +'\' to \'' + model_type + '\' in \'' + test_run + '\'.')
            else:
                data[test_run][model_type][topic] = newData
                print('Added \'' + topic +'\' to \'' + model_type + '\' in \'' + test_run + '\'.')
            # if cam2 in data[test_run][model_type]:
            #     if len(data[test_run][model_type][cam2]) != len(image_data_infra2_np):
            #         data[test_run][model_type][cam2] = image_data_infra2_np
            #         print('Added \''+cam2+'\' to \'' + model_type + '\' in \'' + test_run + '\'.')
            # else:
            #     data[test_run][model_type][cam2] = image_data_infra1_np
            #     print('Added \''+cam2+'\' to \'' + model_type + '\' in \'' + test_run + '\'.')
        else: 
            print('\'Data\' does not contain data for ' + model_type + ' and will be added now.')
            data[test_run][model_type] = {}
            data[test_run][model_type][topic] = newData
            # data[test_run][model_type][cam2] = image_data_infra2_np
            print('Added \'' + topic +'\' to ' + model_type + '\' in \'' + test_run + '\'.')
    else: 
        print('\'data\' does not contain data for ' +  test_run + ' and will be added now.')
        data[test_run] = {}
        data[test_run][model_type] = {}
        data[test_run][model_type][topic] = newData
        # data[test_run][model_type][cam2] = image_data_infra2_np
        print('Added \'' + topic +'\' to \'' + model_type + '\' in \'' + test_run + '\'.')

    # save data to pickle file
    with open(data_filename, "wb") as file:
        pickle.dump(data, file, pickle.HIGHEST_PROTOCOL)
        file.close()
    print('\'data\' saved.')
    # print('\n')

    # data[test_run][model_type]['depth'] = []
    # data[test_run][model_type]['depth_estimate1'] = []
    # data[test_run][model_type]['depth_estimate2'] = []

    # if 'depth' in data[test_run][model_type]:
    # if 'depth_estimate1' in data[test_run][model_type]:
    # if 'depth_estimate2' in data[test_run][model_type]:

    # new_category = 'depth_rs'

    # if test_run in data:
    #     print('\'Data\' already contains data for \'' +  test_run + '\'.')
    #     if model_type in data[test_run]:
    #         print('\'Data\' also already contains data for \'' + model_type + '\'.')
    #         if new_category in data[test_run][model_type]:
    #             if len(data[test_run][model_type][new_category]) != len(depth_measurement_images):
    #                 data[test_run][model_type][new_category] = depth_measurement_images
    #                 print('Added \'' + new_category + '\' to \'' + model_type + '\' in \'' + test_run + '\'.')
    #         else:
    #             data[test_run][model_type][new_category] = depth_measurement_images
    #             print('Added \'' + new_category + '\' to \'' + model_type + '\' in \'' + test_run + '\'.')
    #     else: 
    #         print('\'Data\' does not contain data for ' + model_type + ' and will be added now.')
    #         data[test_run][model_type] = {}
    #         data[test_run][model_type][new_category] = depth_measurement_images
    #         print('Added \'' + new_category + '\' to \'' + model_type + '\' in \'' + test_run + '\'.')
    # else: 
    #     print('\'data\' does not contain data for \'' +  test_run + '\' and will be added now.')
    #     data[test_run] = {}
    #     data[test_run][model_type] = {}
    #     data[test_run][model_type][new_category] = depth_measurement_images
    #     print('Added \'' + new_category + '\' to \'' + model_type + '\' in \'' + test_run + '\'.')



def create_parallel_plots(frame1, frame2, cam1, cam2, data_filename, test_run, model_type):
    # Load data
    data = load_pickle(data_filename)

    # Create the figure and axes
    fig, axes = plt.subplots(1, 2, figsize=(10, 10))
    
    # Plot the first subplot
    axes[0].imshow(data[test_run][model_type][cam1][frame1],cmap='gray')
    axes[0].set_title(cam1 + " picture number " + str(frame1))

    # Plot the second subplot
    axes[1].imshow(data[test_run][model_type][cam2][frame2],cmap='gray')
    axes[1].set_title(cam2 + " picture number " + str(frame2))

    # Adjust the spacing between subplots
    plt.tight_layout()

    # Show the plots
    plt.show()



def create_mono_plots(frame1, cam1, data_filename, test_run, model_type):
    # Load data
    data = load_pickle(data_filename)

    plt.figure() #figsize=(10, 10)
    plt.imshow(data[test_run][model_type][cam1][frame1],cmap='gray')
    plt.suptitle(cam1 + " picture number " + str(frame1))
    plt.show()



def create_differencing_plot(frame1, frame2, data, cam1, cam2, test_run, model_type):
    # Dispersion
    fig = plt.figure(figsize =(10, 10))
    plt.imshow(data[test_run][model_type][cam1][frame1]-data[test_run][model_type][cam2][frame2],cmap='gray')
    plt.title(cam1 + '-' + cam2 + " dispersion for pictures number " + str(frame1) + " and " + str(frame2))
    plt.show()



def extract_image_data(bag, img_topic='/d455/infra1/image_rect_raw'):
    image_data_np = []
    height, width = None, None

    # Get the number of messages on the specified topic
    num_messages = bag.get_message_count(topic_filters=[img_topic])

    # Preallocate the image_data_np list with the expected size
    image_data_np = [None] * num_messages

    for i, (_, msg, _) in enumerate(bag.read_messages(topics=[img_topic])):
        np_array = np.frombuffer(msg.data, dtype=np.uint8).reshape(msg.height, msg.width)
        image_data_np[i] = np_array

        if height is None:
            height, width = msg.height, msg.width

    return image_data_np, height, width



def extract_depth_data(bag, img_topic = '/d455/depth/image_rect_raw'):
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
    
    '''
    Converts a list of 'sensor_msgs_Image' into a list of numpy arrays.
    '''
    np_list = []
    for pic in image_data:
        np_list.append(np.frombuffer(pic.data, dtype=np.uint16).reshape(pic.height, pic.width))
    return np_list



# def load_images_from_folder(folder):
#     images = []
#     for filename in os.listdir(folder):
#         img = cv2.imread(os.path.join(folder,filename))
#         if img is not None:
#             img = img[:, :, 0]     # TODO: make it dynamic
#             images.append(img)
#     return images



def get_closest_index(bag_file_name,topic_cam_given, index_cam_given, topic_cam_wanted):
    '''
    When given a image of a certain topic it
    returns the index of the image of another topic that is closest timewise. 
    '''
    bag = rosbag.Bag(os.path.join('drone_data', bag_file_name))

    timestamps_cam_given = []
    timestamps_cam_wanted = []
    
    for msg in bag.read_messages(topics=[topic_cam_given]):
        timestamps_cam_given.append(msg.timestamp.to_sec())

    for msg in bag.read_messages(topics=[topic_cam_wanted]):
        timestamps_cam_wanted.append(msg.timestamp.to_sec())

    target_timestamp = timestamps_cam_given[index_cam_given]
    closest_index = None    
    min_difference = float('inf')
    
    for i, timestamp in enumerate(timestamps_cam_wanted):
        difference = abs(target_timestamp - timestamp)
        if difference < min_difference:
            min_difference = difference
            closest_index = i

    return closest_index



