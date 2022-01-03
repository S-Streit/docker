# coding=utf-8
import json
import sys
import os
import argparse
import uuid
from datetime import datetime
from path import Path

def get_commit(repo_path):
    git_folder = Path(repo_path,'.git')
    head_name = Path(git_folder, 'HEAD').read_text().split('\n')[0].split(' ')[-1]
    head_ref = Path(git_folder,head_name)
    commit = head_ref.read_text().replace('\n','')

    return commit


outer_command_config = "/usr/local/mount/config/hqc_command_config.json"
default_command_config = "/usr/local/wrapper/hqc/default_command_config.json"

# open config file for "RUN-COMMAND"
if os.path.isfile(outer_command_config):
    with open(outer_command_config) as json_file:
        hqc_cmd_config = json.loads(json_file.read())
else:
    with open(default_command_config) as json_file:
        hqc_cmd_config = json.loads(json_file.read())

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

    output_path = hqc_cmd_config["output_path"] + out_id # set output folder
    # choose config file :
    # use config file mounted from outside OR ELSE use default file from "hqc_command_config.json"

    config_path = hqc_cmd_config["config_path"]

    base_path = "-p " + hqc_cmd_config["base_path"] if len(hqc_cmd_config["base_path"]) > 1 else "" # default in qc_pipeline: "" (empty string)
    force = "-f" if hqc_cmd_config["force"] else "" # force overwrite existing output files: default in qc_pipeline: False
    batch_size = "-b" + int(hqc_cmd_config["batch_size"]) if int(hqc_cmd_config["batch_size"]) > 0 else "" # default in config: 0 leads to default in qc_pipeline: float("inf")
    n_threads = "-n" + int(hqc_cmd_config["n_threads"]) if int(hqc_cmd_config["n_threads"]) > 1 else "" # default in qc_pipeline: 1
    symlink_off = "-s" if hqc_cmd_config["symlink_off"] else "" # default in qc_pipeline: True

    # get filename from command line arguments:

    # create input path:
    input_folder = "/usr/local/mount/data"
    src_path = "/usr/local/src"
    wrapper_path = "/usr/local/wrapper"
    # create correct command to start HQC:
    command_hqc = "python /usr/local/src/qc_pipeline.py {0}/*.svs -o {1} -c {2} {3} {4} {5}".format(input_folder, output_path, config_path, n_threads, force, base_path)
    
    algorithm = "HistoQC"
    hqc_version = get_commit(src_path)
    wrapper_version = get_commit(wrapper_path)
    print("HQC V.:", hqc_version)
    print("Wrapper V.:", wrapper_version)

    start_time = datetime.now().strftime('%d-%m-%Y %H:%M:%S')

    print(command_hqc)
    # start HQC:
    os.system(command_hqc)