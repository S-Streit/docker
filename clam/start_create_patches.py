import json
import sys
import os
import argparse
import h5py
import pandas as pd
from glob import glob

# open config file for "RUN-COMMAND"
with open("/usr/local/wrapper/clam/clam_command_config.json") as json_file:
    clam_config = json.loads(json_file.read())

def output_to_json(output_path):

    patch_path = output_path + "/patches"
    print("patch_path:", patch_path)
    h5file = os.listdir(patch_path)[0]
    h5_path = patch_path + "/" + h5file

    temp_list = []
    with h5py.File(h5_path, 'r') as f:
        num_patches = f['coords'].shape[0]
        # if keys == 2: COORDS, FEATURES
        if len(f.keys()) == 2:
            for patch_num in range(num_patches):
                patch_id = "patch_{}".format(patch_num)
                d_ = {'patch_id' : patch_id, 'coord_x' : f['coords'][patch_num][0], 'coords_y' : f['coords'][patch_num][1], 'features' :f['features'][patch_num]}
                temp_list.append(d_)
        # ELSE: store COORDS only
        else:
            for patch_num in range(num_patches):
                patch_id = "patch_{}".format(patch_num)
                d_ = {'patch_id' : patch_id, 'coord_x' : f['coords'][patch_num][0], 'coords_y' : f['coords'][patch_num][1]}
                temp_list.append(d_)

    out_json_path = output_path + "results.json"
    df = pd.DataFrame.from_dict(temp_list).set_index('patch_id')
    df.to_json(out_json_path, orient='index')

def call_create_patches(args):

    if args.config:
        # try to read dict from json string and update default values
        try:
            config_dict = json.loads(args.config)
            clam_config.update(config_dict)
        except:
            print("Not a valid json config string. Using default")

    # file_name = args.input_folder[0]
    input_folder = "/usr/local/data"
    svs_files = glob(input_folder + "/*.svs")
    print("Detected Files: ", svs_files)
    if len(svs_files) == 1:
        file_name = svs_files[0]
    else:
        print("More than one file detected: {0} \n Please Check mounted directory")
    # print("File Name:", file_name)
    patch_size = clam_config["patch_size"] # set patch size (128 needed for ARA-NET / 224 needed for VGG16 feature extraction)
    seg = "--seg" if json.loads(clam_config["seg"].lower()) else ""
    patch = "--patch" if json.loads(clam_config["patch"].lower()) else ""
    stitch = "--stitch" if json.loads(clam_config["stitch"].lower()) else ""
    no_auto_skip = "--no_auto_skip" if json.loads(clam_config["no_auto_skip"].lower()) else ""
    preset = "--preset preset.csv"
    patch_level = "--patch_level {0}".format(int(clam_config["patch_level"])) # downsample level for patch calculation
    process_list = "--process_list process_list.csv"
    output_path = clam_config["output_path"] # set output folder

    print("CONFIG:")
    print(clam_config)
    # get filename from command line arguments:
    # create input path:
    input_path = file_name
    # create correct command to create patch coordinates using CLAM:
    clam_command = "python3 /usr/local/src/clam/create_patches_fp.py --source {0} --save_dir {1} --patch_size {2} {3} {4} {5}".format(input_folder, output_path, patch_size, seg, patch, stitch)
    # start CLAM:
    os.system(clam_command)
    print(clam_command)
    output_to_json(output_path)


def call_extract_features(args):

    # input_folder = args.input_folder[0]
    input_folder = "/usr/local/data"
    svs_files = glob(input_folder + "/*.svs")
    input_path = input_folder
    output_path = clam_config["output_path"] # set output folder
    feat_dir = output_path + "/features"
    csv_path = output_path + "/process_list_autogen.csv"
    data_h5_dir = output_path

    clam_command = "CUDA_VISIBLE_DEVICES=0 python3 /usr/local/src/clam/extract_features_fp.py --data_slide_dir {0} --csv_path {1} --feat_dir {2} --data_h5_dir {3} --slide_ext .svs".format(input_folder, csv_path, feat_dir, data_h5_dir)

    os.system(clam_command)
    print(clam_command)

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='')
    # parser.add_argument('input_folder',
    #             help="one input folder that contains a WSI: example.svs",
    #             nargs=1)
    parser.add_argument('-c', '--config', help="json string with config parameters: \n Defaults: {0}".format(clam_config), type=str)
    parser.add_argument('-cp', '--create_patches', help="call create_patches.py", default=False, action="store_true")
    parser.add_argument('-ef', '--extract_features', help="call extract_features.py",default=False, action="store_true")

    args = parser.parse_args()
    print(args)

    if args.create_patches:
        call_create_patches(args)
    elif args.extract_features:   
        call_extract_features(args)