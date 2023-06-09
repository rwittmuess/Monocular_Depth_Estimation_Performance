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

# import matplotlib.cm as cm
import numpy as np
from sklearn.cluster import KMeans


from collections import defaultdict


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



def save_data(data_filename, data):
    # save data to pickle file
    with open(data_filename, "wb") as file:
        pickle.dump(data, file, pickle.HIGHEST_PROTOCOL)
        file.close()
    print('\'data\' saved.')



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



def post_process_depth_data(depth_measurement_images):
    # replaces 0 with 65535
    for idx, image in enumerate(depth_measurement_images):
        depth_measurement_images[idx] = np.where(image == 0, 65535, image)

    return depth_measurement_images



def update_data(key, data_filename, test_run, model_type, newData): # first input 'key' was called 'topic' before

    data = defaultdict(list, load_pickle(data_filename))

    data[test_run][model_type][key] = newData
    data = dict(data)

    with open(data_filename, "wb") as file:
        pickle.dump(data, file, pickle.HIGHEST_PROTOCOL)
        file.close()
    print('\'data\' saved.')

    # if test_run in data:
    #     print('\'Data\' already contained data for \'' +  test_run + '\'.')
    #     if model_type in data[test_run]:
    #         print('\'Data\' also already contained data for \'' + model_type + '\'.')
    #         if topic in data[test_run][model_type]:
    #             # if len(data[test_run][model_type][topic]) != len(newData):
    #             data[test_run][model_type][topic] = newData
    #             print('Added \'' + topic +'\' to \'' + model_type + '\' in \'' + test_run + '\'.')
    #         # else:
    #         #     data[test_run][model_type][topic] = newData
    #         #     print('Added \'' + topic +'\' to \'' + model_type + '\' in \'' + test_run + '\'.')

    #         # if cam2 in data[test_run][model_type]:
    #         #     if len(data[test_run][model_type][cam2]) != len(image_data_infra2_np):
    #         #         data[test_run][model_type][cam2] = image_data_infra2_np
    #         #         print('Added \''+cam2+'\' to \'' + model_type + '\' in \'' + test_run + '\'.')
    #         # else:
    #         #     data[test_run][model_type][cam2] = image_data_infra1_np
    #         #     print('Added \''+cam2+'\' to \'' + model_type + '\' in \'' + test_run + '\'.')
    #     else: 
    #         print('\'Data\' does not contain data for ' + model_type + ' and will be added now.')
    #         data[test_run][model_type] = {}
    #         data[test_run][model_type][topic] = newData
    #         # data[test_run][model_type][cam2] = image_data_infra2_np
    #         print('Added \'' + topic +'\' to ' + model_type + '\' in \'' + test_run + '\'.')
    # else: 
    #     print('\'data\' does not contain data for ' +  test_run + ' and will be added now.')
    #     data[test_run] = {}
    #     data[test_run][model_type] = {}
    #     data[test_run][model_type][topic] = newData
    #     # data[test_run][model_type][cam2] = image_data_infra2_np
    #     print('Added \'' + topic +'\' to \'' + model_type + '\' in \'' + test_run + '\'.')

    # # save data to pickle file
    # with open(data_filename, "wb") as file:
    #     pickle.dump(data, file, pickle.HIGHEST_PROTOCOL)
    #     file.close()
    # print('\'data\' saved.')
    # # print('\n')

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
    axes[0].imshow(data[test_run][model_type][cam1][frame1])
    # axes[0].imshow(data[test_run][model_type][cam1][frame1],cmap='gray')
    axes[0].set_title(cam1 + " picture number " + str(frame1))

    # Plot the second subplot
    axes[1].imshow(data[test_run][model_type][cam2][frame2])
    # axes[1].imshow(data[test_run][model_type][cam2][frame2],cmap='gray')
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



def get_closest_index(index_cam_given, timestamps_cam_given, timestamps_cam_wanted):
    '''
    When given a image of a certain topic it
    returns the index of the image of another topic that is closest timewise. 
    '''
    # bag = rosbag.Bag(os.path.join('drone_data', bag_file_name))

    # timestamps_cam_given = []
    # timestamps_cam_wanted = []
    
    # for msg in bag.read_messages(topics=[topic_cam_given]):
    #     timestamps_cam_given.append(msg.timestamp.to_sec())

    # for msg in bag.read_messages(topics=[topic_cam_wanted]):
    #     timestamps_cam_wanted.append(msg.timestamp.to_sec())

    target_timestamp = timestamps_cam_given[index_cam_given]
    closest_index = None    
    min_difference = float('inf')
    
    for i, timestamp in enumerate(timestamps_cam_wanted):
        difference = abs(target_timestamp - timestamp)
        if difference < min_difference:
            min_difference = difference
            closest_index = i

    return closest_index



def get_max_depth_in_frames(data, test_run, model_type, cam_key):
    # returns a list of max. depth in every picture
    max_depth_list = []
    for frame in data[test_run][model_type][cam_key]:
        max_depth_list.append(frame.max())
    return max_depth_list



def get_indices_images_not_max_depth(max_depth, max_depth_list):
    # max_depth NEEDS to be a LIST
    # find depth-pictures in which max. depth is not 65535 = (2**16)-1 or 255
    indices_not_max_depth = []      # (index_ value)
    for i in range(len(max_depth_list)):
        if max_depth_list[i] not in max_depth:
            indices_not_max_depth.append((i, max_depth_list[i]))

    return np.array(indices_not_max_depth)
    # # get max. depth in every depth-picture
    # max_estimated_depth = []
    # for frame in data[test_run][model_type][cam1rgb_key]:
    #     max_estimated_depth.append(frame.max())

    # # find depth-pictures in which max. depth is not 65535 = (2**16)-1
    # indices_not_max_depth = []      # (index, value)
    # for i in range(len(max_estimated_depth)):
    #     if max_estimated_depth[i] != 255:
    #         indices_not_max_depth.append((i, max_estimated_depth[i]))

    # indices_not_max_depth = np.array(indices_not_max_depth)



def visualize_errors(frame1_idx, frame2_idx, data, cam1_key, cam2_key, test_run, model_type):
    image_subtraction_pic = abs(data[test_run][model_type][cam1_key][frame1_idx] - data[test_run][model_type][cam2_key][frame2_idx])

    fig, axes = plt.subplots(nrows=4, ncols=4, figsize =(15, 10))
    for idx, ax in enumerate(axes.flat):

        error_matrix = image_subtraction_pic

        # Find the unique values in the array
        unique_values = np.unique(error_matrix)

        # Sort the unique values in descending order and get the 'largest_amount' largest ones
        largest_amount = 1000*(idx+1)
        largest_values = np.sort(unique_values)[::-1][:(largest_amount)]

        # Create a Boolean mask that sets the largest 10 unique values to True
        mask = np.isin(error_matrix, largest_values)

        difference_pic_zero_extremes = np.zeros_like(error_matrix)
        difference_pic_zero_extremes[mask] = 255

        # fig = plt.figure(figsize =(15, 15))
        roundingval = 2
        text = "n = "+str(largest_amount) + " (" + str(round(largest_values[0],roundingval)) + " - " +str(round(largest_values[-1],roundingval)) + ")"
        ax.set_title(text)   
        
        im = ax.imshow(difference_pic_zero_extremes, vmin=0, vmax=255)

    fig.subplots_adjust(right=0.8)
    cbar_ax = fig.add_axes([0.85, 0.15, 0.05, 0.7])
    fig.colorbar(im, cax=cbar_ax)

    fig.suptitle('Location of the n largest, unique errors', fontsize=16)
    plt.show()
    # plt.colorbar(label="error", orientation="horizontal")



def plot_extreme_pixels(array):
    # Create a figure with three subplots
    fig, axs = plt.subplots(1, 3, figsize=(12, 4))

    # Plot grayscale image with red for smalles Values (left subplot)
    axs[0].imshow(array, cmap='gray')
    axs[0].imshow(array == array.min(), cmap='Reds', alpha=0.5)

    # Plot grayscale image with blue for 65535 (middle subplot)
    axs[1].imshow(array, cmap='gray')
    axs[1].imshow(array == array.max(), cmap='Blues', alpha=0.5)

    # Plot grayscale image with red for zeros and blue for 65535 (right subplot)
    axs[2].imshow(array, cmap='gray')
    axs[2].imshow(array == array.min(), cmap='Reds', alpha=0.5)
    axs[2].imshow(array == array.max(), cmap='Blues', alpha=0.5)

    # Set titles for the subplots
    axs[0].set_title('Pixels with value ' + str(array.min()))
    axs[1].set_title('Pixels with value ' + str(array.max()))
    axs[2].set_title('Pixels with value ' + str(array.min()) + ' and ' + str(array.max()))

    # Hide tick marks and labels
    for ax in axs:
        ax.set_xticks([])
        ax.set_yticks([])

    fig.suptitle('Visualization of Extrema')

    # Adjust spacing between subplots
    plt.tight_layout()

    # Display the plots
    plt.show()



def plot_clustered_maxima(data, num_clusters, circle_scaling_factor):
    plt.figure(figsize=(10, 8))
    plt.imshow(data, cmap='gray')
    plt.title("Clustered Maxima with " + str(num_clusters) + " clusters")

    # Rescaling the data to [0, 1]
    data = data.astype(float) / 65535.0

    # Reshaping the data for clustering
    flattened_data = data.reshape(-1, 1)

    # Clustering the data
    kmeans = KMeans(n_clusters=num_clusters, n_init=10)  # Set n_init explicitly
    kmeans.fit(flattened_data)
    cluster_labels = kmeans.predict(flattened_data)

    # Getting the maximum values within each cluster
    max_values = []
    for cluster in range(num_clusters):
        cluster_indices = np.where(cluster_labels == cluster)[0]
        cluster_max_index = np.argmax(flattened_data[cluster_indices])
        max_values.append(cluster_indices[cluster_max_index])

    # Plotting circles around maxima
    for index in max_values:
        row = index // data.shape[1]
        col = index % data.shape[1]
        cluster = cluster_labels[index]
        cluster_indices = np.where(cluster_labels == cluster)[0]
        max_radius = np.max(np.linalg.norm(flattened_data[cluster_indices] - flattened_data[index]))
        circle = plt.Circle((col, row), max_radius*circle_scaling_factor, color='red', fill=False)
        plt.gca().add_patch(circle)

    plt.show()



def plot_error_histogram(text, difference_picture, num_bins):
    fig = plt.figure(figsize =(10, 7))

    plt.hist(difference_picture, bins=num_bins) 

    max_error = difference_picture.max()
    min_error = difference_picture.min()

    text = text + " (Range: " + str(min_error) + "-" + str(max_error) + ")"
    plt.title(text)
    plt.show()



def get_difference_picture(pic1,pic2,values_to_neglect):
    '''
        returns the absolute difference of the pictures
        neglecting a list values if wanted
    '''
    result = np.abs(pic1 - pic2)
    
    mask = np.isin(pic1, values_to_neglect) | np.isin(pic2, values_to_neglect)
    result[mask] = 0
    
    return result



def create_plot(difference_picture):
    plt.figure() #figsize=(10, 10)
    plt.imshow(difference_picture)
    plt.show()