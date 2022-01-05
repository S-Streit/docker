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
import yaml


SOURCE_PATH = "/usr/local/src"
OUTER_CONFIG = False
DEFAULT_CONFIG = False
FINISHED = False
START_TIME = datetime.now().strftime('%d-%m-%Y %H:%M:%S')
END_TIME = 'None'

def parse_cmd_config(outer_command_config, default_command_config):
    # open mounted config file or use default for "RUN-COMMAND"
    if os.path.isfile(outer_command_config):
        with open(outer_command_config) as json_file:
            cmd_config = json.loads(json_file.read())
            OUTER_CONFIG = True
    else:
        with open(default_command_config) as json_file:
            cmd_config = json.loads(json_file.read())
            DEFAULT_CONFIG = True

    return cmd_config


def get_commit(repo_path):
    git_folder = Path(repo_path,'.git')
    head_name = Path(git_folder, 'HEAD').read_text().split('\n')[0].split(' ')[-1]
    head_ref = Path(git_folder,head_name)
    commit = head_ref.read_text().replace('\n','')

    return commit
def get_repo_name(repo_path):
    git_folder = Path(repo_path,'.git/config')
    name = git_folder.read_text().split('Pacific89/')[1].split('\n')[0].split('.')[0]
    print("NAME", name)

    return name

def save_config_info(cmd_config, start_command):

    cfg_dict = {}
    meta_cfg_dict = {}

    meta_cfg_dict["algorithm"] = get_repo_name(cmd_config["src_path"])
    meta_cfg_dict["version"] = get_commit(cmd_config["src_path"])
    meta_cfg_dict["wrapper_version"] = get_commit(cmd_config["wrapper_path"])
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

    json_file = save_config_path + "/start_config.json"
    if os.path.isfile(json_file):
        os.remove(json_file)

    with open(json_file, 'w') as cfg_json:
        json.dump(cfg_dict, cfg_json)

    # copy config file
    if cmd_config["config_path"] and os.path.isfile(cmd_config["config_path"]):
        shutil.copy2(cmd_config["config_path"], save_config_path)

def hovernet():

    outer_command_config = "/usr/local/mount/config/hover_command_config.json"
    default_command_config = "/usr/local/wrapper/hover-net/hover_command_config.json"
    cmd_config = parse_cmd_config(outer_command_config, default_command_config)

    parser = argparse.ArgumentParser(description='')
    # parser.add_argument('input_folder',
    #             help="one input folder that contains a WSI: example.svs",
    #             nargs=1)
    parser.add_argument('-c', '--config', help="json string with config parameters: \n Defaults: {0}".format(cmd_config), type=str)
    # parser.add_argument('-ch', '--call_hovernet', help="call create_patches.py", default=False, action="store_true")
    parser.add_argument('-u', '--uuid', help="UUID for current algorithm run", type=str, default="")

    args = parser.parse_args()
    print(args)

    hovernet_base_command = "python3 /usr/local/src/run_infer.py"

    if not args.uuid:
        out_id = uuid.uuid4().hex
    else:
        out_id = args.uuid

    # add UUID to output directory
    cmd_config["output_path"] = cmd_config["output_path"] + out_id

    gpu = " --gpu=" + cmd_config["gpu"]
    types =  " --nr_types=" + str(cmd_config["types"])
    type_info_path = " --type_info_path=" + cmd_config["config_path"]
    batch_size = " --batch_size=" + str(cmd_config["batch_size"])
    mode = " --model_mode=" + cmd_config["mode"]
    model_path = " --model_path=" + cmd_config["model_path"]
    nr_inf_workers = " --nr_inference_workers=" + str(cmd_config["nr_inf_workers"])
    nr_post_workers = " --nr_post_proc_workers=" + str(cmd_config["nr_post_workers"])
    wsi = cmd_config["wsi"]
    in_dir = " --input_dir=" + cmd_config["input_path"]
    out_dir = " --output_dir=" + cmd_config["output_path"] # set output folder with UUID
    save_thumb = " --save_thumb" if cmd_config["save_thumb"] else ""
    proc_mag = " --proc_mag=" + str(cmd_config["proc_mag"])
    save_mask = " --save_mask" if cmd_config["save_mask"] else ""

    start_cmd = hovernet_base_command + gpu + types + type_info_path + batch_size + mode + model_path + nr_inf_workers + nr_post_workers + wsi + in_dir + out_dir + save_thumb + save_mask + proc_mag
    
    run_project(start_cmd, cmd_config)

def hqc():
    outer_command_config = "/usr/local/mount/config/hqc_command_config.json"
    default_command_config = "/usr/local/wrapper/hqc/default_command_config.json"

    cmd_config = parse_cmd_config(outer_command_config, default_command_config)

    parser = argparse.ArgumentParser(description='')
    # parser.add_argument('input_pattern',
    #             help="one input file: example.svs",
    #             nargs="*")

    parser.add_argument('-c', '--config', help="json string with config parameters: \n Defaults: {0}".format(cmd_config), default=default_command_config, type=str)
    parser.add_argument('-u', '--uuid', help="UUID for current algorithm run", type=str, default="")

    args = parser.parse_args()

    if args.config:
        # try to read dict from json string and update default values
        try:
            config_dict = json.loads(args.config)
            cmd_config.update(config_dict)
        except:
            print("Not a valid json config string. Using default")
    
    if not args.uuid:
        out_id = uuid.uuid4().hex
    else:
        out_id = args.uuid

    cmd_config["output_path"] = cmd_config["output_path"] + "/" + out_id # set output folder in command_dict
    output_path = cmd_config["output_path"] # set output folder
    # choose config file :
    # use config file mounted from outside OR ELSE use default file from "hqc_command_config.json"

    config_path = cmd_config["config_path"]

    base_path = "-p " + cmd_config["base_path"] if len(cmd_config["base_path"]) > 1 else "" # default in qc_pipeline: "" (empty string)
    force = "-f" if cmd_config["force"] else "" # force overwrite existing output files: default in qc_pipeline: False
    batch_size = "-b" + int(cmd_config["batch_size"]) if int(cmd_config["batch_size"]) > 0 else "" # default in config: 0 leads to default in qc_pipeline: float("inf")
    n_threads = "-n" + int(cmd_config["n_threads"]) if int(cmd_config["n_threads"]) > 1 else "" # default in qc_pipeline: 1
    symlink_off = "-s" if cmd_config["symlink_off"] else "" # default in qc_pipeline: True

    input_folder = cmd_config["input_path"]
    src_path = cmd_config["src_path"]
    wrapper_path = cmd_config["wrapper_path"]

    # create correct command to start HQC:
    start_cmd = "python /usr/local/src/qc_pipeline.py {0}/*.svs -o {1} -c {2} {3} {4} {5}".format(input_folder, output_path, config_path, n_threads, force, base_path)

    run_project(start_cmd, cmd_config)

def _clam_create_patches(cmd_config):

    input_folder = cmd_config["input_path"]
    svs_files = glob(input_folder + "/*.svs")
    print("Detected Files: ", svs_files)
    if len(svs_files) == 1:
        file_name = svs_files[0]
    else:
        print("More than one file detected: {0} \n Please Check mounted directory")
    # print("File Name:", file_name)
    patch_size = cmd_config["patch_size"] # set patch size (128 needed for ARA-NET / 224 needed for VGG16 feature extraction)
    seg = "--seg" if json.loads(cmd_config["seg"].lower()) else ""
    patch = "--patch" if json.loads(cmd_config["patch"].lower()) else ""
    stitch = "--stitch" if json.loads(cmd_config["stitch"].lower()) else ""
    no_auto_skip = "--no_auto_skip" if json.loads(cmd_config["no_auto_skip"].lower()) else ""
    preset = "--preset preset.csv"
    patch_level = "--patch_level {0}".format(int(cmd_config["patch_level"])) # downsample level for patch calculation
    process_list = "--process_list process_list.csv"
    output_path = cmd_config["output_path"] # set output folder

    print("CONFIG:")
    print(cmd_config)
    # get filename from command line arguments:
    # create input path:
    input_path = file_name
    # create correct command to create patch coordinates using CLAM:
    start_cmd = "python3 /usr/local/src/create_patches_fp.py --source {0} --save_dir {1} --patch_size {2} {3} {4} {5}".format(input_folder, output_path, patch_size, seg, patch, stitch)

    return start_cmd, cmd_config

def _clam_extract_features(cmd_config, patch_run_dir):

    input_folder = cmd_config["input_path"]
    svs_files = glob(input_folder + "/*.svs")
    output_path = cmd_config["output_path"] # set output folder
    feat_dir = output_path + "/features"
    csv_path = patch_run_dir + "/process_list_autogen.csv"
    batch_size = cmd_config["batch_size"]
    data_h5_dir = patch_run_dir

    start_cmd = "CUDA_VISIBLE_DEVICES=0 python3 /usr/local/src/extract_features_fp.py --data_slide_dir {0} --csv_path {1} --feat_dir {2} --data_h5_dir {3} --batch_size={4} --slide_ext .svs".format(input_folder, csv_path, feat_dir, data_h5_dir, batch_size)

    return start_cmd, cmd_config

def _clam_create_heatmaps(cmd_config):

    # yaml_dict = yaml.safe_load(cmd_config["heatmap_config_path"])
    with open(cmd_config["heatmap_config_path"]) as yaml_file:
        yaml_dict = yaml.load(yaml_file, Loader=yaml.FullLoader)
    
    yaml_dict["exp_arguments"]["raw_save_dir"] = cmd_config["output_path"] + "/raw"
    yaml_dict["exp_arguments"]["production_save_dir"] = cmd_config["output_path"] + "/production"

    yaml_save_path = cmd_config["output_path"] + "/" + "heatmap_config.yaml"
    with open(yaml_save_path, 'w') as yaml_file:
        yaml.dump(yaml_dict, yaml_file)
        
    heatmap_config = yaml_save_path
    start_cmd = "python3 /usr/local/src/create_heatmaps.py --config {0}".format(heatmap_config)

    return start_cmd, cmd_config

def clam():


    parser = argparse.ArgumentParser(description='')
    # parser.add_argument('input_folder',
    #             help="one input folder that contains a WSI: example.svs",
    #             nargs=1)
    parser.add_argument('-c', '--config', help="json string with config parameters", type=str)
    parser.add_argument('-cp', '--create_patches', help="call create_patches.py", default=False, action="store_true")
    parser.add_argument('-ef', '--extract_features', help="call extract_features.py",default=False, action="store_true")
    parser.add_argument('-ch', '--create_heatmaps', help="call create_heatmaps.py", default=False, action="store_true")
    parser.add_argument('-a', '--all', help="Call Full Pipeline: Create Patches, Extract Features and Create Heatmaps with default configuration", default=False, action="store_true")
    parser.add_argument('-u', '--uuid', help="UUID for current algorithm run", type=str, default="")
    parser.add_argument('--patch_run_dir', help='UUID of extract-patches run', type=str, default="")

    args = parser.parse_args()
    print(args)

    outer_command_config = "/usr/local/mount/config/clam_command_config.json"
    default_command_config = "/usr/local/wrapper/clam/clam_command_config.json"

    cmd_config = parse_cmd_config(outer_command_config, default_command_config)

    if args.patch_run_dir:
        patch_run_dir = cmd_config["output_path"] + "/" + args.patch_run_dir
    
    if not args.uuid:
        out_id = uuid.uuid4().hex
    else:
        out_id = args.uuid

    cmd_config["output_path"] = cmd_config["output_path"] + "/" + out_id # set output folder in command_dict

    if args.create_patches:
        start_cmd, cmd_config = _clam_create_patches(cmd_config)
        run_project(start_cmd, cmd_config)
    if args.extract_features:
        if os.path.isdir(patch_run_dir):
            start_cmd, cmd_config = _clam_extract_features(cmd_config, patch_run_dir)
            run_project(start_cmd, cmd_config)
        else:
            print("Please Check Patch Directory Path: ", args.patch_run_dir)
        
    if args.create_heatmaps:
        start_cmd, cmd_config = _clam_create_heatmaps(cmd_config)
        # run_project(start_cmd, cmd_config)

    # if args.all:
    #     call_create_patches(args)
    #     call_extract_features(args)
    #     call_create_heatmaps(args)

def run_project(start_cmd, cmd_config):

    save_config_info(cmd_config, start_cmd)
    return_code = os.system(start_cmd)

    print("Return Code: ", return_code)
    if return_code == 0:
        print("FINISHED!")
        FINISHED = True
        END_TIME = datetime.now().strftime('%d-%m-%Y %H:%M:%S')
        save_config_info(cmd_config, start_cmd)

if __name__ == "__main__":

    repo_name = get_repo_name(SOURCE_PATH)
    print("Preparing {0}".format(repo_name))

    if "HistoQC" in repo_name:
        hqc()
    elif "hover_net" in repo_name:
        hovernet()
    elif "CLAM" in repo_name:
        clam()