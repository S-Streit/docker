import json
import sys
import os
import argparse
import h5py
import pandas as pd
from glob import glob
import uuid
from datetime import datetime
from pathlib import Path
import shutil

outer_command_config = "/usr/local/mount/config/hover_command_config.json"
default_command_config = "/usr/local/wrapper/hover-net/hover_command_config.json"

OUTER_CONFIG = False
DEFAULT_CONFIG = False
FINISHED = False
START_TIME = datetime.now().strftime('%d-%m-%Y %H:%M:%S')
END_TIME = 'None'

# open mounted config file or use default for "RUN-COMMAND"
if os.path.isfile(outer_command_config):
    with open(outer_command_config) as json_file:
        cmd_config = json.loads(json_file.read())
        OUTER_CONFIG = True
else:
    with open(default_command_config) as json_file:
        cmd_config = json.loads(json_file.read())
        DEFAULT_CONFIG = True

def save_config_info(cmd_config, start_command):

    cfg_dict = {}
    meta_cfg_dict = {}

    meta_cfg_dict["algorithm"] = "Hover-Net"
    meta_cfg_dict["version"] = get_commit(src_path)
    meta_cfg_dict["wrapper_version"] = get_commit(wrapper_path)
    meta_cfg_dict["finished"] = FINISHED
    meta_cfg_dict["default_cfg"] = DEFAULT_CONFIG
    meta_cfg_dict["outer_cfg"] = OUTER_CONFIG
    meta_cfg_dict["start_time"] = START_TIME
    if FINISHED:
        meta_cfg_dict["end_time"] = END_TIME
    meta_cfg_dict["start_command"] = start_command

    save_config_path = cmd_config["output_path"] + "/config"
    cfg_dict["meta_info"] = meta_cfg_dict
    cfg_dict["command_cfg"] = cmd_config

    if not os.path.isdir(save_config_path):
        os.makedirs(save_config_path)

    with open(save_config_path + "/start_config.json", 'w') as cfg_json:
        json.dump(cfg_dict, cfg_json)

    # copy config file
    shutil.copy2(cmd_config["config_path"], save_config_path)

def call_hovernet(args):

    hovernet_base_command = "python3 /usr/local/src/run_infer.py"

    if not args.uuid:
        out_id = uuid.uuid4().hex
    else:
        out_id = args.uuid

    # add UUID to output directory
    cmd_config["output_dir"] = cmd_config["output_dir"] + out_id

    gpu = " --gpu=" + cmd_config["gpu"]
    types =  " --nr_types=" + str(cmd_config["types"])
    type_info_path = " --type_info_path=" + cmd_config["config_path"]
    batch_size = " --batch_size=" + str(cmd_config["batch_size"])
    mode = " --model_mode=" + cmd_config["mode"]
    model_path = " --model_path=" + cmd_config["model_path"]
    nr_inf_workers = " --nr_inference_workers=" + str(cmd_config["nr_inf_workers"])
    nr_post_workers = " --nr_post_proc_workers=" + str(cmd_config["nr_post_workers"])
    wsi = cmd_config["wsi"]
    in_dir = " --input_dir=" + cmd_config["input_dir"]
    out_dir = " --output_dir=" + cmd_config["output_dir"] # set output folder with UUID
    save_thumb = " --save_thumb" if cmd_config["save_thumb"] else ""
    proc_mag = " --proc_mag=" + str(cmd_config["proc_mag"])
    save_mask = " --save_mask" if cmd_config["save_mask"] else ""

    start_command = hovernet_base_command + gpu + types + type_info_path + batch_size + mode + model_path + nr_inf_workers + nr_post_workers + wsi + in_dir + out_dir + save_thumb + save_mask + proc_mag
    
    save_config_info(cmd_config, start_command)
    return_code = os.system(hovernet_command)

    if return_code == 0:
        FINISHED = True
        END_TIME = datetime.now().strftime('%d-%m-%Y %H:%M:%S')
        save_config_info(cmd_config, start_command)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='')
    # parser.add_argument('input_folder',
    #             help="one input folder that contains a WSI: example.svs",
    #             nargs=1)
    parser.add_argument('-c', '--config', help="json string with config parameters: \n Defaults: {0}".format(cmd_config), type=str)
    parser.add_argument('-ch', '--call_hovernet', help="call create_patches.py", default=False, action="store_true")
    parser.add_argument('-u', '--uuid', help="UUID for current algorithm run", type=str, default="")

    args = parser.parse_args()
    print(args)


    if args.call_hovernet:
        call_hovernet(args)