# Monocular Depth Estimation: Performance on Drone Data
Investigating the accuracy of depth estimations computed from single images using MiDaS (https://github.com/isl-org/MiDaS) and drone footage captured with Intel Realsense. 


## Setup

### Setting up the environment/dependencies
First we will create an environment that contains all necessary libraries:

    conda env create -f environment.yaml
    conda activate midas-py310

### Setting up the weights
Download the weights from [https://github.com/isl-org/MiDaS] and place them in the 'weights' folder inside the MiDaS folder.

### Setting up the data for the analysis
Copy the rosbag (.bag) file into the drone data folder.


### Running MiDaS
To run midas:

    python run.py --model_type <model_type> --input_path input --output_path output


e.g. if dpt_beit_large_512.pt is chosen:
    
    python run.py --model_type dpt_beit_large_512 --input_path input --output_path output


To run it from the camera:

    python run.py --model_type <model_type> --side