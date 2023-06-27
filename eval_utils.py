#
#
#   Helper Functions for eval_performance
#
#
#
#


import os
import rosbag
import bag2data as b2d
import pickle

def check_bag_file(bag_file_name):
    if bag_file_name.endswith(".bag"):
        test_run = bag_file_name[:-4]  # remove ".bag" from the end of the filename
    else:
        raise ValueError("File extension must be .bag")

    print('In this run of the script we are investigating bag-file \'' + test_run + '\'.')
    print('In case the analysis has already been performed and data has been saved, the saved data will be used to save computational time.')
    print('\n')
    return test_run



def load_pickle(data_filename):
    try:
        with open(data_filename, 'rb') as file:
            data = pickle.load(file)
            file.close()
            print('\'data\' loaded.')
            
    except FileNotFoundError:
        # If the file doesn't exist, create it with some initial data
        data = {}
        with open(data_filename, 'wb') as file:
            pickle.dump(data, file, pickle.HIGHEST_PROTOCOL)
        file.close()
        print('Created \'data\'.')

    print('\n')
    return data



def get_image_data(bag_file_name,topic_cam1,topic_cam2):
    bag = rosbag.Bag(os.path.join('drone_data', bag_file_name))

    # get data from rosbag
    image_data_infra1_np, height, width = b2d.getImageData(bag, topic_cam1)
    image_data_infra2_np, height, width = b2d.getImageData(bag, topic_cam2)

    print("The bags contain", len(image_data_infra1_np), "and", len(image_data_infra2_np), "frames for the given topics.")

    print('\n')
    return image_data_infra1_np, image_data_infra2_np, height, width



def update_data(data, data_filename, test_run, model_type, image_data_infra1_np, image_data_infra2_np):
    if test_run in data:
        print('\'Data\' already contains data for \'' +  test_run + '\'.')
        if model_type in data[test_run]:
            print('\'Data\' also already contains data for \'' + model_type + '\'.')
            if 'cam1' in data[test_run][model_type]:
                if len(data[test_run][model_type]['cam1']) != len(image_data_infra1_np):
                    data[test_run][model_type]['cam1'] = image_data_infra1_np
                    print('Added \'cam1\' to \'' + model_type + '\' in \'' + test_run + '\'.')
            else:
                data[test_run][model_type]['cam1'] = image_data_infra1_np
                print('Added \'cam1\' to \'' + model_type + '\' in \'' + test_run + '\'.')
            if 'cam2' in data[test_run][model_type]:
                if len(data[test_run][model_type]['cam2']) != len(image_data_infra2_np):
                    data[test_run][model_type]['cam2'] = image_data_infra2_np
                    print('Added \'cam2\' to \'' + model_type + '\' in \'' + test_run + '\'.')
            else:
                data[test_run][model_type]['cam2'] = image_data_infra1_np
                print('Added \'cam2\' to \'' + model_type + '\' in \'' + test_run + '\'.')
        else: 
            print('\'Data\' does not contain data for ' + model_type + ' and will be added now.')
            data[test_run][model_type] = {}
            data[test_run][model_type]['cam1'] = image_data_infra1_np
            data[test_run][model_type]['cam2'] = image_data_infra2_np
            print('Added \'cam1\' and \'cam2\' to ' + model_type + '\' in \'' + test_run + '\'.')
    else: 
        print('\'data\' does not contain data for ' +  test_run + ' and will be added now.')
        data[test_run] = {}
        data[test_run][model_type] = {}
        data[test_run][model_type]['cam1'] = image_data_infra1_np
        data[test_run][model_type]['cam2'] = image_data_infra2_np
        print('Added \'cam1\' and \'cam2\' to \'' + model_type + '\' in \'' + test_run + '\'.')

    # save data to pickle file
    with open(data_filename, "wb") as file:
        pickle.dump(data, file, pickle.HIGHEST_PROTOCOL)
        file.close()

    print('\n')

    # data[test_run][model_type]['depth'] = []
    # data[test_run][model_type]['depth_estimate1'] = []
    # data[test_run][model_type]['depth_estimate2'] = []

    # if 'depth' in data[test_run][model_type]:
    # if 'depth_estimate1' in data[test_run][model_type]:
    # if 'depth_estimate2' in data[test_run][model_type]:


