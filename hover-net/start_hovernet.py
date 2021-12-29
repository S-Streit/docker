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

def call_hovernet(args):

    hovernet_base_command = "python3 /usr/local/src/run_infer.py"

    gpu = " --gpu='0,1'"
    types = " --nr_types=6"
    type_info = " --type_info_path=/usr/local/src/type_info.json"
    batch_size = " --batch_size=64"
    mode = " --model_mode=fast"
    model_path = " --model_path=/usr/local/models/pannuke/hovernet_fast_pannuke_type_tf2pytorch.tar"
    nr_inf_workers = " --nr_inference_workers=8"
    nr_post_workers = " --nr_post_proc_workers=16"
    wsi = " wsi"
    in_dir = " --input_dir=/usr/local/data/"
    out_dir = " --output_dir=/usr/local/data/results/hover-net"
    save_thumb = " --save_thumb"
    proc_mag = " --proc_mag=40"
    save_mask = " --save_mask"

    hovernet_command = hovernet_base_command + gpu + types + type_info + batch_size + mode + model_path + nr_inf_workers + nr_post_workers + wsi + in_dir + out_dir + save_thumb + save_mask + proc_mag
    os.system(hovernet_command)
    print(hovernet_command)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='')
    # parser.add_argument('input_folder',
    #             help="one input folder that contains a WSI: example.svs",
    #             nargs=1)
    parser.add_argument('-c', '--config', help="json string with config parameters: \n Defaults: {0}".format(clam_config), type=str)
    parser.add_argument('-ch', '--call_hovernet', help="call create_patches.py", default=False, action="store_true")

    args = parser.parse_args()
    print(args)

    if args.call_hovernet:
        call_hovernet(args)