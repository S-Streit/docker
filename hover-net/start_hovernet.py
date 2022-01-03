import json
import sys
import os
import argparse
import h5py
import pandas as pd
from glob import glob
import uuid

outer_command_config = "/usr/local/mount/config/hover_command_config.json"
default_command_config = "/usr/local/wrapper/hover-net/hover_command_config.json"
# open config file for "RUN-COMMAND"
if os.path.isfile(outer_command_config):
    with open(outer_command_config) as json_file:
        hover_config = json.loads(json_file.read())
else:
    with open(default_command_config) as json_file:
        hover_config = json.loads(json_file.read())

def call_hovernet(args):

    hovernet_base_command = "python3 /usr/local/src/run_infer.py"

    if not args.uuid:
        out_id = uuid.uuid4().hex
    else:
        out_id = args.uuid

    gpu = " --gpu=" + hover_config["gpu"]
    types =  " --nr_types=" + str(hover_config["types"])
    type_info_path = " --type_info_path=" + hover_config["type_info_path"]
    batch_size = " --batch_size=" + str(hover_config["batch_size"])
    mode = " --model_mode=" + hover_config["mode"]
    model_path = " --model_path=" + hover_config["model_path"]
    nr_inf_workers = " --nr_inference_workers=" + str(hover_config["nr_inf_workers"])
    nr_post_workers = " --nr_post_proc_workers=" + str(hover_config["nr_post_workers"])
    wsi = hover_config["wsi"]
    in_dir = " --input_dir=" + hover_config["in_dir"]
    out_dir = " --output_dir=" + hover_config["out_dir"] + out_id # set output folder with UUID
    save_thumb = " --save_thumb" if hover_config["save_thumb"] else ""
    proc_mag = " --proc_mag=" + str(hover_config["proc_mag"])
    save_mask = " --save_mask" if hover_config["save_mask"] else ""

    hovernet_command = hovernet_base_command + gpu + types + type_info_path + batch_size + mode + model_path + nr_inf_workers + nr_post_workers + wsi + in_dir + out_dir + save_thumb + save_mask + proc_mag
    os.system(hovernet_command)
    print(hovernet_command)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='')
    # parser.add_argument('input_folder',
    #             help="one input folder that contains a WSI: example.svs",
    #             nargs=1)
    parser.add_argument('-c', '--config', help="json string with config parameters: \n Defaults: {0}".format(hover_config), type=str)
    parser.add_argument('-ch', '--call_hovernet', help="call create_patches.py", default=False, action="store_true")
    parser.add_argument('-u', '--uuid', help="UUID for current algorithm run", type=str, default="")

    args = parser.parse_args()
    print(args)


    if args.call_hovernet:
        call_hovernet(args)