"""Compute depth maps for images in the input folder.
"""
import os
import glob
import torch
import utils
import cv2
import argparse
import time

import numpy as np

from imutils.video import VideoStream
from midas.model_loader import default_models, load_model

#import sys
#sys.path.insert(0, '../Monocular_Depth_Estimation')
# import rw_utils #not working
import os
import rosbag
# setting path
import pickle

first_execution = True
def process(device, model, model_type, image, input_size, target_size, optimize, use_camera):
    """
    Run the inference and interpolate.

    Args:
        device (torch.device): the torch device used
        model: the model used for inference
        model_type: the type of the model
        image: the image fed into the neural network
        input_size: the size (width, height) of the neural network input (for OpenVINO)
        target_size: the size (width, height) the neural network output is interpolated to
        optimize: optimize the model to half-floats on CUDA?
        use_camera: is the camera used?

    Returns:
        the prediction
    """
    global first_execution

    if "openvino" in model_type:
        if first_execution or not use_camera:
            # print(f"    Input resized to {input_size[0]}x{input_size[1]} before entering the encoder")
            first_execution = False

        sample = [np.reshape(image, (1, 3, *input_size))]
        prediction = model(sample)[model.output(0)][0]
        prediction = cv2.resize(prediction, dsize=target_size,
                                interpolation=cv2.INTER_CUBIC)
    else:
        sample = torch.from_numpy(image).to(device).unsqueeze(0)

        if optimize and device == torch.device("cuda"):
            if first_execution:
                print("  Optimization to half-floats activated. Use with caution, because models like Swin require\n"
                      "  float precision to work properly and may yield non-finite depth values to some extent for\n"
                      "  half-floats.")
            sample = sample.to(memory_format=torch.channels_last)
            sample = sample.half()

        if first_execution or not use_camera:
            height, width = sample.shape[2:]
            # print(f"    Input resized to {width}x{height} before entering the encoder")
            first_execution = False

        prediction = model.forward(sample)
        prediction = (
            torch.nn.functional.interpolate(
                prediction.unsqueeze(1),
                size=target_size[::-1],
                mode="bicubic",
                align_corners=False,
            )
            .squeeze()
            .cpu()
            .numpy()
        )

    return prediction


def create_side_by_side(image, depth, grayscale):
    """
    Take an RGB image and depth map and place them side by side. This includes a proper normalization of the depth map
    for better visibility.

    Args:
        image: the RGB image
        depth: the depth map
        grayscale: use a grayscale colormap?

    Returns:
        the image and depth map place side by side
    """
    depth_min = depth.min()
    depth_max = depth.max()
    normalized_depth = 255 * (depth - depth_min) / (depth_max - depth_min)
    normalized_depth *= 3

    right_side = np.repeat(np.expand_dims(normalized_depth, 2), 3, axis=2) / 3
    if not grayscale:
        right_side = cv2.applyColorMap(np.uint8(right_side), cv2.COLORMAP_INFERNO)

    if image is None:
        return right_side
    else:
        return np.concatenate((image, right_side), axis=1)


def run(data_filename, test_run, cam, output_path, model_path, model_type="dpt_beit_large_512", optimize=False, side=False, height=None,
        square=False, grayscale=False):
    """Run MonoDepthNN to compute depth maps.

    Args:
        input_path (str): path to input folder
        output_path (str): path to output folder
        model_path (str): path to saved model
        model_type (str): the model type
        optimize (bool): optimize the model to half-floats on CUDA?
        side (bool): RGB and depth side by side in output images?
        height (int): inference encoder image height
        square (bool): resize to a square resolution?
        grayscale (bool): use a grayscale colormap?
    """
    print("Initialize")

    # select device
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print("Device: %s" % device)

    model, transform, net_w, net_h = load_model(device, model_path, model_type, optimize, height, square)

    # get input
    # if input_path is not None:
    #     ''' Images have been placed in the input folder before.
    #     '''
    #     # image_names = glob.glob(os.path.join(input_path, "*"))
    #     # data[test_run][model_type]['cam2']

    #     image_names = glob.glob(os.path.join(input_path, "*"))
    #     num_images = len(image_names)
    # else:
    #     print("No input path specified. Grabbing images from camera.")



    # get input
    if cam is not None:
        ''' Images have been placed in the input folder before.
        '''
        # image_names = glob.glob(os.path.join(input_path, "*"))
        # data[test_run][model_type]['cam2']

        with open(data_filename, 'rb') as file:
            data = pickle.load(file)
            file.close()
            print('\'data\' loaded.')
    # else:
    #     print("No input path specified. Grabbing images from camera.")


    # create output folder
    if output_path is not None:
        os.makedirs(output_path, exist_ok=True)

    print("Start processing")

    if cam is not None:

        category = 'depth_estimate' + cam[-1]
        amount_frames = len(data[test_run][model_type][cam])

        if category not in data[test_run][model_type] or len(data[test_run][model_type][category]) != amount_frames:
            # print('\''+ str(category) + '\' not in \'data\'. Creating dictionary.')
            data[test_run][model_type][category] = []
            if output_path is None:
                print("Warning: No output path specified. Images will be processed but not shown or stored anywhere.")
            for picture_idx, picture in enumerate(data[test_run][model_type][cam]):

                # print("  Processing {} ({}/{})".format(image_name, index + 1, num_images))

                # check if depth estimation for this picture already exists in the output folder.
                
                # filename = os.path.join(output_path,
                #                         os.path.splitext(os.path.basename(image_name))[0]
                #                         + '-' + model_type  + '.png')
                # file_path = os.path.join(input_path, filename)
                # if os.path.exists(filename):
                #     # print(f'The file {filename} already exists in the output folder.')
                #     continue # skip the depth estimation for this input picture as it already exists   
                # else:
                    # print(f'The file {filename} does not exists in the output folder yet .')
                
        

                # input
                # original_image_rgb = utils.read_image(image_name)  # in [0, 1]
                # image = transform({"image": original_image_rgb})["image"]


                print('Processing picture number ' + str(picture_idx+1) + ' out of ' + str(amount_frames))

                img = cv2.cvtColor(picture, cv2.COLOR_BGR2RGB) / 255.0
                image = transform({"image": img})["image"]

                # compute
                with torch.no_grad():
                    prediction = process(device, model, model_type, image, (net_w, net_h), img.shape[1::-1],
                                        optimize, False)

                # output
                if output_path is not None:
                    # filename = os.path.join(
                    #     output_path, os.path.splitext(os.path.basename(image_name))[0] + '-' + model_type
                    # )
                    if not side:
                        # utils.write_depth(filename, prediction, grayscale, bits=2)
                        new_pic = utils.write_depth_dict_format(prediction, grayscale, bits=2)
                        data[test_run][model_type][category].append(new_pic)
            
                    else:
                        original_image_bgr = np.flip(original_image_rgb, 2)
                        content = create_side_by_side(original_image_bgr*255, prediction, grayscale)
                        cv2.imwrite(filename + ".png", content)
                    # utils.write_pfm(filename + ".pfm", prediction.astype(np.float32))

    else:
        with torch.no_grad():
            fps = 1
            video = VideoStream(0).start()
            time_start = time.time()
            frame_index = 0
            while True:
                frame = video.read()
                if frame is not None:
                    original_image_rgb = np.flip(frame, 2)  # in [0, 255] (flip required to get RGB)
                    image = transform({"image": original_image_rgb/255})["image"]

                    prediction = process(device, model, model_type, image, (net_w, net_h),
                                         original_image_rgb.shape[1::-1], optimize, True)

                    original_image_bgr = np.flip(original_image_rgb, 2) if side else None
                    content = create_side_by_side(original_image_bgr, prediction, grayscale)
                    cv2.imshow('MiDaS Depth Estimation - Press Escape to close window ', content/255)

                    if output_path is not None:
                        filename = os.path.join(output_path, 'Camera' + '-' + model_type + '_' + str(frame_index))
                        cv2.imwrite(filename + ".png", content)

                    alpha = 0.1
                    if time.time()-time_start > 0:
                        fps = (1 - alpha) * fps + alpha * 1 / (time.time()-time_start)  # exponential moving average
                        time_start = time.time()
                    print(f"\rFPS: {round(fps,2)}", end="")

                    if cv2.waitKey(1) == 27:  # Escape key
                        break

                    frame_index += 1
        print()


    # save data to pickle file
    with open("data.pickle", "wb") as file:
        pickle.dump(data, file, pickle.HIGHEST_PROTOCOL)
        file.close()

    print("Finished")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument('-i', '--input_path',
                        default=None,
                        help='Folder with input images (if no input path is specified, images are tried to be grabbed '
                             'from camera)'
                        )

    parser.add_argument('-o', '--output_path',
                        default=None,
                        help='Folder for output images'
                        )

    parser.add_argument('-m', '--model_weights',
                        default=None,
                        help='Path to the trained weights of model'
                        )

    parser.add_argument('-t', '--model_type',
                        default='dpt_beit_large_512',
                        help='Model type: '
                             'dpt_beit_large_512, dpt_beit_large_384, dpt_beit_base_384, dpt_swin2_large_384, '
                             'dpt_swin2_base_384, dpt_swin2_tiny_256, dpt_swin_large_384, dpt_next_vit_large_384, '
                             'dpt_levit_224, dpt_large_384, dpt_hybrid_384, midas_v21_384, midas_v21_small_256 or '
                             'openvino_midas_v21_small_256'
                        )

    parser.add_argument('-s', '--side',
                        action='store_true',
                        help='Output images contain RGB and depth images side by side'
                        )

    parser.add_argument('--optimize', dest='optimize', action='store_true', help='Use half-float optimization')
    parser.set_defaults(optimize=False)

    parser.add_argument('--height',
                        type=int, default=None,
                        help='Preferred height of images feed into the encoder during inference. Note that the '
                             'preferred height may differ from the actual height, because an alignment to multiples of '
                             '32 takes place. Many models support only the height chosen during training, which is '
                             'used automatically if this parameter is not set.'
                        )
    parser.add_argument('--square',
                        action='store_true',
                        help='Option to resize images to a square resolution by changing their widths when images are '
                             'fed into the encoder during inference. If this parameter is not set, the aspect ratio of '
                             'images is tried to be preserved if supported by the model.'
                        )
    parser.add_argument('--grayscale',
                        action='store_true',
                        help='Use a grayscale colormap instead of the inferno one. Although the inferno colormap, '
                             'which is used by default, is better for visibility, it does not allow storing 16-bit '
                             'depth values in PNGs but only 8-bit ones due to the precision limitation of this '
                             'colormap.'
                        )

    args = parser.parse_args()


    if args.model_weights is None:
        args.model_weights = default_models[args.model_type]

    # set torch options
    torch.backends.cudnn.enabled = True
    torch.backends.cudnn.benchmark = True

    # compute depth maps
    run(args.input_path, args.output_path, args.model_weights, args.model_type, args.optimize, args.side, args.height,
        args.square, args.grayscale)
