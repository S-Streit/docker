# coding=utf-8
import json
import sys
import os
import argparse
import uuid
from datetime import datetime
from pathlib import Path
import shutil

outer_command_config = "/usr/local/mount/config/hqc_command_config.json"
default_command_config = "/usr/local/wrapper/hqc/default_command_config.json"

OUTER_CONFIG = False
DEFAULT_CONFIG = False
FINISHED = False

# open config file for "RUN-COMMAND"
if os.path.isfile(outer_command_config):
    with open(outer_command_config) as json_file:
        hqc_cmd_config = json.loads(json_file.read())
        OUTER_CONFIG = True
else:
    with open(default_command_config) as json_file:
        hqc_cmd_config = json.loads(json_file.read())
        DEFAULT_CONFIG = True

def get_commit(repo_path):
    git_folder = Path(repo_path,'.git')
    head_name = Path(git_folder, 'HEAD').read_text().split('\n')[0].split(' ')[-1]
    head_ref = Path(git_folder,head_name)
    commit = head_ref.read_text().replace('\n','')

    return commit


def save_config_info(hqc_cmd_config, start_command):

    cfg_dict = {}
    meta_cfg_dict = {}

    meta_cfg_dict["algorithm"] = "HistoQC"
    meta_cfg_dict["version"] = get_commit(src_path)
    meta_cfg_dict["wrapper_version"] = get_commit(wrapper_path)
    meta_cfg_dict["finished"] = FINISHED
    meta_cfg_dict["default_cfg"] = DEFAULT_CONFIG
    meta_cfg_dict["outer_cfg"] = OUTER_CONFIG
    meta_cfg_dict["start_time"] = datetime.now().strftime('%d-%m-%Y %H:%M:%S')
    meta_cfg_dict["start_command"] = start_command

    save_config_path = hqc_cmd_config["output_path"] + "/config"
    cfg_dict["meta_info"] = meta_cfg_dict
    cfg_dict["command_cfg"] = hqc_cmd_config

    if not os.path.isdir(save_config_path):
        os.makedirs(save_config_path)

    with open(save_config_path + "/start_config.json", 'w') as cfg_json:
        json.dump(cfg_dict, cfg_json)

    # copy config.ini for HQC pipeline
    shutil.copy2(hqc_cmd_config["config_path"], save_config_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='')
    # parser.add_argument('input_pattern',
    #             help="one input file: example.svs",
    #             nargs="*")

    parser.add_argument('-c', '--config', help="json string with config parameters: \n Defaults: {0}".format(hqc_cmd_config), default=default_command_config, type=str)
    parser.add_argument('-u', '--uuid', help="UUID for current algorithm run", type=str, default="")

    args = parser.parse_args()

    if args.config:
        # try to read dict from json string and update default values
        try:
            config_dict = json.loads(args.config)
            hqc_cmd_config.update(config_dict)
        except:
            print("Not a valid json config string. Using default")
    
    if not args.uuid:
        out_id = uuid.uuid4().hex
    else:
        out_id = args.uuid

    hqc_cmd_config["output_path"] = hqc_cmd_config["output_path"] + "/" + out_id # set output folder in command_dict
    output_path = hqc_cmd_config["output_path"] # set output folder
    # choose config file :
    # use config file mounted from outside OR ELSE use default file from "hqc_command_config.json"

    config_path = hqc_cmd_config["config_path"]

    base_path = "-p " + hqc_cmd_config["base_path"] if len(hqc_cmd_config["base_path"]) > 1 else "" # default in qc_pipeline: "" (empty string)
    force = "-f" if hqc_cmd_config["force"] else "" # force overwrite existing output files: default in qc_pipeline: False
    batch_size = "-b" + int(hqc_cmd_config["batch_size"]) if int(hqc_cmd_config["batch_size"]) > 0 else "" # default in config: 0 leads to default in qc_pipeline: float("inf")
    n_threads = "-n" + int(hqc_cmd_config["n_threads"]) if int(hqc_cmd_config["n_threads"]) > 1 else "" # default in qc_pipeline: 1
    symlink_off = "-s" if hqc_cmd_config["symlink_off"] else "" # default in qc_pipeline: True

    input_folder = hqc_cmd_config["input_path"]
    src_path = hqc_cmd_config["src_path"]
    wrapper_path = hqc_cmd_config["wrapper_path"]

    # create correct command to start HQC:
    start_command = "python /usr/local/src/qc_pipeline.py {0}/*.svs -o {1} -c {2} {3} {4} {5}".format(input_folder, output_path, config_path, n_threads, force, base_path)

    save_config_info(hqc_cmd_config, start_command)
    # start HQC:
    return_code = os.system(start_command)

    if return_code == 0:
        FINISHED = True
        save_config_info(hqc_cmd_config, start_command)


